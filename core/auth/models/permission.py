from enum import Enum


class PermissionsEnum(Enum):
    
    USER_READ_VALUES = {"value": "user.read", "display_name": "Can Read User"}
    USER_CREATE_VALUES = {"value": "user.create", "display_name": "Can Create User"}
    USER_UPDATE_VALUES = {"value": "user.update", "display_name": "Can Update User"}
    USER_DELETE_VALUES = {"value": "user.delete", "display_name": "Can Delete User"}
    USER_ADD_WEBAUTHN_CREDENTIAL = {
        "value": "user.add_webauthn_credential",
        "display_name": "Can Add Webauthn Credential",
    }
    ROLE_READ_VALUES = {"value": "role.read", "display_name": "Can Read Role"}
    ROLE_CREATE_VALUES = {"value": "role.create", "display_name": "Can Create Role"}
    ROLE_UPDATE_VALUES = {"value": "role.update", "display_name": "Can Update Role"}
    ROLE_DELETE_VALUES = {"value": "role.delete", "display_name": "Can Delete Role"}
    ACCOUNT_READ_VALUES = {
        "value": "account.read",
        "display_name": "Can Read Account",
    }
    ACCOUNT_CREATE_VALUES = {
        "value": "account.create",
        "display_name": "Can Create Account",
    }
    ACCOUNT_UPDATE_VALUES = {
        "value": "account.update",
        "display_name": "Can Update Account",
    }
    ACCOUNT_DELETE_VALUES = {
        "value": "account.delete",
        "display_name": "Can Delete Account",
    }
    
    AUDIT_READ_VALUES = {
        "value": "audit.read",
        "display_name": "Can Read Audit Read",
    }
    CONFIGURATION_READ_VALUES = {
        "value": "configuration.read",
        "display_name": "Can Read Configuration",
    }
    CONFIGURATION_CREATE_VALUES = {
        "value": "configuration.create",
        "display_name": "Can Create Configuration",
    }
    CONFIGURATION_UPDATE_VALUES = {
        "value": "configuration.update",
        "display_name": "Can Update Configuration",
    }
    CONFIGURATION_DELETE_VALUES = {
        "value": "configuration.delete",
        "display_name": "Can Delete Configuration",
    }


PERMISSION_VALUE_TO_DISPLAY_NAME = {
    item.value["value"]: item.value["display_name"] for item in PermissionsEnum
}
