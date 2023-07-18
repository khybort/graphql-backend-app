from typing import Optional

import strawberry
from strawberry.file_uploads import Upload

from core.base_graphql_error import AuthenticationExceptionType, BaseErrorType
from core.graphql_base_model import (
    AllOptional,
    BaseGraphQLModel,
    BaseGraphQLQueryMeta,
    BaseRead,
)


@strawberry.type
class AvatarRead:
    path: str
    name: str


@strawberry.type
class BaseAccount:
    firstname: str
    lastname: str
    phone: Optional[str] = strawberry.UNSET
    job_title: Optional[str] = strawberry.UNSET


@strawberry.type
class AccountRead(BaseAccount, BaseRead):
    avatar: Optional[AvatarRead] = strawberry.UNSET


@strawberry.type
class AccountList:
    response: list[AccountRead]
    meta: BaseGraphQLQueryMeta


@strawberry.input
class AccountCreate(BaseAccount, BaseGraphQLModel):
    avatar: Optional[Upload] = strawberry.UNSET


@strawberry.input
class AccountUpdate(AccountCreate, metaclass=AllOptional):
    avatar: Optional[Upload] = strawberry.UNSET


@strawberry.input
class AccountQuery(AccountUpdate):
    id: Optional[strawberry.ID] = strawberry.UNSET


############################################
###### Query & Mutation Return Types #######
############################################

AccountListResponse = strawberry.union(
    "AccountListResponse",
    (
        AccountList,
        BaseErrorType,
        AuthenticationExceptionType,
    ),
)

mutation_responses = (
    AccountRead,
    BaseErrorType,
    AuthenticationExceptionType,
)

AccountCreateResponse = strawberry.union(
    "AccountCreateResponse",
    mutation_responses,
)

AccountUpdateResponse = strawberry.union(
    "AccountUpdateResponse",
    mutation_responses,
)
