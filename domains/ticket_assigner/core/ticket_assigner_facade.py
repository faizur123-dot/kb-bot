from domains.ticket_assigner.domain_infrastructure.ticket_service_client import TicketServiceClient
from domains.ticket_assigner.domain_infrastructure.db_client_impl import DBClient
from domains.ticket_assigner.core.ports.incoming.ticket_assigner_interface import TicketAssignerInterface
from utils.response import MyResponse
from utils.exception import MyError
from utils.singleton_class import SingletonMeta


class TicketAssigner(TicketAssignerInterface, metaclass=SingletonMeta):

    def __init__(self):
        self.ticket_service_client = TicketServiceClient()
        self.db_client = DBClient()

    def create_ticket(self, bug_description: str, bug_category: str, user_name: str, workflow_id: int):
        try:
            self.db_client.update_kb_workflow_status_current_state(workflow_id)
            ticket_url = self.ticket_service_client.create_ticket(bug_summary=bug_description,
                                                                  bug_category=bug_category,
                                                                  user_name=user_name)
            self.db_client.add_jira_bug_detail(workflow_id, ticket_url)
            response = {
                "ticket_link": ticket_url
            }
            return MyResponse(200, response)
        except Exception as err:
            raise MyError(error_code=500, error_message=f"Unable to assign ticket to user: {err}")
