from langchain.text_splitter import RecursiveCharacterTextSplitter
from domains.knowledge_base.core.text_splitters.text_splitter_interface import TextSplitterInterface


class RecursiveTextSplitter(TextSplitterInterface):
    def __init__(self, chunk_size, chunk_overlap) -> None:
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.recursive_text_splitter = RecursiveCharacterTextSplitter(chunk_size=self.chunk_size,
                                                                      chunk_overlap=self.chunk_overlap,
                                                                      length_function=len)

    def split_text_documents(self, list_of_documents):
        text_splitters = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
        )
        text_file_for_upload_in_doc_form_splitted = text_splitters.split_documents(
            list_of_documents
        )
        return text_file_for_upload_in_doc_form_splitted
