from fastapi import APIRouter, Request, Response, HTTPException
from utils.logger import logger, set_req_id
from utils import common_utils
from domains.kb_workflow.application.kb_workflow_controller import invoke_function_by_key

router = APIRouter(
    prefix="",
)


@router.post("/process")
async def respond_in_slack(request: Request):
    set_req_id(common_utils.get_unique_id())
    logger.info("respond_in_slack")

    body = await request.json()

    res = invoke_function_by_key("process_slack_message", body)

    try:
        res = Response(
            content=res["body"], status_code=res["statusCode"], headers=res["headers"]
        )
    except Exception as e:
        logger.error(f"Error in respond_answer_to_user : {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

    return res
