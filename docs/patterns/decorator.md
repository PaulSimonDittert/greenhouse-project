# Decorator Pattern — Actuator Policies

## Problem

Actuator commands need policies such as maximum run time and execution logging without changing the actuator adapter or requiring callers to know which policies are active. Keeping those policies in routes would mix transport concerns with actuator behavior, while adding each policy to the adapter would couple the simulation implementation to application rules.

## Solution

Each layer implements the same `ActuatorPort.apply(device_id, command, payload)` interface and wraps another port:

```text
LoggingActuatorDecorator
  → MaxRunTimeActuatorDecorator
    → SimulationActuatorAdapter
```

The application service composes this chain. The simulation adapter remains the innermost implementation; callers use the decorated port.

The max-run-time decorator checks the persisted actuator state before forwarding the command. If the state is `running` and its `updated_at` is at least 30 minutes old, it raises `MaxRunTimeExceededError` without invoking the inner port. Otherwise, it forwards the original device ID, command, and payload unchanged. Command validation is intentionally outside this phase.

The outer logging decorator records a successful attempt with `success=true`, policy `logging`, and no message. If max-run-time blocks the attempt, it records `success=false`, policies `maxRunTime` and `logging`, and message `Max run time exceeded`, then propagates the policy exception. Other adapter failures are also recorded as unsuccessful attempts before being propagated.

Execution records are written to `actuator_execution_log` through `ActuatorExecutionLogRepository`; they are not only application log messages.

## Why use decorators instead of inheritance?

Policies can be composed around any `ActuatorPort` implementation without subclassing each adapter for every combination. The same adapter can be wrapped with different policies, and callers keep one stable interface. This also keeps policy behavior separate from the simulation adapter.

## Where to look in code

- Shared port: `backend/src/domain/actuators/ports.py`
- Innermost simulation implementation: `backend/src/infrastructure/adapters/actuators/simulation.py`
- Runtime policy: `backend/src/infrastructure/adapters/actuators/max_runtime_decorator.py`
- Execution logging wrapper: `backend/src/infrastructure/adapters/actuators/logging_decorator.py`
- Execution persistence: `backend/src/infrastructure/persistence/execution_log_repository.py`
- Composition and application mapping: `backend/src/application/devices/actuator_execution_service.py`
- API and dashboard execution list: `backend/src/interfaces/api/actuators.py`, `frontend/src/features/actuators/ExecutionLog.tsx`
- Decorator and persistence tests: `backend/tests/test_actuator_decorators.py`, `backend/tests/test_actuator_executions.py`
