import uuid
from dataclasses import replace
from datetime import datetime

from sqlalchemy.orm import Session

from application.readings.dto import ReadingDto
from domain.devices.entity import Device
from domain.sensors.ports import SensorPort
from domain.sensors.reading import Reading
from infrastructure.adapters.sensors.selector import select_sensor_adapter
from infrastructure.persistence.device_repository import DeviceRepository
from infrastructure.persistence.reading_repository import ReadingRepository


class DeviceNotFoundError(LookupError):
    pass


def _reading_to_dto(reading: Reading) -> ReadingDto:
    return ReadingDto(
        device_id=reading.device_id,
        value=reading.value,
        unit=reading.unit,
        source=reading.source,
        recorded_at=reading.recorded_at,
    )


class ReadingIngest:
    def __init__(self, db: Session):
        self._devices = DeviceRepository(db)
        self._readings = ReadingRepository(db)

    def take_reading(self, device_id: uuid.UUID, *, recorded_at: datetime | None = None) -> ReadingDto:
        device = self._get_sensor(device_id)
        adapter = select_sensor_adapter(device)
        if not isinstance(adapter, SensorPort):
            raise ValueError("MQTT sensors accept translated readings; they cannot be read locally")

        reading = adapter.read(device)
        if recorded_at is not None:
            reading = replace(reading, recorded_at=recorded_at)
        return self._record_for_device(device, reading)

    def record(self, device_id: uuid.UUID, reading: Reading) -> ReadingDto:
        device = self._get_sensor(device_id)
        return self._record_for_device(device, reading)

    def list_readings(self, device_id: uuid.UUID, limit: int = 20) -> list[ReadingDto]:
        self._get_sensor(device_id)
        if limit < 1:
            raise ValueError("Reading limit must be at least 1")
        return [_reading_to_dto(reading) for reading in self._readings.list_for_device(device_id, limit)]

    def _get_sensor(self, device_id: uuid.UUID) -> Device:
        device = self._devices.get_device(device_id)
        if device is None:
            raise DeviceNotFoundError(f"Device {device_id} not found")
        if device.role != "sensor":
            raise ValueError("Readings can only be recorded for sensor devices")
        return device

    def _record_for_device(self, device: Device, reading: Reading) -> ReadingDto:
        if device.id != reading.device_id:
            raise ValueError("Reading device_id does not match the requested device")
        if reading.recorded_at.tzinfo is None or reading.recorded_at.utcoffset() is None:
            raise ValueError("Reading timestamp must be timezone-aware")
        return _reading_to_dto(self._readings.insert(reading))