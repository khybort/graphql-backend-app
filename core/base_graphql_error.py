import strawberry


@strawberry.type
class BaseErrorType:
    message: str


@strawberry.type
class FieldValidationErrorType:
    field: str
    message: str


@strawberry.type
class ValidationErrorType:
    errors: list[FieldValidationErrorType]


@strawberry.type
class AlreadyExistsErrorType(BaseErrorType):
    pass


@strawberry.type
class DoesNotExistErrorType(BaseErrorType):
    pass


@strawberry.type
class UserHasNotPermissionsType(BaseErrorType):
    pass


@strawberry.type
class AuthenticationExceptionType(BaseErrorType):
    pass
