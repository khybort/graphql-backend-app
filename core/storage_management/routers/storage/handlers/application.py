import os

from core.auth.crud.account import AccountCrud
from core.config import settings

DOCKER_PATH = settings.DOCKER_PATH
FILE_PATH = settings.FILE_PATH

class AvatarHandler:
    @staticmethod
    def get_file_path(id, file_name):
        account = AccountCrud.get_partial({"id": id}, ["avatar"])
        return os.path.join(DOCKER_PATH, account.avatar.path, file_name)
