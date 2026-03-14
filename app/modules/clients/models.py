import uuid
from datetime import datetime, date
from sqlalchemy import ForeignKey, String, Date
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base
from app.core.models import TenantMixin

class Client(Base, TenantMixin):
    __tablename__ = "clients"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(nullable=False)
    cpf: Mapped[str] = mapped_column(String(11), nullable=False) # Lembre-se: único por tenant na lógica
    birth_date: Mapped[date] = mapped_column(Date, nullable=False)
    phone: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))