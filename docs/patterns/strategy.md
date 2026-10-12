# Strategy Pattern — Automation Decisions

## Problem

The greenhouse automation logic must choose irrigation actions from the latest moisture readings and each zone's configured low/high thresholds. If that logic stays in the API layer, the route becomes responsible for both HTTP concerns and business decisions. That makes the behavior harder to change, harder to test, and easier to duplicate across endpoints.

We also need the decision logic to remain pluggable: the system stores one active strategy per location, but the algorithm should be swappable without changing the rest of the application.

## Solution

The project uses the Strategy pattern.

- `AutomationStrategy` defines the common interface: `decide(context)`.
- `ConservativeMoistureStrategy` and `AggressiveMoistureStrategy` implement the interface.
- `get_strategy(key)` selects a concrete strategy by key and rejects unknown keys before any decision is made.
- The service layer builds a plain context object, not ORM rows, and passes that to the chosen strategy.

This keeps the decision logic isolated from SQLAlchemy and from the API transport layer.

## Why this is the right pattern

The same input can legitimately produce different actions depending on the selected strategy. For example, with a zone whose low threshold is `0.25` and high threshold is `0.45`, a moisture value of `0.40` is:

- `conservative`: `wait`, because `0.40` stays above the low threshold.
- `aggressive`: `irrigate`, because `0.40` falls below the high threshold.

That difference is intentional and is encoded in tests so we can verify the strategy is truly pluggable.

## Where to look in code

- Domain strategy and algorithm implementations: `backend/src/domain/automation/strategy.py`
- Plain context object carrying moisture + thresholds: `backend/src/domain/automation/context.py`
- Service orchestration and strategy selection: `backend/src/application/automation/service.py`
- Persisted active strategy per location: `backend/src/infrastructure/persistence/models.py`
- Save/evaluate API routes: `backend/src/interfaces/api/automation.py`
- Dashboard panel: `frontend/src/features/automation/StrategyPanel.tsx`

## Extension exercise: add a third strategy

Create a balanced strategy, for example `BalancedMoistureStrategy`, that irrigates only when moisture drops below a midpoint threshold between the low and high values.
