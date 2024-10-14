from fastapi import APIRouter, Request, Response, HTTPException

from domains.knowledge_base.application.knowledge_base_controller import (
    invoke_function_by_key,
)
from utils import common_utils
from utils.logger import set_req_id, logger

router = APIRouter(
    prefix="/knowledgebase",
)


@router.get("/query")
async def get_knowledge_base_answer(request: Request):
    set_req_id(common_utils.get_unique_id())
    logger.info("getting answer")
    query_params = request.query_params

    body = {
        "workflow_id": query_params.get("workflow_id"),
        "question": query_params.get("question"),
    }

    res = invoke_function_by_key("query_knowledge_base", body)

    try:
        res = Response(
            content=res["body"], status_code=res["statusCode"], headers=res["headers"]
        )
    except Exception as e:
        logger.error(f"Error in route_to_query knowledge base : {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

    return res


@router.get("/category")
async def get_knowledge_base_answer(request: Request):
    set_req_id(common_utils.get_unique_id())
    logger.info("getting answer")
    query_params = request.query_params

    body = {
        "workflow_id": query_params.get("workflow_id"),
        "bug_message_text": query_params.get("bug_message_text"),
    }

    res = invoke_function_by_key("categorise_bug", body)

    try:
        res = Response(
            content=res["body"], status_code=res["statusCode"], headers=res["headers"]
        )
    except Exception as e:
        logger.error(f"Error in route_to_query knowledge base : {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

    return res


@router.post("/document/helpsite")
async def add_to_knowledge_base(request: Request):
    set_req_id(common_utils.get_unique_id())
    logger.info("adding to knowledge base document/helpsite")

    body = await request.json()

    res = invoke_function_by_key("add_data_to_knowledge_base", body)

    try:
        res = Response(
            content=res["body"], status_code=res["statusCode"], headers=res["headers"]
        )
    except Exception as e:
        logger.error(f"Error in route_to_add_data_to_knowledge_base : {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

    return res


@router.post("/document/solution")
async def add_to_knowledge_base(request: Request):
    set_req_id(common_utils.get_unique_id())
    logger.info("adding to knowledge base /document/solution")

    body = await request.json()

    res = invoke_function_by_key("add_data_to_knowledge_base", body)

    try:
        res = Response(
            content=res["body"], status_code=res["statusCode"], headers=res["headers"]
        )
    except Exception as e:
        logger.error(f"Error in route_to_add_data_to_knowledge_base : {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

    return res
