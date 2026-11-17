# Phase 11 — Observer questions

**Pattern / focus:** Observer.

**Read first:** [Guide 11](../../materials/guides/11-observer.md) · [Requirements](requirements.md)

## How to answer

- Use your own wording. Do not paste teaching-example types (for example live auction bids) as if they were your greenhouse classes.
- When a question asks about *this application*, refer to the event bus, alerts, publishers, and the event feed from the lab.
- Short answers are fine when the question is narrow. Write a few sentences when it asks you to explain or compare.
- Write each answer inside the matching **Your Answer** note. Replace the placeholder; leave the question text unchanged.

## A. Pattern

1. State the intent of Observer in plain language. What is a **one-to-many** dependency here, and why must the subject notify dependents **without** knowing their concrete classes?

> [!NOTE]
>Intent: Behavioral Desgin Pattern. Define a subscription mechanism to notify multible objects about any events that happen to the object they are observing.
>One to many: The "one to many" dependency describes the relationship between the object being observed (publisher) and the observers observing it. The publisher pushes notification in one interfaces, which then reaches all object subscribed to it. 
>Why: When the publisher stay "ignorant" towards its subscribers and simply uses its interface, the mechanism stay flexible easy to implement. This also does not wire the classes to closely together, because observers might like to subscribe and unsubscribe at any time. 

2. Name the participants (**subject / event bus**, **observer / subscriber**, **concrete observers**, **event**, **publisher**). What does `subscribe` / `unsubscribe` / `publish` (or `notify`) each do?

> [!NOTE]
>Subject / event bus: `bus` defines a methode for `subscribe` and `publishe`. It stores listeners and dispatches notifications. 
>Observer / subscriber: Declares a callback/handler to recieve event notifications.
>Concrete Observer: Unique implementations of the notification interface, which can be subscribed to a publisher and utualize the events for their own executions.
>Event: Domain object being published (`ReadingCreated`,`ThresholdCrossed`, `CommandFailed`).
>Publisher: The service that triggers the event after a successful action.

>`subscribe`: Registeres a handler for a specific event type.
>`unsubscribe`: Not present in this project. Otherwiese, would remove a handler from a specific event type.
>`publish/notify`: Dispatches the event to all currently subscribed handlers for that event type.

3. When should you use Observer, and when should you skip it (only one listener forever; or you need a strict multi-step workflow with guaranteed order)?

> [!NOTE]
>When to use: Use Observer when one object changes state or produces an event and multiple other objects may need to react, without the producer knowing or depending on those objects directly.
>When to skip: Skip Observer when there is only one fixed listener and no need for flexible fan-out. Also skip it for a strict, ordered workflow where every step must happen in a guaranteed sequence.

## B. This phase of the application

4. Give at least two **domain events** you publish in this lab, including `reading.created` (only when `tracking_enabled` is true), a threshold-crossed event, and command-failed. Who publishes `reading.created`, and why do a manual read, the simulation sampler, and MQTT translation share that one ingest publish? Why must a publisher **not** import the alerts repository or the UI?

> [!NOTE]
>Examples: Two clear domain events in this lab are `reading.created` and `threshold.crossed`. A third is `command.failed`.
>
>Who: `reading.created` is published by the reading ingest application service, specifically when a reading is successfully inserted in the ingest pipeline, persisted and `device.tracking_enabled` is true. 

>Why: Manual reads, the simulation sampler, and MQTT-translated readings all share that same ingest publish because they all pass through the same record-creation path; the source of the data is different, but the event meaning is the same.
>
>Why: Because it should only emit a domain event, not perform side effects. The alert persistence logic belongs in subscribers, while the UI and API simply read from the stored alerts later. [decoupleing and reusable]

5. What does `AlertPersistenceSubscriber` (or your equivalent) do when it handles an event? Why do alerts live in the `alerts` table so the event feed still shows them after a **refresh**?

