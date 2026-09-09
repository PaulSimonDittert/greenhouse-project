from abc import ABC, abstractmethod
from .entity import Sensor

class SensorCreator(ABC):
    @abstractmethod
    def create_sensor(self, display_name: str | None = None) -> Sensor:
        pass

class MoistureSensorCreator(SensorCreator):
    def create_sensor(self, display_name: str | None = None) -> Sensor:
        return Sensor(
            device_type="moisture_sensor",
            display_name=display_name or "Soil Moisture Sensor",
            default_config={"unit": "vwc", "sampling_interval_seconds": 300, "threshold": 20.0}
        )

class LightSensorCreator(SensorCreator):
    def create_sensor(self, display_name: str | None = None) -> Sensor:
        return Sensor(
            device_type="light_sensor",
            display_name=display_name or "Ambient Light Sensor",
            default_config={"unit": "lux", "sampling_interval_seconds": 60}
        )

def get_creator(sensor_type: str) -> SensorCreator:
    if sensor_type == "moisture":
        return MoistureSensorCreator()
    elif sensor_type == "light":
        return LightSensorCreator()
    else:
        raise ValueError(f"Unknown sensor type: {sensor_type}")