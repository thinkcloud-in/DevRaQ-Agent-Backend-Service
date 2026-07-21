import os
import logging
from logging.handlers import RotatingFileHandler
import contextvars

# Environment variables
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_DIR = os.getenv("LOG_DIR", "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Formatter
formatter = logging.Formatter(
    fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(request_id)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Handlers
file_handler = RotatingFileHandler(
    filename=os.path.join(LOG_DIR, "devraq_backend.log"),
    maxBytes=10 * 1024 * 1024,
    backupCount=5,
)
# ContextVar for request ID
request_id_var = contextvars.ContextVar("request_id", default="-")

class RequestIDFilter(logging.Filter):
    def filter(self, record):
        record.request_id = request_id_var.get()
        return True

file_handler.setFormatter(formatter)
file_handler.addFilter(RequestIDFilter())

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.addFilter(RequestIDFilter())

# Root logger configuration
logging.basicConfig(level=LOG_LEVEL, handlers=[file_handler, console_handler])
