import threading

from utils.logger import logger


class SingletonMeta(type):
    _instances = {}
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
                logger.info(f"Creating new instance of {cls.__name__} with id: {id(instance)}")
            else:
                instance = cls._instances[cls]
                logger.info(f"Using existing instance of {cls.__name__} with id: {id(instance)}")
        return instance
