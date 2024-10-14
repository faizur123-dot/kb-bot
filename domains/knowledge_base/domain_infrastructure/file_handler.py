import os
from utils.logger import logger
from utils.common_utils import get_unique_id
import constants.constants


def fetch_file(filepath: str) -> str:
    environment = os.environ.get("ENVIRONMENT")
    if environment == constants.constants.LOCAL_ENVIRONMENT:
        logger.info("File is already downloaded")
        return filepath


def convert_src_text_to_txt_file(src_text: str):
    file_path = f"{constants.constants.FILE_PERSIST_LOCATION}" + f"{get_unique_id()}.txt"
    with open(file_path, "w") as txt_file:
        txt_file.write(src_text)

    return file_path
