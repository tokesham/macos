from core.base_agent import BaseAgent
from core.models import Invoice, Message, InvoiceStatus

class TaxCalculationAgent(BaseAgent):
    def __init__(self, agent_id: str, broker):
        super().__init__(agent_id, broker)
        self.tax_rates = {"USD": 0.20, "EUR": 0.21, "GBP": 0.20, "CAD": 0.15}

    async def process_message(self, message: Message):
        if message.message_type == "compliance_checked":
            invoice_id = message.payload["invoice_id"]
            invoice = self.state.get(f"invoice_{invoice_id}")
            if invoice:
                tax_details = self._calculate_tax(invoice)
                invoice.tax_details = tax_details
                invoice.tax_amount = tax_details["tax_amount"]
                invoice.status = InvoiceStatus.TAX_CALCULATED
                self.state[f"invoice_{invoice_id}"] = invoice
                await self.send_message(
                    "audit_agent",
                    "tax_calculated",
                    {"invoice_id": invoice_id, "tax_details": tax_details}
                )

    def _calculate_tax(self, invoice: Invoice) -> dict:
        rate = self.tax_rates.get(invoice.currency, 0.20)
        taxable_amount = invoice.total_amount / (1 + rate)
        tax_amount = invoice.total_amount - taxable_amount
        return {
            "tax_rate": rate,
            "taxable_amount": round(taxable_amount, 2),
            "tax_amount": round(tax_amount, 2),
            "currency": invoice.currency
        }
