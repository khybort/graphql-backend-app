from core.auth.crud.role import RoleCrud
from core.auth.models.permission import PermissionsEnum


def get_data():
    return [
        {
            "name": "tester",
            "description": "only test user",
            "permissions": [
                {"value": "user.read", "display_name": "Can Read User"},
            ],
        },
        {
            "name": "Default User",
            "description": "Default User Role",
            "permissions": [
                {"value": "user.read", "display_name": "Can Read User"},
            ],
        },
        {
            "name": "Admin",
            "description": "Admin Role",
            "permissions": [perm.value for perm in PermissionsEnum],
        },
    ]


def seed():
    for role in get_data():
        RoleCrud.create(role)


def update():
    role_name = {role["name"] for role in RoleCrud.get_many({})}

    for role in get_data():
        if role["name"] not in role_name:
            RoleCrud.create(role)
        else:
            role_model = RoleCrud.get_partial({"name": role["name"]}, ["id"])
            RoleCrud.update({"id": role_model.id}, role)


def delete_all():
    RoleCrud.delete_many()
