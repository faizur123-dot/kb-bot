from typing import List


class LLMInterface():
    def embed_query(self, query) -> List[float]:
        pass

    def answer_question(self, question: str) -> str:
        pass

    def categorise_bug(self, text: str):
        pass
