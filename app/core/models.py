import uuid
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

class TenantMixin:
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )