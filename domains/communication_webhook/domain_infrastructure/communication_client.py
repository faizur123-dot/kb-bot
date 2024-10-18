from infrastructure.slack_client import SlackClientImpl
from domains.communication_webhook.core.ports.outgoing.slack_client_interface import CommunicationClientInterface
from utils.exception import MyError


class CommunicationClient(CommunicationClientInterface):

    def __init__(self):
        self.communication_client = SlackClientImpl()

    def post_private_message_to_user(self, channel: str, user: str, message: str, blocks, thread_ts=None):
        try:
            self.communication_client.post_ephemeral_message(
                channel=channel,
                user=user,
                message=message,
                blocks=blocks,
                thread_ts=thread_ts,
            )
        except Exception as err:
            raise MyError(
                error_code=500,
                error_message=f"could not send message to the user: {err}"
            )

    def post_thread_message(self, channel: str, message: str, thread_ts, blocks=None):
        try:
            self.communication_client.post_message_in_thread(
                channel=channel,
                message=message,
                blocks=blocks,
                thread_ts=thread_ts,
            )
        except Exception as err:
            raise MyError(
                error_code=500,
                error_message=f"could not send message to the user: {err}"
            )
