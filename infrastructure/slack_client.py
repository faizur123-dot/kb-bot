from slack_bolt import App
import os
from slack_sdk.signature import SignatureVerifier
import json
from utils.exception import MyError


class SlackClientImpl:
    def __init__(self, bot_token=None):
        if bot_token is None:
            workspace_bot_token = os.environ.get("WORKSPACE_BOT_TOKEN")
            if not workspace_bot_token:
                raise MyError(error_code=500, error_message=f"Workspace bot token not given")
            bot_token = workspace_bot_token
        self.bot_token = bot_token
        self.app = App(
            token=bot_token,
            signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
        )

    @staticmethod
    def validate_slack_request(body, timestamp, signature):
        is_valid_request = False
        signature_verifier = SignatureVerifier(
            signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
        )

        try:
            is_valid_request = signature_verifier.is_valid(body, timestamp, signature)
        except Exception as err:
            print(err)

        return is_valid_request

    def post_ephemeral_message(self, channel, user, message, blocks=None, thread_ts=None):
        client = self.app.client
        if thread_ts is not None:
            client.chat_postEphemeral(
                channel=channel,
                user=user,
                text=message,
                blocks=blocks,
                thread_ts=thread_ts,
            )
        else:
            client.chat_postEphemeral(
                channel=channel, user=user, text=message, blocks=blocks
            )
