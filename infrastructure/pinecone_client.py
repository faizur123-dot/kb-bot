from pinecone import Pinecone

import constants.constants
from utils.logger import logger
import os
from utils.exception import MyError


class PineConeClient:

    def __init__(self):
        self.pinecone_api_key = os.environ.get("PINECONE_API_KEY")
        if self.pinecone_api_key is None:
            raise MyError(error_code=500, error_message="PINECONE_API_KEY not set.")
        self.client = Pinecone(api_key=self.pinecone_api_key)
        self.index = self.client.Index(constants.constants.PINECONE_INDEX)

    def insert_documents(self, embedded_documents: []):
        try:
            response = self.index.upsert(embedded_documents)
            logger.info(f"Insert response: {response}")
            return response
        except Exception as err:
            logger.error(f"Error inserting docs to Pinecone: {err}")
            raise err

    def document_exists(self, checksum: str, filter_string: str, vector_value_of_doc: []) -> bool:
        """Check if a document with the given checksum exists in the index."""
        try:
            query_response = self.index.query(
                top_k=1,
                vector=vector_value_of_doc,
                include_metadata=True,
                filter={filter_string: {"$eq": checksum}}
            )
            exists = len(query_response['matches']) > 0
            return exists
        except Exception as err:
            logger.error(f"Error checking document existence in Pinecone: {err}")
            return False
