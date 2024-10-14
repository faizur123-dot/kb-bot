LOG_CONFIG = {
    "version": 1,
    "filters": {},
    "formatters": {
        "standard": {
            "format": "%(asctime)s | %(name)s.%(module)s.%(funcName)s | %(request_id)s | %(levelname)s | "
                      "%(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "filters": ["request_id"],
            "formatter": "standard",
        }
    },
    "loggers": {
        "": {
            "handlers": ["console"],
            "level": "INFO",
        },
        "app": {
            "handlers": ["console"],
            "level": "INFO",
        },
    },
}
