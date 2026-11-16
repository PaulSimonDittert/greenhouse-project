# Observer Pattern — Greenhouse Events and Alerts

## Problem

Reading ingestion and command execution need to notify other parts of the application when something happens. If those publishers directly write alerts or depend on API or UI code, each new reaction would couple business services to another concern.

## Solution

The backend uses an in-process publish/subscribe `EventBus`, which acts as the subject. Publishers emit domain events; subscribers register handlers for event types and react independently.

- `ReadingIngest` publishes `ReadingCreated` after persisting a reading, and only when tracking is enabled.
- `CommandService` publishes `CommandFailed` for failed or rejected commands.
- `AlertPersistenceSubscriber` handles readings that cross a zone's low moisture threshold, explicit threshold-crossed events, and command failures. It writes alerts through `AlertRepository`.
- The API lists persisted alerts, and the dashboard polls that API every five seconds.

The composition root creates one bus, registers alert persistence, and supplies that bus to the reading and command services and the simulation sampler. Alert persistence opens its own database session for each event, so the subscriber does not retain a request-scoped session.

## Why this pattern

Publishers depend on event contracts rather than alert storage. The subscriber owns alert rules and persistence, while the API and dashboard consume the durable alert records. This keeps ingestion and command services independent of HTTP and presentation concerns.

## Phase 12 boundary

The bus is synchronous and process-local; this phase does not implement WebSockets. In Phase 12, a WebSocket delivery subscriber can be attached to the same bus and send events to connected clients. The persisted alerts remain the source for refreshes and recovery when a client reconnects.

## Where to look

- Event contracts and bus: `backend/src/domain/events/events.py`, `backend/src/domain/events/bus.py`
- Alert subscriber: `backend/src/application/alerts/subscribers.py`
- Publisher services: `backend/src/application/readings/service.py`, `backend/src/application/commands/service.py`
- API and feed: `backend/src/interfaces/api/alerts.py`, `frontend/src/components/events/EventFeed.tsx`
