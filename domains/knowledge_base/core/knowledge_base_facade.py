import constants.constants
from constants.constants import CHUNK_SIZE, CHUNK_OVERLAP, EMBEDDED_TEXT, SRC, SRC_TEXT
from domains.knowledge_base.core.ports.incoming.knowledge_base import KnowledgeBase as KBInterace
from domains.knowledge_base.domain_infrastructure.file_handler import fetch_file
from domains.knowledge_base.core.document_loaders.text_document_loader import TextDocumentLoader
from domains.knowledge_base.core.llms.open_ai_llm import OpenAILLM
from domains.knowledge_base.core.text_splitters.recursive_text_splitter import RecursiveTextSplitter
from domains.knowledge_base.domain_infrastructure.vector_store_client_impl import VectorStoreClientImpl
from domains.knowledge_base.core import helpers
from domains.knowledge_base.domain_infrastructure.db_client_impl import DBClient
from domains.knowledge_base.domain_infrastructure.file_handler import convert_src_text_to_txt_file


class KnowledgeBaseFacade(KBInterace):

    def __init__(self, workflow_id: int = None):
        self.workflow_id = workflow_id
        self.document_loader = TextDocumentLoader()
        self.text_splitter = RecursiveTextSplitter(CHUNK_SIZE, CHUNK_OVERLAP)
        self.vector_store = VectorStoreClientImpl()
        self.llm = OpenAILLM()
        self.db_client = DBClient()
        if workflow_id is not None:
            self.db_client.update_kb_workflow_status_current_state(self.workflow_id)

    def add_data_to_knowledge_base(self, source: str, src_filepath: str = None, bug_resolution_data=None):
        if bug_resolution_data is not None:
            text_file = convert_src_text_to_txt_file(bug_resolution_data)
        else:
            text_file = self._fetch_text_file(src_filepath)
        loaded_documents = self.document_loader.load_data_into_documents(text_file)
        split_text_documents = self.text_splitter.split_text_documents(loaded_documents)
        list_of_documents: [] = self._create_documents(split_text_documents, source)
        self.vector_store.add_docs_to_vector_db(list_of_documents)
        return

    @staticmethod
    def _fetch_text_file(src_filepath: str):
        text_local_filepath = fetch_file(src_filepath)
        return text_local_filepath

    @staticmethod
    def _create_documents(
            split_doc: [],
            source: str,
            src_creation_time: str = None,
    ):
        list_of_dicts = []
        embedder = helpers.get_embeddings()
        for current_doc, text in enumerate(split_doc):
            current_text = text.page_content
            source = source
            src_creation_time = src_creation_time
            embedded_text = embedder.embed_query(current_text)
            text = current_text
            doc = {
                f"{EMBEDDED_TEXT}": embedded_text,
                f"{SRC}": source,
                f"{SRC_TEXT}": text
            }
            list_of_dicts.append(doc)
        return list_of_dicts
