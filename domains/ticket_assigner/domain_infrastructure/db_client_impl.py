import infrastructure.postgres_connector as db_connector
from domains.ticket_assigner.core.ports.outgoing.db_client_interface import DBInterface
from constants import db_tables
from constants.schema import jira_bug_details_fields
from constants.schema import kb_workflow_fields
from constants.schema.current_state_enum import CurrentState


class DBClient(DBInterface):
    """
    Class to handle all the DB operations
    """

    def __init__(self) -> None:
        self.db_connector = db_connector.DatabaseConnection()

    def add_jira_bug_detail(self, workflow_id: int, ticket_link: str, user_name: str = None):
        data = []
        insertion_data = {
            jira_bug_details_fields.WORKFLOW_ID: workflow_id,
            jira_bug_details_fields.TICKET_LINK: ticket_link,
            jira_bug_details_fields.LAST_UPDATED_AT: 'now()',
        }
        if user_name is not None:
            insertion_data[jira_bug_details_fields.ASSIGNEE_USER_NAME] = user_name
        data.append(insertion_data)
        try:
            self.db_connector.upsert_row_into_table(
                db_tables.JIRA_BUG_DETAILS, data, [jira_bug_details_fields.WORKFLOW_ID]
            )
        except Exception as err:
            raise err

    def update_kb_workflow_status_current_state(self, workflow_id: int):
        data = []
        insertion_data = {
            kb_workflow_fields.WORKFLOW_ID: workflow_id,
            kb_workflow_fields.CURRENT_STATE: CurrentState.jira_service.value,
            kb_workflow_fields.LAST_UPDATED_AT: 'now()'
        }
        data.append(insertion_data)
        try:
            self.db_connector.upsert_row_into_table(
                db_tables.KB_WORKFLOW, data, [kb_workflow_fields.WORKFLOW_ID]
            )
        except Exception as err:
            raise err
