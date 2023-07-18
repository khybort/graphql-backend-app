from datetime import datetime

from mongoengine import signals

from core.auth.crud.account import AccountCrud
from core.auth.crud.role import RoleCrud
from core.auth.enum import NotStrongPasswordErrorMessage
from core.auth.models.user import User
from core.auth.utilities.auth_handler import AuthHandler
from core.auth.utilities.utilities import is_strong_password
from core.exception import NotAddExistingUser, NotStrongPasswordError
from core.lib.basecrud import Crud


class UserCrud(Crud):
    model = User

    @classmethod
    def create(cls, user: dict, signal_kwargs: None | dict = None) -> User:
        if cls.find(email=user["email"]):
            raise NotAddExistingUser()
        role = RoleCrud.get(id=user.pop("role"))

        user["account"] = AccountCrud.create(user["account"])
        user["role"] = role
        user["password"] = AuthHandler.get_password_hash(user["password"])
        user_model = User(**user)
        return cls.create_by_uniqueness(
            user_model, {"email": user["email"]}, signal_kwargs=signal_kwargs
        )

    @classmethod
    def update(
        cls, query: dict, update_fields: dict, signal_kwargs: None | dict = None
    ) -> User:
        cls.validate(update_fields)
        user = cls.get(**query)

        if "password" in update_fields:
            response = is_strong_password(update_fields["password"])
            if response is not NotStrongPasswordErrorMessage.SUCCESS:
                raise NotStrongPasswordError(response.value)
            update_fields["password"] = AuthHandler.get_password_hash(
                update_fields["password"]
            )

        if "role" in update_fields:
            update_fields["role"] = RoleCrud.get(id=update_fields.pop("role"))

        if "account" in update_fields:
            account = AccountCrud.get_partial({"id": user.account.id}, {"id"})
            AccountCrud.update(
                {"id": account.id}, update_fields=update_fields.pop("account")
            )

        user.modify(update_fields, signal_kwargs=signal_kwargs)
        return user

    @classmethod
    def delete(cls, id: str, signal_kwargs: None | dict = None) -> bool:
        user = cls.get(id=id)
        user.update(is_deleted=True, deleted_at=datetime.utcnow)
        signals.post_delete.send(user.__class__, document=user, **signal_kwargs)
        AccountCrud.delete(id=user.account.id, signal_kwargs=signal_kwargs)
        return True
