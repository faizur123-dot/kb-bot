import os
from utils.logger import logger
from utils.exception import MyError
import requests


class KBApi:

    def __init__(self):
        self.base_url = os.environ.get("KB_API_BASE_URL")

    def process_slack_message_received(self, workflow_id: int, text: str):
        payload = {
            "workflow_id": int(workflow_id),
            "question": text
        }
        endpoint = f"{self.base_url}/process"
        try:
            response = requests.post(endpoint, json=payload)
            if response.status_code == 200:
                logger.info("Message sent successfully!")
            else:
                logger.error(f"Failed to send message. Status code: {response.status_code}, Response: {response.text}")
                raise MyError(error_code=500, error_message={response.text})
            return response
        except requests.RequestException as e:
            raise MyError(error_code=500, error_message=f"Could not process slack message received {e}")
