import logging
import json
from datetime import datetime


class JsonFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            "time": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
        })


logger = logging.getLogger("app_logger")
logger.setLevel(logging.INFO)

# ❗ REMOVE OLD HANDLERS (VERY IMPORTANT)
logger.handlers.clear()

# File handler
file_handler = logging.FileHandler("app.log")
file_handler.setFormatter(JsonFormatter())

# Console handler (THIS SHOWS TERMINAL LOGS)
console_handler = logging.StreamHandler()
console_handler.setFormatter(
    logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
)

logger.addHandler(file_handler)
logger.addHandler(console_handler)
