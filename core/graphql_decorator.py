import asyncio
import uuid
from functools import wraps

from core.base_graphql_error import (
    AuthenticationExceptionType,
    BaseErrorType,
    FieldValidationErrorType,
    ValidationErrorType,
)
from core.exception import (
    AuthenticationException,
    BaseCoreException,
    EncodeTokenError,
    ExpiredSignatureError,
    InvalidScopeTokenError,
    InvalidTokenError,
    OTPFailedAttemptsError,
    ValidationError,
)
from core.functions import initialize_logger

logger = initialize_logger()


def graphql_exception_handler(func):
    if asyncio.iscoroutinefunction(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return (await func(*args, **kwargs))
            except Exception as error:
                return handle_exception(error)
    else:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as error:
                return handle_exception(error)

    return wrapper

def handle_exception(error):
    try:
        raise error
    except (
        AuthenticationException,
        ExpiredSignatureError,
        InvalidTokenError,
        InvalidScopeTokenError,
        EncodeTokenError,
        OTPFailedAttemptsError,
    ) as e:
        return AuthenticationExceptionType(message=str(e))
    except ValidationError as e:
        return ValidationErrorType(
            errors=[
                FieldValidationErrorType(field=err["field"], message=err["message"])
                for err in e.errors
            ]
        )
    except BaseCoreException as e:
        return BaseErrorType(message=str(e))
    except Exception as e:
        uuid_str = str(uuid.uuid4())
        logger.error(f"{e}, error id: {uuid_str}")
        return BaseErrorType(
            message=f"Something went wrong! Report it with the id: {uuid_str}"
        )