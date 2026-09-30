import random
from datetime import datetime, timezone
from numbers import Real
from typing import Any

from domain.devices.entity import Device
from domain.sensors.ports import SensorPort
from domain.sensors.reading import Reading


class VendorStubSensorAdapter(SensorPort):
    def read(self, device: Device) -> Reading:
        if device.device_type == "moisture_sensor":
            payload = {"measurement": {"reading": random.uniform(20, 60), "scale": "percent"}}
        elif device.device_type == "light_sensor":
            payload = {"measurement": {"reading": random.uniform(20, 186), "scale": "foot_candle"}}
        else:
            raise ValueError(f"Unsupported vendor sensor type: {device.device_type}")

        return self.translate(device, payload)

    def translate(self, device: Device, payload: dict[str, Any]) -> Reading:
        if device.id is None:
            raise ValueError("Cannot translate a reading for an unpersisted device")

        measurement = payload.get("measurement")
        if not isinstance(measurement, dict):
            raise ValueError("Vendor payload must contain a measurement object")

        raw_value = measurement.get("reading")
        raw_scale = measurement.get("scale")
        if isinstance(raw_value, bool) or not isinstance(raw_value, Real):
            raise ValueError("Vendor measurement reading must be numeric")

        if device.device_type == "moisture_sensor" and raw_scale == "percent":
            value = float(raw_value) / 100
            unit = "vwc"
        elif device.device_type == "light_sensor" and raw_scale == "foot_candle":
            value = float(raw_value) * 10.764
            unit = "lux"
        else:
            raise ValueError(f"Unsupported vendor measurement scale: {raw_scale}")

        return Reading(
            device_id=device.id,
            value=value,
            unit=unit,
            source="vendor",
            recorded_at=datetime.now(timezone.utc),
        )