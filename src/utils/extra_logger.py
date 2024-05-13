import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger(__name__)
handler = RotatingFileHandler("D:/FastAPI/prject1/src/logs/app.log", maxBytes=10000, backupCount=1)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(pathname)s %(funcName)s: %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
