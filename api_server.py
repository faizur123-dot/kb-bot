import os

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import domains.knowledge_base.router as knowledge_base_router
import domains.ticket_assigner.router as ticket_assigner_router
import domains.communication_webhook.router as communication_router
import domains.kb_workflow.router as kb_workflow_router
from utils.logger import logger

app = FastAPI()

# components = {
# }
#
# for component_name in components.keys():
#     logger.info(f"Initializing the {component_name}")
#     try:
#         components[component_name]()
#     except Exception as e:
#         logger.error(
#             f"Error in initializing the {component_name} : " + str(e), exc_info=True
#         )
#         raise Exception(f"Error in initializing the {component_name} : " + str(e))
#     logger.info(f"Initialized the {component_name}")
#
# logger.info("Server initialized successfully")

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
app.include_router(kb_workflow_router.router)

if __name__ == "__main__":
    port = os.environ.get("PORT", 8080)
    logger.info("Starting the FastAPI server at port " + str(port))
    uvicorn.run(app, host="", port=port)
