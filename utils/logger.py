import logging
import os
import sys
from datetime import datetime
from config.settings import settings

def setup_logger(name: str = "kira_engine") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))

    if logger.handlers:
        return logger

    # Console Handler
    c_handler = logging.StreamHandler(sys.stdout)
    c_handler.setLevel(logging.DEBUG if settings.debug else logging.INFO)
    c_format = logging.Formatter('%(asctime)s - [%(levelname)s] - %(name)s - %(message)s')
    c_handler.setFormatter(c_format)
    logger.addHandler(c_handler)

    # File Handler
    try:
        os.makedirs(settings.log_dir, exist_ok=True)
        log_file = os.path.join(settings.log_dir, f"kira_{datetime.now().strftime('%Y%m%d')}.log")
        f_handler = logging.FileHandler(log_file, encoding='utf-8')
        f_handler.setLevel(logging.DEBUG)
        f_format = logging.Formatter('%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s:%(lineno)d) - %(message)s')
        f_handler.setFormatter(f_format)
        logger.addHandler(f_handler)
    except Exception as e:
        logger.warning(f"Failed to setup file logging: {e}")

    return logger

logger = setup_logger()
