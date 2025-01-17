import json
import logging
import time
import traceback


class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_message = {
            "requestId": getattr(record, 'aws_request_id', None),
            "level": record.levelname,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.%.3fZ", time.localtime(record.created)),
            "line": f"{record.pathname}/{record.module}::{record.funcName}::{record.lineno}",
        }

        if isinstance(record.msg, str):
            log_message['message'] = record.msg
        elif isinstance(record.msg, dict):
            log_message.update(record.msg)
        else:
            log_message['message'] = str(record.msg)

        if record.exc_info:
            log_message['traceback'] = traceback.format_exc().splitlines()

        return json.dumps(log_message, ensure_ascii=False)


def get_logger(level: int = logging.INFO):
    logger = logging.getLogger()
    logger.setLevel(level)

    for handler in logger.handlers:
        handler.setFormatter(JsonFormatter())

    return logger
