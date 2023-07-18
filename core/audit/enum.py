import strawberry

from core.base_enum import BaseStrEnum


@strawberry.enum
class ActivityTypesEnum(BaseStrEnum):
    LOGIN = "Login"
    PASSWORD_RESET = "Password Reset"
    TWO_FACTOR_AUTHENTICATION = "Two Factor Authentication"
    CREATE = "Create"
    UPDATE = "Update"
    DELETE = "Delete"


@strawberry.enum
class ModulesEnum(BaseStrEnum):
    USER = "User"
    ROLE = "Role"
