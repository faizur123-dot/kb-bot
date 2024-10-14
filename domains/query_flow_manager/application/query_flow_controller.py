import json
import traceback
import utils.exception as custom_exception
from utils.logger import logger
from utils.exception import MyError
from utils.response import MyResponse
from domains.query_flow_manager.core.query_flow_manager_facade import QueryFlowManager


def process_slack_message(params):
    workflow_id = params.get('workflow_id', None)
    question = params.get("question", None)
    if workflow_id in (None, ""):
        raise custom_exception.MyError(
            error_code=422,
            error_message="workflow_id not provided in request. It is required for every request.",
        )
    facade = QueryFlowManager(workflow_id)
    return facade.process_message_received_from_slack(question)


# REVIEW IS INSTANCE REMOVE
def invoke_function_by_key(key, params):
    try:
        function = key_to_function_map.get(key, None)
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
                logger.error(f"Error in {key} : {err.error_message}")
                if err.error_code >= 500:
                    raise err
            except Exception as err:
                logger.error(f"Error in {key} : {err}")
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


key_to_function_map = {
    "process_slack_message": process_slack_message
}
