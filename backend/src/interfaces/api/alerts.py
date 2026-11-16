import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from application.alerts.dto import AlertDto
from infrastructure.db import get_db
from infrastructure.persistence.alert_repository import AlertRepository

router = APIRouter(prefix="/api", tags=["alerts"])


@router.get("/alerts", response_model=list[AlertDto])
def list_alerts(
    status: str | None = Query(default=None),
    location_id: uuid.UUID | None = Query(default=None),
    zone_id: uuid.UUID | None = Query(default=None),
    since: datetime | None = Query(default=None),
    db: Session = Depends(get_db),
):
    rows = AlertRepository(db).list(
        status=status,
        location_id=location_id,
        zone_id=zone_id,
        since=since,
    )
    return [
        AlertDto(
            id=row.id,
            location_id=row.location_id,
            zone_id=row.zone_id,
            device_id=row.device_id,
            severity=row.severity,
            message=row.message,
            event_type=row.event_type,
            status=row.status,
            created_at=row.created_at,
            acknowledged_at=row.acknowledged_at,
        )
        for row in rows
    ]
