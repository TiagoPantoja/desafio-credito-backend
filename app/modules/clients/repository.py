from sqlalchemy.orm import Session
from app.modules.clients.models import Client
from app.core.security import tenant_context
import uuid


class ClientRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, skip: int = 0, limit: int = 10):
        current_tenant_id = tenant_context.get()
        return self.db.query(Client).filter(
            Client.tenant_id == current_tenant_id
        ).offset(skip).limit(limit).all()

    def create(self, client_data: dict, user_id: uuid.UUID):
        current_tenant_id = tenant_context.get()

        db_client = Client(
            **client_data,
            tenant_id=current_tenant_id,
            created_by=user_id
        )

        self.db.add(db_client)
        self.db.commit()
        self.db.refresh(db_client)
        return db_client

    def get_by_id(self, client_id: uuid.UUID):
        current_tenant_id = tenant_context.get()
        return self.db.query(Client).filter(
            Client.id == client_id,
            Client.tenant_id == current_tenant_id
        ).first()