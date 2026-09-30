import uuid
from decimal import Decimal

from sqlalchemy.orm import Session

from domain.sensors.reading import Reading
from infrastructure.persistence.models import ReadingRow


def _reading_from_row(row: ReadingRow) -> Reading:
    return Reading(
        device_id=row.device_id,
        value=float(row.value),
        unit=row.unit,
        source=row.source,
        recorded_at=row.recorded_at,
    )


class ReadingRepository:
    def __init__(self, db: Session):
        self.db = db

    def insert(self, reading: Reading) -> Reading:
        row = ReadingRow(
            device_id=reading.device_id,
            value=Decimal(str(reading.value)),
            unit=reading.unit,
            source=reading.source,
            recorded_at=reading.recorded_at,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return _reading_from_row(row)

    def list_for_device(self, device_id: uuid.UUID, limit: int = 20) -> list[Reading]:
        rows = (
            self.db.query(ReadingRow)
            .filter(ReadingRow.device_id == device_id)
            .order_by(ReadingRow.recorded_at.desc())
            .limit(limit)
            .all()
        )
        return [_reading_from_row(row) for row in rows]

    def latest_for_device(self, device_id: uuid.UUID) -> Reading | None:
        row = (
            self.db.query(ReadingRow)
            .filter(ReadingRow.device_id == device_id)
            .order_by(ReadingRow.recorded_at.desc())
            .first()
        )
        return _reading_from_row(row) if row else None