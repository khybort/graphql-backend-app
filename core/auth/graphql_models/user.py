from typing import Optional

import strawberry

from core.auth.enum import UserTypeEnum
from core.auth.graphql_models.account import (
    AccountCreate,
    AccountRead,
    AccountUpdate,
)
from core.auth.graphql_models.role import RoleRead
from core.auth.resolvers.webauthn import PublicKeyCredentialRequestOptions
from core.base_graphql_error import AuthenticationExceptionType, BaseErrorType
from core.graphql_base_model import (
    AllOptional,
    BaseGraphQLModel,
    BaseGraphQLQueryMeta,
    BaseRead,
)


@strawberry.type
class BaseUser:
    is_superuser: bool
    email: str
    user_type: UserTypeEnum
    role: RoleRead
    account: AccountRead
    is_two_factor_auth_enabled: bool


@strawberry.type
class UserRead(BaseUser, BaseRead):
    pass


@strawberry.type
class MeInfo:
    response: UserRead


@strawberry.type
class UserList:
    response: list[UserRead]
    meta: BaseGraphQLQueryMeta


@strawberry.input
class UserCreate(BaseUser, BaseGraphQLModel):
    account: AccountCreate
    role: str
    is_superuser: Optional[bool] = strawberry.UNSET


@strawberry.input
class UserUpdate(UserCreate, metaclass=AllOptional):
    account: Optional[AccountUpdate] = strawberry.UNSET
    password: Optional[str] = strawberry.UNSET


@strawberry.input
class UserQuery(UserUpdate):
    id: Optional[strawberry.ID] = strawberry.UNSET


@strawberry.input
class UserLoginQuery(BaseGraphQLModel):
    email: str
    password: str


@strawberry.type
class TokenResponse:
    access_token: str
    refresh_token: str


@strawberry.type
class Login:
    user: UserRead
    access_token: Optional[str] = strawberry.UNSET
    refresh_token: Optional[str] = strawberry.UNSET
    mfa_type: Optional[str] = "None"


@strawberry.type
class UserSelfUpdateRead(UserRead, TokenResponse):
    pass


@strawberry.type
class UserOneTimeToken:
    token: str


############################################
########## Mutation Return Types ###########
############################################

UserListResponse = strawberry.union(
    "UserListResponse",
    (
        UserList,
        BaseErrorType,
        AuthenticationExceptionType,
    ),
)
MeInfoResponse = strawberry.union(
    "MeInfoResponse",
    (
        MeInfo,
        BaseErrorType,
        AuthenticationExceptionType,
    ),
)

mutation_error_responses = (
    BaseErrorType,
    AuthenticationExceptionType,
)

UserCreateResponse = strawberry.union(
    "UserCreateResponse",
    (UserRead, *mutation_error_responses),
)

UserUpdateResponse = strawberry.union(
    "UserUpdateResponse", (UserRead, *mutation_error_responses)
)

UpdateSelfUserResponse = strawberry.union(
    "UpdateSelfUserResponse", (UserSelfUpdateRead, *mutation_error_responses)
)

UserLoginResponse = strawberry.union(
    "UserLoginResponse",
    (TokenResponse, *mutation_error_responses),
)

LoginResponse = strawberry.union(
    "LoginResponse",
    (Login, PublicKeyCredentialRequestOptions, *mutation_error_responses),
)

UserOneTimeTokenResponse = strawberry.union(
    "UserOneTimeTokenResponse",
    (UserOneTimeToken, *mutation_error_responses),
)
