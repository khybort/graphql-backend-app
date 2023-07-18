import strawberry

from core.base_enum import BaseStrEnum

@strawberry.enum
class OrderByEnum(BaseStrEnum):
    ASC = "+"
    DESC = "-"