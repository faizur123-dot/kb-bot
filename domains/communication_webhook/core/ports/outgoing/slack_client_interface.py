class CommunicationClientInterface:

    def post_private_message_to_user(self, channel: str, user: str, message: str, blocks, thread_ts=None):
        pass
