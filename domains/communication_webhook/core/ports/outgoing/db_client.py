class DBClientInterface:

    def create_workflow_for_the_trigger(self, slack_trigger_id: str):
        pass

    def get_response_to_user_for_workflow(self, workflow_id):
        pass

    def add_slack_message_details(self, workflow_id: int, slack_message_user_id: str, slack_message_channel_id: str,
                                  slack_message_text: str, team_id: str):
        pass

    def mark_workflow_status_as_success(self, workflow_id):
        pass

    def update_kb_workflow_status_current_state(self, workflow_id: int):
        pass
