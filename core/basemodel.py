from copy import deepcopy
from datetime import datetime, timezone

from mongoengine import (
    DateTimeField,
    DictField,
    Document,
    EmbeddedDocument,
    EmbeddedDocumentField,
)
from mongoengine import EmbeddedDocumentListField as BaseEmbeddedDocumentListField
from mongoengine import (
    EnumField,
    GenericReferenceField,
    IntField,
    ObjectIdField,
    ReferenceField,
    StringField,
    BooleanField,
)

from core.exception import ValidationError
from core.signals import post_modify


class BaseModel(Document):
    meta = {"abstract": True}
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    is_deleted = BooleanField(required=True, default=False)
    deleted_at = DateTimeField()

    def modify(self, update_fields: dict, signal_kwargs=None, query=None):
        will_be_updated = self._get_updated_fields(update_fields)
        update_fields["updated_at"] = datetime.now(timezone.utc)
        old_instance = deepcopy(self)
        super().modify(query=query, **update_fields)
        update_fields.pop("updated_at")
        if not signal_kwargs:
            signal_kwargs = {}

        post_modify.send(
            self.__class__,
            document=old_instance,
            update_fields=will_be_updated,
            **signal_kwargs,
        )

    def update_instance(self, **set_fields):
        for field in self._fields_ordered:
            if field in set_fields:
                setattr(self, field, self._reload(field, set_fields[field]))

    @classmethod
    def get_reference_fields(cls) -> set[str]:
        return {
            k
            for k, v in cls.__dict__.items()
            if isinstance(v, (GenericReferenceField, ReferenceField))
        }

    @classmethod
    def get_embedded_fields_model(cls) -> dict[str]:
        fields = {}
        for k, v in cls.__dict__.items():
            if isinstance(v, (EmbeddedDocumentField)):
                fields[k] = v
            elif isinstance(v, EmbeddedDocumentListField):
                fields[k] = v.field.document_type_obj

        return fields

    def _get_updated_fields(self, update_fields: dict) -> dict:
        updated_fields = {}
        for k, v in update_fields.items():
            if k.startswith("add_to_set"):
                _, field_name = k.split("__")
                if v not in getattr(self, field_name):
                    updated_fields[k] = v
            else:
                updated_fields[k] = v

        return updated_fields


class PolimorficRelation(EmbeddedDocument):
    id = ObjectIdField(required=True)
    name = StringField(required=True)


class EmbeddedDocumentListField(BaseEmbeddedDocumentListField):
    def __init__(
        self,
        document_type,
        is_unique_in_list=False,
        unique_fields_in_list: set | None = None,
        **kwargs,
    ):
        super().__init__(document_type, **kwargs)
        self.is_unique_in_list = is_unique_in_list
        self.unique_fields_in_list = unique_fields_in_list

    def validate(self, value):
        super().validate(value)
        if self.is_unique_in_list and self.unique_fields_in_list:
            self._validate_unique_in_list(value)

    def _validate_unique_in_list(self, value):
        errors = []
        for field in self.unique_fields_in_list:
            value_list = [getattr(item, field) for item in value if item]
            if len(set(value_list)) != len(value_list):
                errors.append(
                    {
                        "field": field,
                        "message": f"{field} field must be unique within the list.",
                    }
                )

        if errors:
            raise ValidationError(message="ValidationError", errors=errors)

