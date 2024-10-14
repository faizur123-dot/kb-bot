from typing import List

from langchain.schema import Document
from langchain.document_loaders import TextLoader

from domains.knowledge_base.core.document_loaders.document_loader import DocumentLoader as DocumentLoaderInterface


class TextDocumentLoader(DocumentLoaderInterface):

    def load_data_into_documents(self, document_path: str) -> List[Document]:
        loader = TextLoader(document_path)
        documents: List[Document] = loader.load()
        return documents
