import copy
from typing import Any

from mongoengine import Document

from core.audit.crud.audit import AuditCrud
from core.audit.enum import ActivityTypesEnum
from core.auth.models.user import User


class BaseAuditHandler:
    @classmethod
    def create_audit_for_create_opr(
        cls,
        sender: Document.__class__,
        document: Document,
        created: Any | bool,
        created_by: User | None = None,
        source_address: str | None = None,
        user_agent: str | None = None,
        is_audit=False,
    ):
        if not is_audit:
            return
        audit_fields = {}
        audit_data_fields = []
        audit_fields["source_address"] = source_address
        audit_fields["source_user_agent"] = user_agent
        audit_fields["created_by"] = created_by
        audit_fields["model"] = document
        audit_fields["activity"] = ActivityTypesEnum.CREATE
        audit_fields["model_name"] = document._class_name
        audit_dict = document.to_mongo().to_dict()
        for field, new_value in audit_dict.items():
            audit_data_fields.append(
                {
                    "field": field,
                    "new": new_value,
                }
            )
        audit_fields[
            "message"
        ] = f"{{0}} {str(document.__class__.__name__).lower()} created."
        audit_fields["params"] = [document]
        audit_fields["data"] = audit_data_fields
        AuditCrud.create(audit_fields)

    @classmethod
    def create_audit_for_update_opr(
        cls,
        sender: Document.__class__,
        document: Document,
        update_fields: dict,
        created_by: User | None = None,
        source_address: str | None = None,
        user_agent: str | None = None,
        is_audit=False,
    ):
        if not is_audit or not update_fields:
            return
        audit_fields = {}
        audit_data_fields = []
        audit_fields["source_address"] = source_address
        audit_fields["source_user_agent"] = user_agent
        audit_fields["model_name"] = document._class_name
        for field, new_value in update_fields.items():
            audit_data_fields.append(
                {
                    "field": field,
                    "old": getattr(document, field),
                    "new": new_value,
                }
            )
        if len(update_fields) > 1:
            audit_fields["message"] = f"{{0}}'s multiple fields updated."
            audit_fields["params"] = [document]
        elif len(update_fields) == 1:
            updated_field = copy.deepcopy(audit_data_fields[0]["field"])
            if updated_field in sender.get_reference_fields():
                audit_fields[
                    "message"
                ] = f"{{0}}'s {updated_field} updated {{1}} to {{2}}"
                audit_fields["params"] = [
                    document,
                    audit_data_fields[0]["old"],
                    audit_data_fields[0]["new"],
                ]
            else:
                audit_fields["message"] = f"{{0}}'s {updated_field} updated."
                audit_fields["params"] = [document]
        audit_fields["data"] = audit_data_fields
        audit_fields["activity"] = ActivityTypesEnum.UPDATE
        audit_fields["created_by"] = created_by
        audit_fields["model"] = document
        AuditCrud.create(audit_fields)

    @classmethod
    def create_audit_for_delete_opr(
        cls,
        sender: Document.__class__,
        document: Document,
        created_by: User | None = None,
        source_address: str | None = None,
        user_agent: str | None = None,
        is_audit=False,
    ):
        if not is_audit:
            return
        audit_fields = {}
        audit_data_fields = []
        audit_fields["source_address"] = source_address
        audit_fields["source_user_agent"] = user_agent
        audit_fields["created_by"] = created_by
        document_dict = document.to_mongo().to_dict()
        for field, old_value in document_dict.items():
            audit_data_fields.append(
                {
                    "field": field,
                    "old": old_value,
                }
            )
        audit_fields["data"] = audit_data_fields
        audit_fields["model"] = document
        audit_fields[
            "message"
        ] = f"{{0}} {str(document.__class__.__name__).lower()} removed."
        audit_fields["params"] = [document]

        AuditCrud.create(audit_fields)
