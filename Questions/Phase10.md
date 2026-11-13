# Phase 10 — Command questions

**Pattern / focus:** Command.

**Read first:** [Guide 10](../../materials/guides/10-command.md) · [Requirements](requirements.md)

## How to answer

- Use your own wording. Do not paste teaching-example types (for example editor undo commands) as if they were your greenhouse classes.
- When a question asks about _this application_, refer to command objects, the invoker, `command_log`, and the controls UI from the lab.
- Short answers are fine when the question is narrow. Write a few sentences when it asks you to explain or compare.
- Write each answer inside the matching **Your Answer** note. Replace the placeholder; leave the question text unchanged.

## A. Pattern

1. State the intent of Command in plain language. What does it mean to **objectify a request**, and what can you do with that object that you cannot do with a bare `actuator.start()` call (queue, audit, undo, history)?

> [!NOTE]
>Intent: Command packages an action as an object, separating the request from its execution.
>
>Objectify: Represent a request such as `actuator.start()` as a command object containing its type, device, and payload.
>
>What it enables: The object can be queued, audited in `command_log`, or tracked for history; undo requires explicit support and capturing prior state.

2. Name the participants (**command**, **receiver**, **invoker**, **client**). Who creates the command, who triggers `execute()`, and who actually changes actuator/hardware state?

> [!NOTE]
>Command: `StartPumpCommand`, `StopPumpCommand`, and `SetLightLevelCommand` represent requests.

>Receiver: The actuator port and its adapter carry out the operation.

>Invoker: `CommandInvoker` calls `execute()`.

>Client: The HTTP handler passes the request to the application command service, which creates the command through the registry.
>
>The adapter communicates with the hardware, which changes state.

3. If a command supports undo, when must it capture the data needed to reverse the action? Why is “capture **before** mutate” critical?

> [!NOTE]
>When: Capture the current state immediately before changing it.
>
>Why: Mutation can overwrite the original values; capturing first preserves what undo must restore.

## B. This phase of the application

4. Which command types did you implement (for example `start_pump`, `stop_pump`, `set_light_level`)? Why does the HTTP handler create a command and pass it to an **invoker** (or application service) instead of calling the actuator adapter from the router?

> [!NOTE]
>Which: I implemented `start_pump`, `stop_pump`, and `set_light_level`.
>
>Why: The service creates the command and runs it through the invoker, keeping routing separate and preserving state guards, decorators, and `command_log`; direct adapter calls could bypass them.

5. Walk through the execute path: (1) consult State / `allowed_commands`, (2) if illegal → **rejected**, (3) if legal → decorated `apply`, update `actuator_states`, log **success** or **failed**. Why must a rejected command **not** change actuator state and **not** reach inner `apply`?

> [!NOTE]
>Walk through: The service checks State's `allowed_commands`. Illegal requests are logged `rejected` and stop. Legal requests execute through the decorated port; success updates `actuator_states` when needed and logs `success`, while execution errors log `failed` without a state update.
>
>Why: Rejecting before `apply` prevents illegal hardware side effects and keeps state accurate while preserving the rejection in `command_log`.

6. Distinguish **`rejected`** vs **`failed`** vs **`success`** in `command_log`. Give one greenhouse example of each. Why is “illegal in this state” not the same as “policy or adapter error after the command was accepted”?

> [!NOTE]
>Distinguish: `rejected`: stopping an idle pump is disallowed by State. `failed`: an accepted pump operation exceeds the decorator's run-time policy. `success`: an idle pump starts successfully.
>
>Why: Rejection occurs before execution because the state disallows the request; failure occurs after acceptance when policy or adapter execution errors.

7. Why is `command_log` a **different** table from Phase 9 `actuator_execution_log`? What concern does each log record (operator intent vs policy/adapter attempt)?

> [!NOTE]
>Why: They record different stages; a rejected request has no actuator execution attempt.
>
>What: `command_log` records operator intent, payload, and outcome (`success`, `failed`, or `rejected`). Phase 9's `actuator_execution_log` records decorated-port attempts and applied policies.

## C. Compare, contrast, and scenarios

8. Contrast Command with **Strategy**. Strategy is an interchangeable **algorithm** (decide / quote). Command is a **side-effectful request** with history. How do they cooperate in this app (Phase 6 recommends; Phase 10 executes)?

> [!NOTE]
>Contrast: Strategy is an interchangeable algorithm that recommends an action; Command is a specific side-effectful request with a recorded outcome.
>
>How: Phase 6 recommends from sensor and zone context; Phase 10 executes the action as a command through the invoker and guarded, decorated port.

9. Contrast Command with **State**. Who **triggers** the action, and who **decides whether it is legal**? Why must commands not bypass state guards?

> [!NOTE]
>Contrast: The command represents the action; the invoker calls `execute()`. State (`ActuatorContext`) decides legality and validates transitions.
>
>Why: Guards prevent illegal hardware changes and inaccurate state; rejected requests are logged without execution.

10. The controls UI should disable actions that are not in `allowed_commands`. Why must the **backend** still reject illegal commands even if the UI is correct? What happens if a classmate’s command calls the raw adapter and skips State and Decorator?

> [!NOTE]
>Why: The UI can be stale or bypassed, so the backend must enforce `allowed_commands` for every request.
>
>What: A raw adapter call bypasses State and Decorator, potentially allowing an illegal hardware action and skipping policy enforcement and execution logging.