from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum

class InvoiceStatus(Enum):
    PENDING = "pending"
    INGESTED = "ingested"
    VALIDATED = "validated"
    COMPLIANT = "compliant"
    TAX_CALCULATED = "tax_calculated"
    AUDITED = "audited"
    REPORTED = "reported"
    REJECTED = "rejected"

@dataclass
class Invoice:
    invoice_id: str
    supplier_id: str
    customer_id: str
    issue_date: datetime
    currency: str
    total_amount: float
    tax_amount: float
    line_items: List[Dict] = field(default_factory=list)
    status: InvoiceStatus = InvoiceStatus.PENDING
    validation_errors: List[str] = field(default_factory=list)
    compliance_issues: List[str] = field(default_factory=list)
    tax_details: Dict = field(default_factory=dict)
    audit_trail: List[Dict] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)

@dataclass
class Message:
    sender: str
    receiver: str
    message_type: str
    payload: Dict
    timestamp: datetime = field(default_factory=datetime.now)
    message_id: str = field(default_factory=lambda: f"msg_{datetime.now().timestamp()}")
