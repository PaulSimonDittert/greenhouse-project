import uuid

from sqlalchemy.orm import Session
from domain.sensors.entity import Sensor
from domain.devices.entity import Device
from infrastructure.persistence.models import DeviceRow


def _device_from_row(row: DeviceRow) -> Device:
    return Device(
        id=row.id,
        device_type=row.device_type,
        role=row.role,
        device_family=row.device_family,
        display_name=row.display_name or row.device_type,
        default_config=row.default_config,
        zone_id=row.zone_id,
        location_id=row.location_id,
        sampling_interval_seconds=row.sampling_interval_seconds,
        tracking_enabled=row.tracking_enabled,
    )


def _sampling_interval(default_config: dict) -> int:
    value = default_config.get("sampling_interval_seconds")
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    return 300


class DeviceRepository:
    def __init__(self, db: Session):
        self.db = db

    def save_sensor(self, sensor: Sensor) -> Sensor:
        row = DeviceRow(
            device_type=sensor.device_type,
            role="sensor",
            device_family="simulation",
            display_name=sensor.display_name,
            default_config=sensor.default_config,
            sampling_interval_seconds=_sampling_interval(sensor.default_config),
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
                default_config=d.default_config,
                sampling_interval_seconds=_sampling_interval(d.default_config),
            )
            rows.append(row)
            self.db.add(row)
        
        self.db.commit()
        
        result = []
        for row, d in zip(rows, devices):
            self.db.refresh(row)
            result.append(_device_from_row(row))
        return result

    def get_device(self, device_id: uuid.UUID) -> Device | None:
        row = self.db.query(DeviceRow).filter(DeviceRow.id == device_id).first()
        return _device_from_row(row) if row else None

    def update_sampling_settings(
        self,
        device_id: uuid.UUID,
        sampling_interval_seconds: int,
        tracking_enabled: bool,
    ) -> Device | None:
        row = self.db.query(DeviceRow).filter(DeviceRow.id == device_id).first()
        if row is None:
            return None
        row.sampling_interval_seconds = sampling_interval_seconds
        row.tracking_enabled = tracking_enabled
        self.db.commit()
        self.db.refresh(row)
        return _device_from_row(row)

    def list_simulation_sensors(self) -> list[Device]:
        rows = (
            self.db.query(DeviceRow)
            .filter(
                DeviceRow.role == "sensor",
                DeviceRow.tracking_enabled.is_(True),
                DeviceRow.default_config["protocol"].as_string() == "simulation",
            )
            .all()
        )
        return [_device_from_row(row) for row in rows]

    def list_devices(self, *, device_family: str | None = None, role: str | None = None) -> list[Device]:
        query = self.db.query(DeviceRow)
        if device_family:
            query = query.filter(DeviceRow.device_family == device_family)
        if role:
            query = query.filter(DeviceRow.role == role)
            
        rows = query.order_by(DeviceRow.created_at.desc()).all()
        return [_device_from_row(row) for row in rows]