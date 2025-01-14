import json
import logging


class JsonLoggingHandler(logging.Handler):
    def emit(self, record):
        try:
            message = record.getMessage()
            if isinstance(message, dict):
                message = json.dumps(message, ensure_ascii=False)
        except Exception:
            self.handleError(record)


def get_logger(name: str = "", level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(JsonLoggingHandler())
    return logger
