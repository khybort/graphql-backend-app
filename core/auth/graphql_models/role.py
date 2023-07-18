from typing import Optional

import strawberry

from core.base_graphql_error import AuthenticationExceptionType, BaseErrorType
from core.graphql_base_model import (
    AllOptional,
    BaseGraphQLModel,
    BaseGraphQLQueryMeta,
    BaseRead,
)


@strawberry.type
class BaseRole:
    name: str
    description: Optional[str] = strawberry.UNSET


@strawberry.type
class Permission:
    value: str
    display_name: str


@strawberry.type
class RoleRead(BaseRole, BaseRead):
    permissions: list[Permission]


@strawberry.type
class RoleList:
    response: list[RoleRead]
    meta: BaseGraphQLQueryMeta


@strawberry.input
class RoleCreate(BaseRole, BaseGraphQLModel):
    permissions: list[str]


@strawberry.input
class RoleUpdate(RoleCreate, metaclass=AllOptional):
    pass


@strawberry.input
class RoleQuery(RoleUpdate):
    id: Optional[strawberry.ID] = strawberry.UNSET


############################################
########## Mutation Return Types ###########
############################################

RoleListResponse = strawberry.union(
    "RoleListResponse",
    (
        RoleList,
        BaseErrorType,
        AuthenticationExceptionType,
    ),
)

mutation_responses = (
    RoleRead,
    BaseErrorType,
    AuthenticationExceptionType,
)

RoleCreateResponse = strawberry.union(
    "RoleCreateResponse",
    mutation_responses,
)

RoleUpdateResponse = strawberry.union(
    "RoleUpdateResponse",
    mutation_responses,
)
