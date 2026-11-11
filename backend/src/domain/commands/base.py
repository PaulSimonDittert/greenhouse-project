from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from typing import Any

from domain.actuators.ports import ActuatorPort


class Command(ABC):
    command_type: str
    target_state: str | None = None

    def __init__(self, device_id: uuid.UUID, payload: dict[str, Any] | None = None) -> None:
        self.device_id = device_id
        self.payload = payload or {}

    @abstractmethod
    def execute(self, port: ActuatorPort) -> None:
        raise NotImplementedError
