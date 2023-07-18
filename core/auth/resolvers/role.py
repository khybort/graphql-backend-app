from typing import Optional

import strawberry
from strawberry.types import Info

from core.auth.crud.role import RoleCrud
from core.auth.graphql_models.role import (
    RoleCreate,
    RoleCreateResponse,
    RoleList,
    RoleListResponse,
    RoleQuery,
    RoleRead,
    RoleUpdate,
    RoleUpdateResponse,
)
from core.auth.models.permission import (
    PERMISSION_VALUE_TO_DISPLAY_NAME,
    PermissionsEnum,
)
from core.auth.utilities.decorators import check_perm
from core.utils import (
    db_to_graphql_type_converter,
    get_requested_fields,
)
from core.graphql_base_model import (
    BaseGraphQLQueryMeta,
    BaseGraphQLQueryMetaInput,
    DeleteOutput,
)
from core.graphql_base_responses import DeleteResponse
from core.graphql_decorator import graphql_exception_handler

MUTATION_READ_OBJECT = RoleRead


@graphql_exception_handler
@check_perm(PermissionsEnum.ROLE_READ_VALUES)
def resolve_roles(
    info: Info,
    query: RoleQuery,
    meta: Optional[BaseGraphQLQueryMetaInput] = None,
    search_text: Optional[str] = None,
) -> RoleListResponse:
    if not meta:
        meta = BaseGraphQLQueryMetaInput()
    requested_fields = get_requested_fields(info, "RoleList")
    roles, has_more, count = RoleCrud.get_many_partial_with_pagination(
        query.to_dict(), requested_fields, **meta.to_dict(), search_text=search_text
    )
    return RoleList(
        response=roles,
        meta=BaseGraphQLQueryMeta(**meta.to_dict(), has_more=has_more, count=count),
    )


@graphql_exception_handler
@db_to_graphql_type_converter(MUTATION_READ_OBJECT)
@check_perm(PermissionsEnum.ROLE_CREATE_VALUES)
def resolve_create_role(info: Info, role: RoleCreate) -> RoleCreateResponse:
    role_dict = role.to_dict()
    if "permissions" in role_dict:
        role_dict["permissions"] = [
            {
                "value": perm_value,
                "display_name": PERMISSION_VALUE_TO_DISPLAY_NAME[perm_value],
            }
            for perm_value in role_dict["permissions"]
        ]
    return RoleCrud.create(
        role_dict,
        signal_kwargs={
            "created_by": info.context.user,
            **info.context.source_info,
            "is_audit": True,
        },
    )


@graphql_exception_handler
@db_to_graphql_type_converter(MUTATION_READ_OBJECT)
@check_perm(PermissionsEnum.ROLE_UPDATE_VALUES)
def resolve_update_role(
    info: Info, id: strawberry.ID, set: RoleUpdate
) -> RoleUpdateResponse:
    update_fields = set.to_dict()
    if "permissions" in update_fields:
        update_fields["permissions"] = [
            {
                "value": perm_value,
                "display_name": PERMISSION_VALUE_TO_DISPLAY_NAME[perm_value],
            }
            for perm_value in update_fields["permissions"]
        ]
    return RoleCrud.update(
        {"id": id},
        update_fields,
        signal_kwargs={
            "created_by": info.context.user,
            **info.context.source_info,
            "is_audit": True,
        },
    )


@graphql_exception_handler
@check_perm(PermissionsEnum.ROLE_DELETE_VALUES)
def resolve_delete_role(info: Info, id: strawberry.ID) -> DeleteResponse:
    return DeleteOutput(
        message="Deleted successfully",
        success=RoleCrud.delete(
            id,
            signal_kwargs={
                "created_by": info.context.user,
                **info.context.source_info,
                "is_audit": True,
            },
        ),
    )
