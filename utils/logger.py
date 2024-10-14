import logging.config

from constants.logger_constants import LOG_CONFIG

logger_request_id = ""


def set_req_id(req_id):
    global logger_request_id
    logger_request_id = req_id


def get_req_id():
    return logger_request_id


class RequestIdFilter(logging.Filter):
    def filter(self, record):
        record.request_id = logger_request_id
        return True


log_config = LOG_CONFIG.copy()
log_config["filters"] = {
    "request_id": {
        "()": RequestIdFilter,
    }
}
logging.config.dictConfig(log_config)
logger = logging.getLogger(__name__)
