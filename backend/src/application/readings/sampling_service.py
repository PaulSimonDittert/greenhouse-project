import uuid

from sqlalchemy.orm import Session

from application.readings.dto import SamplingSettingsDto
from application.readings.service import DeviceNotFoundError
from infrastructure.persistence.device_repository import DeviceRepository


class DeviceSamplingService:
    def __init__(self, db: Session):
        self._devices = DeviceRepository(db)

    def update_settings(
        self,
        device_id: uuid.UUID,
        sampling_interval_seconds: int,
        tracking_enabled: bool,
    ) -> SamplingSettingsDto:
        if sampling_interval_seconds < 5:
            raise ValueError("sampling_interval_seconds must be at least 5")

        device = self._devices.update_sampling_settings(
            device_id,
            sampling_interval_seconds,
            tracking_enabled,
        )
        if device is None:
            raise DeviceNotFoundError(f"Device {device_id} not found")

        return SamplingSettingsDto(
            sampling_interval_seconds=device.sampling_interval_seconds,
            tracking_enabled=device.tracking_enabled,
        )