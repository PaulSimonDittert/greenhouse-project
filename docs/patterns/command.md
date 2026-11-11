# Command Pattern — Actuator Requests and Audit History

## Problem

HTTP routes should not directly call actuator adapters or know which state transition a command implies. If route handlers branch on `command_type` and invoke port methods directly, the transport layer becomes responsible for business rules, and illegal commands can be executed without a consistent audit trail.

We also need every attempted actuator action to be recorded in PostgreSQL as an auditable command log, while still protecting the state machine from illegal transitions.

## Solution

The project uses the Command pattern.

- `Command` defines the common interface: `execute(port)`.
- `StartPumpCommand`, `StopPumpCommand`, and `SetLightLevelCommand` encapsulate device-specific behavior and target state.
- `command_for(command_type, device_id, payload)` maps a string to a concrete command class through a registry instead of branching on the type string in the router or service.
- `CommandInvoker.run(command, port)` calls `command.execute(port)` without knowing the concrete command type.

This shifts request handling from routing code into the domain layer, where state-aware checks and command semantics belong.

## Why this is the right pattern

The same actuator action can be created from different HTTP payloads or UI controls, but each request still becomes a first-class object. That gives us a single place to encode:

- allowed command names
- target state transitions
- invocation against the decorated actuator port
- audit logging for success, rejection, and failure

In other words, the router sends a command request, while the service and invoker decide whether the command is legal and then execute it through the Phase 9 decorator stack.

## How the project uses it

The main flow is:

1. `POST /api/commands` receives a JSON body with `command_type`, `device_id`, and optional `payload`.
2. `CommandService.execute(...)` validates the device and current state.
3. The service resolves the command using `command_for(...)` and runs it through `CommandInvoker`.
4. The invoker calls the command's `execute(port)` method.
5. The port is the decorated actuator stack built by `build_actuator_port(...)`.
6. The service writes the audit row to `command_log` with `success`, `failed`, or `rejected` depending on the outcome.

This keeps command execution separate from HTTP concerns and makes the system auditable.

## Why not call the port directly from the router?

That would bypass the command abstraction and reintroduce control flow in the transport layer. The router should only accept input and delegate. The command object and invoker provide the required boundary between API concerns and actuator behavior.

## Where to look in code

- Command base and concrete commands: `backend/src/domain/commands/base.py`, `backend/src/domain/commands/pump.py`, `backend/src/domain/commands/light.py`
- Registry and invoker: `backend/src/domain/commands/invoker.py`
- Application service: `backend/src/application/commands/service.py`
- API endpoints: `backend/src/interfaces/api/commands.py`
- Audit table: `backend/src/infrastructure/persistence/models.py`, `backend/src/infrastructure/persistence/command_log_repository.py`
