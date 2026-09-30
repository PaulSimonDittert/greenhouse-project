# Adapter Pattern — Sensor and Actuator Ports

## Problem

Sensor sources do not share one interface or data format. The simulation generator creates values in code, a vendor device can return vendor-specific fields and units, and MQTT supplies an inbound payload. Application code should not need separate persistence or DTO logic for each source, and it should not depend on hardware SDKs or a broker client.

## Solution in This Project

`SensorPort` defines the domain-facing operation `read(device) -> Reading`. The simulation and vendor-stub adapters implement that port and return the normalized `Reading` value object with `device_id`, `value`, `unit`, `source`, and a timezone-aware `recorded_at`.

- `SimulationSensorAdapter` generates plausible moisture and light values in process.
- `VendorStubSensorAdapter` translates a different nested raw shape and unit into the domain reading. It translates data; it does not decide irrigation policy.
- `MqttSensorAdapter` translates an inbound `{ "value": ..., "unit": ... }` payload. It does not open a connection or implement a local read operation. MQTT transport is outside this phase.

`ReadingIngest` selects a read adapter, maps the result to a DTO, and persists it through `ReadingRepository`. It is the application write path for manual reads, sampler output, and already-translated readings. `SimulationSampler` uses that same path for enabled simulation sensors when their interval has elapsed.

The actuator side has an `ActuatorPort.apply(device_id, command, payload)` contract. `SimulationActuatorAdapter` records a copied command in memory only; it does not access GPIO. It is the innermost actuator implementation that a later decorator can wrap.

## Adapter Selection

The selector reads `default_config.protocol`:

- `simulation` selects the in-process simulation adapter.
- `mqtt` selects the payload translator. A one-shot local read is not available until a transport supplies an inbound payload.
- Missing protocol defaults to `simulation` for earlier sensor records; `sim-virtual` is accepted as a legacy simulation value.

The vendor exercise is selected separately with `default_config.sensor_adapter = "vendor_stub"`, which takes precedence over `protocol`. This avoids confusing the vendor translation stub with the Edge/MQTT path. Other protocol values are rejected rather than treated as GPIO drivers.

## Where to Look in Code

- Domain sensor contract and normalized value: `backend/src/domain/sensors/ports.py`, `backend/src/domain/sensors/reading.py`
- Sensor selector and adapters: `backend/src/infrastructure/adapters/sensors/`
- Single reading ingest path: `backend/src/application/readings/service.py`
- Interval sampler: `backend/src/application/readings/sampler.py`
- Actuator contract and stub: `backend/src/domain/actuators/ports.py`, `backend/src/infrastructure/adapters/actuators/simulation.py`

## Extension Exercise: Add Another Vendor

Add a new adapter that implements `SensorPort`, reads or accepts the third vendor's raw shape, and converts its value and unit to `Reading`. Add a distinct selector flag, such as `sensor_adapter: "vendor_b"`, and test the translation with a representative payload. Keep vendor SDK details in the infrastructure adapter; keep persistence in `ReadingIngest`, and do not put device policy in the adapter.
