from typing import Optional

from bson.objectid import ObjectId

from core.audit.models.audit import Audit
from core.auth.crud.user import UserCrud
from core.auth.models.user import User
from core.lib.basecrud import Crud
from core.exception import InvalidObjectId

class AuditCrud(Crud):
    model = Audit

    @classmethod
    def create(cls, audit: dict) -> Audit:
        audit_model = cls.model(**audit)
        audit_model.save()
        return audit_model

    @classmethod
    def get_many_partial_with_pagination(
        cls,
        query: dict,
        fields: set,
        offset: int = 0,
        limit: int = 0,
        order_by: Optional[list] = None,
        search_text: Optional[str] = None,
    ) -> tuple[list, bool]:
        if "users" in query:
            query["created_by__in"] = cls.get_users_instance(query.pop("users"))
        return super().get_many_partial_with_pagination(
            query, fields, offset, limit, order_by, search_text=search_text
        )

    @classmethod
    def get_users_instance(cls, users: list) -> list[User]:
        users_id = []
        for user in users:
            if ObjectId.is_valid(user):
                users_id.append(user)
            else:
                InvalidObjectId(user)
        return UserCrud.get_many({"id__in": users_id})

