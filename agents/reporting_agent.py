from datetime import datetime
from core.base_agent import BaseAgent
from core.models import Invoice, Message, InvoiceStatus
import json

class ReportingAgent(BaseAgent):
    def __init__(self, agent_id: str, broker):
        super().__init__(agent_id, broker)
        self.reports = {}

    async def process_message(self, message: Message):
        if message.message_type == "ready_for_reporting":
            invoice_id = message.payload["invoice_id"]
            invoice = self.state.get(f"invoice_{invoice_id}")
            if invoice:
                report = self._generate_report(invoice)
                self.reports[invoice_id] = report
                invoice.status = InvoiceStatus.REPORTED
                self.state[f"invoice_{invoice_id}"] = invoice
                self.state[f"report_{invoice_id}"] = report
                await self.send_message(
                    "orchestrator_agent",
                    "report_generated",
                    {"invoice_id": invoice_id, "report": report}
                )

    def _generate_report(self, invoice: Invoice) -> dict:
        return {
            "report_id": f"RPT-{invoice.invoice_id}",
            "generated_at": datetime.now().isoformat(),
            "invoice_id": invoice.invoice_id,
            "supplier": invoice.supplier_id,
            "customer": invoice.customer_id,
            "total_amount": invoice.total_amount,
            "tax_amount": invoice.tax_amount,
            "currency": invoice.currency,
            "status": invoice.status.value,
            "audit_entries": len(invoice.audit_trail),
            "compliance_status": "PASS" if not invoice.compliance_issues else "FAIL"
        }
