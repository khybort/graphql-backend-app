from enum import Enum
from typing import _SpecialForm

import strawberry

from core.exception import FieldTypeError


class BaseStrEnum(str, Enum):
    @classmethod
    def has_value(cls, value):
        return value in cls.__members__.values()


def validate_enum(typedef: BaseStrEnum):
    def _validate_enum(value):
        if not typedef.has_value(
            value if (isinstance(value, str)) else str(value.value)
        ):
            raise FieldTypeError(f"Invalid value for {typedef.__name__}: {value}")
        return value

    return _validate_enum


@_SpecialForm
def ValidateEnumStr(self, parameters):
    return strawberry.scalar(parameters, serialize=validate_enum(parameters))
