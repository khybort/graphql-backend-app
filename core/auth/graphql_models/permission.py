import strawberry

from core.base_graphql_error import AuthenticationExceptionType, BaseErrorType


@strawberry.type
class PermissionRead:
    value: str
    display_name: str


@strawberry.type
class PermissionList:
    response: list[PermissionRead]


############################################
########## Mutation Return Types ###########
############################################

PermissionListResponse = strawberry.union(
    "PermissionListResponse",
    (
        PermissionList,
        BaseErrorType,
        AuthenticationExceptionType,
    ),
)
