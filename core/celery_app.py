import sys

from celery import Celery
from mongoengine import signals

from core.audit.audit_handlers.role import RoleAuditHandler
from core.audit.audit_handlers.user import UserAuditHandler
from core.auth.models.role import Role
from core.auth.models.user import User
from core.functions import connect_db
from core.signals import non_db_signal, post_modify

sys.path.append("/core")
connect_db()

app = Celery(
    name=__name__,
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0",
)

config = {
    "redbeat_redis_url": "redis://redis:6379/1",
    "redbeat_lock_timeout": 40,
}
print("------------------------------------------------")

import ipdb
ipdb.set_trace()

app.conf.update(**config)

signals.post_save.connect(UserAuditHandler.create_audit_for_create_opr, sender=User)
post_modify.connect(UserAuditHandler.create_audit_for_update_opr, sender=User)
signals.post_delete.connect(UserAuditHandler.create_audit_for_delete_opr, sender=User)

signals.post_save.connect(RoleAuditHandler.create_audit_for_create_opr, sender=Role)
post_modify.connect(RoleAuditHandler.create_audit_for_update_opr, sender=Role)
signals.post_delete.connect(RoleAuditHandler.create_audit_for_delete_opr, sender=Role)

non_db_signal.connect(UserAuditHandler.create_audit_for_login_opr, sender=User)
