from datetime import datetime

from sqlalchemy.orm import Session

from application.readings.service import ReadingIngest
from infrastructure.persistence.device_repository import DeviceRepository
from infrastructure.persistence.reading_repository import ReadingRepository


class SimulationSampler:
    def __init__(self, db: Session):
        self._devices = DeviceRepository(db)
        self._readings = ReadingRepository(db)
        self._ingest = ReadingIngest(db)

    def run_once(self, now: datetime) -> None:
        if now.tzinfo is None or now.utcoffset() is None:
            raise ValueError("Sampler time must be timezone-aware")

        for device in self._devices.list_simulation_sensors():
            if device.id is None:
                continue

            latest = self._readings.latest_for_device(device.id)
            if latest is not None:
                elapsed_seconds = (now - latest.recorded_at).total_seconds()
                if elapsed_seconds < device.sampling_interval_seconds:
                    continue

            self._ingest.take_reading(device.id, recorded_at=now)