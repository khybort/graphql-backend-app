from core.auth.graphql_models.permission import (
    PermissionList,
    PermissionListResponse,
    PermissionRead,
)
from core.auth.models.permission import PermissionsEnum
from core.graphql_decorator import graphql_exception_handler


@graphql_exception_handler
def resolve_permissions() -> PermissionListResponse:
    return PermissionList(
        response=[
            PermissionRead(
                value=permission.value["value"],
                display_name=permission.value["display_name"],
            )
            for permission in PermissionsEnum
        ]
    )
