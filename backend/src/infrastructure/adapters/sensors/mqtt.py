from datetime import datetime, timezone
from numbers import Real
from typing import Any

from domain.devices.entity import Device
from domain.sensors.reading import Reading


class MqttSensorAdapter:
    def translate(self, device: Device, payload: dict[str, Any]) -> Reading:
        if device.id is None:
            raise ValueError("Cannot translate a reading for an unpersisted device")

        value = payload.get("value")
        unit = payload.get("unit")
        if isinstance(value, bool) or not isinstance(value, Real):
            raise ValueError("MQTT payload value must be numeric")
        if not isinstance(unit, str) or not unit.strip():
            raise ValueError("MQTT payload unit must be a non-empty string")

        return Reading(
            device_id=device.id,
            value=float(value),
            unit=unit.strip(),
            source="mqtt",
            recorded_at=datetime.now(timezone.utc),
        )