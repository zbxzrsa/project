import logging
import json
from datetime import datetime
from typing import Any
import watchtower
import boto3
from backend.core.config import settings


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)
        return json.dumps(log_data)


def setup_logging():
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(JsonFormatter())
    root_logger.addHandler(console_handler)
    
    if settings.ENABLE_CLOUDWATCH and settings.AWS_ACCESS_KEY_ID:
        try:
            watchtower_handler = watchtower.CloudWatchLogHandler(
                log_group="/aws/codequality/api",
                boto3_session=boto3.Session(
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                    region_name=settings.AWS_REGION,
                ),
            )
            watchtower_handler.setFormatter(JsonFormatter())
            root_logger.addHandler(watchtower_handler)
        except Exception as e:
            root_logger.warning(f"Failed to setup CloudWatch logging: {e}")
    
    return root_logger


logger = logging.getLogger(__name__)
