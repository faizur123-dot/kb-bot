import uuid
import hashlib
import base64
import re
from pathlib import Path
from utils.exception import MyError
import json


def get_unique_id():
    return str(uuid.uuid4())


def compute_checksum(text: str) -> str:
    """Compute SHA-256 hash of the given text."""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def encode_string(text: str):
    encoded_string = base64.b64encode(text.encode()).decode()
    return encoded_string


def decode_string(encoded_text: str) -> str:
    decoded_bytes = base64.b64decode(encoded_text)
    decoded_string = decoded_bytes.decode()
    return decoded_string


def update_json_variables(input_json, variable_map):
    """
    Update json variables with the values from the variable map

    Args:
        input_json (dict): The json to update
        variable_map (dict): The variable map to use for updating the json

    Returns:
        dict|list: The updated json
    """
    if isinstance(input_json, list):
        for item in input_json:
            update_json_variables(item, variable_map)
    elif isinstance(input_json, dict):
        for key in input_json:
            if isinstance(input_json[key], dict) or isinstance(input_json[key], list):
                update_json_variables(input_json[key], variable_map)
            elif isinstance(input_json[key], str) and re.search("__", input_json[key]):
                variable_name = input_json[key]
                # Sanitize variable name
                variable_name = variable_name.replace("__", "")

                # Lowercase
                variable_name = variable_name.lower()

                variable = variable_map.get(variable_name, None)
                if variable is not None:
                    if type(variable) is dict or type(variable) is list:
                        input_json[key] = variable
                    else:
                        input_json[key] = re.sub(
                            "(__)(.*)(__)", variable, input_json[key]
                        )

    return input_json


def get_json_from_path(path):
    """
    Get json from a file path

    Args:
        path (str): The path to the file
    """
    try:
        path = Path(path)
        with open(path) as file:
            data = json.load(file)
            return data
    except Exception as e:
        raise MyError(
            error_code=f"Error getting json from path: {path}",
            error_message=e,
        )
