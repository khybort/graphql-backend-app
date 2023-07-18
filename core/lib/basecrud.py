from abc import abstractmethod
from datetime import datetime
from typing import Optional

from mongoengine import signals

from core.basemodel import BaseModel
from core.constant import UPDATE_OPERATORS_TUPLE
from core.utils import convert_to_snake_case
from core.exception import (
    AlreadyExistWithSameName,
    DatabaseItemNotFound,
    FieldTypeError,
)


class Crud:
    model: BaseModel

    @classmethod
    @abstractmethod
    def update(cls, query: dict, update_fields: dict, **kwargs: dict) -> BaseModel:
        pass

    @classmethod
    def get(cls, **kwargs):
        if instance := cls.model.objects.filter(**kwargs, is_deleted=False).first():
            return instance
        else:
            raise DatabaseItemNotFound(cls.model.__name__)

    @classmethod
    def find(cls, **kwargs):
        return cls.model.objects.filter(**kwargs, is_deleted=False).first()

    @classmethod
    def get_partial(cls, query: dict, fields: list) -> dict:
        query["is_deleted"] = False
        if instance := cls.model.objects.filter(**query).only(*fields).first():
            return instance
        else:
            raise DatabaseItemNotFound(cls.model.__name__)

    @classmethod
    def get_many(cls, query: dict) -> list:
        query["is_deleted"] = False
        return list(cls.model.objects.filter(**query))

    @classmethod
    def get_many_with_pagination(
        cls,
        query: dict,
        limit: int = 0,
        offset: int = 0,
        order_by: Optional[list] = None,
    ) -> tuple[list, bool]:
        _limit = limit + 1 if limit else 0
        if not order_by:
            order_by = []
        query["is_deleted"] = False
        _order_by = [convert_to_snake_case(str(order)) for order in order_by]
        data = list(
            cls.model.objects.filter(**query)
            .order_by(*_order_by)
            .skip(offset)
            .limit(_limit)
        )
        if len(data) > limit and limit != 0:
            return data[:-1], True
        return data, False

    @classmethod
    def get_many_partial(cls, query: dict, fields: set) -> list:
        reference_fields = cls.model.get_reference_fields()
        query["is_deleted"] = False
        if fields.intersection(reference_fields):
            data = list(
                cls.model.objects.filter(**query).only(*fields).select_related()
            )
        else:
            data = list(cls.model.objects.filter(**query).only(*fields))

        return data

    @classmethod
    def get_many_partial_with_pagination(
        cls,
        query: dict,
        fields: set,
        offset: int = 0,
        limit: int = 0,
        order_by: Optional[list] = None,
        search_text: Optional[str] = None,
    ) -> tuple[list, bool, int]:
        _limit = limit + 1 if limit else 0  # if limit equals 0 pull all
        if not order_by:
            order_by = []
        query["is_deleted"] = False
        reference_fields = cls.model.get_reference_fields()
        _order_by = [convert_to_snake_case(str(order)) for order in order_by]
        query_set = (
            cls.model.objects.filter(**query)
            .search_text(search_text)
            .only(*fields)
            .order_by(*_order_by)
            .skip(offset)
            .limit(_limit)
            if search_text
            else cls.model.objects.filter(**query)
            .only(*fields)
            .order_by(*_order_by)
            .skip(offset)
            .limit(_limit)
        )
        count = query_set.count() if limit else len(query_set)
        if fields.intersection(reference_fields):
            query_set = query_set.select_related()

        data = list(query_set)

        if len(data) > limit and limit != 0:
            return data[:-1], True, count

        return data, False, count

    @classmethod
    def get_latest(cls, **kwargs):
        return cls.model.objects(**kwargs, is_deleted=False).order_by("-id").first()

    @classmethod
    def get_many_single_field(cls, query: dict, field: str) -> list:
        query["is_deleted"] = False
        if field == "id":
            return list(map(str, cls.model.objects(**query).values_list("id")))
        return list(cls.model.objects(**query).values_list(field))

    @classmethod
    def validate(cls, payload: dict):
        for k, v in payload.items():
            if not hasattr(cls.model, k):
                continue

            first, *remain = k.split("__")
            if first in UPDATE_OPERATORS_TUPLE:
                k = "__".join(remain)

            field = getattr(cls.model, k)
            if (field.unique or field.required) and v is None:
                raise FieldTypeError(f"{k} attribute cannot be null")

    @classmethod
    def create_by_uniqueness(
        cls, document: dict, unique_field: dict, signal_kwargs: None | dict = None
    ):
        if cls.count(**unique_field) != 0:
            raise AlreadyExistWithSameName(str(cls.model.__name__).lower())
        document.save(signal_kwargs=signal_kwargs)
        return document

    @classmethod
    def delete(cls, id: str, signal_kwargs: None | dict = None) -> bool:
        model_instance = cls.get(id=id)
        model_instance.update(is_deleted=True, deleted_at=datetime.utcnow)
        if signal_kwargs:
            signals.post_delete.send(
                model_instance.__class__, document=model_instance, **signal_kwargs
            )
        return True

    @classmethod
    def delete_many(cls, **query) -> bool:
        if not query:
            query = {}
        cls.model.objects.delete(**query)
        return True

    @classmethod
    def count(cls, **kwargs) -> int:
        return cls.model.objects.filter(**kwargs, is_deleted=False).count()

    @classmethod
    def create_embedded_fields(cls, **update_fields) -> dict:
        fields = {}
        embedded_fields_model = cls.model.get_embedded_fields_model()
        for key, value in update_fields.items():
            parts = key.split("__")
            field_name = parts[0] if len(parts) == 1 else parts[1]
            embedded_field_model = embedded_fields_model[field_name]
            if isinstance(value, list):
                fields[key] = [embedded_field_model(**item) for item in value]
            elif isinstance(value, dict):
                fields[key] = embedded_field_model(**value)
            else:
                fields[key] = value

        return fields
