from core.base_agent import BaseAgent
from core.models import Invoice, Message, InvoiceStatus

class ComplianceCheckAgent(BaseAgent):
    def __init__(self, agent_id: str, broker):
        super().__init__(agent_id, broker)
        self.compliance_rules = {
            "max_amount": 1000000,
            "required_fields": ["supplier_id", "customer_id", "total_amount"],
            "allowed_currencies": ["USD", "EUR", "GBP", "CAD"]
        }

    async def process_message(self, message: Message):
        if message.message_type == "invoice_validated":
            invoice_id = message.payload["invoice_id"]
            invoice = self.state.get(f"invoice_{invoice_id}")
            if invoice:
                issues = self._check_compliance(invoice)
                invoice.compliance_issues = issues
                invoice.status = InvoiceStatus.COMPLIANT if not issues else InvoiceStatus.REJECTED
                self.state[f"invoice_{invoice_id}"] = invoice
                next_agent = "tax_agent" if not issues else "orchestrator_agent"
                await self.send_message(
                    next_agent,
                    "compliance_checked" if not issues else "compliance_failed",
                    {"invoice_id": invoice_id, "issues": issues, "status": invoice.status.value}
                )

    def _check_compliance(self, invoice: Invoice) -> list:
        issues = []
        if invoice.total_amount > self.compliance_rules["max_amount"]:
            issues.append(f"Amount exceeds max limit of {self.compliance_rules['max_amount']}")
        if invoice.currency not in self.compliance_rules["allowed_currencies"]:
            issues.append(f"Currency {invoice.currency} not allowed")
        return issues
