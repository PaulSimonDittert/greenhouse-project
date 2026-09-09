from sqlalchemy.orm import Session
from domain.sensors.entity import Sensor
from infrastructure.persistence.models import DeviceRow

class DeviceRepository:
    def __init__(self, db: Session):
        self.db = db

    def save_sensor(self, sensor: Sensor) -> Sensor:
        row = DeviceRow(
            device_type=sensor.device_type,
            role="sensor",
            display_name=sensor.display_name,
            default_config=sensor.default_config
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        
        # Populate the database-generated ID back into the domain entity
        sensor.id = row.id
        return sensor

    def list_sensors(self) -> list[Sensor]:
        rows = self.db.query(DeviceRow).filter(DeviceRow.role == "sensor").order_by(DeviceRow.created_at.desc()).all()
        return [
            Sensor(
                id=row.id,
                device_type=row.device_type,
                display_name=row.display_name,
                default_config=row.default_config
            )
            for row in rows
        ]