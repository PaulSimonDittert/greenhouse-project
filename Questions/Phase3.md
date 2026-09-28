# Phase 3 — Abstract Factory questions

**Pattern / focus:** Abstract Factory.

**Read first:** [Guide 03](../../materials/guides/03-abstract-factory.md) · [Requirements](requirements.md)

## How to answer

- Use your own wording. Do not paste teaching-example types (for example warrior/mage class kits) as if they were your greenhouse classes.
- When a question asks about *this application*, refer to device families, provision, and the unified devices API from the lab.
- Short answers are fine when the question is narrow. Write a few sentences when it asks you to explain or compare.
- Write each answer inside the matching **Your Answer** note. Replace the placeholder; leave the question text unchanged.

## A. Pattern

1. State the intent of Abstract Factory in plain language. What goes wrong when related products are chosen independently (`if format` for each piece) instead of as a **family**?

> [!NOTE]
> Intent of the Abstract Factory: Without specifying concrete classes, the Abstract Factory can create an entire family of dependent/related Objects.
> What goes wrong: Unrelated Objects might get mixed up together. For example, an "edge" physical water pump might be paired with a "simmulation" virtual sensor which can not work together. 


2. Name the main participants (**abstract factory**, **concrete factory**, **abstract products**, **concrete products**, **client**). How does choosing a factory at the start **commit** the client to one family?

> [!NOTE]
> Participants: Abstract Factory = DeviceFamilyFactory; Concrete Factory = SimulationDeviceFactory; Abstract Products = Device; Concrete Products = Simulated Pump, Edge Pump; Client = DeviceFamilyService;
> Commitement: Calling the factory at the beginning with "edge" param, locks the client. Afterwards when the client asks for a device, an "edge" compatible device is guranteed.

3. When should you use Abstract Factory, and when should you skip it (for example only one product type per request, or mixing siblings is valid)?

> [!NOTE]
> When it makes sense to use it: When a system is configured to work with multiple families of products, and these products in turn must also work together wiith one another to form, for example, specific pairs.
> When it should rather be skiped: When the system can mix unrelated objects with one antoher, without causing issues. As well as when the system only creates objects one at a tim.

## B. This phase of the application

4. In this lab, what is a **device family**, and what does `create_device_set()` (or your equivalent) return? Why must a simulation kit and an edge kit not mix incompatible siblings?

> [!NOTE]
> What is a device family: A matching "kit" of sensors and actuators built specifically for one envionment. 
> create_device_set() returns: A list of Device domain entities.
> Why they must not mix: If they would be mixed up, it will either fail to trigger or crash the App, because they have completely incompatible hardware interfaces. 

5. Phase 2 Factory Method creators still exist. How does Abstract Factory **compose** them rather than replace them? What would you lose if you deleted the sensor creators and inlined all construction inside the family factory?

> [!NOTE]
> Hows it composes: The SimulationDeviceFactory literally calls the Phase 2 MoistureSensorCreator to build the base sensor, then tags it with the "simulation" family name.
> What would be lost: If you deleted the Phase 2 creators and inlined everything, the code reuse would be completely lost. Any time the base default config for a moisture sensor changes, you would have to update it in multiple different family factories instead of just one place.

6. Why add a `device_family` column on the existing `devices` table (with a default/backfill such as `"simulation"`) instead of a new table per family? What happens to Phase 2 sensor rows if you forget the backfill?

> [!NOTE]
> Why a new column: Because simulation and edge devices use the exact same columns. A new table would make querying the DB more difficult and more inefficient. 
> Forgetting the backfill: Forgetting to backfill old sensors would result in a NULL column, which could crash the DB and/or break frontend filters.

7. `POST /api/devices/provision` returns a kit (expected size: two sensors and two actuators). `GET /api/devices` can filter by `family` and `role`. Why must the UI be able to filter by family? Why do `/api/sensors` routes from Phase 2 still need to work?

> [!NOTE]
> Why must the UI filter: The user needs to view only the environment they are currently testing. Seeing virtual sensors mixed with physical edge hardware on the dashboard would be confusing and useless.
> Why old routers still need to work: For single-device creation and backwards copatibility. 

## C. Compare, contrast, and scenarios

8. Draw the contrast in one paragraph: Factory Method vs Abstract Factory. Use the questions “which **one** product?” versus “which product **line**?” and mention that Abstract Factory often **uses** Factory Method–style methods inside.

> [!NOTE]
> Factory Method answers the question “which one product?” by providing a way to create a single specific item (like a moisture sensor) while letting subclasses figure out its exact setup. In contrast, Abstract Factory answers the question “which product line?” by managing the creation of a whole family of related items (like a matching simulation kit of sensors and actuators) to make sure they all work perfectly together. Because an abstract factory needs to put together multiple separate pieces to finish that product line, it often uses Factory Method-style steps behind the scenes to actually build each specific part of the kit.

9. A DTO or HTTP handler constructs concrete simulation/edge device types directly, bypassing the family factory. What consistency bug can that reintroduce? How should HTTP stay on the abstract factory / service instead?

> [!NOTE]
> Possible consistency bug: A developer could accidentally write an HTTP endpoint that provisions a "simulation" sensor but an "edge" actuator at the same time, completely destroying the family consistency the pattern was meant to protect.
> Potential Fix: The HTTP layer should stay simple and ignorant. It should only pass the string "edge" to the Application Service. The service then uses the Abstract Factory, which safely handles the complex creation logic.

10. Someone proposes a single “god factory” that creates locations, readings, and devices “because we already have a factory.” Why is that a misuse of Abstract Factory?

> [!NOTE]
> Misuse: Abstract Factory is designed to group products that belong to the same family and must interact with each other (like matching hardware). Locations, telemetry readings, and devices are completely separate domain concepts with different lifecycles, not interchangeable parts of a hardware family. A "god factory" just becomes a bloated mess of unrelated code.