import pandas as pd
from constants.schema import workflow_response_to_user_fields
from infrastructure.postgres_connector import DatabaseConnection
from constants.schema import kb_workflow_fields
from constants import db_tables
from constants.schema.current_state_enum import CurrentState
from constants.schema.workflow_status_enum import WorkflowStatus
from constants.schema import slack_message_fields
from utils.common_utils import encode_string
from utils.common_utils import decode_string
from utils.exception import MyError
from domains.communication_webhook.core.ports.outgoing.db_client import DBClientInterface


class DBClient(DBClientInterface):
    """
    Class to handle all the DB operations
    """

    def __init__(self) -> None:
        self.db_connector = DatabaseConnection()

    def create_workflow_for_the_trigger(self, slack_trigger_id: str):
        existing_workflow_id = self._get_workflow_id_of_trigger(slack_trigger_id)
        if existing_workflow_id is None:
            data = []
            insertion_data = {
                kb_workflow_fields.SLACK_TRIGGER_ID: slack_trigger_id,
                kb_workflow_fields.CURRENT_STATE: CurrentState.slack_service.value,
                kb_workflow_fields.WORKFLOW_STATUS: WorkflowStatus.in_progress.value
            }
            data.append(insertion_data)
            try:
                self.db_connector.insert_row_into_table(
                    db_tables.KB_WORKFLOW, data
                )
                new_workflow_id = self._get_workflow_id_of_trigger(slack_trigger_id)
                if new_workflow_id is None:
                    raise MyError(error_code=500, error_message=f"Cant find the workflow id created")
                return new_workflow_id
            except Exception as err:
                raise err
        return existing_workflow_id

    def get_response_to_user_for_workflow(self, workflow_id):
        condition_dict = dict()
        condition_dict[workflow_response_to_user_fields.WORKFLOW_ID] = [workflow_id]
        try:
            df = self.db_connector.get_rows_from_table(
                db_tables.WORKFLOW_RESPONSE_TO_USER, workflow_response_to_user_fields.RESPONSE_TEXT,
                where_condition_dict=condition_dict
            )
            if df.empty:
                return None
            else:
                return decode_string(df[workflow_response_to_user_fields.RESPONSE_TEXT].iloc[0])
        except Exception as err:
            raise err

    def _get_workflow_id_of_trigger(self, slack_trigger_id: str):
        condition_dict = dict()
        condition_dict[kb_workflow_fields.SLACK_TRIGGER_ID] = [slack_trigger_id]
        try:
            df = self.db_connector.get_rows_from_table(
                db_tables.KB_WORKFLOW,
                kb_workflow_fields.WORKFLOW_ID,
                where_condition_dict=condition_dict,
            )
            if df.empty:
                return None
            return df[kb_workflow_fields.WORKFLOW_ID].iloc[0]
        except Exception as err:
            raise err

    def add_slack_message_details(self, workflow_id: int, slack_message_user_id: str, slack_message_channel_id: str,
                                  slack_message_text: str, team_id: str):
        data = []
        slack_message_text = encode_string(slack_message_text)
        insertion_data = {
            slack_message_fields.WORKFLOW_ID: workflow_id,
            slack_message_fields.SLACK_MESSAGE_USER_ID: slack_message_user_id,
            slack_message_fields.SLACK_MESSAGE_CHANNEL_ID: slack_message_channel_id,
            slack_message_fields.SLACK_MESSAGE_TEXT: slack_message_text,
            slack_message_fields.TEAM_ID: team_id
        }
        data.append(insertion_data)
        try:
            self.db_connector.insert_row_into_table(
                db_tables.SLACK_MESSAGE, data
            )
        except Exception as err:
            raise err

    def mark_workflow_status_as_success(self, workflow_id):
        condition_dict = dict()
        condition_dict[kb_workflow_fields.WORKFLOW_ID] = [workflow_id]
        data = {
            kb_workflow_fields.WORKFLOW_STATUS: WorkflowStatus.completed.value
        }
        try:
            self.db_connector.update_row_into_table(
                db_tables.KB_WORKFLOW, data, where_condition_dict=condition_dict
            )
        except Exception as err:
            raise err

    def update_kb_workflow_status_current_state(self, workflow_id: int):
        data = []
        insertion_data = {
            kb_workflow_fields.WORKFLOW_ID: workflow_id,
            kb_workflow_fields.CURRENT_STATE: CurrentState.slack_service.value,
            kb_workflow_fields.LAST_UPDATED_AT: 'now()'
        }
        data.append(insertion_data)
        try:
            self.db_connector.upsert_row_into_table(
                db_tables.KB_WORKFLOW, data, [kb_workflow_fields.WORKFLOW_ID]
            )
        except Exception as err:
            raise err
