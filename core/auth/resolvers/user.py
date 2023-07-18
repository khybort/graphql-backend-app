import json
from datetime import datetime, timedelta, timezone
from typing import Optional

import strawberry
from strawberry.types import Info
from webauthn import generate_authentication_options, verify_authentication_response
from webauthn.helpers import base64url_to_bytes
from webauthn.helpers.structs import (
    AuthenticationCredential,
    AuthenticatorAssertionResponse,
)
from webauthn.helpers.structs import (
    PublicKeyCredentialDescriptor as LibPublicKeyCredentialDescriptor,
)

from core.auth.crud.user import UserCrud
from core.auth.graphql_models.user import (
    Login,
    LoginResponse,
    MeInfo,
    MeInfoResponse,
    TokenResponse,
    UpdateSelfUserResponse,
    UserCreate,
    UserCreateResponse,
    UserList,
    UserListResponse,
    UserLoginQuery,
    UserLoginResponse,
    UserOneTimeToken,
    UserOneTimeTokenResponse,
    UserQuery,
    UserRead,
    UserSelfUpdateRead,
    UserUpdate,
    UserUpdateResponse,
)
from core.auth.graphql_models.webauhtn import (
    AuthenticationInput,
    PublicKeyCredentialRequestOptions,
)
from core.auth.models.permission import PermissionsEnum
from core.auth.models.user import User
from core.auth.utilities.auth_handler import AuthHandler
from core.auth.utilities.decorators import check_perm
from core.auth.utilities.utilities import (
    check_digit_code_failed_attempts,
    generate_digit_code,
    generate_invite_token,
    generate_one_time_token,
    generate_password,
    get_mail_template,
    get_register_mail_template,
    get_user_id_by_one_time_token,
    send_mail,
)
from core.config import settings
from core.utils import (
    convert_to_graphql_type,
    db_to_graphql_type_converter,
    get_requested_fields,
)
from core.exception import (
    AuthenticationException,
    DigitCodeError,
    InvalidTokenError,
    InviteExpiredSignatureError,
    InviteLinkError,
    NotMatchExceptionError,
)
from core.graphql_base_model import (
    BaseGraphQLQueryMeta,
    BaseGraphQLQueryMetaInput,
    DeleteOutput,
)
from core.graphql_base_responses import DeleteResponse
from core.graphql_decorator import graphql_exception_handler
from core.redis import Redis
from core.signals import non_db_signal
from core.auth.enum import UserTypeEnum

@graphql_exception_handler
@check_perm(PermissionsEnum.USER_READ_VALUES)
def resolve_users(
    info: Info,
    query: UserQuery,
    meta: Optional[BaseGraphQLQueryMetaInput] = None,
    search_text: Optional[str] = None,
) -> UserListResponse:
    if not meta:
        meta = BaseGraphQLQueryMetaInput()
    requested_fields = get_requested_fields(info, "UserList")
    users, has_more, count = UserCrud.get_many_partial_with_pagination(
        query.to_dict(), requested_fields, **meta.to_dict(), search_text=search_text
    )
    return UserList(
        response=users,
        meta=BaseGraphQLQueryMeta(**meta.to_dict(), has_more=has_more, count=count),
    )


@graphql_exception_handler
def resolve_me_info(info: Info) -> MeInfoResponse:
    user = UserCrud.get(id=info.context.user["id"])
    return MeInfo(response=user)


@graphql_exception_handler
@db_to_graphql_type_converter(UserRead)
@check_perm(PermissionsEnum.USER_CREATE_VALUES)
def resolve_create_user(info: Info, user: UserCreate) -> UserCreateResponse:
    expiration_date = datetime.now(timezone.utc) + timedelta(days=7)
    token = generate_invite_token()
    token_value = {
        "email": user.email,
        "expiration_date": expiration_date.strftime("%Y-%m-%d %H:%M:%S"),
    }
    token_value = json.dumps(token_value)
    user.password = generate_password()
    Redis.set(token, token_value, timedelta(days=7))
    mail_body = get_register_mail_template(
        f"{settings.ALLOW_HOST}/reset-password/{token}"
    )
    new_user = UserCrud.create(
        user.to_dict(),
        signal_kwargs={
            "created_by": info.context.user,
            **info.context.source_info,
            "is_audit": True,
        },
    )
    send_mail(user.email, "App Invite", mail_body)

    return new_user


