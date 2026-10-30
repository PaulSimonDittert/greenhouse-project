# State Pattern — Actuator Lifecycle

## Problem

The greenhouse system needs to persist each actuator's lifecycle state, expose the current state to the API and UI, and reject illegal transitions before any write occurs. If that logic lives only in the API or UI, it becomes easy to drift from the real business rules and to accidentally persist invalid actuator states.

## Solution

The project uses a small State pattern around an actuator context and a transition table.

- `domain/actuators/state.py` declares the valid states and the legal transitions.
- `domain/actuators/context.py` wraps the current state and raises `IllegalTransitionError` when a transition is not allowed.
- `allowed_commands` is derived from the current state rather than being hard-coded in the router or frontend.
- `actuator_states` is persisted in the database so the lifecycle survives restarts and does not live only in process memory.

## Valid states

The accepted actuator states are:

- `off`
- `idle`
- `running`
- `error`
- `maintenance`

## Legal transitions

The current allowed edges are:

- `off -> idle`
- `idle -> running`
- `idle -> maintenance`
- `idle -> error`
- `running -> idle`
- `running -> error`
- `error -> idle`
- `error -> off`
- `maintenance -> idle`
- `maintenance -> error`

Anything outside this matrix is rejected and must not update the stored state.

## Why this is the right pattern

The state machine is explicit, centralized, and testable. The API does not need to know the legal edges; it asks the domain context to transition the actuator and then persists the result. That keeps the business rule in one place and prevents hidden transition logic from being duplicated in routes or React components.

## Where to look in code

- Domain state rules: `backend/src/domain/actuators/state.py`
- Actuator context wrapper: `backend/src/domain/actuators/context.py`
- Persistence model: `backend/src/infrastructure/persistence/models.py`
- Repository for persisted states: `backend/src/infrastructure/persistence/actuator_state_repository.py`
- Application service: `backend/src/application/devices/actuator_state_service.py`
- Device API state fields: `backend/src/interfaces/api/devices.py`
- Frontend badges: `frontend/src/components/devices/DeviceList.tsx`

## Extension exercise

Add a dedicated `reset` command flow for an actuator in `error` state, then document the exact transition and the commands enabled after recovery.
