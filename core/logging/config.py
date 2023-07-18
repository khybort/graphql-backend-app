import logging

from core.logging.formatter.colorize import ColorizeLogFormat


def configure_colorized_logging():
    logger = logging.getLogger("colorizedLogger")
    handler = logging.StreamHandler()
    handler.setFormatter(ColorizeLogFormat())
    logger.addHandler(handler)
