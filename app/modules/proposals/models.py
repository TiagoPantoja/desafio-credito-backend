import uuid
from datetime import datetime
from sqlalchemy import ForeignKey, String, Numeric, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base
from app.core.models import TenantMixin


class Proposal(Base, TenantMixin):
    __tablename__ = "proposals"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    client_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("clients.id"), nullable=False)

    type: Mapped[str] = mapped_column(String(50), nullable=False, default="personal")

    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    installments: Mapped[int] = mapped_column(nullable=False)

    status: Mapped[str] = mapped_column(String(20), default="pending")

    external_protocol: Mapped[str] = mapped_column(String(100), nullable=True)
    installment_value: Mapped[float] = mapped_column(Numeric(10, 2), nullable=True)
    bank_response: Mapped[dict] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))

