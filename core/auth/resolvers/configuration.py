from typing import Optional

import strawberry
from strawberry.types import Info

from core.auth.crud.configuration import ConfigurationCrud
from core.auth.graphql_models.configuration import (
    SettingsConfigurationCreate,
    SettingsConfigurationCreateResponse,
    SettingsConfigurationList,
    SettingsConfigurationListResponse,
    SettingsConfigurationQuery,
    SettingsConfigurationRead,
    SettingsConfigurationUpdate,
    SettingsConfigurationUpdateResponse,
)
from core.auth.models.permission import PermissionsEnum
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


@graphql_exception_handler
@check_perm(PermissionsEnum.CONFIGURATION_READ_VALUES)
def resolve_configuration(
    info: Info,
    query: SettingsConfigurationQuery,
    meta: Optional[BaseGraphQLQueryMetaInput] = None,
    search_text: Optional[str] = None,
) -> SettingsConfigurationListResponse:
    if not meta:
        meta = BaseGraphQLQueryMetaInput()
    requested_fields = get_requested_fields(info, "SettingsConfigurationList")
    configs, has_more, count = ConfigurationCrud.get_many_partial_with_pagination(
        query.to_dict(), requested_fields, **meta.to_dict(), search_text=search_text
    )

    return SettingsConfigurationList(
        response=configs,
        meta=BaseGraphQLQueryMeta(**meta.to_dict(), has_more=has_more, count=count),
    )


@graphql_exception_handler
@db_to_graphql_type_converter(SettingsConfigurationRead)
@check_perm(PermissionsEnum.CONFIGURATION_CREATE_VALUES)
def resolve_create_configuration(
    info: Info, configuration: SettingsConfigurationCreate
) -> SettingsConfigurationCreateResponse:
    create_field = {**configuration.to_dict()}
    return ConfigurationCrud.create(create_field)


@graphql_exception_handler
@db_to_graphql_type_converter(SettingsConfigurationRead)
@check_perm(PermissionsEnum.CONFIGURATION_UPDATE_VALUES)
def resolve_update_configuration(
    info: Info, id: strawberry.ID, set: SettingsConfigurationUpdate
) -> SettingsConfigurationUpdateResponse:
    return ConfigurationCrud.update({"id": id}, set.to_dict())


@graphql_exception_handler
@check_perm(PermissionsEnum.CONFIGURATION_DELETE_VALUES)
def resolve_delete_configuration(info: Info, id: strawberry.ID) -> DeleteResponse:
    return DeleteOutput(
        message="Deleted successfully", success=ConfigurationCrud.delete(id)
    )
