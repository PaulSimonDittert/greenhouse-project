from abc import ABC, abstractmethod
from typing import Any
import uuid


class ActuatorPort(ABC):
    @abstractmethod
    def apply(self, device_id: uuid.UUID, command: str, payload: dict[str, Any]) -> None:
        raise NotImplementedError