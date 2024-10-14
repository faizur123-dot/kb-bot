import constants.constants
from langchain_pinecone import PineconeVectorStore
from domains.knowledge_base.core.helpers import get_embeddings


class Retriever:

    def __init__(self):
        self.retriever = PineconeVectorStore(index_name=constants.constants.PINECONE_INDEX,
                                             embedding=get_embeddings(),
                                             text_key="source_text")
