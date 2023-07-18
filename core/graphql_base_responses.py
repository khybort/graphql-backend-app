import strawberry

from core.base_graphql_error import AuthenticationExceptionType, BaseErrorType
from core.graphql_base_model import DeleteOutput

DeleteResponse = strawberry.union(
    "DeleteResponse", (DeleteOutput, BaseErrorType, AuthenticationExceptionType)
)