> [!NOTE]
>What: When one of these events arrives, that it has subscribed to, it checks the device and zone context, decides whether the event should create an alert, and then inserts an alert row through the alert repository.
>
>Why: Alerts live in the `alerts` table because the dashboard event feed is DB-backed and polls `GET /api/alerts`. [Persit the alter historie]

6. The dashboard Event feed **polls** `GET /api/alerts` (or events). `services/realtime.ts` is only a **stub**. Why is full WebSocket **not** required in this phase? What should Phase 12 plug into so you do **not** re-implement pub/sub inside socket handlers?

> [!NOTE]
>Why: Because the learning goal is to implement the event bus and persistence pattern, not the real-time transport. This phase is about “what happened” and “who should react,” not about the socket transport itself.
>
>What: Phase 12 should plug into the same event bus and subscriber system. The socket layer should just receive or forward the already-published domain events, while subscribers and the API remain the source of truth.

7. Describe the must-demo path: a **tracked** low-moisture reading leads to an alert row that appears in the feed after poll. Which objects collaborate (reading pipeline → bus → subscriber → API → UI), and which object must **not** write the alert directly? What is stored, and what is not published, when `tracking_enabled` is false?

> [!NOTE]
>Path: The must-demo path starts with a sensor reading that is successfully stored by the reading ingest pipeline. Because the device has `tracking_enabled = true`, the ingest service publishes a `ReadingCreated` event on the event bus. The bus then notifies the `AlertPersistenceSubscriber`, which evaluates the moisture threshold and inserts an alert row in the `alerts` table. The API exposes those rows over `GET /api/alerts`, and the frontend Event feed polls that endpoint and displays the alert in the dashboard.
>
>Which: The reading pipeline (`ReadingIngest`), the event bus, the alert subscriber, the alert repository/database, the alerts API, and the dashboard feed UI. 
>
>Which: The object that must not write the alert directly is the publisher itself; it should never import the alert repository or perform database writes. It should only publish an event and let the subscriber handle the persistence.
>
>What: When `tracking_enabled` is false, the reading is still stored in the readings table, but no `reading.created` event is published. (Persistance, but no event/publish)

## C. Compare, contrast, and scenarios

8. Contrast Observer with **Facade**. Facade simplifies **calling into** a subsystem. Observer **fans out** notifications after something happened. How do both appear in this greenhouse (Phase 7 overview vs this phase)?

> [!NOTE]
>A facade hides a complex subsystem and simplifies calling into it, which is how the greenhouse overview in earlier phases can present a cleaner interface to reading, device, or command logic. 
>Observer is different: it is not about simplifying a call, it is about notifying multiple listeners after something already happened, such as a reading being stored or a command failing.

9. Contrast Observer with **Command**. Command captures **intent to act**. Observer propagates **outcomes**. How can `execute()` publish an event without the command class knowing who persists alerts?

> [!NOTE]
>Contrast: A command represents what should happen, while an observer pattern represents what already happened. A `Command` object captures intent to execute a task, such as “turn pump on” or “start watering cycle.” An `Observer` event describes the outcome after execution, such as “command failed” or “threshold crossed.” 
>
>How: In this design, `execute()` can publish an event to the bus after it finishes or fails, without ever importing the alert repository. It simply creates a domain event object and calls `event_bus.publish(...)`. The bus then notifies all subscribed handlers, including the alert persistence subscriber, which inserts the alert row. That is the decoupling: the command class knows about the outcome event, not the concrete alert writer.

10. One subscriber throws during `notify` / `publish` and aborts the loop, so later subscribers never run. Why is that a trap? What should the bus do so a failing alert writer does not block metrics (or later WebSocket) subscribers?

> [!NOTE]
>Why: A single failing subscriber can stop the entire notification fan-out. This creates inconsistent behavior and makes the whole system fragile.
>
>What: The bus should isolate failures per subscriber so that one exception does not abort the loop. It should catch exceptions around each handler invocation, log or report the failure, and continue notifying the remaining subscribers. 