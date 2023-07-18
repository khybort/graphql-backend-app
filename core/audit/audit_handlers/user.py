import copy

from mongoengine import Document

from core.audit.audit_handlers.base import BaseAuditHandler
from core.audit.crud.audit import AuditCrud
from core.audit.enum import ActivityTypesEnum
from core.auth.models.user import User


class UserAuditHandler(BaseAuditHandler):
    @classmethod
    def create_audit_for_login_opr(
        cls,
        sender: Document.__class__,
        document: Document,
        source_address: str | None = None,
        user_agent: str | None = None,
        is_audit=False,
        exception="",
    ):
        if not is_audit:
            return
        audit_fields = {}
        audit_data_fields = []
        audit_fields["model"] = document
        audit_fields["created_by"] = document
        audit_fields["model_name"] = document._class_name
        audit_fields["source_address"] = source_address
        audit_fields["source_user_agent"] = user_agent
        audit_fields["message"] = (
            f"Logged into the system."
            if not exception == "login_failed"
            else f"Attempted to log in but failed due to incorrect credentials"
        )
        audit_fields["activity"] = ActivityTypesEnum.LOGIN
        audit_fields["params"] = []
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
        audit_fields["activity"] = ActivityTypesEnum.UPDATE
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
            elif updated_field == "password":
                audit_fields["message"] = f"{{0}} reset {updated_field}"
                audit_fields["params"] = [document]
                audit_fields["activity"] = ActivityTypesEnum.PASSWORD_RESET
            elif updated_field == "is_two_factor_auth_enabled":
                audit_fields["message"] = (
                    f"Two factor authentication is disabled for the {{0}}"
                    if audit_data_fields[0]["old"]
                    else f"Two factor authentication is enabled for the {{0}}"
                )
                audit_fields["params"] = [document]
                audit_fields["activity"] = ActivityTypesEnum.TWO_FACTOR_AUTHENTICATION
            else:
                audit_fields["message"] = f"{{0}}'s {updated_field} updated."
                audit_fields["params"] = [document]
        audit_fields["data"] = audit_data_fields
        audit_fields["created_by"] = created_by
        audit_fields["model"] = document
        AuditCrud.create(audit_fields)
