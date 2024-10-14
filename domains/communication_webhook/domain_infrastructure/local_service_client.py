from infrastructure.local_service_invoker import LocalServiceInvoker
from infrastructure.kb_api_client import KBApi
from domains.communication_webhook.core.ports.outgoing.local_service_client_interface import \
    ServiceInvokeClientInterface


class ServiceInvokeClient(ServiceInvokeClientInterface):

    def __init__(self):
        self.service_invoker = LocalServiceInvoker()
        self.kb_client = KBApi()

    def invoke_kb_workflow(
            self, workflow_id: int, text: str
    ):
        return self.kb_client.process_slack_message_received(workflow_id=workflow_id, text=text)
