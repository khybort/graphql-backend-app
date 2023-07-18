from strawberry.types import Info
from webauthn import (
    generate_authentication_options,
    generate_registration_options,
    verify_registration_response,
)
from webauthn.helpers import base64url_to_bytes, bytes_to_base64url
from webauthn.helpers.structs import (
    AuthenticatorAttestationResponse as LibAuthenticatorAttestationResponse,
)
from webauthn.helpers.structs import (
    PublicKeyCredentialDescriptor as LibPublicKeyCredentialDescriptor,
)
from webauthn.helpers.structs import RegistrationCredential as LibRegistrationCredential

from core.auth.crud.user import UserCrud
from core.auth.graphql_models.webauhtn import (
    AttestationConveyancePreference,
    OptionsInput,
    PublicKeyCredentialCreationOptions,
    PublicKeyCredentialRequestOptions,
    RegistrationInput,
    VerificationStatus,
    WebAuthnCreationOptionsResponse,
    WebAuthnCredential,
    WebAuthnCredentialsResponse,
    WebAuthnRequestOptionsResponse,
    WebAuthnVerifyRegistrationResponse,
)
from core.auth.models.permission import PermissionsEnum
from core.auth.models.user import PublicKeyCredential
from core.auth.utilities.decorators import check_perm
from core.config import settings
from core.utils import convert_to_graphql_type
from core.exception import AuthenticationException
from core.graphql_decorator import graphql_exception_handler
from core.redis import Redis


@graphql_exception_handler
@check_perm(PermissionsEnum.USER_ADD_WEBAUTHN_CREDENTIAL)
def resolve_webauthn_generate_registration_options(
    info: Info,
) -> WebAuthnCreationOptionsResponse:
    user = info.context.user

    if not user:
        raise AuthenticationException("User not found")

    display_name = user.account.fullname

    registration_options = generate_registration_options(
        rp_id=settings.RP_ID,
        rp_name=settings.RP_NAME,
        # FIXME: generate a hashed user id
        user_id=str(user.id),
        user_name=user.email,
        user_display_name=display_name,
        # why: get transport type
        attestation=AttestationConveyancePreference.DIRECT,
        timeout=int(settings.TIMEOUT),
    )

    Redis.set(
        f"webauthn_challenge_{user.email}",
        registration_options.challenge,
        exp=int(settings.TIMEOUT),
    )

    return convert_to_graphql_type(
        registration_options, PublicKeyCredentialCreationOptions
    )


@graphql_exception_handler
@check_perm(PermissionsEnum.USER_ADD_WEBAUTHN_CREDENTIAL)
def resolve_webauthn_verify_registration_response(
    info: Info, input: RegistrationInput
) -> WebAuthnVerifyRegistrationResponse:
    user = info.context.user

    expected_challenge = Redis.get_raw(f"webauthn_challenge_{user.email}")
    Redis.delete(f"webauthn_challenge_{user.email}")

    credential = input.credential
    response = credential.response

    verification = verify_registration_response(
        credential=LibRegistrationCredential(
            id=credential.id,
            raw_id=credential.raw_id,
            response=LibAuthenticatorAttestationResponse(
                client_data_json=response.client_data_json,
                attestation_object=response.attestation_object,
            ),
            authenticator_attachment=credential.authenticator_attachment,
            transports=credential.transports,
            type=credential.type,
        ),
        expected_challenge=expected_challenge,
        expected_rp_id=settings.RP_ID,
        expected_origin=settings.EXPECTED_ORIGIN,
        require_user_verification=True,
    )

    new_credential = PublicKeyCredential(
        id=bytes_to_base64url(verification.credential_id),
        public_key=bytes_to_base64url(verification.credential_public_key),
        username=user.email,
        sign_count=verification.sign_count,
        device_type=verification.credential_device_type,
        backed_up=verification.credential_backed_up,
        transports=credential.transports,
    )

    UserCrud.update({"email": user.email}, {"public_key_credential": new_credential})

    return VerificationStatus(verified=True)


@graphql_exception_handler
@check_perm(PermissionsEnum.USER_READ_VALUES)
def resolve_webauthn_credentials(
    info: Info,
) -> WebAuthnCredentialsResponse:
    user = info.context.user

    if not user:
        raise AuthenticationException("User not found")

    return convert_to_graphql_type(user.public_key_credential, WebAuthnCredential)


@graphql_exception_handler
def resolve_webauthn_generate_authentication_options(
    info: Info, input: OptionsInput
) -> WebAuthnRequestOptionsResponse:
    user = UserCrud.get(email=input.email)

    if not user:
        raise AuthenticationException("User not found")

    existing_credential = user.public_key_credential

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
        f"webauthn_challenge_{input.email}",
        authentication_options.challenge,
        exp=int(settings.TIMEOUT),
    )

    return convert_to_graphql_type(
        authentication_options, PublicKeyCredentialRequestOptions
    )
