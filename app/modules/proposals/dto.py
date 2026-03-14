from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional

class ProposalCreate(BaseModel):
    client_id: UUID
    amount: float = Field(..., gt=0)
    installments: int = Field(..., gt=0)

class ProposalResponse(BaseModel):
    id: UUID
    client_id: UUID
    amount: float
    installments: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class BankWebhookPayload(BaseModel):
    status: str
    protocol: Optional[str] = None
    installment_value: Optional[float] = None
    reason: Optional[str] = None