from core.auth.models.role import Role
from core.lib.basecrud import Crud


class RoleCrud(Crud):
    model = Role

    @classmethod
    def create(cls, role: dict, signal_kwargs: None | dict = None) -> Role:
        role_model = Role(**role)
        return cls.create_by_uniqueness(role_model, {"name":role['name']}, signal_kwargs=signal_kwargs)

    @classmethod
    def update(
        cls, query: dict, update_fields: dict, signal_kwargs: None | dict = None
    ) -> Role:
        cls.validate(update_fields)
        role = cls.get(**query)
        role.modify(update_fields, signal_kwargs=signal_kwargs)
        return role
