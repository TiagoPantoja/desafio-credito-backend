from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.common.deps import get_current_user_context
from app.modules.proposals.dto import ProposalCreate, ProposalResponse
from app.modules.proposals.service import ProposalService
import uuid

router = APIRouter(prefix="/proposals", tags=["Proposals"])

def get_proposal_service(db: Session = Depends(get_db)):
    return ProposalService(db)

@router.post("/", response_model=ProposalResponse, status_code=status.HTTP_201_CREATED)
def create_proposal(
    data: ProposalCreate,
    service: ProposalService = Depends(get_proposal_service),
    user_data: dict = Depends(get_current_user_context)
):
    return service.create_proposal(data, user_id=uuid.UUID(user_data["user_id"]))

@router.post("/{proposal_id}/include")
def include_proposal(
    proposal_id: uuid.UUID,
    service: ProposalService = Depends(get_proposal_service),
    user_data: dict = Depends(get_current_user_context)
):
    return service.include_proposal(proposal_id)

@router.get("/{proposal_id}", response_model=ProposalResponse)
def get_proposal(
    proposal_id: uuid.UUID,
    service: ProposalService = Depends(get_proposal_service)
):
    proposal = service.repository.get_by_id(proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposta não encontrada")
    return proposal