# Builder Pattern — Location Configuration

## Problem

A location configuration contains a location name and one or more zones. Each zone has a name, moisture thresholds, and an optional schedule. Constructing and validating this configuration in an API handler or persistence repository would spread domain rules across layers and could allow incomplete configurations to reach storage.

## Intent in This Project

`LocationConfigBuilder` incrementally collects a location name and zone definitions, then returns one immutable `LocationConfig` from `build()`. The create-config application service translates the request DTO into builder calls and persists the finished domain configuration through the repository.

The builder validates non-empty names, threshold bounds and ordering, unique zone names, and the presence of at least one zone. These checks live in the domain layer so callers cannot create an invalid configuration merely by bypassing HTTP validation. Saved-location operations such as listing, deleting, and editing zones belong to the application service and repository, not to the builder.

## Why Builder, Not Factory Method or Abstract Factory

Factory Method selects a concrete implementation for one product, such as the Phase 2 sensor creators. Abstract Factory creates a family of related products, such as a compatible simulation device kit. Location configuration is neither a variant-selection problem nor a product family: it is a multi-step assembly of one object with several related values and invariants. A fluent Builder makes those steps explicit and provides one validation point at `build()`.

## `location_id` Naming

Zones reference their parent with `location_id`, and assigned devices carry both `zone_id` and the matching `location_id`. The name expresses the actual relationship and remains consistent across the schema, API DTOs, and JSON. No `greenhouse_id` alias is used.

Device assignment is intentionally not a builder operation. Moving a device changes an existing relationship through `ZoneAssignmentService`; it does not reconstruct the location or its configuration.

## Where to Look in Code

- Domain builder and validation: `backend/src/domain/locations/config_builder.py`
- Domain value objects: `backend/src/domain/locations/entity.py`
- Create-and-persist orchestration: `backend/src/application/locations/config_service.py`
- Persistence mapping: `backend/src/infrastructure/persistence/location_repository.py`

## Extension Exercise

Add a zone-level light threshold to the domain `Zone`, builder method, request DTO, persistence model, and migration. Add its validation to the domain builder and test it without involving the database or device-assignment service.