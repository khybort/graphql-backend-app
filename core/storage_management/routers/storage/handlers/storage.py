import mimetypes
import os

from fastapi import HTTPException

from core.storage_management.routers.storage.handlers.application import (
    AvatarHandler,
)
from core.storage_management.routers.storage.handlers.file_handler import AgentsHandler

VALID_COLLECTIONS = {
    "account": AvatarHandler,
    "agents": AgentsHandler,
}

VALID_TYPES = [
    "image/png",
    "image/jpeg",
    "image/jpg",
    "image/ppm",
    "image/gif",
    "image/tiff",
    "image/bmp",
    "image/svg+xml",
]


class StorageHandler:
    @staticmethod
    def get_handler(collection: str) -> object:
        if collection not in VALID_COLLECTIONS:
            raise HTTPException(status_code=404, detail="Not found")
        return VALID_COLLECTIONS[collection]

    @classmethod
    def validate(cls, file: str) -> bool:
        return cls.validate_mimetype(file) and cls.validate_file_exist(file)

    @classmethod
    def validate_mimetype(cls, file: str) -> bool:
        mimetype = mimetypes.guess_type(file)[0]
        return mimetype in VALID_TYPES

    @classmethod
    def validate_file_exist(cls, file: str) -> bool:
        return os.path.exists(file)
