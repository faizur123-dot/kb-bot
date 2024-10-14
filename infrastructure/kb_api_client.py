import os
from utils.logger import logger
from utils.exception import MyError
from constants.schema.slack_message_fields import SLACK_MESSAGE_TEXT, SLACK_MESSAGE_USER_ID, SLACK_MESSAGE_CHANNEL_ID
import requests


class KBApi:

    def __init__(self):
        self.base_url = os.environ.get("KB_API_BASE_URL")

    def query_knowledge_base(self, workflow_id: int, question: str):
        payload = {
            "workflow_id": int(workflow_id),
            "question": question
        }
        endpoint = f"{self.base_url}/knowledgebase/query"
        try:
            response = requests.get(endpoint, params=payload)
            return response
        except Exception as err:
            raise err

    def send_message_to_user(self, workflow_id: int, slack_message_detail: dict, response: str):
        payload = {
            "workflow_id": int(workflow_id),
            "question": slack_message_detail.get(SLACK_MESSAGE_TEXT),
            "user_id": slack_message_detail.get(SLACK_MESSAGE_USER_ID),
            "channel_id": slack_message_detail.get(SLACK_MESSAGE_CHANNEL_ID),
            "answer": response
        }

        endpoint = f"{self.base_url}/slack/respond"

        try:
            response = requests.post(endpoint, json=payload)

            if response.status_code == 200:
                logger.info("Message sent successfully!")
            else:
                logger.info(f"Failed to send message. Status code: {response.status_code}, Response: {response.text}")

        except requests.RequestException as e:
            logger.error(f"An error occurred: {e}")
            raise MyError(error_code=500, error_message="Unable to send response to user")

    def categorise_bug(self, workflow_id: int, question: str):
        payload = {
            "workflow_id": int(workflow_id),
            "bug_message_text": question
        }

        endpoint = f"{self.base_url}/knowledgebase/category"

        try:
            response = requests.get(endpoint, params=payload)
            if response.status_code == 200:
                logger.info("Message sent successfully!")
            else:
                logger.error(f"Failed to send message. Status code: {response.status_code}, Response: {response.text}")
                raise MyError(error_code=500, error_message={response.text})
            return response
        except requests.RequestException as e:
            logger.error(f"An error occurred: {e}")
            raise MyError(error_code=500, error_message=f"could not categorise bug {e}")

    def assign_ticket_to_jira_user(self, workflow_id: int, user_name: str, bug_description: str, bug_category: str):
        payload = {
            "workflow_id": int(workflow_id),
            "user_name": user_name,
            "bug_description": bug_description,
            "bug_category": bug_category
        }
        endpoint = f"{self.base_url}/ticket/assign"
        try:
            response = requests.post(endpoint, json=payload)

            if response.status_code == 200:
                logger.info("Message sent successfully!")
            else:
                logger.error(f"Failed to send message. Status code: {response.status_code}, Response: {response.text}")
                raise MyError(error_code=500, error_message={response.text})
            return response
        except requests.RequestException as e:
            raise MyError(error_code=500, error_message=f"could not process assigning ticket to Jira user {e}")

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
