import asyncio
from datetime import datetime
from core.broker import MessageBroker
from agents.ingest_agent import InvoiceIngestAgent
from agents.validation_agent import ValidationAgent
from agents.compliance_agent import ComplianceCheckAgent
from agents.tax_agent import TaxCalculationAgent
from agents.audit_agent import AuditTrailAgent
from agents.reporting_agent import ReportingAgent
from agents.orchestrator_agent import OrchestratorAgent

async def main():
    print("=" * 60)
    print("MACOS - Multi-Agent Compliance Operating System")
    print("E-Invoicing 7-Agent MVP")
    print("=" * 60)
    
    broker = MessageBroker()
    
    agents = {
        "ingest_agent": InvoiceIngestAgent("ingest_agent", broker),
        "validation_agent": ValidationAgent("validation_agent", broker),
        "compliance_agent": ComplianceCheckAgent("compliance_agent", broker),
        "tax_agent": TaxCalculationAgent("tax_agent", broker),
        "audit_agent": AuditTrailAgent("audit_agent", broker),
        "reporting_agent": ReportingAgent("reporting_agent", broker),
        "orchestrator_agent": OrchestratorAgent("orchestrator_agent", broker)
    }
    
    for agent in agents.values():
        await agent.setup()
    
    print("\n[SYSTEM] All 7 agents initialized and ready\n")
    
    test_invoices = [
        {
            "invoice_id": "INV-001",
            "supplier_id": "SUP-123",
            "customer_id": "CUST-456",
            "issue_date": datetime.now().isoformat(),
            "currency": "USD",
            "total_amount": 1200.00,
            "tax_amount": 0,
            "line_items": [{"desc": "Consulting", "amount": 1200}]
        },
        {
            "invoice_id": "INV-002",
            "supplier_id": "SUP-789",
            "customer_id": "CUST-012",
            "issue_date": datetime.now().isoformat(),
            "currency": "EUR",
            "total_amount": 2421.00,
            "tax_amount": 0,
            "line_items": [{"desc": "Software License", "amount": 2421}]
        },
        {
            "invoice_id": "INV-003",
            "supplier_id": "",
            "customer_id": "CUST-999",
            "issue_date": datetime.now().isoformat(),
            "currency": "USD",
            "total_amount": 500.00,
            "tax_amount": 0,
            "line_items": []
        }
    ]
    
    for invoice_data in test_invoices:
        await agents["orchestrator_agent"].start_invoice_processing(invoice_data)
        await asyncio.sleep(0.5)
    
    await asyncio.sleep(2)
    
    print("\n" + "=" * 60)
    print("WORKFLOW STATUS")
    print("=" * 60)
    status = agents["orchestrator_agent"].get_status()
    print(f"Completed: {status['completed']}")
    print(f"Failed: {status['failed']}")
    
    print("\n" + "=" * 60)
    print("REPORTS GENERATED")
    print("=" * 60)
    for inv_id in status['completed']:
        report = agents["reporting_agent"].state.get(f"report_{inv_id}")
        if report:
            print(f"\nReport for {inv_id}:")
            for key, val in report.items():
                print(f"  {key}: {val}")

if __name__ == "__main__":
    asyncio.run(main())
