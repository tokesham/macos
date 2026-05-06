import json
from datetime import datetime
from core.base_agent import BaseAgent
from core.models import Invoice, Message, InvoiceStatus

class InvoiceIngestAgent(BaseAgent):
    async def process_message(self, message: Message):
        if message.message_type == "ingest_invoice":
            invoice_data = message.payload
            invoice = self._parse_invoice(invoice_data)
            self.state[f"invoice_{invoice.invoice_id}"] = invoice
            await self.send_message(
                "validation_agent",
                "invoice_ingested",
                {"invoice_id": invoice.invoice_id, "status": InvoiceStatus.INGESTED.value}
            )
            await self.send_message(
                "orchestrator_agent",
                "task_completed",
                {"agent": self.agent_id, "invoice_id": invoice.invoice_id, "action": "ingested"}
            )

    def _parse_invoice(self, data: dict) -> Invoice:
        return Invoice(
            invoice_id=data.get("invoice_id", f"INV-{datetime.now().timestamp()}"),
            supplier_id=data.get("supplier_id", ""),
            customer_id=data.get("customer_id", ""),
            issue_date=datetime.fromisoformat(data.get("issue_date", datetime.now().isoformat())),
            currency=data.get("currency", "USD"),
            total_amount=float(data.get("total_amount", 0)),
            tax_amount=float(data.get("tax_amount", 0)),
            line_items=data.get("line_items", []),
            status=InvoiceStatus.INGESTED,
            metadata=data.get("metadata", {})
        )
