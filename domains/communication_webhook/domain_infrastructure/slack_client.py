from infrastructure.slack_client import SlackClientImpl
from domains.communication_webhook.core.ports.outgoing.slack_client_interface import SlackClientInterface


class SlackClient(SlackClientInterface):

    def __init__(self):
        self.communication_client = SlackClientImpl()

    def post_private_message_to_user(self, channel: str, user: str, message: str, blocks, thread_ts=None):
        self.communication_client.post_ephemeral_message(
            channel=channel,
            user=user,
            message=message,
            blocks=blocks,
            thread_ts=thread_ts,
        )
