from mongoengine import (
    BooleanField,
    EmailField,
    EmbeddedDocument,
    EmbeddedDocumentField,
    EnumField,
    IntField,
    StringField,
)

from core.auth.enum import SlaTypeEnum, TimeUnitEnum, TimezoneEnum
from core.basemodel import BaseModel


class DatetimeConfiguration(EmbeddedDocument):
    timezone = EnumField(TimezoneEnum, default=TimezoneEnum.UTC)
    date_format = StringField()
    time_format = StringField()


class TimeUnit(EmbeddedDocument):
    value = IntField(default=5)
    unit = EnumField(TimeUnitEnum, default=TimeUnitEnum.MINUTE)


class SlaConfiguration(EmbeddedDocument):
    sla_type = EnumField(SlaTypeEnum, default=SlaTypeEnum.ALL_ALERT)
    alert_type = EnumField(SlaTypeEnum, default=SlaTypeEnum.ALL_ALERT)
    period = EmbeddedDocumentField(TimeUnit, required=True)
    time = EmbeddedDocumentField(TimeUnit, required=True)


class EmailConfiguration(EmbeddedDocument):
    display_name = StringField(required=True)
    email_address = EmailField(required=True)
    username = StringField(required=True)
    password = StringField(required=True)
    server = StringField(required=True)
    port = IntField(required=True)
    use_ssl = BooleanField(default=True)


class Configuration(BaseModel):
    meta = {
        "collection": "configurations",
        "indexes": [
            {
                "fields": ["$email_configuration"],
                "default_language": "english",
            }
        ],
    }
    email_configuration = EmbeddedDocumentField(EmailConfiguration)
    sla_configuration = EmbeddedDocumentField(SlaConfiguration)
    datetime_configuration = EmbeddedDocumentField(DatetimeConfiguration)
