import infrastructure.postgres_connector as db_connector
from domains.knowledge_base.core.ports.outgoing.db_client_interface import DBInterface
from utils.common_utils import encode_string
from constants import db_tables
from constants.schema import llm_response_metadata_fields
from constants.schema import message_bug_category_fields
from constants.schema import kb_workflow_fields
from constants.schema.current_state_enum import CurrentState


class DBClient(DBInterface):
    """
    Class to handle all the DB operations
    """

    def __init__(self) -> None:
        self.db_connector = db_connector.DatabaseConnection()

    def add_kb_response(self, workflow_id: int, answer: str):
        encoded_answer = encode_string(answer)
        data = []
        insertion_data = {
            llm_response_metadata_fields.WORKFLOW_ID: workflow_id,
            llm_response_metadata_fields.LLM_RESPONSE_TEXT: encoded_answer,
            llm_response_metadata_fields.LAST_UPDATED_AT: 'now()'
        }
        data.append(insertion_data)
        try:
            self.db_connector.upsert_row_into_table(
                db_tables.LLM_RESPONSE_METADATA, data, [llm_response_metadata_fields.WORKFLOW_ID]
            )
        except Exception as err:
            raise err

    def add_message_bug_category(self, workflow_id: int, answer: str):
        data = []
        insertion_data = {
            message_bug_category_fields.WORKFLOW_ID: workflow_id,
            message_bug_category_fields.MESSAGE_BUG_CATEGORY: answer,
            llm_response_metadata_fields.LAST_UPDATED_AT: 'now()'
        }
        data.append(insertion_data)
        try:
            self.db_connector.upsert_row_into_table(
                db_tables.MESSAGE_BUG_CATEGORY, data, [llm_response_metadata_fields.WORKFLOW_ID]
            )
        except Exception as err:
            raise err

    def update_kb_workflow_status_current_state(self, workflow_id: int):
        data = []
        insertion_data = {
            kb_workflow_fields.WORKFLOW_ID: workflow_id,
            kb_workflow_fields.CURRENT_STATE: CurrentState.llm_service.value,
            kb_workflow_fields.LAST_UPDATED_AT: 'now()'
        }
        data.append(insertion_data)
        try:
            self.db_connector.upsert_row_into_table(
                db_tables.KB_WORKFLOW, data, [kb_workflow_fields.WORKFLOW_ID]
            )
        except Exception as err:
            raise err
