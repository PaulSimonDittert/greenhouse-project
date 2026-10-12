import uuid

from sqlalchemy.orm import Session

from infrastructure.persistence.models import AutomationRuleRow, DeviceRow, LocationRow, ReadingRow, ZoneRow


class AutomationRuleRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_for_location(self, location_id: uuid.UUID) -> AutomationRuleRow | None:
        return (
            self.db.query(AutomationRuleRow)
            .filter(AutomationRuleRow.location_id == location_id)
            .first()
        )

    def upsert_for_location(self, location_id: uuid.UUID, strategy_key: str, parameters: dict | None = None) -> AutomationRuleRow:
        row = self.get_for_location(location_id)
        if row is None:
            row = AutomationRuleRow(
                location_id=location_id,
                strategy_key=strategy_key,
                parameters=parameters,
            )
            self.db.add(row)
        else:
            row.strategy_key = strategy_key
            row.parameters = parameters
        self.db.commit()
        self.db.refresh(row)
        return row

    def get_zone_moisture(self, zone_id: uuid.UUID) -> float | None:
        row = (
            self.db.query(ReadingRow)
            .join(DeviceRow, DeviceRow.id == ReadingRow.device_id)
            .filter(DeviceRow.zone_id == zone_id, DeviceRow.device_type == "moisture_sensor")
            .order_by(ReadingRow.recorded_at.desc())
            .first()
        )
        if row is None:
            return None
        return float(row.value)

    def get_location_config(self, location_id: uuid.UUID) -> tuple[LocationRow, list[ZoneRow]] | None:
        location = self.db.query(LocationRow).filter(LocationRow.id == location_id).first()
        if location is None:
            return None
        zones = self.db.query(ZoneRow).filter(ZoneRow.location_id == location_id).all()
        return location, zones
