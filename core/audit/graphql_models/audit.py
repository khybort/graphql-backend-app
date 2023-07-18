from datetime import datetime
from typing import List, Optional

import strawberry

from core.audit.enum import ActivityTypesEnum, ModulesEnum
from core.auth.graphql_models.account import AccountRead
from core.auth.graphql_models.role import RoleRead
from core.auth.graphql_models.user import UserRead
from core.auth.models.account import Account
from core.auth.models.role import Role
from core.auth.models.user import User
from core.base_graphql_error import AuthenticationExceptionType, BaseErrorType
from core.filter_lookup import FilterLookup
from core.graphql_base_model import (
    BaseGraphQLModel,
    BaseGraphQLQueryMeta,
    BaseRead,
    StrawberryFieldConverter,
)

ModelRead = strawberry.union(
    "ModelRead",
    (
        UserRead,
        RoleRead,
        AccountRead,
    ),
)
ParamTypeAudit = strawberry.union(
    "ParamTypeAudit",
    (
        UserRead,
        RoleRead,
        AccountRead,
    ),
)


@strawberry.type
class AuditRead(BaseRead):
    created_by: Optional[UserRead] = strawberry.UNSET
    activity: Optional[str] = strawberry.UNSET
    source_address: Optional[str] = strawberry.UNSET
    source_user_agent: Optional[str] = strawberry.UNSET
    message: Optional[str] = strawberry.UNSET
    params: Optional[List[ParamTypeAudit]] = StrawberryFieldConverter(
        default=strawberry.UNSET,
        db_model_graphql_type_mapping={
            User: UserRead,
            Role: RoleRead,
            Account: AccountRead,
        },
    )
    model: Optional[ModelRead] = StrawberryFieldConverter(
        default=strawberry.UNSET,
        db_model_graphql_type_mapping={
            User: UserRead,
            Role: RoleRead,
            Account: AccountRead,
        },
    )


@strawberry.type
class AuditList:
    response: list[AuditRead]
    meta: BaseGraphQLQueryMeta


@strawberry.input
class AuditQuery(BaseGraphQLModel):
    id: Optional[strawberry.ID] = strawberry.UNSET
    users: Optional[list[strawberry.ID]] = strawberry.UNSET
    activity: Optional[ActivityTypesEnum] = strawberry.UNSET
    model_name: Optional[ModulesEnum] = strawberry.UNSET
    created_at: Optional[FilterLookup[datetime]] = strawberry.UNSET


############################################
########## Mutation Return Types ###########
############################################

AuditListResponse = strawberry.union(
    "AuditListResponse",
    (AuditList, BaseErrorType, AuthenticationExceptionType),
)
