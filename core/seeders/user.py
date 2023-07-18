from core.auth.crud.role import RoleCrud
from core.auth.crud.user import UserCrud


def get_data():
    admin_role = RoleCrud.get_partial({"name": "Admin"}, ["id"])

    return [
        {
            "email": "admin@app.io",
            "password": "AppDevAdmin",
            "is_superuser": True,
            "role": str(admin_role.id),
            "account": {"firstname": "Admin", "lastname": "Admin"},
        }
    ]


def seed():
    for user in get_data():
        UserCrud.create(user)


def update():
    email = {user["email"] for user in UserCrud.get_many({})}

    for user in get_data():
        if user["email"] not in email:
            UserCrud.create(user)


def delete_all():
    UserCrud.delete_many()
