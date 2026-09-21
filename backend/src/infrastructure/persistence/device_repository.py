from sqlalchemy.orm import Session
from domain.sensors.entity import Sensor
from domain.devices.entity import Device
from infrastructure.persistence.models import DeviceRow

class DeviceRepository:
    def __init__(self, db: Session):
        self.db = db

    def save_sensor(self, sensor: Sensor) -> Sensor:
        row = DeviceRow(
            device_type=sensor.device_type,
            role="sensor",
            device_family="simulation",
            display_name=sensor.display_name,
            default_config=sensor.default_config
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
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

    def save_devices(self, devices: list[Device]) -> list[Device]:
        rows = []
        for d in devices:
            row = DeviceRow(
                device_type=d.device_type,
                role=d.role,
                device_family=d.device_family,
                display_name=d.display_name,
                default_config=d.default_config
            )
            rows.append(row)
            self.db.add(row)
        
        self.db.commit()
        
        result = []
        for row, d in zip(rows, devices):
            self.db.refresh(row)
            result.append(Device(
                id=row.id, device_type=d.device_type, role=d.role, 
                device_family=d.device_family, display_name=d.display_name, 
                default_config=d.default_config
            ))
        return result

    def list_devices(self, *, device_family: str | None = None, role: str | None = None) -> list[Device]:
        query = self.db.query(DeviceRow)
        if device_family:
            query = query.filter(DeviceRow.device_family == device_family)
        if role:
            query = query.filter(DeviceRow.role == role)
            
        rows = query.order_by(DeviceRow.created_at.desc()).all()
        return [
            Device(id=row.id, device_type=row.device_type, role=row.role, device_family=row.device_family, display_name=row.display_name, default_config=row.default_config)
            for row in rows
        ]