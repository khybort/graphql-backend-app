from mongoengine import EmbeddedDocument, StringField

from core.basemodel import BaseModel, EmbeddedDocumentListField


class Permission(EmbeddedDocument):
    value = StringField(required=True)
    display_name = StringField(required=True)


class Role(BaseModel):
    meta = {
        "collection": "roles",
        "indexes": [
            {
                "fields": ["$name", "$description"],
                "default_language": "english",
            }
        ],
    }
    name = StringField(required=True)
    permissions = EmbeddedDocumentListField(Permission, required=True)
    description = StringField()
