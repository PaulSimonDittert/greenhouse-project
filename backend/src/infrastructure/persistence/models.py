import uuid
from sqlalchemy import String, text, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base

class DeviceRow(Base):
    __tablename__ = "devices"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        server_default=text("gen_random_uuid()")
    )
    device_type: Mapped[str] = mapped_column(String(64), nullable=False)
    role: Mapped[str] = mapped_column(String(32), default="sensor", server_default="sensor")
    device_family: Mapped[str] = mapped_column(String(32), nullable=False, server_default="simulation")
    display_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    default_config: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    created_at = mapped_column(
        TIMESTAMP(timezone=True), 
        server_default=text("now()"), 
        nullable=False
    )

    __table_args__ = (
        Index("ix_devices_role", "role"),
        Index("ix_devices_family", "device_family"),
    )