@graphql_exception_handler
@db_to_graphql_type_converter(UserRead)
@check_perm(PermissionsEnum.USER_UPDATE_VALUES)
def resolve_update_user(
    info: Info, id: strawberry.ID, set: UserUpdate
) -> UserUpdateResponse:
    return UserCrud.update(
        {"id": id},
        set.to_dict(),
        signal_kwargs={
            "created_by": info.context.user,
            **info.context.source_info,
            "is_audit": True,
        },
    )


@graphql_exception_handler
@db_to_graphql_type_converter(UserSelfUpdateRead)
def resolve_update_self_user(info: Info, set: UserUpdate) -> UpdateSelfUserResponse:
    user = UserCrud.update(
        {"id": info.context.user["id"]},
        set.to_dict(),
        signal_kwargs={
            "created_by": info.context.user,
            **info.context.source_info,
            "is_audit": True,
        },
    )
    user.access_token = AuthHandler.encode_token(
        email=user.email, scope="access_token", ttl={"days": 0, "hours": 2}
    )
    user.refresh_token = AuthHandler.encode_token(
        email=user.email, scope="refresh_token", ttl={"days": 0, "hours": 20}
    )
    Redis.set(
        f"{user.email}_refresh_token",
        user.refresh_token,
        exp=timedelta(days=0, hours=20),
    )
    return user


@graphql_exception_handler
@check_perm(PermissionsEnum.USER_DELETE_VALUES)
def resolve_delete_user(info: Info, id: strawberry.ID) -> DeleteResponse:
    return DeleteOutput(
        message="Deleted successfully",
        success=UserCrud.delete(
            id,
            signal_kwargs={
                "created_by": info.context.user,
                **info.context.source_info,
                "is_audit": True,
            },
        ),
    )


@graphql_exception_handler
def resolve_login(info: Info, query: UserLoginQuery) -> LoginResponse:
    auth_data = UserCrud.get(email=query.email)
    if not auth_data or not AuthHandler.verify_password(
        query.password, auth_data["password"]
    ):
        if not AuthHandler.verify_password(query.password, auth_data["password"]):
            non_db_signal.send(
                User,
                document=auth_data,
                **{**info.context.source_info, "is_audit": True, "exception": "login_failed"},
            )
        raise AuthenticationException()
    if auth_data.user_type == UserTypeEnum.API:
        access_token = AuthHandler.encode_token(
        query.email, scope="access_token", ttl={"days": 365, "hours": 2})
        
        refresh_token = AuthHandler.encode_token(
            query.email, scope="refresh_token", ttl={"days": 365, "hours": 20}
        )
    else:
        access_token = AuthHandler.encode_token(
            query.email, scope="access_token", ttl={"days": 0, "hours": 2}
        )
        refresh_token = AuthHandler.encode_token(
            query.email, scope="refresh_token", ttl={"days": 0, "hours": 20}
        )
    Redis.set(
        f"{auth_data.email}_access_token",
        access_token,
        exp=timedelta(days=0, hours=2),
    )
    Redis.set(
        f"{auth_data.email}_refresh_token",
        refresh_token,
        exp=timedelta(days=0, hours=20),
    )

    non_db_signal.send(
        User, document=auth_data, **{**info.context.source_info, "is_audit": True}
    )
    if auth_data.is_two_factor_auth_enabled is False:
        return Login(
            access_token=access_token, refresh_token=refresh_token, user=auth_data
        )

    if auth_data.public_key_credential:
        existing_credential = auth_data.public_key_credential

        authentication_options = generate_authentication_options(
            rp_id=settings.RP_ID,
            user_verification="required",
            allow_credentials=[
                LibPublicKeyCredentialDescriptor(
                    id=base64url_to_bytes(existing_credential.id),
                    transports=existing_credential.transports,
                )
            ],
            timeout=settings.TIMEOUT,
        )

        Redis.set(
            f"webauthn_challenge_{auth_data.email}",
            authentication_options.challenge,
            exp=int(settings.TIMEOUT),
        )

        return convert_to_graphql_type(
            authentication_options, PublicKeyCredentialRequestOptions
        )

    digit_code = generate_digit_code()

    Redis.set(
        f"{auth_data.email}_digit_code",
        digit_code,
        exp=timedelta(days=0, hours=0, minutes=3),
    )
    Redis.set(f"{auth_data.email}_failed_attempts", "0")

    mail_template = get_mail_template(
        firstname=auth_data.account.firstname, digit_code=digit_code
    )

    send_mail(
        body=mail_template,
        subject="2 Factor Auth",
        to_email=auth_data.email,
    )

    return Login(mfa_type="one-time-password", user=auth_data)


@graphql_exception_handler
def resolve_refresh_token(info: Info, refresh_token: str) -> UserLoginResponse:
    email = AuthHandler.decode_token(refresh_token, "refresh_token")
    store_refresh_token = Redis.get(f"{email}_refresh_token")

    if store_refresh_token != refresh_token:
        raise InvalidTokenError()

    access_token = AuthHandler.refresh_token(refresh_token)
    refresh_token = AuthHandler.encode_token(
        email, scope="refresh_token", ttl={"days": 0, "hours": 20}
    )

    Redis.set(
        f"{email}_refresh_token",
        refresh_token,
        exp=timedelta(days=0, hours=20),
    )

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@graphql_exception_handler
def resolve_verify_auth(info: Info, input: AuthenticationInput) -> UserLoginResponse:
    user = UserCrud.get(email=input.email)

    if input.digit_code:
        digit_code_in_redis = Redis.get(f"{input.email}_digit_code")
        if digit_code_in_redis is None or input.digit_code != digit_code_in_redis:
            check_digit_code_failed_attempts(input.email)
            raise DigitCodeError()

    elif input.credential:
        existing_credential = user.public_key_credential
        expected_challenge = Redis.get_raw(f"webauthn_challenge_{input.email}")
        Redis.delete(f"webauthn_challenge_{input.email}")

        response = input.credential.response

        verify_authentication_response(
            credential=AuthenticationCredential(
                id=input.credential.id,
                raw_id=input.credential.raw_id,
                response=AuthenticatorAssertionResponse(
                    client_data_json=response.client_data_json,
                    authenticator_data=response.authenticator_data,
                    signature=response.signature,
                    user_handle=response.user_handle,
                ),
                type=input.credential.type,
            ),
            expected_challenge=expected_challenge,
            expected_rp_id=settings.RP_ID,
            expected_origin=settings.EXPECTED_ORIGIN,
            credential_public_key=base64url_to_bytes(existing_credential.public_key),
            require_user_verification=True,
            credential_current_sign_count=existing_credential.sign_count,
        )
    else:
        raise AuthenticationException()

    refresh_token = Redis.get(f"{input.email}_refresh_token")
    access_token = Redis.get(f"{input.email}_access_token")
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@graphql_exception_handler
def resolve_generate_one_time_token(info: Info) -> UserOneTimeTokenResponse:
    user_id = str(info.context.user["id"])
    token = generate_one_time_token(user_id)
    return UserOneTimeToken(token=token)


@graphql_exception_handler
def resolve_get_token_by_one_time_token(
    info: Info, one_time_token: str
) -> UserLoginResponse:
    user_id = get_user_id_by_one_time_token(one_time_token)
    email = UserCrud.get_partial({"id": user_id}, fields=["email"])["email"]
    refresh_token = Redis.get(f"{email}_refresh_token")
    access_token = Redis.get(f"{email}_access_token")

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@graphql_exception_handler
@db_to_graphql_type_converter(UserSelfUpdateRead)
def resolve_reset_password(
    info: Info, token: str, password: str, confirm_password: str
) -> UpdateSelfUserResponse:
    if password != confirm_password:
        raise NotMatchExceptionError()

    invite = Redis.get(token)

    if invite is None:
        raise InviteLinkError()

    invite = json.loads(invite)

    if datetime.now(timezone.utc) > datetime.strptime(
        invite["expiration_date"], "%Y-%m-%d %H:%M:%S"
    ).replace(tzinfo=timezone.utc):
        raise InviteExpiredSignatureError()

    user = UserCrud.get(email=invite["email"])

    update_fields = {"password": password}

    if not user.verified_at:
        update_fields["verified_at"] = datetime.utcnow

    user = UserCrud.update(
        {"email": invite["email"]},
        update_fields,
        signal_kwargs={
            "created_by": user,
            **info.context.source_info,
            "is_audit": True,
        },
    )
    user.access_token = AuthHandler.encode_token(
        email=user.email, scope="access_token", ttl={"days": 0, "hours": 2}
    )
    user.refresh_token = AuthHandler.encode_token(
        email=user.email, scope="refresh_token", ttl={"days": 0, "hours": 20}
    )
    Redis.delete(token)

    return user
