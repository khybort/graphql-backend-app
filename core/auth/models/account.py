from mongoengine import EmbeddedDocument, EmbeddedDocumentField, StringField

from core.basemodel import BaseModel


class Avatar(EmbeddedDocument):
    name = StringField(required=True)
    path = StringField(required=True)


class Account(BaseModel):
    meta = {
        "collection": "accounts",
        "indexes": [
            {
                "fields": ["$firstname", "$lastname", "$phone", "$job_title"],
                "default_language": "english",
            }
        ],
    }
    firstname = StringField(required=True)
    lastname = StringField(required=True)
    phone = StringField()
    job_title = StringField()
    avatar = EmbeddedDocumentField(Avatar)

    @property
    def fullname(self):
        return f"{self.firstname} {self.lastname}"
