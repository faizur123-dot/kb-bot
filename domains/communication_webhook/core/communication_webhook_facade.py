import json
from domains.communication_webhook.domain_infrastructure.db_client_impl import DBClient
from utils.common_utils import update_json_variables, get_json_from_path
from domains.communication_webhook.domain_infrastructure.communication_client import CommunicationClient
from constants.constants import KNOWLEDGE_BASE_QUERY_RESPONSE_MESSAGE
from domains.communication_webhook.core.ports.incoming.communication_webhook import \
    CommunicationWebhookInterface as CommWebhookInterface


class CommunicationWebhook(CommWebhookInterface):

    def __init__(self, workflow_id=None):
        self.db_client = DBClient()
        self.communication_client = CommunicationClient()
        self.workflow_id = workflow_id
        if workflow_id is not None:
            self.db_client.update_kb_workflow_status_current_state(workflow_id)

    @staticmethod
    def url_verification(challenge):
        return {"challenge": challenge}

    def process_user_query(self, text: str, user_id: str, team_id: str, channel_id: str, trigger_id: str,
                           thread_ts: str = None):
        try:
            workflow_id = self.db_client.create_workflow_for_the_trigger(trigger_id)
            response_to_user_for_workflow = self.db_client.get_response_to_user_for_workflow(workflow_id)
            if response_to_user_for_workflow is not None:
                return self.send_response_to_user(text, response_to_user_for_workflow, channel_id, user_id,
                                                  thread_ts=thread_ts)
            self.db_client.add_slack_message_details(workflow_id=workflow_id, slack_message_user_id=user_id,
                                                     slack_message_channel_id=channel_id, slack_message_text=text,
                                                     team_id=team_id, thread_ts=thread_ts)
            return workflow_id
        except Exception as err:
            raise err

    def send_response_to_user(self, question: str, answer: str, channel_id: str, user_id: str, thread_ts=None):
        knowledge_base_response_json = get_json_from_path(
            "constants/query_response.json"
        )

        variable_map = {"question": question, "answer": answer}
        forward_blocks = update_json_variables(
            knowledge_base_response_json, variable_map
        )
        json_list = json.dumps(forward_blocks, indent=2)
        if thread_ts is None:
            self.communication_client.post_private_message_to_user(channel=channel_id,
                                                                   message=KNOWLEDGE_BASE_QUERY_RESPONSE_MESSAGE,
                                                                   blocks=json_list,
                                                                   user=user_id)
        else:
            self.communication_client.post_thread_message(channel=channel_id, message=answer,
                                                          thread_ts=thread_ts)
        self.db_client.mark_workflow_status_as_success(workflow_id=self.workflow_id)
        return
