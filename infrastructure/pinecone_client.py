from pinecone import Pinecone
from utils.logger import logger
import os


class PineConeClient:

    def __init__(self, index: str):
        self.client = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
        self.index = self.client.Index(index)

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
