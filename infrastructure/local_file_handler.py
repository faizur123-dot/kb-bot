import os

import pandas as pd

import utils.exception as custom_excpt
from utils.logger import logger
from constants import constants


def read_file_from_local_into_df(filepath, file_format, index_col=None):
    if file_format == constants.FILE_FORMAT_PARQUET:
        raw_data = pd.read_parquet(filepath)
    elif file_format == constants.FILE_FORMAT_CSV:
        raw_data = pd.read_csv(filepath, index_col=index_col)
    elif file_format == constants.FILE_FORMAT_JSON:
        raw_data = pd.read_json(filepath)
    else:
        logger.error(
            message="Cannot process data, input file type not supported yet!",
        )
        raise custom_excpt.MyError(
            error_code=500,
            error_message="Cannot process data, input file type not supported yet!",
        )
    return raw_data


def write_file_into_local(df, filepath, file_format):
    folder_path = filepath.rsplit("/", 1)[0] + "/"
    df = df.drop_duplicates()
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    if file_format == constants.FILE_FORMAT_PARQUET:
        df.to_parquet(filepath)
    elif file_format == constants.FILE_FORMAT_CSV:
        df.to_csv(filepath, index=False)
    else:
        logger.error(
            message="Cannot write to file file type not supported yet!",
        )
        raise custom_excpt.MyError(
            error_code=400,
            error_message="Cannot write to file file type not supported yet!",
        )
