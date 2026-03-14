from sqlalchemy.orm import Session
from app.modules.proposals.repository import ProposalRepository
from app.modules.proposals.dto import ProposalCreate
from app.modules.clients.models import Client
from app.core.sqs import send_to_queue
from app.core.external_bank import ExternalBankClient
from fastapi import HTTPException, status
import uuid


class ProposalService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = ProposalRepository(db)

    def create_proposal(self, data: ProposalCreate, user_id: uuid.UUID):
        proposal = self.repository.create(data.model_dump(), user_id)

        message = {
            "proposal_id": str(proposal.id),
            "tenant_id": str(proposal.tenant_id)
        }

        try:
            send_to_queue(message)
        except Exception as e:
            print(f"Erro ao enviar para fila: {e}")

        return proposal

    def update_from_webhook(self, proposal_id: uuid.UUID, data: dict):
        proposal = self.repository.get_by_id(proposal_id)

        if not proposal:
            raise HTTPException(status_code=404, detail="Proposta não encontrada")

        terminal_statuses = ["approved", "included", "rejected"]
        if proposal.status in terminal_statuses:
            print(f"Webhook ignorado: Proposta {proposal_id} já está como {proposal.status}")
            return {"message": "Proposta já processada anteriormente", "status": proposal.status}

        new_status = data.get("status")
        external_protocol = data.get("protocol")

        self.repository.update_status(
            proposal_id=proposal_id,
            status=new_status,
            protocol=external_protocol
        )

        print(f"Proposta {proposal_id} atualizada via Webhook para: {new_status}")
        return {"message": "Status atualizado com sucesso", "status": new_status}

    def include_proposal(self, proposal_id: uuid.UUID):
        proposal = self.repository.get_by_id(proposal_id)
        if not proposal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Proposta não encontrada."
            )

        if proposal.status != "approved":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Apenas propostas aprovadas podem ser incluídas. Status atual: {proposal.status}"
            )

        client = self.db.query(Client).filter(Client.id == proposal.client_id).first()
        if not client:
            raise HTTPException(status_code=404, detail="Cliente associado não encontrado.")

        bank_client = ExternalBankClient()
        payload = {
            "protocol": proposal.external_protocol,
            "client_name": client.name,
            "client_cpf": client.cpf,
            "client_birth_date": client.birth_date.isoformat() if client.birth_date else None,
            "amount": float(proposal.amount),
            "installments": proposal.installments,
            "webhook_url": f"http://api:8000/api/webhooks/bank-callback?proposal_id={proposal.id}"
        }

        print(f"Solicitando inclusão final para protocolo: {proposal.external_protocol}")
        result = bank_client.incluir(payload)

        if "protocol" in result or result.get("status") in ["included", "success"]:
            proposal.status = "included"
            proposal.bank_response = result
            self.db.commit()
            return {"message": "Proposta incluída com sucesso", "status": proposal.status}

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O banco externo recusou a inclusão da proposta."
        )