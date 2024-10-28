from typing import List
from utils.common_utils import get_unique_id
import constants.constants
from constants.constants import EMBEDDED_TEXT, SRC, SRC_TEXT, SRC_TEXT_CHECKSUM
from infrastructure.pinecone_client import PineConeClient
from utils.logger import logger
from utils.common_utils import compute_checksum

from domains.knowledge_base.core.ports.outgoing.vector_store_client_interface import \
    VectorStoreClient as VectorStoreClientInterface
from langchain.embeddings.openai import OpenAIEmbeddings


class VectorStoreClientImpl(VectorStoreClientInterface):

    def __init__(self):
        self.vector_store = PineConeClient()
        self.embeddings = OpenAIEmbeddings()
        self.index = self.vector_store.index

    def add_docs_to_vector_db(self, list_of_documents: List):
        try:
            all_docs = []
            for doc in list_of_documents:
                source_id = get_unique_id()
                checksum = compute_checksum(doc[SRC_TEXT])

                if self.vector_store.document_exists(checksum, SRC_TEXT_CHECKSUM, doc[EMBEDDED_TEXT]):
                    logger.info(f"Document with checksum {checksum} already exists, skipping insertion.")
                    continue

                current_doc = {
                    "id": source_id,
                    "values": doc[EMBEDDED_TEXT],
                    "metadata": {
                        SRC_TEXT: doc[SRC_TEXT],
                        SRC: doc[SRC],
                        SRC_TEXT_CHECKSUM: checksum
                    }
                }
                all_docs.append(current_doc)

            if all_docs:
                self.vector_store.insert_documents(all_docs)
                logger.info("Documents successfully inserted")
            else:
                logger.info("No new documents to insert.")
        except Exception as err:
            logger.error("Error adding documents to vector DB")
            raise err
