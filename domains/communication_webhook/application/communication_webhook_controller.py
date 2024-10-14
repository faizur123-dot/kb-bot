from utils.logger import logger
from domains.communication_webhook.application.helpers import validate_slack_request
from domains.communication_webhook.application.helpers import get_slack_operation_type
import traceback
from domains.communication_webhook.core.communication_webhook_facade import CommunicationWebhook
from domains.communication_webhook.application.helpers import get_command
from utils.common_utils import update_json_variables, get_json_from_path
from utils.response import MyResponse
import json
from utils.exception import MyError
import threading
from domains.communication_webhook.domain_infrastructure.local_service_client import ServiceInvokeClient
from domains.communication_webhook.domain_infrastructure.db_client_impl import DBClient


def validate_process_user_query(params):
    text = params.get("text", None)
    user_id = params.get("user_id", None)

    if text is None:
        raise Exception("Text is missing")

    if user_id is None:
        raise Exception("User id is missing")


def validate_send_response_to_user(params):
    question = params.get("question", None)
    answer = params.get("answer", None)
    user_id = params.get("user_id", None)
    workflow_id = params.get("workflow_id", None)
    if question is None:
        raise Exception("question is missing")
    if workflow_id is None:
        raise Exception("workflow id is missing")
    if user_id is None:
        raise Exception("User id is missing")

    if answer is None:
        raise Exception("answer is missing")


def send_response_to_user(params):
    try:
        validate_send_response_to_user(params)
        logger.info(params)
        question = params.get("question", None)
        workflow_id = params.get("workflow_id", None)
        user_id = params.get("user_id", None)
        answer = params.get("answer", None)
        channel_id = params.get("channel_id", None)
        facade = CommunicationWebhook(workflow_id)
        facade.send_response_to_user(question, answer, channel_id, user_id)
        DBClient().mark_workflow_status_as_success(workflow_id=workflow_id)
    except Exception as err:
        raise MyError(error_code=500, error_message=f"Unable to send response to user: {err}")


def handle_user_query(params):
    validate_process_user_query(params)
    logger.info(params)

    user_id = params.get("user_id", None)
    team_id = params.get("team_id", None)
    trigger_id = params.get("trigger_id", " ")
    text = params.get("text", None)
    text = text.strip()
    text = text.replace("+", " ")
    channel_id = params.get("channel_id", None)

    knowledge_base_acknowledge_response = get_json_from_path(
        "constants/query_response_acknowledge.json"
    )

    knowledge_base_acknowledge_response = update_json_variables(
        knowledge_base_acknowledge_response,
        {
            "query_text": "*Query:* " + text,
        },
    )

    # Create and start a new thread
    query_thread = threading.Thread(
        target=process_user_query,
        args=(text, user_id, team_id, channel_id, trigger_id)
    )
    query_thread.start()

    return knowledge_base_acknowledge_response


def process_user_query(text, user_id, team_id, channel_id, trigger_id):
    try:
        # Log the processing of the query
        logger.info(f"Processing query for user_id: {user_id}, text: {text}")
        facade = CommunicationWebhook()
        # Call your facade method to process the query
        workflow_id = facade.process_user_query(
            text=text,
            user_id=user_id,
            team_id=team_id,
            channel_id=channel_id,
            trigger_id=trigger_id
        )
        # Log successful processing
        logger.info(f"Successfully processed query for user_id: {user_id}")
        if workflow_id is None:
            return
        ServiceInvokeClient().invoke_query_flow_manager(workflow_id, text)
    except Exception as e:
        # Log any errors that occur during processing
        logger.error(f"Error processing query for user_id: {user_id}, error: {e}", exc_info=True)


def invoke_slack_function_by_event_type(event, params):
    """
    This function invokes the slack function based on the event type
    """

    if params.get("ssl_check", None) is not None:
        logger.info("SSL check request acknowledged")
        return {"statusCode": 200, "body": "OK"}

    try:
        validate_slack_request(event)
    except Exception as e:
        logger.error(
            f"Error: {e.with_traceback(traceback.print_exc())} while processing request",
            exc_info=True,
        )
        return {"statusCode": 403, "body": "Invalid request"}

    # x-slack-retry-num header is sent by slack when it retries the request
    # We don't want to process the request again if it is a retry
    if (
            event.get("headers", {}).get(
                "x-slack-retry-num", event.get("headers", {}).get("X-Slack-Retry-Num", None)
            )
            is not None
    ):
        return {"statusCode": 200, "body": "OK"}

    slack_operation_type = get_slack_operation_type(params)
    if slack_operation_type == "slash_command":
        command = get_command(params)
        function_name = command
    else:
        err = {
            "error_code": 404,
            "error_message": "No function found for slack operation type : "
                             + str(slack_operation_type),
        }
        logger.error("No function found.  Error = {}".format(err), exc_info=True)
        return {"statusCode": 404, "body": err["error_message"]}

    try:
        function = action_to_function_map.get(function_name, None)

        logger.info(function_name)
        if function is not None:
            try:
                response = function(params)
                logger.info("Response")
                logger.info(response)
                return {
                    "statusCode": 200,
                    "body": response,
                    "headers": {
                        "Content-Type": "application/json",
                    },
                }
            except Exception as err:
                logger.error(
                    f"Error in invoking function : {str(function_name)}. Error = {str(err)}",
                    exc_info=True,
                )

                return {"statusCode": 500, "body": err.args[0]}
    except Exception as e:
        logger.error(
            f"Error: {e.with_traceback(traceback.print_exc())} while processing request - {function_name}",
            exc_info=True,
        )
        err = {
            "error_code": 500,
            "error_message": f"Error:: {e.with_traceback(traceback.print_exc())} while processing request - {function_name}",
        }
        return {"statusCode": 500, "body": err["error_message"]}


def invoke_function_by_key(key, params):
    try:
        function = action_to_function_map.get(key, None)
        if function is not None:
            try:
                response = function(params)
                if isinstance(response, MyResponse):
                    logger.info(
                        f"Response from {key} : Status Code : {response.status_code} Body : {response.body}"
                    )
                    return {
                        "statusCode": response.status_code,
                        "body": json.dumps(response.body),
                        "headers": {
                            "Content-Type": "application/json",
                        },
                    }
                else:
                    logger.info(f"Response from {key} : {response}")
                    return {
                        "statusCode": 200,
                        "body": json.dumps(response),
                        "headers": {
                            "Content-Type": "application/json",
                        },
                    }
            except MyError as err:
                logger.error(f"Error in {key} : {err.error_message}", exc_info=True)
                if err.error_code >= 500:
                    raise err
            except Exception as err:
                logger.error(f"Error in {key} : {err}", exc_info=True)
                raise err
        else:
            err = {
                "error_code": 404,
                "error_message": "Invoking unknown function : " + str(key),
            }
            logger.error(err["error_message"], exc_info=True)
            raise Exception(err["error_message"])
    except MyError as e:
        err = {
            "error_code": e.error_code,
            "error_message": e.error_message,
        }
        return {
            "statusCode": e.error_code,
            "body": json.dumps({"error": err["error_message"]}),
            "headers": {"Content-Type": "application/json"},
        }
    except Exception as e:
        err = {
            "error_code": 500,
            "error_message": f"Error:: {e.with_traceback(traceback.print_exc())} while processing request - {key}",
        }
        return {
            "statusCode": 500,
            "body": json.dumps({"error": err["error_message"]}),
            "headers": {"Content-Type": "application/json"},
        }


action_to_function_map = {
    "/ask": handle_user_query,
    "respond_answer_to_user": send_response_to_user
}
