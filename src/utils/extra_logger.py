import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger('app_logger')
handler = RotatingFileHandler("D:/FastAPI/prject1/src/logs/app.log", maxBytes=10000, backupCount=1)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(pathname)s %(funcName)s: %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


# Настройки для логгера Celery
cel_logger = logging.getLogger('celery_logger')
cel_handler = RotatingFileHandler("D:/FastAPI/prject1/src/logs/celery.log", maxBytes=10000, backupCount=1)
cel_formatter = logging.Formatter('%(asctime)s %(levelname)s %(pathname)s %(funcName)s: %(message)s')
cel_handler.setFormatter(cel_formatter)
cel_logger.addHandler(cel_handler)
cel_logger.setLevel(logging.INFO)