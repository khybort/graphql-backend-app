import strawberry

from core.auth.resolvers.account import (
    resolve_create_account,
    resolve_delete_account,
    resolve_update_account,
)
from core.auth.resolvers.configuration import (
    resolve_create_configuration,
    resolve_delete_configuration,
    resolve_update_configuration,
)
from core.auth.resolvers.role import (
    resolve_create_role,
    resolve_delete_role,
    resolve_update_role,
)
from core.auth.resolvers.user import (
    resolve_create_user,
    resolve_delete_user,
    resolve_generate_one_time_token,
    resolve_get_token_by_one_time_token,
    resolve_login,
    resolve_refresh_token,
    resolve_reset_password,
    resolve_update_self_user,
    resolve_update_user,
    resolve_verify_auth,
)
from core.auth.resolvers.webauthn import (
    resolve_webauthn_generate_authentication_options,
    resolve_webauthn_generate_registration_options,
    resolve_webauthn_verify_registration_response,
)


@strawberry.type
class Mutations:

    create_role = strawberry.mutation(resolver=resolve_create_role)
    update_role = strawberry.mutation(resolver=resolve_update_role)
    delete_role = strawberry.mutation(resolver=resolve_delete_role)

    create_user = strawberry.mutation(resolver=resolve_create_user)
    update_user = strawberry.mutation(resolver=resolve_update_user)
    update_self_user = strawberry.mutation(resolver=resolve_update_self_user)
    delete_user = strawberry.mutation(resolver=resolve_delete_user)
    login = strawberry.mutation(resolver=resolve_login)
    verify_auth = strawberry.mutation(resolver=resolve_verify_auth)
    generate_new_token = strawberry.mutation(resolver=resolve_refresh_token)
    reset_password = strawberry.mutation(resolver=resolve_reset_password)
    generate_one_time_token = strawberry.mutation(
        resolver=resolve_generate_one_time_token
    )
    get_token_from_one_time_token = strawberry.mutation(
        resolver=resolve_get_token_by_one_time_token
    )

    webauthn_generate_registration_options = strawberry.mutation(
        resolver=resolve_webauthn_generate_registration_options
    )
    webauthn_verify_registration_response = strawberry.mutation(
        resolver=resolve_webauthn_verify_registration_response
    )
    webauthn_generate_authentication_options = strawberry.mutation(
        resolver=resolve_webauthn_generate_authentication_options
    )

    create_account = strawberry.mutation(resolver=resolve_create_account)
    update_account = strawberry.mutation(resolver=resolve_update_account)
    delete_account = strawberry.mutation(resolver=resolve_delete_account)

    create_configuration = strawberry.mutation(resolver=resolve_create_configuration)
    update_configuration = strawberry.mutation(resolver=resolve_update_configuration)
    delete_configuration = strawberry.mutation(resolver=resolve_delete_configuration)

    create_configuration = strawberry.mutation(resolver=resolve_create_configuration)
    update_configuration = strawberry.mutation(resolver=resolve_update_configuration)
    delete_configuration = strawberry.mutation(resolver=resolve_delete_configuration)