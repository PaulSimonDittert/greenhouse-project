from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from infrastructure.persistence.models import AlertRow


class AlertRepository:
    def __init__(self, db: Session):
        self.db = db

    def insert(
        self,
        *,
        location_id: uuid.UUID | None,
        zone_id: uuid.UUID | None,
        device_id: uuid.UUID | None,
        severity: str,
        message: str,
        event_type: str,
        status: str = "active",
        acknowledged_at: datetime | None = None,
    ) -> AlertRow:
        row = AlertRow(
            location_id=location_id,
            zone_id=zone_id,
            device_id=device_id,
            severity=severity,
            message=message,
            event_type=event_type,
            status=status,
            acknowledged_at=acknowledged_at,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row

    def list(
        self,
        *,
        status: str | None = None,
        location_id: uuid.UUID | None = None,
        zone_id: uuid.UUID | None = None,
        since: datetime | None = None,
    ) -> list[AlertRow]:
        query = self.db.query(AlertRow)
        if status is not None:
            query = query.filter(AlertRow.status == status)
        if location_id is not None:
            query = query.filter(AlertRow.location_id == location_id)
        if zone_id is not None:
            query = query.filter(AlertRow.zone_id == zone_id)
        if since is not None:
            query = query.filter(AlertRow.created_at >= since)
        return query.order_by(AlertRow.created_at.desc()).all()
