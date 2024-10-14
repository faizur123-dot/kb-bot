from infrastructure.jira_client import JiraClient
from constants import constants
from domains.ticket_assigner.core.ports.outgoing.ticket_service_client_interface import TicketServiceClientInterface


class TicketServiceClient(TicketServiceClientInterface):

    def __init__(self):
        self.ticket_service_client = JiraClient()

    def create_ticket(self, bug_summary: str, bug_category: str, user_name: str):
        project_key = constants.PROJECT_KEY
        return self.ticket_service_client.create_ticket_and_return_url(project_key=project_key, bug_summary=bug_summary,
                                                                       bug_category=bug_category,
                                                                       user_name=user_name)
