import random
from datetime import datetime, timezone

from domain.devices.entity import Device
from domain.sensors.ports import SensorPort
from domain.sensors.reading import Reading


class SimulationSensorAdapter(SensorPort):
    def read(self, device: Device) -> Reading:
        if device.id is None:
            raise ValueError("Cannot read an unpersisted device")

        if device.device_type == "moisture_sensor":
            value = random.uniform(0.2, 0.6)
            unit = "vwc"
        elif device.device_type == "light_sensor":
            value = random.uniform(200, 2000)
            unit = "lux"
        else:
            raise ValueError(f"Unsupported simulation sensor type: {device.device_type}")

        return Reading(
            device_id=device.id,
            value=value,
            unit=unit,
            source="simulation",
            recorded_at=datetime.now(timezone.utc),
        )