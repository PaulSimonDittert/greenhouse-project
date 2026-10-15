# Phase 7 — Facade questions

**Pattern / focus:** Facade.

**Read first:** [Guide 07](../../materials/guides/07-facade.md) · [Requirements](requirements.md)

## How to answer

- Use your own wording. Do not paste teaching-example types (for example a video publish pipeline) as if they were your greenhouse classes.
- When a question asks about _this application_, refer to the location overview, the facade, and the dashboard Overview page from the lab.
- Short answers are fine when the question is narrow. Write a few sentences when it asks you to explain or compare.
- Write each answer inside the matching **Your Answer** note. Replace the placeholder; leave the question text unchanged.

## A. Pattern

1. State the intent of Facade in plain language. What problem appears when every HTTP handler (or every UI screen) repeats the same multi-step dance across repositories and services?

> [!NOTE]
>A Facade gives callers one simple entry point for work that needs several parts of an application. Without it, each route or screen would have to repeat the steps for loading data, calling services, and combining results. That duplicates code and makes changes harder, because the same coordination logic can drift in different places.

2. A facade **orchestrates** collaborators. What should it **not** become (a god object that owns all domain logic)? Where should irrigation policy, sensor translation, and persistence stay instead?

> [!NOTE]
>The facade should coordinate existing parts, not take over all their jobs. The facade assembles the overview by calling those existing parts, instead of existing of those parts and then "printing its own output".

>Irrigation decisions belong in the automation strategies and service, sensor protocol translation belongs in the adapters, and database queries and writes belong in repositories.

3. When should you use Facade, and when should you skip it (a single repository call is enough; or you actually need to **translate** a mismatched interface)?

> [!NOTE]
>Use a Facade when one task needs several existing services or repositories and callers should not need to coordinate them. 
>Skip it when one repository call already does the job; adding another layer then gives little benefit. If the main problem is that an outside system has a different interface, use an Adapter to translate that interface instead.

## B. This phase of the application

4. What does `GET /api/locations/{location_id}/overview` return? Name the main pieces of the overview DTO: location, assigned device counts, and `zones` (thresholds, assigned devices, and those devices’ latest readings, including `tracking_enabled` and `sampling_interval_seconds`), plus strategy key and last recommendation. Why may those reading rows come from the sampler or MQTT ingest, not only from `POST /read`? Why is overview scoped by `location_id`?

> [!NOTE]
>The GET returns a summary of one location and its current devices, readings, zones, and automation status.
>
>The main parts of the overview are:
>**Location:** its id and name.
>**Assigned device counts:** the number of sensors and actuators assigned to zones at that location.
>**Zones:** every zone, with its moisture thresholds, assigned devices, and each device's latest reading when it has one. A reading includes its value, unit, time, tracking setting, and sampling interval.
>**Strategy key:** the saved key, or null if no strategy has been saved.
>**Last recommendation:** the action and reason calculated using the saved strategy, or null if there is no saved strategy.
>
>The sampler and MQTT ingest can save readings to the same readings table as a manual read. The overview uses the newest saved reading regardless of how it got there, so it is not limited to readings from `POST /read`.
>
>The overview is about one location: its zones, assigned devices, and saved strategy all belong to a specific `location_id`. Using that id makes clear which location's information the GET should return.

5. Why does this phase **not** require a new business table? What already exists from Phases 2–6 that the facade only **composes**?

> [!NOTE]
>The overview is a summary for the dashboard, not new information that needs its own table. The earlier phases already store the pieces it needs:
>
>**Phase 2–3:** sensors and actuators in the shared `devices` table, including their type, role, family, and defaults.
>**Phase 4:** locations and zones, their moisture thresholds, and each device's location and zone assignment.
>**Phase 5:** sensor readings in `sensor_readings`, plus each device's tracking setting and sampling interval. Manual reads, the sampler, and translated MQTT readings use the shared readings data.
>**Phase 6:** the saved strategy key for each location in `automation_rules`, along with the automation service that calculates a recommendation.
>
>The facade gathers those existing records into one response. It calculates the recommendation when the overview is requested, so it does not need to store a duplicate or potentially stale recommendation.

6. The overview HTTP handler should call **only** the facade, not reading/strategy/device repositories directly. Why? How does that help tests and later changes to the query shape?

> [!NOTE]
>**Why:** The handler should focus on HTTP details, such as the path parameter, response model, and mapping a missing location to 404. The facade coordinates the repositories and services, so the route does not need to know how the overview is assembled.
>
>**How:** The facade can be tested as one application operation, without making the handler responsible for every data source. If the query shape changes later, the facade can change how it loads the data while the handler and response contract stay the same.

7. The location selector may use the existing locations list. The Overview cards come from **one** overview fetch, and Refresh repeats that same fetch. Why must the React page not stitch device, reading, and automation calls together to build the same snapshot? How does a new reading or a saved strategy show up on overview without extra frontend glue?

> [!NOTE]
>**Why must React:** Calling the device, readings, and automation endpoints separately would make the page responsible for combining their results. It could also show a mixed snapshot if the data changes between calls, and duplicates coordination that belongs on the backend.
>
>**How:** Selecting a location or pressing Refresh fetches the overview again. The backend reads the current data, so the next response includes a new reading or saved strategy without React needing extra calls or merge logic.

## C. Compare, contrast, and scenarios

8. Contrast Facade with **Adapter**. One makes an existing interface usable; the other makes a subsystem simpler to call. Which is which, and how do both appear in this greenhouse app (Phase 5 vs Phase 7)?

> [!NOTE]
>**Adapter — makes an existing interface usable:** In Phase 5, sensor adapters translate different inputs, such as simulation values or an MQTT payload, into the application's common `Reading` format through the sensor port.
>
>**Facade — makes a subsystem simpler to call:** In Phase 7, `LocationOverviewFacade` gives the dashboard one entry point that coordinates location data, assigned devices, readings, and automation, returning one overview response.

9. This phase mentions **N+1** queries. What is an N+1 problem in an overview that lists latest readings for many devices, and what can the facade (or its repository) do about it without putting SQL in the router?

> [!NOTE]
>**N+1:** The application loads the devices, then makes a separate query for each device to find its latest reading. So a location with many devices causes many extra database queries.
>
>**What can the Facade do:** It can pass all assigned device ids to a repository query that returns the newest reading for each device in one batch. The router still just calls the facade, and devices with no reading can remain in the device list without a separate query for each one.

10. A classmate hides every error behind a generic “overview failed,” so a missing location, a DB outage, and a strategy error look the same. Why is that a trap for a facade?

> [!NOTE]
>**Why this is a trap:** A facade should make it easier to call several parts of the system, not hide what went wrong when one of them fails. A missing location should be reported as not found, while a database outage or strategy error should remain an operational error. If every problem becomes “overview failed,” the API gives misleading feedback and it is harder to diagnose and fix the real cause.