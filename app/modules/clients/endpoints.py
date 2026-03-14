from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.common.deps import get_current_user_context
from app.modules.clients.dto import ClientCreate, ClientResponse, ClientUpdate
from app.modules.clients.service import ClientService
import uuid

router = APIRouter(prefix="/clients", tags=["Clients"])

@router.post("/", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
def create_client(
    data: ClientCreate,
    db: Session = Depends(get_db),
    user_data: dict = Depends(get_current_user_context)
):
    service = ClientService(db)
    return service.create_client(data, user_id=uuid.UUID(user_data["user_id"]))

@router.get("/", response_model=List[ClientResponse])
def list_clients(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    user_data: dict = Depends(get_current_user_context)
):
    service = ClientService(db)
    return service.list_clients(skip=skip, limit=limit)

@router.get("/{client_id}", response_model=ClientResponse)
def get_client(
    client_id: uuid.UUID,
    db: Session = Depends(get_db),
    user_data: dict = Depends(get_current_user_context)
):
    service = ClientService(db)
    return service.get_client(client_id)