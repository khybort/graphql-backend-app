import importlib.util
import logging
import logging.config
import os

from mongoengine import connect

from core.logging.config import configure_colorized_logging



def import_module_by_path(path: str):
    cwd = get_current_path()
    path = os.path.join(cwd, path)
    spec = importlib.util.spec_from_file_location("", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def get_current_path():
    return os.getcwd()


# functions for multiprocessing works successfully
def create_logger():
    logger = logging.getLogger("colorizedLogger")
    logging.config.fileConfig("logging.conf", disable_existing_loggers=False)
    configure_colorized_logging()
    return logger


def initialize_logger():
    return logging.getLogger("colorizedLogger")


def connect_db():
    connect("app", host="mongodb://mongo:27017/")
