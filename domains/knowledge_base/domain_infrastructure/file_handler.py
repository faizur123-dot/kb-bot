import os
from utils.logger import logger

import constants.constants


# USE ENUM INSTEAD OF CONSTANTS
def fetch_file(filepath: str) -> str:
    environment = os.environ.get("ENVIRONMENT")
    if environment == constants.constants.LOCAL_ENVIRONMENT:
        logger.info("File is already downloaded")
        return filepath
