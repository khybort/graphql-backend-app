from mongoengine import (
    CASCADE,
    BooleanField,
    DateTimeField,
    EmailField,
    EmbeddedDocument,
    EmbeddedDocumentField,
    EnumField,
    IntField,
    ListField,
    ReferenceField,
    StringField,
)

from core.auth.enum import UserTypeEnum
from core.auth.models.account import Account
from core.auth.models.role import Role
from core.basemodel import BaseModel


class PublicKeyCredential(EmbeddedDocument):
    id = StringField(required=True)
    public_key = StringField(required=True)
    username = StringField(required=True)
    sign_count = IntField(required=True)
    # is_discoverable_credential = bool
    device_type = StringField(required=True)
    backed_up = BooleanField(required=True)
    transports = ListField(StringField(), required=True)


class User(BaseModel):
    meta = {
        "collection": "users",
        "indexes": [
            {
                "fields": ["$email"],
                "default_language": "english",
            }
        ],
    }
    is_superuser = BooleanField(default=False)
    email = EmailField(required=True)
    password = StringField(required=True)
    role = ReferenceField(Role)
    user_type = EnumField(UserTypeEnum, default=UserTypeEnum.STANDARD)
    account = ReferenceField(Account, reverse_delete_rule=CASCADE)
    is_two_factor_auth_enabled = BooleanField(default=False)
    verified_at = DateTimeField(default=None)
    public_key_credential = EmbeddedDocumentField(PublicKeyCredential)
