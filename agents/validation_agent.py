from core.base_agent import BaseAgent
from core.models import Invoice, Message, InvoiceStatus

class ValidationAgent(BaseAgent):
    async def process_message(self, message: Message):
        if message.message_type == "invoice_ingested":
            invoice_id = message.payload["invoice_id"]
            invoice = self.state.get(f"invoice_{invoice_id}")
            if not invoice:
                invoice = await self._fetch_invoice(invoice_id)
            if invoice:
                errors = self._validate_invoice(invoice)
                invoice.validation_errors = errors
                invoice.status = InvoiceStatus.VALIDATED if not errors else InvoiceStatus.REJECTED
                self.state[f"invoice_{invoice_id}"] = invoice
                next_agent = "compliance_agent" if not errors else "orchestrator_agent"
                await self.send_message(
                    next_agent,
                    "invoice_validated" if not errors else "invoice_rejected",
                    {"invoice_id": invoice_id, "errors": errors, "status": invoice.status.value}
                )

    def _validate_invoice(self, invoice: Invoice) -> list:
        errors = []
        if not invoice.supplier_id:
            errors.append("Missing supplier ID")
        if not invoice.customer_id:
            errors.append("Missing customer ID")
        if invoice.total_amount <= 0:
            errors.append("Invalid total amount")
        if invoice.issue_date > invoice.issue_date.now():
            errors.append("Future invoice date")
        return errors

    async def _fetch_invoice(self, invoice_id: str) -> Invoice:
        return self.state.get(f"invoice_{invoice_id}")
