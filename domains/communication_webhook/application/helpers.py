import json
from urllib.parse import unquote
from utils.exception import MyError
from infrastructure.slack_client import SlackClientImpl


def get_event_params(content_type, body):
    if content_type == "application/json":
        params = json.loads(body)
        return params

    elif content_type == "application/x-www-form-urlencoded":
        params = {}
        for param in body.split("&"):
            key, value = param.split("=")
            value = unquote(value)
            params[key] = value

        return params


def validate_slack_request(event):
    body = event.get("body", None)
    if body is None:
        raise MyError(error_code=403, error_message="body is missing")

    headers = event.get("headers", {})
    if headers is None:
        raise MyError(error_code=403, error_message="headers is missing")

    timestamp = headers.get(
        "X-Slack-Request-Timestamp", headers.get("x-slack-request-timestamp", None)
    )
    if timestamp is None:
        raise MyError(
            error_code=403, error_message="slack request timestamp is missing"
        )

    signature = headers.get("X-Slack-Signature", headers.get("x-slack-signature", None))
    if signature is None:
        raise MyError(
            error_code=403, error_message="slack request signature is missing"
        )

    is_valid = SlackClientImpl().validate_slack_request(
        body=body, timestamp=timestamp, signature=signature
    )

    if not is_valid:
        raise MyError(error_code=403, error_message="invalid slack request")


def get_slack_operation_type(params):
    slack_operation_type = "event"
    if "command" in params:
        slack_operation_type = "slash_command"
    if "type" in params:
        if params["type"] == "url_verification":
            slack_operation_type = "url_verification"
    return slack_operation_type


def get_slack_event_type(params):
    if "event" in params:
        event = params["event"]
        if "type" in event:
            event_type = event["type"]
            if event["type"] == "message":
                if "client_msg_id" not in event:
                    event_type = event_type + ":" + "bot"
                    return event_type
                elif "thread_ts" in event:
                    event_type = event_type + ":" + "thread"
                    return event_type
                else:
                    return event_type + ":" + "parent"
    return None


def get_command(params):
    if "command" in params:
        return params["command"]
    return None
