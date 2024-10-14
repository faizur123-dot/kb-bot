from domains.knowledge_base.core.ports.incoming.knowledge_base_query import KnowledgeBaseQuery as KBQueryInterface
from domains.knowledge_base.core.llms.open_ai_llm import OpenAILLM
from domains.knowledge_base.domain_infrastructure.db_client_impl import DBClient
from utils.response import MyResponse


class KnowledgeBaseQueryFacade(KBQueryInterface):

    def __init__(self, workflow_id: int):
        self.workflow_id = workflow_id
        self.llm = OpenAILLM()
        self.db_client = DBClient()
        self.db_client.update_kb_workflow_status_current_state(self.workflow_id)

    def get_answer(self, question: str):
        answer = self.llm.answer_question(question)
        if len(answer) == 0:
            body = {
                "status_code": 404
            }
            return MyResponse(404, body=body)
        else:
            self.db_client.add_kb_response(self.workflow_id, answer)
            body = {
                "status_code": 200,
                "answer": answer
            }
            return MyResponse(200, body=body)

    def categorise_bug(self, bug_text: str):
        answer = self.llm.categorise_bug(bug_text)
        if len(answer) == 0:
            body = {
                "status_code": 404,
                "data": []
            }
            return MyResponse(404, body=body)
        else:
            self.db_client.add_message_bug_category(self.workflow_id, answer)
            body = {
                "answer": answer
            }
            response = MyResponse(200, body=body)
            return response
