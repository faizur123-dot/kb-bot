import json
import traceback
from utils.logger import logger
from domains.ticket_assigner.core.ticket_assigner_facade import TicketAssigner
from utils.response import MyResponse
from utils.exception import MyError


def assign_ticket_to_user(params):
    workflow_id = params.get('workflow_id', None)
    bug_description = params.get("bug_description", None)
    user_name = params.get("user_name", None)
    bug_category = params.get("bug_category", None)
    if workflow_id in (None, ""):
        raise MyError(
            error_code=422,
            error_message="workflow_id not provided in request. It is required for every request.",
        )
    if bug_description in (None, ""):
        raise MyError(
            error_code=422,
            error_message="bug_message_text not provided in request. it is required for every request"
        )
    facade = TicketAssigner(workflow_id)
    return facade.create_ticket(bug_description=bug_description, user_name=user_name, bug_category=bug_category)


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
    "assign_ticket_to_user": assign_ticket_to_user
}
