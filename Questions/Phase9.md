# Phase 9 — Decorator questions

**Pattern / focus:** Decorator.

**Read first:** [Guide 09](../../materials/guides/09-decorator.md) · [Requirements](requirements.md)

## How to answer

- Use your own wording. Do not paste teaching-example types (for example HTTP client wrappers) as if they were your greenhouse classes.
- When a question asks about *this application*, refer to `ActuatorPort`, policy decorators, and `actuator_execution_log` from the lab.
- Short answers are fine when the question is narrow. Write a few sentences when it asks you to explain or compare.
- Write each answer inside the matching **Your Answer** note. Replace the placeholder; leave the question text unchanged.

## A. Pattern

1. State the intent of Decorator in plain language. Why is stacking wrappers a flexible alternative to a combinatorial explosion of subclasses (`LoggingRetryMaxRuntimeActuator`, …)?

> [!NOTE]
>Intent: Decorator is a structural desgin pattern. The intent of the Decorator is to alter objects at runtime to give them additional behavior. This is done by "wrapping" an object inside new object(s).
>Flexible alternative: Stackings warppers is a flexible alternative because every subclass is turned into a concrete decorator, which then add additional behaviors. This keeps the subclass count to "x", instead of "x*x" when one creates a new subclass for every subclass combination. 

2. Name the participants (**component**, **concrete component**, **decorator**, **concrete decorators**). What interface does every decorator present to the caller, and why must that match the wrapped component?

> [!NOTE]
>Component (ActuatorPort): Interface for both wrappers and wraped objects.
>Concrete Component (SimulationActuatorAdapter): The base object which then may be "wrapped and decorated".
>Decorator: Has a field to refference the "wrappee" type as Interface, which the Decorator delegates all operations to. 
>Concrete Decorators (LoggingAc.;MaxRunTimeAc.): Define extra behavior that may be added to the base objects. They override methodes od the base object and either run teir own code before, or after the excecution of the parent's code. 

>Every decorator presents the interface of the wrappee base object. It is important because then the wrapped object can both contain the base object itself, or any decorators. 

3. **Order matters.** Using logging and retry (or logging and max-run-time) as an example, explain how wrapping A around B can change what you observe compared with wrapping B around A.

> [!NOTE]
>Wrapping either A around B, or B around A will change how detailed the logging of the runtime observations will be. 

> Wrapping logging around max-run-time means `LoggingActuatorDecorator(MaxRunTimeActuatorDecorator(SimulationActuatorAdapter))`. The outer logging decorator sees both successful calls and max-run-time exceptions, so it can persist every attempt. If the actuator has been running for at least 30 minutes, max-run-time prevents the simulation adapter from being called, and logging records `success=false` with policies `maxRunTime` and `logging`.
>
> Reversing the order to `MaxRunTimeActuatorDecorator(LoggingActuatorDecorator(SimulationActuatorAdapter))` changes that observation: a blocked call throws in the outer max-run-time decorator before reaching logging, so no execution row is recorded for it.

## B. This phase of the application

4. What is `ActuatorPort` here, and which **at least two** decorators did you stack around the real adapter (for example logging and max run-time)? Where is the chain wired (composition root / factory), and why not inside the HTTP router?

> [!NOTE]
>`ActuatorPort` is the shared interface / the component. 
>`LoggingActuatorDecorator` and `MaxRunTimeActuatorDecorator` can be wrapped around the component. The chain is logging → max run-time → `SimulationActuatorAdapter`, wired in `ActuatorExecutionService`.
>Keeping it there means the router handles HTTP, while the service owns how actuator behavior is composed. This preserves the initial layering of the project. 

5. Max run-time can **short-circuit**: the inner adapter is never called. Why must a blocked attempt still produce a row in `actuator_execution_log` with `success=false` and the policy named in `policy_applied`?

> [!NOTE]
>Why: A blocked command is still an attempt worth recording. The row makes it visible in the dashboard and shows why it was blocked; success=false and policy_applied identify the outcome and the policy responsible.

6. How does max run-time know the actuator has been running too long (for example `actuator_states.updated_at` from Phase 8)? Why is that data from **State**, not something the decorator should invent as a second lifecycle?

> [!NOTE]
>How: It checks whether the saved state is `running` and whether `updated_at` is at least 30 minutes old.
>
>Why: Because `actuator_states` is the source of truth for the actuator’s current state and when it changed, the decorator can use state and `updated_at` to decide whether the actuator has been running for 30 minutes. If the decorator tracked its own timer, it could get out of sync with the persisted state and create a second, conflicting lifecycle.

7. `GET /api/actuators/executions` feeds the dashboard execution log. Why persist attempts in the database instead of only printing to stdout? What should the UI show after a blocked attempt and a refresh?

> [!NOTE]
>Why: Database records persist and can be retrieved by the API after a page refresh. Output printed to stdout is temporary and is not available to the dashboard.

>What: After a blocked attempt and refresh, the UI should show a failed execution row with the message `Max run time exceeded` and policies `maxRunTime` and `logging`.

## C. Compare, contrast, and scenarios

8. Contrast Decorator with **Adapter**. Both wrap. One **keeps** the interface and **adds** behaviour; the other **changes** the interface and **translates**. Which is which in this greenhouse (Phase 9 vs Phase 5)?

> [!NOTE]
>Decorator adds behavior without changing the port; Adapter translates an incompatible implementation so it fits the port.

>In Phase 9, the decorators keep the same `ActuatorPort.apply(device_id, command, payload)` interface and add behavior around the wrapped actuator. For example, logging records the attempt and max run-time can block it before it reaches `SimulationActuatorAdapter`, so callers still use the actuator in the same way.
>
>An Adapter solves a different problem: it translates one interface or data format into the one the application expects. In Phase 5, sensor adapters such as `VendorStubSensorAdapter` convert vendor-shaped payloads and units into the common `Reading` format used by the app.

9. Contrast Decorator with **inheritance** of combined policies. How does composition let you add or remove a policy without a new subclass for every combination?

> [!NOTE]
>Inheritance makes policies part of the class hierarchy, so every new policy combination becomes a new subclass (for example `LoggingRetryMaxRuntimeActuator`, `LoggingMaxRuntimeActuator`, and so on). That is rigid and duplicates behavior across many classes.
>
>With Decorator, each policy is its own wrapper that implements the same `ActuatorPort` and delegates to the inner actuator. The application composes the chain at runtime, such as `LoggingActuatorDecorator(MaxRunTimeActuatorDecorator(SimulationActuatorAdapter))`. To add a policy, wrap another decorator around the port; to remove one, stop composing it. The same base actuator can be reused with different policy stacks without creating a subclass for every combination.

10. A classmate’s decorator changes the method signature “a little” (extra required argument, different return type). Another ignores wrap order and cannot explain whether logging runs once per logical call or per inner attempt. Explain why each is a trap.

> [!NOTE]
>The first trap is a broken contract. A decorator must preserve the same `ActuatorPort.apply(device_id, command, payload)` signature and behavior as the wrapped component. If it adds a required argument or returns a different type, the caller can no longer treat the decorator and the real actuator as interchangeable, and the entire stack stops being composable. In a decorator, the wrapper must be substitutable for the wrapped object, not “almost” the same.
>
>The second trap is a logic trap about sequencing. Decorator order determines what runs before or after what. If logging is the outer wrapper, it records one logical call around the whole operation. If logging is inside a retry or max-run-time wrapper, it may run once per inner attempt, per retry, or not at all depending on the exception path. Because the stack is nested, order changes both observable behavior and business meaning, so without a clear wrapper order you cannot explain whether the log represents a single user action or multiple internal attempts.