class DBClientInterface:

    def update_kb_workflow_status_current_state(self, workflow_id: int, service_name=None):
        pass

    def update_kb_workflow_status(self, workflow_id: int, current_status: str):
        pass

    def get_slack_message_details(self, workflow_id: int):
        pass

    def get_jira_user_name_of_bug_category(self, bug_category: str):
        pass

    def upsert_response_data_for_workflow(self, workflow_id: int, response_text: str):
        pass
