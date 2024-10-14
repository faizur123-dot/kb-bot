import os
from langchain.llms import OpenAI

import constants.constants
from domains.knowledge_base.core.llms import llm_interface as llm
from typing import List
from domains.knowledge_base.core.retriver import Retriever
from domains.knowledge_base.core.helpers import get_embeddings
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate


class OpenAILLM(llm.LLMInterface):
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.llm = OpenAI(openai_api_key=self.openai_api_key, temperature=0.1)
        self.retrieve = Retriever().retriever

    def embed_query(self, query) -> List[float]:
        return get_embeddings().embed_query(query)

    def categorise_bug(self, text: str):
        prompt = PromptTemplate(
            input_variables=["categories", "text"],
            template=constants.constants.CATEGORISE_BUG_TEMPLATE,
        )
        formatted_prompt = prompt.format(categories=", ".join(constants.constants.CATEGORIES), text=text)

        response = self.llm(formatted_prompt)
        return response

    def answer_question(self, question: str) -> str:
        qa = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.retrieve.as_retriever()
        )
        response_metadata = qa.invoke(question)
        answer = response_metadata.get("result")
        unsure_responses = constants.constants.UNSURE_RESPONSES_LIST
        if any(phrase in answer for phrase in unsure_responses):
            return ""
        return answer
