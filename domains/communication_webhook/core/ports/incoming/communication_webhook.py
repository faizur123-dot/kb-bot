class CommunicationWebhookInterface:

    def process_user_query(self, text: str, user_id: str, team_id: str, channel_id: str, trigger_id: str):
        pass

    def send_response_to_user(self, question: str, answer: str, channel_id: str, user_id: str, workflow_id: int,
                              thread_ts=None):
        pass
