import os

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import domains.knowledge_base.router as knowledge_base_router
import domains.ticket_assigner.router as ticket_assigner_router
import domains.communication_webhook.router as communication_router
import domains.query_flow_manager.router as query_workflow_router
from utils.logger import logger

app = FastAPI()

ALLOWED_ORIGINS = [
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(knowledge_base_router.router)
app.include_router(ticket_assigner_router.router)
app.include_router(communication_router.router)
app.include_router(query_workflow_router.router)

if __name__ == "__main__":
    port = os.environ.get("PORT", 8080)
    logger.info("Starting the FastAPI server at port " + str(port))
    uvicorn.run(app, host="", port=port)
