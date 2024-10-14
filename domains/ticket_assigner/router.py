from fastapi import APIRouter, Request, Response, HTTPException

from domains.ticket_assigner.application.ticket_assigner_controller import (
    invoke_function_by_key,
)
from utils import common_utils
from utils.logger import set_req_id, logger

router = APIRouter(
    prefix="/ticket",
)


@router.post("/assign")
async def assign_ticket(request: Request):
    set_req_id(common_utils.get_unique_id())
    logger.info("assigining ticket")

    body = await request.json()

    res = invoke_function_by_key("assign_ticket_to_user", body)

    try:
        res = Response(
            content=res["body"], status_code=res["statusCode"], headers=res["headers"]
        )
    except Exception as e:
        logger.error(f"Error in route_to_add_data_to_knowledge_base : {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

    return res
