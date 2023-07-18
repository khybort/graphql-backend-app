from base64 import urlsafe_b64decode, urlsafe_b64encode
from typing import List, NewType, Optional

import strawberry

from core.base_enum import BaseStrEnum, ValidateEnumStr
from core.base_graphql_error import AuthenticationExceptionType, BaseErrorType
from core.graphql_base_model import BaseGraphQLModel

Base64Url = strawberry.scalar(
    NewType("Base64Url", bytes),
    serialize=lambda v: urlsafe_b64encode(v).decode("utf-8").replace("=", ""),
    # why: we need to add padding to the end of the string to make it a multiple of 4
    parse_value=lambda v: urlsafe_b64decode(v + "==="),
)


@strawberry.enum
class COSEAlgorithmIdentifier(BaseStrEnum):
    ECDSA_SHA_256 = -7
    EDDSA = -8
    ECDSA_SHA_512 = -36
    RSASSA_PSS_SHA_256 = -37
    RSASSA_PSS_SHA_384 = -38
    RSASSA_PSS_SHA_512 = -39
    RSASSA_PKCS1_v1_5_SHA_256 = -257
    RSASSA_PKCS1_v1_5_SHA_384 = -258
    RSASSA_PKCS1_v1_5_SHA_512 = -259
    RSASSA_PKCS1_v1_5_SHA_1 = -65535


@strawberry.enum
class PublicKeyCredentialType(BaseStrEnum):
    PUBLIC_KEY = "public-key"


@strawberry.enum
class AuthenticatorTransport(BaseStrEnum):
    USB = "usb"
    NFC = "nfc"
    BLE = "ble"
    INTERNAL = "internal"
    CABLE = "cable"
    HYBRID = "hybrid"


@strawberry.enum
class AttestationConveyancePreference(BaseStrEnum):
    NONE = "none"
    INDIRECT = "indirect"
    DIRECT = "direct"
    ENTERPRISE = "enterprise"


@strawberry.enum
class AuthenticatorAttachment(BaseStrEnum):
    PLATFORM = "platform"
    CROSS_PLATFORM = "cross-platform"


@strawberry.enum
class ResidentKeyRequirement(BaseStrEnum):
    DISCOURAGED = "discouraged"
    PREFERRED = "preferred"
    REQUIRED = "required"


@strawberry.enum
class UserVerificationRequirement(BaseStrEnum):
    REQUIRED = "required"
    PREFERRED = "preferred"
    DISCOURAGED = "discouraged"


@strawberry.type
class PublicKeyCredentialRpEntity:
    name: str
    id: Optional[str] = None


@strawberry.type
class PublicKeyCredentialUserEntity:
    id: Base64Url
    name: str
    display_name: str


@strawberry.type
class PublicKeyCredentialParameters:
    type: ValidateEnumStr[PublicKeyCredentialType]
    alg: ValidateEnumStr[COSEAlgorithmIdentifier]


@strawberry.type
class PublicKeyCredentialDescriptor:
    id: Base64Url
    type: ValidateEnumStr[PublicKeyCredentialType]
    transports: Optional[List[ValidateEnumStr[AuthenticatorTransport]]] = None


@strawberry.type
class AuthenticatorSelectionCriteria:
    authenticator_attachment: Optional[ValidateEnumStr[AuthenticatorAttachment]] = None
    resident_key: Optional[ValidateEnumStr[ResidentKeyRequirement]] = None
    require_resident_key: Optional[bool] = False
    user_verification: Optional[
        ValidateEnumStr[UserVerificationRequirement]
    ] = UserVerificationRequirement.PREFERRED


@strawberry.type
class PublicKeyCredentialCreationOptions:
    rp: PublicKeyCredentialRpEntity
    user: PublicKeyCredentialUserEntity
    challenge: Base64Url
    pub_key_cred_params: List[PublicKeyCredentialParameters]
    timeout: Optional[int] = None
    exclude_credentials: Optional[List[PublicKeyCredentialDescriptor]] = None
    authenticator_selection: Optional[AuthenticatorSelectionCriteria] = None
    attestation: ValidateEnumStr[
        AttestationConveyancePreference
    ] = AttestationConveyancePreference.NONE


