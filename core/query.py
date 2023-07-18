import strawberry

from core.audit.resolvers.audit import resolve_audits
from core.auth.resolvers.account import resolve_account
from core.auth.resolvers.configuration import resolve_configuration
from core.auth.resolvers.permission import resolve_permissions
from core.auth.resolvers.role import resolve_roles
from core.auth.resolvers.user import resolve_me_info, resolve_users
from core.auth.resolvers.webauthn import resolve_webauthn_credentials


@strawberry.type
class Query:
    
    roles = strawberry.field(resolver=resolve_roles)
    users = strawberry.field(resolver=resolve_users)
    me = strawberry.field(resolver=resolve_me_info)
    permissions = strawberry.field(resolver=resolve_permissions)
    accounts = strawberry.field(resolver=resolve_account)
    webauthn_credentials = strawberry.field(resolver=resolve_webauthn_credentials)
    configurations = strawberry.field(resolver=resolve_configuration)
