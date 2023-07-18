from datetime import datetime

from mongoengine import (
    CASCADE,
    DateTimeField,
    DynamicField,
    EmbeddedDocument,
    EmbeddedDocumentListField,
    EnumField,
    GenericReferenceField,
    ListField,
    ReferenceField,
    StringField,
)

from core.audit.enum import ActivityTypesEnum
from core.auth.models.account import Account
from core.auth.models.role import Role
from core.auth.models.user import User
from core.basemodel import BaseModel


class DataRecord(EmbeddedDocument):
    field = StringField()
    old = DynamicField()
    new = DynamicField()


class Audit(BaseModel):
    meta = {
        "collection": "audits",
        "indexes": [
            {
                "fields": ["$message", "$source_user_agent", "$source_address"],
                "default_language": "english",
            }
        ],
    }
    created_by = ReferenceField(User, required=True, reverse_delete_rule=CASCADE)
    time = DateTimeField(default=datetime.utcnow)
    model = GenericReferenceField(
        choices=[User, Role, Account]
    )
    activity = EnumField(ActivityTypesEnum)
    model_name = StringField()
    source_address = StringField()
    source_user_agent = StringField()
    message = StringField()
    # the primitive parameters will be interpolated to the message directly as it is not
    # possible to define union types that might be scalar or object in GraphQL
    params = ListField(
        GenericReferenceField(
            choices=[User, Role, Account]
        )
    )
    data = EmbeddedDocumentListField(DataRecord)
