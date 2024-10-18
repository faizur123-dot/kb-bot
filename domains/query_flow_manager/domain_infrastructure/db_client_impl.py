import infrastructure.postgres_connector as db_connector
from constants import db_tables
from constants.schema import kb_workflow_fields
from constants.schema.current_state_enum import CurrentState
from constants.schema import slack_message_fields
from utils.common_utils import decode_string
from constants.schema import jira_bug_cateogry_domain_owner_fields
from constants.schema import user_fields
from utils.exception import MyError
from constants.schema import workflow_response_to_user_fields
from utils.common_utils import encode_string
from domains.query_flow_manager.core.ports.outgoing.db_client import DBClientInterface


class DBClient(DBClientInterface):
    """
    Class to handle all the DB operations
    """

    def __init__(self):
        pass

    def update_kb_workflow_status_current_state(self, workflow_id: int, service_name=None):
        data = []
        insertion_data = dict()
        insertion_data[kb_workflow_fields.WORKFLOW_ID] = workflow_id
        insertion_data[kb_workflow_fields.LAST_UPDATED_AT] = 'now()'
        if service_name is None:
            insertion_data[kb_workflow_fields.CURRENT_STATE] = CurrentState.driver_service.value
        else:
            insertion_data[kb_workflow_fields.CURRENT_STATE] = service_name
        data.append(insertion_data)
        try:
            db_connector.DatabaseConnection().upsert_row_into_table(
                db_tables.KB_WORKFLOW, data, [kb_workflow_fields.WORKFLOW_ID]
            )
        except Exception as err:
            raise err

    def update_kb_workflow_status(self, workflow_id: int, current_status: str):
        condition_dict = dict()
        condition_dict[kb_workflow_fields.WORKFLOW_ID] = [workflow_id]
        data = {
            kb_workflow_fields.WORKFLOW_STATUS: current_status
        }
        try:
            db_connector.DatabaseConnection().update_row_into_table(
                db_tables.KB_WORKFLOW, data, where_condition_dict=condition_dict
            )
        except Exception as err:
            raise err

    def get_slack_message_details(self, workflow_id: int) -> dict:
        condition_dict = dict()
        condition_dict[slack_message_fields.WORKFLOW_ID] = [workflow_id]
        column_list = [
            slack_message_fields.SLACK_MESSAGE_USER_ID,
            slack_message_fields.SLACK_MESSAGE_CHANNEL_ID,
            slack_message_fields.SLACK_MESSAGE_TEXT,
            slack_message_fields.TEAM_ID,
            slack_message_fields.SLACK_MESSAGE_TS
        ]
        try:
            response_dict = dict()
            df = db_connector.DatabaseConnection().get_rows_from_table(
                db_tables.SLACK_MESSAGE, *column_list, where_condition_dict=condition_dict
            )
            if not df.empty:
                slack_message_text = df[slack_message_fields.SLACK_MESSAGE_TEXT].iloc[0]
                if len(slack_message_text) > 0:
                    slack_message_text = decode_string(slack_message_text)
                response_dict = {
                    slack_message_fields.SLACK_MESSAGE_USER_ID: df[slack_message_fields.SLACK_MESSAGE_USER_ID].iloc[0],
                    slack_message_fields.SLACK_MESSAGE_CHANNEL_ID:
                        df[slack_message_fields.SLACK_MESSAGE_CHANNEL_ID].iloc[0],
                    slack_message_fields.SLACK_MESSAGE_TEXT: slack_message_text,
                    slack_message_fields.TEAM_ID: df[slack_message_fields.TEAM_ID].iloc[0],
                    slack_message_fields.SLACK_MESSAGE_TS: df[slack_message_fields.SLACK_MESSAGE_TS].iloc[0]
                }
            return response_dict
        except Exception as err:
            raise err

    def get_jira_user_name_of_bug_category(self, bug_category: str):
        user_id = self._get_domain_owner_user_id_for_the_bug_category(bug_category)
        jira_user_name = self._get_jira_user_name_for_user_id(user_id)
        return jira_user_name

    def _get_domain_owner_user_id_for_the_bug_category(self, bug_category: str):
        condition_dict = dict()
        condition_dict[jira_bug_cateogry_domain_owner_fields.BUG_CATEGORY] = [bug_category]
        try:
            df = db_connector.DatabaseConnection().get_rows_from_table(
                db_tables.JIRA_BUG_CATEGORY_DOMAIN_OWNER, jira_bug_cateogry_domain_owner_fields.BUG_CATEGORY,
                jira_bug_cateogry_domain_owner_fields.DOMAIN_OWNER_USER_ID, where_condition_dict=condition_dict
            )
            if not df.empty:
                domain_user_id = df[jira_bug_cateogry_domain_owner_fields.DOMAIN_OWNER_USER_ID].iloc[0]
                return domain_user_id
            else:
                raise MyError(error_code=404, error_message=f"Domain owner for the bug category not found")
        except Exception as err:
            raise err

    def _get_jira_user_name_for_user_id(self, user_id: str):
        condition_dict = dict()
        condition_dict[user_fields.USER_ID] = [user_id]
        try:
            df = db_connector.DatabaseConnection().get_rows_from_table(
                db_tables.USER_METADATA, user_fields.JIRA_USER_NAME, where_condition_dict=condition_dict
            )
            if not df.empty:
                jira_user_name = df[user_fields.JIRA_USER_NAME].iloc[0]
                if jira_user_name not in (None, ""):
                    return jira_user_name
                else:
                    raise MyError(error_code=404, error_message=f"User_id for Jira user name not found")
            else:
                raise MyError(error_code=404, error_message=f"Jira user id not found")

        except Exception as err:
            raise MyError(error_code=500, error_message=f"Jira user name for user_id not found: {err}")

    def upsert_response_data_for_workflow(self, workflow_id: int, response_text: str):
        response_text = encode_string(response_text)
        data = []
        insertion_data = dict()
        insertion_data[workflow_response_to_user_fields.WORKFLOW_ID] = workflow_id
        insertion_data[workflow_response_to_user_fields.RESPONSE_TEXT] = response_text
        insertion_data[workflow_response_to_user_fields.LAST_UPDATED_AT] = 'now()'
        data.append(insertion_data)
        try:
            db_connector.DatabaseConnection().upsert_row_into_table(
                db_tables.WORKFLOW_RESPONSE_TO_USER, data, [kb_workflow_fields.WORKFLOW_ID]
            )
        except Exception as err:
            raise err
