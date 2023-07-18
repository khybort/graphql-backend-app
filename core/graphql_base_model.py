import dataclasses
from abc import ABCMeta
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, List, Mapping, Optional, Sequence, Type, Union

import strawberry
from strawberry.annotation import StrawberryAnnotation
from strawberry.field import StrawberryField
from strawberry.permission import BasePermission
from strawberry.scalars import JSON
from strawberry.types import Info
from strawberry.types.fields.resolver import StrawberryResolver

from core.utils import convert_to_graphql_type
from core.enum import OrderByEnum

DateTimeWithTimezone = strawberry.scalar(
    datetime,
    serialize=lambda value: value.replace(tzinfo=timezone.utc).isoformat(),
    parse_value=lambda value: datetime.fromisoformat(value).replace(
        tzinfo=timezone.utc
    ),
)


@strawberry.type
class BaseRead:
    id: strawberry.ID
    created_at: datetime
    updated_at: datetime


@strawberry.type
class DeleteOutput:
    message: str
    success: bool


class BaseGraphQLModel:
    def to_dict(self):
        res = {}
        for k, v in self.__dict__.items():
            if v == strawberry.UNSET:
                continue
            if isinstance(v, BaseGraphQLModel):
                res[k] = v.to_dict()
            elif isinstance(v, Enum):
                res[k] = v.value
            elif isinstance(v, list):
                res[k] = [
                    i.to_dict() if isinstance(i, BaseGraphQLModel) else i for i in v
                ]
            else:
                res[k] = v
        return res


class AllOptional(ABCMeta):
    def __new__(cls, name: str, bases: tuple, namespaces: dict, **kwargs):
        mro = super().__new__(cls, name, bases, namespaces, **kwargs).mro()
        annotations = namespaces.get("__annotations__", {})
        fields: list[str] = []
        for base in mro[:-1]:  # object class has no __annotations__ attr
            for k, v in base.__annotations__.items():
                if k not in annotations:
                    annotations[k] = v

            if hasattr(base, "_type_definition"):
                fields.extend(field.name for field in base._type_definition.fields)

        for field in annotations:
            if not field.startswith("_"):
                annotations[field] = Optional[annotations[field]]

        namespaces["__annotations__"] = annotations
        klass = super().__new__(cls, name, bases, namespaces, **kwargs)
        for field in fields:
            if not hasattr(klass, field):
                setattr(klass, field, strawberry.UNSET)

        return klass


class StrawberryFieldConverter(StrawberryField):
    def __init__(
        self,
        db_model_graphql_type_mapping: dict[Any, Any],
        python_name: Optional[str] = None,
        graphql_name: Optional[str] = None,
        type_annotation: Optional[StrawberryAnnotation] = None,
        origin: Optional[Union[Type, Callable, staticmethod, classmethod]] = None,
        is_subscription: bool = False,
        description: Optional[str] = None,
        base_resolver: Optional[StrawberryResolver] = None,
        permission_classes: List[Type[BasePermission]] = (),
        default: object = dataclasses.MISSING,
        default_factory: Union[Callable[[], Any], object] = dataclasses.MISSING,
        metadata: Optional[Mapping[Any, Any]] = None,
        deprecation_reason: Optional[str] = None,
        directives: Sequence[object] = (),
    ):
        super().__init__(
            python_name,
            graphql_name,
            type_annotation,
            origin,
            is_subscription,
            description,
            base_resolver,
            permission_classes,
            default,
            default_factory,
            metadata,
            deprecation_reason,
            directives,
        )
        self.db_model_graphql_type_mapping = db_model_graphql_type_mapping

    def get_result(
        self, source: Any, info: Optional[Info], args: list[Any], kwargs: dict[str, Any]
    ):
        db_object = getattr(source, self.name)
        if not db_object:
            return

        if isinstance(db_object, list):
            return self.convert_db_object_list_graphql(db_object)

        object_type = type(db_object)
        graphql_type = self.db_model_graphql_type_mapping[object_type]
        return convert_to_graphql_type(db_object, graphql_type)

    def convert_db_object_list_graphql(self, db_objects: list[Any]) -> list[Any]:
        graphql_objects = []
        for db_object in db_objects:
            db_model = type(db_object)
            graphql_type = self.db_model_graphql_type_mapping[db_model]
            graphql_objects.append(convert_to_graphql_type(db_object, graphql_type))

        return graphql_objects


@strawberry.input
class OrderByInput:
    field: str
    direction: OrderByEnum

    def __str__(self):
        return f"{self.direction.value}{self.field}"


@strawberry.type
class OrderByOutput(OrderByInput):
    pass


@strawberry.input
class BaseGraphQLQueryMetaInput(BaseGraphQLModel):
    offset: Optional[int] = 0
    limit: Optional[int] = 0
    order_by: Optional[List[OrderByInput]] = StrawberryField(default_factory=list)


@strawberry.type
class BaseGraphQLQueryMeta:
    offset: int = 0
    limit: int = 0
    has_more: bool
    order_by: List[OrderByOutput]
    count: int = 0
