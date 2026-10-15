# Facade Pattern — Location Overview

## Problem

The dashboard needs a location-level snapshot that combines location and zone details, assigned devices, each device's latest reading, and the saved automation strategy. If the HTTP route or frontend coordinates those separate subsystems, either layer has to know how the persistence and automation pieces fit together. That spreads query and business orchestration across the application and can produce inconsistent or chatty reads.

The overview must also reflect current database state: a newly stored reading or changed strategy should appear on the next request. Recommendations should use the existing automation policy rather than introduce another copy of it or persist a stale result.

## Solution

The project uses the Facade pattern through `LocationOverviewFacade`.

- `get_overview(location_id)` is the single application entry point for building the location overview read model.
- The facade loads the location and its zones, then queries devices assigned to that location. It includes every zone and excludes devices without a zone assignment.
- It retrieves the newest reading for the assigned device ids using one batched query, rather than issuing a reading query for each device. Devices without readings remain in the device list and have no reading summary.
- The facade reads the saved strategy key and calls `AutomationService.evaluate(location_id)` only when a key exists. The existing automation service remains responsible for moisture lookups and strategy decisions.
- The API route calls only the facade and returns its DTO. The frontend renders cards from this single overview response rather than combining device, reading, and automation responses.

This keeps the dashboard-facing operation simple while allowing the existing repositories and automation service to retain their own responsibilities.

## Why this is the right pattern

An overview is a composed read model, not a new business entity or persistence boundary. A facade provides one entry point for the dashboard without turning the HTTP handler into a coordinator for multiple repositories.

The recommendation is computed by the existing evaluate service on each overview request when a strategy key is saved. It is not cached or written to a new table, so it reflects the same policy used by the automation endpoint and avoids stale stored recommendations.

The facade avoids an N+1 pattern for readings: it loads the assigned devices once and performs one newest-reading query for their ids. Evaluate may still retrieve moisture once per zone; that lookup stays inside the automation service, where the strategy context is assembled, instead of duplicating `decide` or moving policy into the facade.

No migration or overview-specific view is required. Existing `locations`, `zones`, `devices`, `sensor_readings`, and `automation_rules` tables provide the data used by the read model.

## Where to look in code

- Overview DTO contract: `backend/src/application/overview/dto.py`
- Facade and read-model assembly: `backend/src/application/overview/facade.py`
- Existing evaluate service and strategy orchestration: `backend/src/application/automation/service.py`
- Persistence models for locations, zones, devices, readings, and rules: `backend/src/infrastructure/persistence/models.py`
- Overview route and response schema: `backend/src/interfaces/api/overview.py`
- Overview panel: `frontend/src/components/overview/OverviewPanel.tsx`
- Overview integration test: `backend/tests/test_overview.py`

## Extension exercise: add another overview field

Add a field that belongs to the dashboard snapshot by extending the overview DTO and loading its source through the appropriate existing subsystem. Keep the route dependent only on the facade, avoid per-item queries, and do not persist values that can be computed from current state unless a separate requirement calls for caching.
