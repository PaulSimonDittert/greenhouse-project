# Phase 5 — Adapter questions

**Pattern / focus:** Adapter.

**Read first:** [Guide 05](../../materials/guides/05-adapter.md) · [Requirements](requirements.md)

## How to answer

- Use your own wording. Do not paste teaching-example types (for example a legacy XML calendar client) as if they were your greenhouse classes.
- When a question asks about *this application*, refer to sensor ports, adapters, readings, and `sensor_readings` from the lab.
- Short answers are fine when the question is narrow. Write a few sentences when it asks you to explain or compare.
- Write each answer inside the matching **Your Answer** note. Replace the placeholder; leave the question text unchanged.

## A. Pattern

1. State the intent of Adapter in plain language. What problem appears when business code speaks a vendor or legacy protocol (odd field names, units, XML, status codes) directly?

> [!NOTE]
>Intent: Adapter makes two incompatible interfaces work together by translating one into the other. In this project, a vendor or legacy source might send odd field names, units, or status codes that do not match the projects’s reading model.
>
>The problem is that business logic would have to know all the external formatting. Such a business logic codebase would be very hard to maintain, change and extend. Via an Adapter all the external struggels can be kept in one place. 

2. Name the participants (**target / port**, **adaptee**, **adapter**, **client**). What does the adapter translate, and what must it **not** decide (business policy)?

> [!NOTE]
>Target/port: `SensorPort`, the interface the application expects.
>Adaptee: the vendor, simulation, or raw payload that uses a different format.
>Adapter: the translator that converts input into the normalized reading type the project needs.
> Client: the service/API that wants a clean reading, without caring where it came from.
>
>The adapter translates the data format and meaning, but it must not decide business policy. It should not decide irrigation rules, threshold actions, or greenhouse behavior. Such decission belong to business logic and not the adapter.

3. GoF distinguishes an **object adapter** (composition) from a **class adapter** (inheritance). Which does modern code prefer, and why?

> [!NOTE]
>Modern code usually prefers the object adapter. It wraps the adaptee instead of inheriting from it, which keeps the design more flexible. In this project, each sensor source has a different format, but all of them should produce the same reading.

## B. This phase of the application

4. What is `SensorPort` in this lab, and what normalized value type (for example `Reading`) do adapters return? Why do application services depend on the port rather than on a simulation driver or vendor SDK?

> [!NOTE]
>`SensorPort` is the contract that that reads a sensor and returns a formatted reading. In this lab, adapters return a `Reading`-style value with a device ID, source, timestamp, and clean sensor value.
>
>Application services depend on the port because they want the same behavior. It should not matter if the data came from a simulation, a vendor, or MQTT. This keeps the project independent from the specific driver or SDK behind the source.

5. You need three translations onto the same normalized reading: a simulation adapter, a vendor stub, and an MQTT translator that accepts a payload dict. Why is the different raw shape the point of the exercise? How does `source` (`simulation`, `vendor`, or `mqtt`) show which adapter produced the reading, and why must the MQTT translator not open a broker in this phase? Phase 12 may deliver that same dict on a device HTTP route or through an optional broker — why must this phase still not open either transport?

> [!NOTE]
>The point of the exercise is that the project should not care whether the raw input comes in a different shape. A simulation adapter, a vendor stub, and MQTT payloads all produce the same normalized reading, even though the input data looks different.
>
> `source` tells us which adapter produced the reading: `simulation`, `vendor`, or `mqtt`, by having its value be set by the adapter that was handeling it. That makes debugging and traceability easier without changing the business logic.
>
>The MQTT translator must not open a broker in this phase because this phase is about translating data, not managing transport. Phase 12 may later route the same dict over HTTP or an optional broker, but this phase still must not open either transport. Otherwise the adapter becomes responsible for networking, which is the wrong boundary.

6. Readings are **appended** to `sensor_readings` (history grows). Why not keep only the latest value in memory or overwrite a single row, and which later phase consumes this history? Why do a manual read, the simulation sampler, and (later) MQTT share **one** writer of that table? Why does the sampler skip devices with tracking off and MQTT devices, and why do sensor cards poll the latest stored reading until Phase 12?

> [!NOTE]
>Readings are stored as history because greenhouse data is time-based. Keeping only the latest value in memory would lose context, and overwriting a single row would destroy the timeline.
>
>There will come a later phases that, for example, visalises the Data that has been collected in, for example, a graph or table.
>
>A manual read, the simulation sampler, and later MQTT all write through the same `sensor_readings` table because they are all creating the same normalized reading event.
>
>The sampler skips devices with tracking turned off because those devices are intentionally not being recorded. It also skips MQTT devices because MQTT is a separate transport path for a later phase. Sensor cards poll the latest stored reading until Phase 12 because that gives a stable current view while real-time transport is not implemented yet.

7. `POST /api/sensors/{id}/read` runs an adapter, persists, and returns a DTO. What HTTP status is appropriate when the device is missing versus when the adapter fails? Why must the router never see vendor-shaped types?

> [!NOTE]
>If the device is missing, the right response is `404 Not Found`. If the adapter fails while translating or reading the sensor, a `500 Internal Server Error` is fitting unless the project has a more specific error for that case.
>
>The router must never see vendor-shaped types because it should only work with application DTOs and normalized domain data. The adapter is the place where external formats are translated; the HTTP layer should not know anything about vendor-specific objects.

## C. Compare, contrast, and scenarios

8. Contrast Adapter with **Facade**. Adapter changes the **shape** of an existing interface; Facade simplifies **how to use** a subsystem. Give a greenhouse-shaped example of each (Adapter this phase; Facade in Phase 7).

> [!NOTE]
>Adapter changes the shape of an existing interface so the app can use it consistently. In this phase, a sensor adapter converts a vendor or simulation payload into a normal reading.
>
>Facade simplifies how a subsystem is used. In Phase 7, a greenhouse facade could hide the details of many location, sensor, and device operations behind one simple service. The adapter changes the interface; the facade hides complexity.

9. Contrast Adapter with **Decorator**. Both wrap an object. What is different about the interface they present to the client?

> [!NOTE]
>Adapter presents a different interface to the client. It changes the original object so it fits the project’s expected contract.
>
>Decorator presents the same interface, but adds behavior around it. It does not change the client-facing method names or contract; it adds logging, validation, or caching while keeping the same calls working.

10. A classmate puts irrigation policy (“if moisture &lt; 0.3 then water”) inside the vendor adapter. Why is that a trap? Where should that decision live instead (later Strategy), and what should stay in the adapter?

> [!NOTE]
>That is a trap because the adapter should translate data, not decide greenhouse policy. If irrigation logic sits in the vendor adapter, the adapter becomes responsible for both external compatibility and business behavior.
>
>That decision should live in a later strategy component or control policy, where the watering rule is chosen and applied. The adapter should only convert vendor data into the project’s normalized reading and keep the raw protocol details out of the business decision.
