from domains.knowledge_base.application.knowledge_base_controller import query_knowledge_base, categorise_bug
from infrastructure.local_service_connector import LocalServiceConnector
from infrastructure.kb_api_client import KBApi
from utils.response import MyResponse
from constants.schema.slack_message_fields import SLACK_MESSAGE_TEXT, SLACK_MESSAGE_USER_ID, SLACK_MESSAGE_CHANNEL_ID
from domains.communication_webhook.application.communication_webhook_controller import send_response_to_user
from domains.ticket_assigner.application.ticket_assigner_controller import assign_ticket_to_user
from domains.query_flow_manager.core.ports.outgoing.local_service_client_interface import ServiceInvokeClientInterface
from utils.response import MyResponse
from utils.exception import MyError


class ServiceInvokeClient(ServiceInvokeClientInterface):

    def __init__(self):
        self.service_invoker = LocalServiceConnector()
        self.kb_api_invoker = KBApi()

    def query_knowledge_base(
            self, workflow_id: int, question: str
    ):
        function_inputs = {
            "workflow_id": workflow_id,
            "question": question
        }
        function_name = query_knowledge_base
        response: MyResponse = self.service_invoker.invoke_local_function(function_name, function_inputs)
        if response.status_code == 200:
            return response.body.get("answer")
        elif response.status_code == 404:
            return None
        else:
            raise MyError(error_code=500, error_message="Didnt get expected response from KB")

    def send_message_to_user(self, workflow_id: int, slack_message_detail: dict, llm_response_data: str):
        payload = {
            "workflow_id": int(workflow_id),
            "question": slack_message_detail.get(SLACK_MESSAGE_TEXT),
            "user_id": slack_message_detail.get(SLACK_MESSAGE_USER_ID),
            "channel_id": slack_message_detail.get(SLACK_MESSAGE_CHANNEL_ID),
            "answer": llm_response_data
        }
        function_name = send_response_to_user
        self.service_invoker.invoke_local_function(function_name, function_input=payload)

    def categorise_the_text_as_one_of_bugs(self, workflow_id: int, question_text: str):
        function_inputs = {
            "workflow_id": workflow_id,
            "bug_message_text": question_text
        }
        response = self.service_invoker.invoke_local_function(categorise_bug, function_inputs)
        if response.status_code == 200:
            return response.body.get("answer")
        else:
            return None

    def create_ticket(self, workflow_id: int, bug_description: str, bug_category: str):
        payload = {
            "workflow_id": int(workflow_id),
            "bug_description": bug_description,
            "bug_category": bug_category
        }
        response: MyResponse = self.service_invoker.invoke_local_function(assign_ticket_to_user, function_input=payload)
        if response.status_code == 200:
            ticket_link = response.body.get("ticket_link")
            return ticket_link
        else:
            raise MyError(error_code=500, error_message="Bug was not raised")
