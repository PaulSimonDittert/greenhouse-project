# Abstract Factory Pattern — Device Families

## Problem
A smart greenhouse needs to run in different environments: a local `simulation` for developers, and real `edge` hardware for production. If we mix a virtual moisture sensor with a physical GPIO water pump, the system will crash or behave unpredictably. We need a way to provision a cohesive "kit" of matching sensors and actuators guaranteed to work together.

## Solution
The **Abstract Factory** pattern provides an interface (`DeviceFamilyFactory`) for creating families of related or dependent objects without specifying their concrete classes. 

The concrete factories (`SimulationDeviceFactory`, `EdgeHardwareFactory`) ensure that when a kit is provisioned, every device in that kit shares the same environment logic and protocols.

## Contrast with Factory Method (Phase 2)
* **Factory Method** creates *one specific product* (e.g., a Moisture Sensor).
* **Abstract Factory** creates a *family of related products* (e.g., a Moisture Sensor + Light Sensor + Water Pump + Grow Light designed for the same environment). In our implementation, the Abstract Factory actually *composes* the Phase 2 Factory Methods to build the sensor parts of the kit!

## Where to Look in Code
* **Abstract Factory & Concrete Families:** `backend/src/domain/devices/family_factory.py`
* **Application Service:** `backend/src/application/devices/family_service.py`
* **API DTOs & Mappers:** `backend/src/application/devices/dto.py` and `mappers.py`

## Why Device ≠ DTO
The domain `Device` entity is a pure Python dataclass containing core business rules. The `DeviceDto` is a Pydantic model responsible strictly for HTTP JSON validation. By keeping them separate and mapping between them in the Application layer, we prevent web-framework details from polluting our core business logic.

## Extension Exercise: Adding a Third Family
To add a testing family:
1. Create `class TestHardwareFactory(DeviceFamilyFactory):` returning mocked devices.
2. Update `get_family_factory()` to route the `"test"` key to the new factory.