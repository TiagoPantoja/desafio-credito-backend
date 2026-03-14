from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.modules.clients.repository import ClientRepository
from app.modules.clients.dto import ClientCreate
from app.modules.clients.models import Client
from app.core.security import tenant_context
import uuid


class ClientService:
    def __init__(self, db: Session):
        self.repository = ClientRepository(db)

    def create_client(self, data: ClientCreate, user_id: uuid.UUID):
        # if not self._is_valid_cpf(data.cpf):
        #     raise HTTPException(status_code=400, detail="CPF inválido.")

        current_tenant_id = tenant_context.get()

        existing = self.repository.db.query(Client).filter(
            Client.cpf == data.cpf,
            Client.tenant_id == current_tenant_id
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe um cliente cadastrado com este CPF neste tenant."
            )

        return self.repository.create(data.model_dump(), user_id)

    def list_clients(self, skip: int = 0, limit: int = 10):
        return self.repository.get_all(skip=skip, limit=limit)

    def get_client(self, client_id: uuid.UUID):
        client = self.repository.get_by_id(client_id)
        if not client:
            raise HTTPException(status_code=404, detail="Cliente não encontrado.")
        return client

    def _is_valid_cpf(self, cpf: str) -> bool:
        if len(cpf) != 11 or len(set(cpf)) == 1:
            return False
        for i in range(9, 11):
            value = sum((int(cpf[num]) * ((i + 1) - num) for num in range(0, i)))
            digit = ((value * 10) % 11) % 10
            if digit != int(cpf[i]):
                return False
        return True