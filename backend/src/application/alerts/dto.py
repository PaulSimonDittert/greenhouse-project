from __future__ import annotations

import uuid
from pydantic import BaseModel


class AlertDto(BaseModel):
    id: uuid.UUID
    location_id: uuid.UUID | None = None
    zone_id: uuid.UUID | None = None
    device_id: uuid.UUID | None = None
    severity: str
    message: str
    event_type: str
    status: str
    created_at: str | None = None
