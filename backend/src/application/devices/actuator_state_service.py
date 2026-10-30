import uuid

from sqlalchemy.orm import Session

from domain.actuators.context import ActuatorContext
from domain.actuators.state import IllegalTransitionError
from infrastructure.persistence.actuator_state_repository import ActuatorStateRepository
from infrastructure.persistence.device_repository import DeviceRepository


class ActuatorNotFoundError(LookupError):
    pass


class ActuatorStateService:
    def __init__(self, db: Session):
        self._devices = DeviceRepository(db)
        self._states = ActuatorStateRepository(db)

    def get_current_state(self, device_id: uuid.UUID) -> str:
        device = self._devices.get_device(device_id)
        if device is None:
            raise ActuatorNotFoundError(f"Device {device_id} not found")
        if device.role != "actuator":
            raise ValueError(f"Device {device_id} is not an actuator")
        return self._states.ensure_for_device(device_id)

    def transition(self, device_id: uuid.UUID, target: str) -> str:
        device = self._devices.get_device(device_id)
        if device is None:
            raise ActuatorNotFoundError(f"Device {device_id} not found")
        if device.role != "actuator":
            raise ValueError(f"Device {device_id} is not an actuator")

        current_state = self._states.get_for_device(device_id) or "idle"
        context = ActuatorContext(current_state)
        try:
            new_state = context.transition(target)
        except IllegalTransitionError:
            raise
        self._states.save(device_id, new_state)
        return new_state
