# src/logger_config.py
import logging
from pathlib import Path
from datetime import datetime

def get_logger(module_name: str) -> logging.Logger:
    TODAY = datetime.today().strftime("%Y-%m-%d")
    LOG_DIR = Path("logs")
    LOG_DIR.mkdir(exist_ok=True)

    logger = logging.getLogger(module_name)
    logger.setLevel(logging.INFO)

    # Prevent duplicate log entry rendering if imported multiple times
    if not logger.handlers:
        file_handler = logging.FileHandler(LOG_DIR / f"scrape_{TODAY}.log", encoding="utf-8")
        file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s [%(name)s] - %(message)s"))

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter("%(levelname)s [%(name)s]: %(message)s"))

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger