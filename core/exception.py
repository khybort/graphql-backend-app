class BaseCoreException(Exception):
    def __init__(self, message: str, *args: object) -> None:
        super().__init__(message, *args)

class FieldTypeError(BaseCoreException):
    pass


class DatabaseItemNotFound(BaseCoreException):
    def __init__(self, model_name: str, *args: object) -> None:
        super().__init__(f"{model_name} not found", *args)


class FileSystemItemNotFound(BaseCoreException):
    def __init__(self, *args: object) -> None:
        super().__init__("File not found", *args)


class UserNotPermissions(BaseCoreException):
    def __init__(self, username: str, *args: object) -> None:
        super().__init__(f"{username} not permitted", *args)


class AuthenticationException(BaseCoreException):
    def __init__(self, *args: object) -> None:
        super().__init__("Invalid username and/or password", *args)


class ExpiredSignatureError(BaseCoreException):
    def __init__(self, *args: object) -> None:
        super().__init__("Signature has expired", *args)


class InvalidTokenError(BaseCoreException):
    def __init__(self, *args: object) -> None:
        super().__init__("Invalid token", *args)


class NotificationErr(BaseCoreException):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class SendMailException(BaseCoreException):
    def __init__(self, *args: object) -> None:
        super().__init__("An error occurred while sending email", *args)


class DigitCodeError(BaseCoreException):
    def __init__(self, *args: object) -> None:
        super().__init__("Signature or Invalid Digit Code", *args)


class MultiCredentialError(BaseCoreException):
    def __init__(self, *args: object) -> None:
        super().__init__("You cannot add more than one credential", *args)


class InviteLinkError(BaseCoreException):
    def __init__(self, *args: object) -> None:
        super().__init__("Invalid Invite Link", *args)


class InviteExpiredSignatureError(BaseCoreException):
    def __init__(self, *args: object) -> None:
        super().__init__("Expired invite link", *args)


class NotStrongPasswordError(BaseCoreException):
    def __init__(self, message: str, *args: object) -> None:
        super().__init__(message, *args)


class InvalidOneTimeTokenError(BaseCoreException):
    def __init__(self, *args: object) -> None:
        super().__init__("Invalid one time code", *args)


class NotMatchExceptionError(BaseCoreException):
    def __init__(self, *args: object) -> None:
        super().__init__("Passwords do not match. Please try again.", *args)


class NotAddExistingUser(BaseCoreException):
    def __init__(self, *args: object) -> None:
        super().__init__("You cannot add an existing user", *args)


class UnsupportedImage(BaseCoreException):
    def __init__(self, *args: object) -> None:
        super().__init__(
            "The image extension must be one of png, jpeg, jpg, ppm, gif, tiff, bmp",
            *args,
        )


class InvalidObjectId(BaseCoreException):
    def __init__(self, *args: object) -> None:
        super().__init__("Invalid object id", *args)


class AlreadyExistWithSameName(BaseCoreException):
    def __init__(self, class_name: str, *args: object) -> None:
        super().__init__(f"{class_name} already exists with the same name", *args)


class RiskyUseVisitorException(BaseCoreException):
    def __init__(self, message: str, *args: object) -> None:
        super().__init__(
            f"Please refrain from using unauthorized functions or libraries. {message}",
            *args,
        )

class ValidationError(BaseCoreException):
    def __init__(self, message: str, errors, *args: object) -> None:
        super().__init__(message, *args)
        self.message = message
        self.errors = errors


class InvalidScopeTokenError(BaseCoreException):
    def __init__(self, *args: object) -> None:
        super().__init__("Invalid scope for token", *args)


class OTPFailedAttemptsError(BaseCoreException):
    def __init__(self, *args: object) -> None:
        super().__init__("Too many incorrect entries", *args)


class EncodeTokenError(BaseCoreException):
    def __init__(self, *args: object) -> None:
        super().__init__("An error occurred while creating the token.", *args)

class UnexpectedIndentException(BaseCoreException):
    def __init__(self, *args: object) -> None:
        super().__init__("Syntax error in code", *args)


class ImportErrorException(BaseCoreException):
    def __init__(self, module: str, *args: object) -> None:
        super().__init__(f"The module '{module}' is not imported.", *args)
