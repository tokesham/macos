from datetime import datetime
from core.base_agent import BaseAgent
from core.models import Invoice, Message, InvoiceStatus

class AuditTrailAgent(BaseAgent):
    async def process_message(self, message: Message):
        if message.message_type == "tax_calculated":
            invoice_id = message.payload["invoice_id"]
            invoice = self.state.get(f"invoice_{invoice_id}")
            if invoice:
                audit_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "action": "tax_calculated",
                    "invoice_id": invoice_id,
                    "tax_details": message.payload.get("tax_details"),
                    "actor": self.agent_id
                }
                invoice.audit_trail.append(audit_entry)
                invoice.status = InvoiceStatus.AUDITED
                self.state[f"invoice_{invoice_id}"] = invoice
                await self.send_message(
                    "reporting_agent",
                    "ready_for_reporting",
                    {"invoice_id": invoice_id, "audit_trail": invoice.audit_trail}
                )

    async def receive_message(self, message: Message):
        await super().receive_message(message)
        if message.message_type == "invoice_rejected" or message.message_type == "compliance_failed":
            invoice_id = message.payload["invoice_id"]
            audit_entry = {
                "timestamp": datetime.now().isoformat(),
                "action": "rejected",
                "invoice_id": invoice_id,
                "reason": message.payload.get("errors") or message.payload.get("issues"),
                "actor": self.agent_id
            }
            self.state[f"audit_{invoice_id}"] = audit_entry
