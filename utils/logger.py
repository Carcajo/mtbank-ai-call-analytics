import os
import sys
import json
import logging
import time
from functools import wraps


class CustomJSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, "%Y-%m-%d %H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage()
        }
        if hasattr(record, "structured_data"):
            log_record.update(record.structured_data)

        return json.dumps(log_record, ensure_ascii=False)


def setup_logger():
    logger = logging.getLogger("mtbank_ai")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = CustomJSONFormatter()
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


app_logger = setup_logger()


def log_agent_io(agent_name: str):
    def decorator(func):
        @wraps(func)
        def wrapper(state, *args, **kwargs):
            input_data = {
                "event": "agent_start",
                "agent": agent_name,
                "input_state_keys": list(state.keys())
            }
            app_logger.info(f"Агент {agent_name} начал работу", extra={"structured_data": input_data})
            start_time = time.time()

            try:
                result = func(state, *args, **kwargs)
                duration = time.time() - start_time
                output_data = {
                    "event": "agent_success",
                    "agent": agent_name,
                    "duration_sec": round(duration, 3),
                    "output_updates": result
                }
                app_logger.info(f"Агент {agent_name} успешно завершил работу", extra={"structured_data": output_data})
                return result

            except Exception as e:
                duration = time.time() - start_time
                error_data = {
                    "event": "agent_error",
                    "agent": agent_name,
                    "duration_sec": round(duration, 3),
                    "error_message": str(e)
                }
                app_logger.error(f"Ошибка в агенте {agent_name}", extra={"structured_data": error_data})
                raise e

        return wrapper

    return decorator
