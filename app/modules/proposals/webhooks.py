from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.modules.proposals.models import Proposal
from app.modules.proposals.dto import BankWebhookPayload
import uuid

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.post("/bank-callback")
def bank_callback(
        proposal_id: uuid.UUID = Query(...),
        payload: BankWebhookPayload = None,
        db: Session = Depends(get_db)
):
    print(f"Webhook recebido para a proposta: {proposal_id}")

    proposal = db.query(Proposal).filter(Proposal.id == proposal_id).first()

    if not proposal:
        raise HTTPException(status_code=404, detail="Proposta não encontrada")

    proposal.status = payload.status
    proposal.external_protocol = payload.protocol
    proposal.installment_value = payload.installment_value
    proposal.bank_response = payload.model_dump()

    db.commit()
    print(f"Proposta {proposal_id} atualizada para: {payload.status}")

    return {"message": "Webhook processado com sucesso"}