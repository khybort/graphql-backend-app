from redbeat.schedulers import RedBeatScheduler as BaseScheduler
from redbeat.schedulers import RedBeatSchedulerEntry as BaseEntry

from core.functions import initialize_logger

logger = initialize_logger()


class RedBeatSchedulerEntry(BaseEntry):
    @classmethod
    def delete_by_name(cls, name, app):
        entry = cls(name=name, app=app)
        entry.delete()


class RedBeatScheduler(BaseScheduler):
    Entry = RedBeatSchedulerEntry
    max_interval = 10
