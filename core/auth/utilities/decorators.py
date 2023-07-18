import asyncio
from functools import wraps

from core.exception import UserNotPermissions

def check_permission_block(permission, **kwargs):
    user_object = kwargs["info"].context.user
    if user_object.is_superuser or permission.value in [
        {"value": i.value, "display_name": i.display_name}
        for i in user_object.role.permissions
    ]:
        return True
    else:
        raise UserNotPermissions(user_object.email)
def check_perm(permission):
    def decorator(func):
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                if check_permission_block(permission, **kwargs):
                    return (await func(*args, **kwargs))
        else:
            @wraps(func)
            def wrapper(*args, **kwargs):
                if check_permission_block(permission, **kwargs):
                    return func(*args, **kwargs)
        return wrapper
    return decorator

