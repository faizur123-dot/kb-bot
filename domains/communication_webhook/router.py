from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import JSONResponse
from domains.communication_webhook.application.helpers import get_event_params
from domains.communication_webhook.application.communication_webhook_controller import \
    invoke_slack_function_by_event_type
from utils.logger import logger, set_req_id
from utils import common_utils
from domains.communication_webhook.application.communication_webhook_controller import invoke_function_by_key

router = APIRouter(
    prefix="/slack",
)


@router.post("/query")
async def post_slack(request: Request):
    logger.info(request)
    body = await request.body()
    body = body.decode("utf-8")
    headers_dict = dict(request.headers)
    event = {"body": body, "headers": headers_dict}
    content_type = event.get("headers", {}).get(
        "Content-Type", event.get("headers", {}).get("content-type", None)
    )
    params = get_event_params(content_type, body)
    res = invoke_slack_function_by_event_type(event=event, params=params)
    return JSONResponse(content=res["body"], status_code=res["statusCode"])


@router.post("/respond")
async def respond_in_slack(request: Request):
    set_req_id(common_utils.get_unique_id())
    logger.info("responding in slack")

    body = await request.json()

    res = invoke_function_by_key("respond_answer_to_user", body)

    try:
        res = Response(
            content=res["body"], status_code=res["statusCode"], headers=res["headers"]
        )
    except Exception as e:
        logger.error(f"Error in respond_answer_to_user : {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

    return res
