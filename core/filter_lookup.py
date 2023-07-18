from typing import Generic, Optional, TypeVar

import strawberry

T = TypeVar("T")


@strawberry.input
class FilterLookup(Generic[T]):
    exact: Optional[T] = strawberry.UNSET
    iexact: Optional[T] = strawberry.UNSET
    contains: Optional[T] = strawberry.UNSET
    icontains: Optional[T] = strawberry.UNSET
    # in_list is equivalent to operator `in` in Mongoengine
    # It is named as in_list as the word `in` is not valid variable name in Python
    in_list: Optional[list[T]] = strawberry.UNSET
    not_in_list: Optional[list[T]] = strawberry.UNSET
    gt: Optional[T] = strawberry.UNSET
    gte: Optional[T] = strawberry.UNSET
    lt: Optional[T] = strawberry.UNSET
    lte: Optional[T] = strawberry.UNSET
    startswith: Optional[T] = strawberry.UNSET
    istartswith: Optional[T] = strawberry.UNSET
    endswith: Optional[T] = strawberry.UNSET
    iendswith: Optional[T] = strawberry.UNSET
    regex: Optional[str] = strawberry.UNSET
    iregex: Optional[str] = strawberry.UNSET


def build_query(query: dict):
    params = {}
    for field, value in query.items():
        if isinstance(value, FilterLookup):
            params |= generate_lookup_fields(field, value)
        else:
            params[field] = value

    return params


def generate_lookup_fields(field, filter_lookup):
    generated_fields = {}
    for lookup_field, value in filter_lookup.__dict__.items():
        if value is strawberry.UNSET:
            continue

        if lookup_field == "in_list":
            lookup_field = "in"
        elif lookup_field == "not_in_list":
            lookup_field = "nin"

        generated_fields[f"{field}__{lookup_field}"] = value

    return generated_fields
