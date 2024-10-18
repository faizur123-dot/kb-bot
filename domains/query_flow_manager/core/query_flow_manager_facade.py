from domains.query_flow_manager.domain_infrastructure.db_client_impl import DBClient
from domains.query_flow_manager.domain_infrastructure.local_service_client import ServiceInvokeClient
from utils.exception import MyError
from constants.schema.current_state_enum import CurrentState
from constants.schema.workflow_status_enum import WorkflowStatus
from domains.query_flow_manager.core.ports.incoming.query_flow_manager import QueryFlowManagerInterface
from utils.singleton_class import SingletonMeta


class QueryFlowManager(QueryFlowManagerInterface, metaclass=SingletonMeta):

    def __init__(self):
        self.db_client = DBClient()
        self.service_invoker = ServiceInvokeClient()

    def process_message_received_from_slack(self, question: str, workflow_id: int):
        try:
            self.db_client.update_kb_workflow_status_current_state(workflow_id,
                                                                   CurrentState.driver_service.value)
            slack_message_detail: dict = self.db_client.get_slack_message_details(workflow_id)
            data_received_from_llm: str = self.service_invoker.query_knowledge_base(workflow_id=workflow_id,
                                                                                    question=question)
            if data_received_from_llm is None:
                response_to_user = self._process_no_response_from_llm(slack_message_detail, question, workflow_id)
            else:
                response_to_user = self._process_llm_service_response(data_received_from_llm, slack_message_detail,
                                                                      workflow_id)
            self.db_client.upsert_response_data_for_workflow(workflow_id=workflow_id,
                                                             response_text=response_to_user)
        except Exception as err:
            self.db_client.update_kb_workflow_status(workflow_id, WorkflowStatus.failed.value)
            raise MyError(error_code=500,
                          error_message=f"Could not successfully process message received from slack {err}")

    def _process_llm_service_response(self, llm_response_data: str, slack_message_detail: dict, workflow_id: int):
        self.service_invoker.send_message_to_user(workflow_id, slack_message_detail, llm_response_data)
        return llm_response_data

    def _process_no_response_from_llm(self, slack_message_detail: dict, question: str, workflow_id: int):
        bug_category: str = self.service_invoker.categorise_the_text_as_one_of_bugs(
            workflow_id, question)
        jira_ticket_link = self._process_bug_categorised(question, bug_category, workflow_id)
        response_text_for_user = self._process_jira_response(jira_ticket_link)
        self.service_invoker.send_message_to_user(workflow_id, slack_message_detail, response_text_for_user)
        return response_text_for_user

    def _process_bug_categorised(self, question: str, bug_category: str, workflow_id: int):
        ticket_link: str = self.service_invoker.create_ticket(workflow_id,
                                                              question, bug_category)
        return ticket_link

    @staticmethod
    def _process_jira_response(jira_ticket_link: str):
        if jira_ticket_link not in (None, ""):
            response_text_for_user = f"Could not find the answer in helpsite. Assigned ticket <{jira_ticket_link}|JIRA>"
            return response_text_for_user
        else:
            raise MyError(error_code=500, error_message="Could not assign ticket to user")

    # AS DISCUSSED, THIS WILL BE added later
    def _get_user_name_for_categorised_bug(self, bug_category: str):
        pass
