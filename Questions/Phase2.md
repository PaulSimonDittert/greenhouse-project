# Phase 2 — Factory Method questions

**Pattern / focus:** Factory Method.

**Read first:** [Guide 02](../../materials/guides/02-factory-method.md) · [Requirements](requirements.md)

## How to answer

- Use your own wording. Do not paste teaching-example types (for example courier notifiers) as if they were your greenhouse classes.
- When a question asks about *this application*, refer to sensors, creators, the `devices` table, and the sensors API from the lab.
- Short answers are fine when the question is narrow. Write a few sentences when it asks you to explain or compare.
- Write each answer inside the matching **Your Answer** note. Replace the placeholder; leave the question text unchanged.

## A. Pattern

1. State the intent of Factory Method in plain language. What problem appears when callers scatter `new` / constructors (or a growing `if type == ...`) across the application?

> [!NOTE]
> ***Your Answer***
>
> The intent of the Factory Method is to define a standrard interface for creating objects. However the objects's subclasses can decide what data and/or configuration to create the object with. For example having one sensor creator that can create a light or moisture sensor. Having an ever growing number of new constructors or growing if-else structures, makes implementing new constructors very painful. For example the correct constructor must first be found and then altered in the Applications and API layers. This causes thight coupling and decreaes maintainability of the project. 

2. Name the main participants of Factory Method (**product**, **concrete product**, **creator**, **concrete creator**, **client**). For each, give one sentence: what it is responsible for.

> [!NOTE]
> ***Your Answer***
>
> Product: The object being reated, for example "sensor"
> Concrete Product: The variation of the object, for example light/moisture
> Creator: The interfaces that declares the create_sensor methode
> Concrete Creator: The class that implements the creation logic and sets the defaults
> Client: The service that gets the sensor without needing to know how that object was build

3. How do you add a **new product variant** when creators are polymorphic (new class + registry entry) versus when creation lives in one shared `if/elif` function? Why does that difference matter for extension?

> [!NOTE]
> ***Your Answer***
>
> When Polymorphic, you can leave the old code as is and write a new creator class and add one more line to the registry. 
> When if/elif, you have to alter and change existing code to implement the new product variant
> Why is that relevant? Because polymoprhism makes the system safer because no existing code must be changed, so no logic could be broken. Polymorphism follows the Open/Closed Principle, which basically means it is easily extendible but closed to modifications.

## B. This phase of the application

4. In this lab, what is the **product** and what are the **concrete creators**? Why must the API handler (or sensor service) go through a creator/registry instead of constructing `MoistureSensor` / `LightSensor` itself?

> [!NOTE]
> ***Your Answer***
>
> The Product is the Sensor dataclass entity
> The Concrete Creatos are the MoistureSensor - and LightSensorCreator
> The API must go through a registry because the API layer should not know what a MoistureSensor is or know its default config. It only needs to pass a string. 

5. `POST /api/sensors` accepts a short `type` key such as `"moisture"` or `"light"`, while the stored/returned field is `device_type` (for example `moisture_sensor`). Why are those two fields different? Who decides the stored `device_type` and `default_config`?

> [!NOTE]
> ***Your Answer***
>
> The two fields are different because device_type is the strict, internal system identifier saved in the database and type is a short and user-friendly API input
> The specific Concrete Creator decides the default_config and device_type

6. Why is there a single `devices` table with `role="sensor"` instead of a dedicated `sensors` table? What later phase does that choice prepare for?

> [!NOTE]
> ***Your Answer***
>
> There is only a single devices table because future hardware and sensors will share the exact same stabase columns 
> This prepares the project for Phase 3, which will introduce actuators

7. What should happen when the client posts an **unknown** `type`? Where should that rejection be decided (registry/service vs router constructing a concrete class anyway)?

> [!NOTE]
> ***Your Answer***
>
> First of all must the API return an HTTP 400 Bad Request error and second of all should that decission be made in the domain registry. The get_creator decides the type is invalid and raises a ValueError

## C. Compare, contrast, and scenarios

8. Contrast Factory Method with a **simple factory** (one function full of `if type == ...`). When is the simple factory “good enough,” and why does this phase still want polymorphic creators?

> [!NOTE]
> ***Your Answer***
>
> The simple factory is one if/elif block, which is "good enough" in smaller projects where the type of objects do not change that much. 
> The reason we still implement the polymorphic creators is because there are still a lot of Phases ahead of us, therefore making the project futureproof. We know that the project will be heavily expanded uppon, and we therefore prepare for that. 

9. Contrast Factory Method with **Abstract Factory** (Phase 3). Factory Method answers which question? Abstract Factory answers which different question? Why is Factory Method enough for Phase 2 sensors?

> [!NOTE]
> ***Your Answer***
>
> The Factory Methode answers the question of "How do I create one specific product?", while the Absstract Factory answers the questions of "How do I create a family of related products?(different sensors)"
> The Factory Method is enough for Phase 2 because we are currently only creating isolated and individual sensors and no "bigger" families/groups.

10. A classmate puts SQLAlchemy session commits (or FastAPI request parsing) **inside** a concrete creator. Why is that a trap? Where should persistence and HTTP stay instead?

> [!NOTE]
> ***Your Answer***
>
> That is a trap because it destroys the seperation of ours layors. It woudl destroy the testing, because a DB connection would be required for it at all times. 
> Persistance belongs inside the infrastructure layer and HTTP parsing belongs inside the API layer.