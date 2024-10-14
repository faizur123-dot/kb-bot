class DBInterface:
    """
    Interface for db client
    """

    def add_kb_response(self, workflow_id: int, answer: str):
        pass

    def add_message_bug_category(self, workflow_id: int, answer: str):
        pass

    def update_kb_workflow_status_current_state(self, workflow_id: int):
        pass