@strawberry.type
class PublicKeyCredentialRequestOptions:
    challenge: Base64Url
    timeout: Optional[int] = None
    rp_id: Optional[str] = None
    allow_credentials: Optional[List[PublicKeyCredentialDescriptor]] = None
    user_verification: Optional[
        ValidateEnumStr[UserVerificationRequirement]
    ] = UserVerificationRequirement.PREFERRED


@strawberry.input
class OptionsInput:
    email: str


@strawberry.input
class AuthenticatorAttestationResponse:
    client_data_json: Base64Url
    attestation_object: Base64Url


@strawberry.input
class RegistrationCredential:
    id: str
    raw_id: Base64Url
    response: AuthenticatorAttestationResponse
    authenticator_attachment: Optional[ValidateEnumStr[AuthenticatorAttachment]] = None
    transports: Optional[List[ValidateEnumStr[AuthenticatorTransport]]] = None
    type: ValidateEnumStr[PublicKeyCredentialType] = PublicKeyCredentialType.PUBLIC_KEY


@strawberry.input
class RegistrationInput:
    credential: RegistrationCredential


@strawberry.enum
class CredentialDeviceType(BaseStrEnum):
    SINGLE_DEVICE = "single_device"
    MULTI_DEVICE = "multi_device"


@strawberry.enum
class AttestationFormat(BaseStrEnum):
    PACKED = "packed"
    TPM = "tpm"
    ANDROID_KEY = "android-key"
    ANDROID_SAFETYNET = "android-safetynet"
    FIDO_U2F = "fido-u2f"
    APPLE = "apple"
    NONE = "none"


@strawberry.type
class VerificationStatus:
    verified: bool


@strawberry.type
class WebAuthnCredential:
    id: str
    public_key: str
    username: str
    sign_count: int
    # is_discoverable_credential: bool
    device_type: ValidateEnumStr[CredentialDeviceType]
    backed_up: bool
    transports: Optional[List[ValidateEnumStr[AuthenticatorTransport]]]


@strawberry.input
class AuthenticatorAssertionResponse:
    client_data_json: Base64Url
    authenticator_data: Base64Url
    signature: Base64Url
    user_handle: Optional[Base64Url] = None


@strawberry.input
class AuthenticationCredential(BaseGraphQLModel):
    id: str
    raw_id: Base64Url
    response: AuthenticatorAssertionResponse
    authenticator_attachment: Optional[ValidateEnumStr[AuthenticatorAttachment]] = None
    type: ValidateEnumStr[PublicKeyCredentialType] = PublicKeyCredentialType.PUBLIC_KEY


@strawberry.input
class WebAuthnInput:
    email: str
    credential: AuthenticationCredential


@strawberry.input
class AuthenticationInput(BaseGraphQLModel):
    email: str
    credential: Optional[AuthenticationCredential] = strawberry.UNSET
    digit_code: Optional[int] = strawberry.UNSET


############################################
########## Mutation Return Types ###########
############################################

mutation_error_responses = (
    BaseErrorType,
    AuthenticationExceptionType,
)

WebAuthnCreationOptionsResponse = strawberry.union(
    "WebAuthnCreationOptionsResponse",
    (PublicKeyCredentialCreationOptions, *mutation_error_responses),
)

WebAuthnRequestOptionsResponse = strawberry.union(
    "WebAuthnRequestOptionsResponse",
    (PublicKeyCredentialRequestOptions, *mutation_error_responses),
)

WebAuthnVerifyRegistrationResponse = strawberry.union(
    "WebAuthnVerifyRegistrationResponse",
    (VerificationStatus, *mutation_error_responses),
)

WebAuthnCredentialsResponse = strawberry.union(
    "WebAuthnCredentialsResponse",
    (WebAuthnCredential, *mutation_error_responses),
)
