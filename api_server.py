import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import domains.knowledge_base.router as knowledge_base_router
import domains.ticket_assigner.router as ticket_assigner_router
import domains.communication_webhook.router as communication_router
import domains.query_flow_manager.router as query_workflow_router
from domains.query_flow_manager.core.query_flow_manager_facade import QueryFlowManager
from domains.knowledge_base.core.knowledge_base_facade import KnowledgeBase
from domains.knowledge_base.core.knowledge_base_query_facade import KnowledgeBaseQueryFacade
from domains.ticket_assigner.core.ticket_assigner_facade import TicketAssigner
from domains.communication_webhook.core.communication_webhook_facade import CommunicationWebhook
from infrastructure.postgres_connector import DatabaseConnection
from utils.logger import logger
from contextlib import asynccontextmanager

components = {
    "DatabaseConnection": DatabaseConnection,
    "QueryFlowManager": QueryFlowManager,
    "KnowledgeBase": KnowledgeBase,
    "KnowledgeBaseQuery": KnowledgeBaseQueryFacade,
    "TicketAssigner": TicketAssigner,
    "CommunicationWebhook": CommunicationWebhook,
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up and initializing components.")
    for component_name, component in components.items():
        logger.info(f"Initializing {component_name}")
        try:
            instance = component()
            components[component_name] = instance
        except Exception as e:
            logger.error(f"Error during initialization of {component_name}: {str(e)}", exc_info=True)
            raise e
    yield
    logger.info("Shutting down and cleaning up resources.")
    try:
        DatabaseConnection().close_connection()
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}", exc_info=True)
    logger.info("Resources cleaned up successfully.")


app = FastAPI(lifespan=lifespan)

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
    logger.info(f"Starting the FastAPI server at port {port}")
    uvicorn.run(app, host="0.0.0.0", port=int(port))
