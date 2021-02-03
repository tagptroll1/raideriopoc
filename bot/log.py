import logging
from logging import handlers
from pathlib import Path


def setup_logging() -> None:
    Path("logs").mkdir(exist_ok=True)
    log_file = Path("logs", "bot.log")

    format_string = '%(asctime)s | %(levelname)s | %(name)s | %(message)s'
    log_format = logging.Formatter(format_string)
    handler = handlers.RotatingFileHandler(
        log_file,
        maxBytes=5242880,
        backupCount=7,
        encoding="utf-8")
    handler.setFormatter(log_format)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    # Set level of existing logger
    logging.getLogger("discord").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.INFO)
