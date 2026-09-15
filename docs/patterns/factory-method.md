# Factory Method Pattern — Sensor Creation

## Problem
In a smart greenhouse system, we need to create various sensor types (e.g., soil moisture, ambient light, temperature) that each require specific default configurations, units, and device type identifiers. 

If API handlers or callers instantiate these classes directly using conditional statements (e.g., `if type == "moisture": MoistureSensor(...)`), the creation logic becomes scattered across the application layer. Adding a new sensor type would require editing every route or handler where sensors are created.

## Solution
The **Factory Method** pattern defines an abstract interface for creating objects (`SensorCreator`) while allowing subclasses (`MoistureSensorCreator`, `LightSensorCreator`) to decide which specific configuration defaults to instantiate.

A registry function (`get_creator`) decouples callers from concrete creator classes. The caller depends solely on the abstract creator interface and passes a type key, keeping creation logic encapsulated and centralized.

## Where to Look in Code
* **Domain Entity:** `backend/src/domain/sensors/entity.py`
* **Creator Interface & Subclasses:** `backend/src/domain/sensors/creators.py`
* **Application Service:** `backend/src/application/sensors/service.py`
* **API Handler:** `backend/src/interfaces/api/sensors.py`

## Extension Exercise: Adding a Temperature Sensor
To extend this implementation with a new `TemperatureSensor`:

1. Open `backend/src/domain/sensors/creators.py`.
2. Define a new concrete creator class:
   ```python
   class TemperatureSensorCreator(SensorCreator):
       def create_sensor(self, display_name: str | None = None) -> Sensor:
           return Sensor(
               device_type="temperature_sensor",
               display_name=display_name or "Temperature Sensor",
               default_config={"unit": "celsius", "sampling_interval_seconds": 120}
           )