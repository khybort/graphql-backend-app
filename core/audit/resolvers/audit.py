from typing import Optional

from strawberry.types import Info

from core.audit.crud.audit import AuditCrud
from core.audit.graphql_models.audit import (
    AuditList,
    AuditListResponse,
    AuditQuery,
)
from core.auth.models.permission import PermissionsEnum
from core.auth.utilities.decorators import check_perm
from core.utils import get_requested_fields
from core.filter_lookup import build_query
from core.graphql_base_model import BaseGraphQLQueryMeta, BaseGraphQLQueryMetaInput
from core.graphql_decorator import graphql_exception_handler


@graphql_exception_handler
@check_perm(PermissionsEnum.AUDIT_READ_VALUES)
def resolve_audits(
    info: Info,
    query: AuditQuery,
    meta: Optional[BaseGraphQLQueryMetaInput] = None,
    search_text: Optional[str] = None,
) -> AuditListResponse:
    if not meta:
        meta = BaseGraphQLQueryMetaInput()
    query_dict = build_query(query.to_dict())
    requested_fields = get_requested_fields(info, "AuditList")
    audits, has_more, count = AuditCrud.get_many_partial_with_pagination(
        query_dict, requested_fields, **meta.to_dict(), search_text=search_text
    )
    return AuditList(
        response=audits,
        meta=BaseGraphQLQueryMeta(**meta.to_dict(), has_more=has_more, count=count),
    )
