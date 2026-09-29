# Phase 4 — Builder questions

**Pattern / focus:** Builder.

**Read first:** [Guide 04](../../materials/guides/04-builder.md) · [Requirements](requirements.md)

## How to answer

- Use your own wording. Do not paste teaching-example types (for example ramen orders) as if they were your greenhouse classes.
- When a question asks about _this application_, refer to locations, zones, `location_id`, and the configuration wizard from the lab.
- Short answers are fine when the question is narrow. Write a few sentences when it asks you to explain or compare.
- Write each answer inside the matching **Your Answer** note. Replace the placeholder; leave the question text unchanged.

## A. Pattern

1. State the intent of Builder in plain language. Why does construction of a complex object need **stepwise assembly** and **validation at the end** (`build()`), instead of a telescoping constructor or a half-filled dict written straight to the database?

> [!NOTE]
> Intent: Builder separates the step-by-step collection of values from producing the finished domain object. In this project, the location name and zone definitions are gathered first, and `build()` returns a `LocationConfig` only when the required configuration is valid.
>
> Why stepwise assembly: A location has several zones, and each zone has multiple related fields. A telescoping constructor or a half-filled dictionary makes it easy to omit fields or create inconsistent combinations. `build()` provides a clear point where required parts and invariants are checked before persistence is attempted.

2. Name the main participants (**product**, **builder**, **optional director**, **client**). Until `build()` succeeds, is the intermediate object a finished domain product? Why does that distinction matter?

> [!NOTE]
> Product: `LocationConfig`, containing a `Location` and its zones.
>
> Builder: `LocationConfigBuilder`, which accepts the location name and zone definitions and validates them.
>
> Optional director: This project does not use a separate Director. The application service supplies the builder steps directly from the request DTO.
>
> Client: `LocationConfigService` orchestrates construction, and the API handler supplies the request data through that service.
>
> Intermediate state: Before `build()` succeeds, the builder's stored name and zone list are only construction state, not a finished domain product. That matters because only a complete, validated `LocationConfig` should be passed to persistence.

3. List at least three kinds of invalid configuration a location/zone `build()` should reject in **this** lab (name, zones, moisture thresholds). Why must those rules live in the **domain** builder, not only in the HTTP layer?

> [!NOTE]
> Invalid cases: Reject a blank location name, a blank zone name, a configuration with no zones, duplicate zone names, thresholds outside the 0.0–1.0 VWC range, and a low threshold greater than or equal to the high threshold.
>
> Why domain validation: The HTTP layer can provide early feedback, but other callers may use the domain builder without FastAPI. Keeping the rules in `LocationConfigBuilder` means every caller must satisfy the same business invariants before it can get a `LocationConfig`.

## B. This phase of the application

4. What aggregate does the builder produce (location plus zones)? Why does this course use **`location_id`** (and never `greenhouse_id`) as the name for that scope?

> [!NOTE]
> Aggregate: The builder produces one `LocationConfig` containing a `Location` and a tuple of `Zone` values. Zones are part of that location's configuration and are later persisted with its `location_id` foreign key.
>
> Naming: `location_id` describes the parent relationship consistently in the database, DTOs, and API. `greenhouse_id` would name a different concept and make the scope ambiguous; this phase uses `location_id` everywhere.

5. Describe the path from API request to persistence: DTO → builder steps → `build()` → repository. What must **not** be persisted if `build()` raises `ConfigurationError` (or equivalent)? Why does assigning a device wait until the zone row exists, and why does the client send only `zone_id`?

> [!NOTE]
> Request-to-persistence path: FastAPI parses the JSON into `BuildLocationConfigRequestDto`. `LocationConfigService` passes the location name and each zone's fields to `LocationConfigBuilder`; after all steps, it calls `build()`. Only the returned `LocationConfig` is passed to `LocationRepository.save_config()` for mapping to database rows.
>
> On validation failure: If the builder raises `ConfigurationError`, the repository has not been called, so neither a location row nor any zone rows should be persisted.
>
> Assignment: A device can only reference a zone after that zone row exists, because `zone_id` is a foreign key. The client sends only `zone_id`; the server looks up the zone and copies its `location_id` onto the device. This prevents a client from submitting a mismatched location and zone.

6. Saving a location and its zones must be **one transaction**. What goes wrong if the location row commits and a later zone insert fails? How does that relate to “no half-built aggregates in the database”?

> [!NOTE]
> Transaction: `save_config()` adds the location, flushes it to obtain its generated ID, adds all zone rows, then commits once. The flush does not commit the transaction.
>
> If a zone insert fails before commit, the transaction must not leave the location committed by itself. A committed location with missing zones would be a partial aggregate that violates the builder's requirement that a saved location config has at least one zone. The whole operation should commit or roll back as one unit; on database failure, the session must be rolled back rather than reused in its failed transaction state.

7. The configuration wizard UI collects fields in steps. How does that UI map to Builder without turning React (or the HTTP handler) into the place that owns domain validation?

> [!NOTE]
> The wizard collects the location name and zone fields in form state, and can show simple inline checks such as required names, threshold range/order, and valid schedule JSON. On submit it sends the request DTO to the API; it does not construct or persist domain entities itself.
>
> React validation is for immediate usability, not the authority. The API service passes the parsed DTO through `LocationConfigBuilder`, whose domain rules remain authoritative even if a client bypasses the wizard or sends a crafted request. The API returns a clear validation error when those rules reject the configuration.

## C. Compare, contrast, and scenarios

8. Contrast Builder with Factory Method and with Abstract Factory. Which pattern answers “which type?”, which answers “which matching kit?”, and which answers “how do we assemble one **valid whole** in steps?”

> [!NOTE]
> Factory Method answers “which type?” by allowing a creator to choose one concrete product, such as a sensor type. Abstract Factory answers “which matching kit?” by producing a compatible family of devices, such as a simulation or edge kit. Builder answers “how do we assemble one valid whole in steps?”; here that whole is a location plus its validated zones.

9. Fluent method chaining (`builder.add_zone(...).build()`) is a coding style. Why is a fluent interface **not** the same thing as the Builder pattern?

> [!NOTE]
> A fluent interface is a chaining style: methods return an object so calls can be written one after another. Builder is a construction pattern with a separate assembly object, a product assembled from required parts, and a point such as `build()` that produces the completed product after enforcing its rules. Chaining can make a builder easier to read, but chaining alone does not make an API a Builder.

10. A classmate validates thresholds only in FastAPI / Pydantic and leaves `build()` empty. Another mutates builder fields after `build()` while treating the product as immutable. Explain why each is a trap.

> [!NOTE]
> Validation only in FastAPI: Pydantic protects the HTTP boundary, but the domain can also be called from tests or another service. If `build()` does not enforce its invariants, those callers could create invalid configurations and pass them toward persistence. The builder must validate the domain rules itself.
>
> Mutating after `build()`: The built product is meant to represent the validated snapshot, not a live view of the builder's working state. Changing the builder and expecting an existing product to change (or remain safely immutable despite shared mutable values) makes behavior surprising and can undermine validation. In this implementation, the product dataclasses are frozen and zones are held in a tuple, but `schedule` is a mutable dictionary, so code should not mutate a schedule after building; deep immutability would require copying or freezing that nested value too.