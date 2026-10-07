import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy import (
    Boolean,
    Float,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    desc,
    text,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

class LocationRow(Base):
    __tablename__ = "locations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        server_default=text("gen_random_uuid()")
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    created_at = mapped_column(
        TIMESTAMP(timezone=True), 
        server_default=text("now()"), 
        nullable=False
    )
    
    zones = relationship("ZoneRow", back_populates="location", cascade="all, delete-orphan")

class ZoneRow(Base):
    __tablename__ = "zones"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        server_default=text("gen_random_uuid()")
    )
    location_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("locations.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    moisture_threshold_low: Mapped[float] = mapped_column(Float, nullable=False)
    moisture_threshold_high: Mapped[float] = mapped_column(Float, nullable=False)
    schedule: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    location = relationship("LocationRow", back_populates="zones")

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
    sampling_interval_seconds: Mapped[int] = mapped_column(Integer, nullable=False, server_default="300")
    tracking_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
    created_at = mapped_column(
        TIMESTAMP(timezone=True), 
        server_default=text("now()"), 
        nullable=False
    )

    zone_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("zones.id", ondelete="SET NULL"), 
        nullable=True, 
        index=True
    )
    location_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("locations.id", ondelete="SET NULL"), 
        nullable=True
    )

    __table_args__ = (
        Index("ix_devices_role", "role"),
        Index("ix_devices_family", "device_family"),
    )


class ReadingRow(Base):
    __tablename__ = "sensor_readings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    device_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("devices.id", ondelete="CASCADE"),
        nullable=False,
    )
    value: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    unit: Mapped[str] = mapped_column(String(32), nullable=False)
    source: Mapped[str] = mapped_column(String(32), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    __table_args__ = (
        Index("ix_sensor_readings_device_recorded_at", "device_id", desc("recorded_at")),
    )


class AutomationRuleRow(Base):
    """Persist one active automation strategy separately for each location."""

    __tablename__ = "automation_rules"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    location_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("locations.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    strategy_key: Mapped[str] = mapped_column(String(64), nullable=False)
    parameters: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
        onupdate=text("now()"),
    )
