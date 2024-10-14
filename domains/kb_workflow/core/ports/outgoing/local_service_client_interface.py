class ServiceInvokeClientInterface:

    def query_knowledge_base(
            self, workflow_id: int, question: str
    ):
        pass

    def send_message_to_user(self, workflow_id: int, slack_message_detail: dict, llm_response_data: str):
        pass

    def categorise_the_text_as_one_of_bugs(self, workflow_id: int, question_text: str):
        pass

    def create_ticket(self, workflow_id: int, bug_description: str, bug_category: str):
        pass
