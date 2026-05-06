from core.base_agent import BaseAgent
from core.models import Message
from datetime import datetime

class OrchestratorAgent(BaseAgent):
    def __init__(self, agent_id: str, broker):
        super().__init__(agent_id, broker)
        self.workflow_status = {}
        self.completed_invoices = []
        self.failed_invoices = []

    async def process_message(self, message: Message):
        if message.message_type == "task_completed":
            invoice_id = message.payload["invoice_id"]
            agent = message.payload["agent"]
            if invoice_id not in self.workflow_status:
                self.workflow_status[invoice_id] = {}
            self.workflow_status[invoice_id][agent] = "completed"
            
        elif message.message_type == "report_generated":
            invoice_id = message.payload["invoice_id"]
            self.completed_invoices.append(invoice_id)
            print(f"[ORCHESTRATOR] Invoice {invoice_id} processing complete!")
            
        elif message.message_type == "invoice_rejected" or message.message_type == "compliance_failed":
            invoice_id = message.payload["invoice_id"]
            self.failed_invoices.append(invoice_id)
            print(f"[ORCHESTRATOR] Invoice {invoice_id} rejected/failed compliance")

    async def start_invoice_processing(self, invoice_data: dict):
        await self.send_message(
            "ingest_agent",
            "ingest_invoice",
            invoice_data
        )
        print(f"[ORCHESTRATOR] Started processing invoice {invoice_data.get('invoice_id')}")

    def get_status(self) -> dict:
        return {
            "completed": self.completed_invoices,
            "failed": self.failed_invoices,
            "in_progress": self.workflow_status
        }
