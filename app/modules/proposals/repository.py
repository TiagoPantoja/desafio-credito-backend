from sqlalchemy.orm import Session
from app.modules.proposals.models import Proposal
from app.core.security import tenant_context
from datetime import datetime, timezone
import uuid


class ProposalRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, proposal_id: uuid.UUID):
        return self.db.query(Proposal).filter(Proposal.id == proposal_id).first()

    def create(self, proposal_data: dict, user_id: uuid.UUID):
        current_tenant_id = tenant_context.get()
        now = datetime.now(timezone.utc)

        db_proposal = Proposal(
            **proposal_data,
            tenant_id=current_tenant_id,
            created_by=user_id,
            status="pending",
            type="personal",
            updated_at=now
        )

        self.db.add(db_proposal)
        self.db.commit()
        self.db.refresh(db_proposal)
        return db_proposal

    def update_status(self, proposal_id: uuid.UUID, status: str, protocol: str = None):
        proposal = self.get_by_id(proposal_id)
        if proposal:
            proposal.status = status
            proposal.updated_at = datetime.now(timezone.utc)

            if protocol:
                proposal.external_protocol = protocol

            self.db.commit()
            self.db.refresh(proposal)
            return proposal
        return None