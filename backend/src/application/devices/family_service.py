from sqlalchemy.orm import Session
from domain.devices.family_factory import get_family_factory
from domain.devices.entity import Device
from infrastructure.persistence.device_repository import DeviceRepository

class DeviceFamilyService:
    def __init__(self, db: Session):
        self._repo = DeviceRepository(db)

    def provision_family(self, family: str) -> list[Device]:
        factory = get_family_factory(family)
        devices = factory.create_device_set()
        return self._repo.save_devices(devices)

    def list_devices(self, *, device_family: str | None = None, role: str | None = None) -> list[Device]:
        return self._repo.list_devices(device_family=device_family, role=role)