# Phase 8 — State questions

**Pattern / focus:** State.

**Read first:** [Guide 08](../../materials/guides/08-state.md) · [Requirements](requirements.md)

## How to answer

- Use your own wording. Do not paste teaching-example types (for example support-ticket states) as if they were your greenhouse classes.
- When a question asks about *this application*, refer to actuator lifecycle, persisted state, and `allowed_commands` from the lab.
- Short answers are fine when the question is narrow. Write a few sentences when it asks you to explain or compare.
- Write each answer inside the matching **Your Answer** note. Replace the placeholder; leave the question text unchanged.

## A. Pattern

1. State the intent of the State pattern in plain language. What problem appears when lifecycle is modelled as boolean flags and scattered `if` guards?

> [!NOTE]
>The State pattern is solving the pain of the "Finite-State Mashine", which basically describes when a lifecycle is modelled as boolean flags and scattered 'if' guards. The main object becomes the context, which stores a refference to a State, which in turn holds all the relevant code for that state. This way, giant if/elif and boolean codeblocks can be avoided. 
>
>Propably the biggest problem that occurs is maintainability and scalability, which become basically impossible, espacially if multiple objects can have states that influence each other. It also makes the code hard to read and unwanted behavior can easily be implemented. 


2. Name the participants (**context**, **state interface**, **concrete states**, **client**). How does a successful command lead to a **transition**, and where do **guards** live?

> [!NOTE]
>Context: `ActuatorContext` — it holds the current actuator state and exposes the transition behavior.
>State interface: the shared domain contract for state behavior, mainly `transition(...)`, `allowed_commands`, and the underlying rules like `can_transition(...)` / `get_allowed_commands(...)`.
>Concrete states: the valid actuator states, which in this app are `off`, `idle`, `running`, `error`, and `maintenance`.
>Client: the service or API layer that asks the context to change state, like the actuator service or route.
>
>How does a successful command lead to a transition: the client asks the context to move from the current state to the requested target. The context checks the current state against the legal edges, and only if it is allowed does it update the state.
>
>Where do guards live: in the domain transition table/rules. In this project they live in the state logic (`ALLOWED_TRANSITIONS` and `can_transition`), so illegal moves are rejected before anything is saved.


3. What is `allowed_commands` (or equivalent) for? Why is exposing “what can I do **now**?” better than letting the UI guess from a raw state string?

> [!NOTE]
>allowed_commands: is the list of legal actions for the current actuator state. For example, `idle` allows `start_pump`, `running` allows `stop_pump`, and `error` allows `reset`. It is basically the answer to “what can I do right now?”
>
>It is better than letting the UI guess from a raw state string because the UI should not be the place where business rules live. If React decides what is allowed, the rules get duplicated, drift, and can disagree with the backend. Exposing `allowed_commands` makes the API tell the UI the truth.


## B. This phase of the application

4. Which actuator states did you implement (for example idle, running, error)? Sketch the **legal** transitions (which command or event moves idle → running, running → idle, into error, and out of error).

> [!NOTE]
>The project implements these states: `off`, `idle`, `running`, `error`, and `maintenance`.
>
>The legal transitions are:
> - `off -> idle`
> - `idle -> running`
> - `idle -> maintenance`
> - `idle -> error`
> - `running -> idle`
> - `running -> error`
> - `error -> idle`
> - `error -> off`
> - `maintenance -> idle`
> - `maintenance -> error`

5. Why is actuator state stored in `actuator_states` (or equivalent) rather than only in process memory? What must still be true after you restart the backend?

> [!NOTE]
>Why: If the state lives only in process memory, it disappears as soon as the backend restarts. That means the app would forget whether an actuator was running, in error, or idle. The whole point of this phase is that the lifecycle is persisted.
>
>After restart, the backend must still be able to load the stored state from `actuator_states` and know the actuator’s current lifecycle. The correct state must still be visible from the API and the UI, and the legal transitions must still be enforced from the domain rules.


6. An **illegal** transition must raise a domain error and **must not** update the database. Why? Which HTTP status is reasonable for that case (400 or 409), and why should the rule live in the domain rather than in React?

> [!NOTE]
>Why: An illegal transition must raise a domain error and must not update the database because the state machine is a business rule. If the app lets an invalid move through, the actuator can end up in a state that the system says is impossible, and the database becomes inconsistent.
>
>Which: `409 Conflict` is a good HTTP status here because the request conflicts with the actuator’s current lifecycle state. `400 Bad Request` would imply that the request which has been made was in some way or form faulty. The context/hint of having an illeagle transition could be easily lost.
>
>Why: The rule should live in the domain rather than in React because React is only the UI. The browser can be bypassed, the logic can be duplicated, and the rule can drift from the real backend behavior. The domain owns the actual invariant: only legal transitions are allowed, and the DB is written only after that check succeeds.


7. Device JSON gains `state` and `allowed_commands`. How does the dashboard use those fields (badges, disable illegal buttons)? How does this prepare **Phase 10 Command**?

> [!NOTE]
>The dashboard reads those fields and shows an actuator badge like `idle`, `running`, or `error`, with a color and a hover tooltip listing the allowed commands.
>
>This sets up Phase 10 Command because the command layer can use the same contract: it checks the current actuator state and compares it to `allowed_commands` before executing. The UI and the command system will share the same domain truth instead of each building their own guess.


## C. Compare, contrast, and scenarios

8. Contrast State with **Strategy**. Both look like “context delegates to an object.” Who typically **changes** the active object, and is the variation a **lifecycle** or a **selectable policy**? Give a greenhouse example of each (this phase vs Phase 6).

> [!NOTE]
>Who: In State, the active object changes because the object itself moves through its lifecycle. In Strategy, the active object changes because the system chooses a policy to use.
>
>The variation: State is a lifecycle; Strategy is a selectable policy.
>
>Example of each: in this phase, the actuator changes state as it goes from `idle` to `running` to `error` and back to `idle`. That is State. In Phase 6, the location chooses a watering strategy, and the automation engine follows that selected strategy. That is Strategy.


9. Contrast State with a pile of booleans (`is_running`, `is_fault`, `is_maintenance`). Why do illegal combinations of flags appear, and how do explicit state objects (or a transition table) prevent that?

> [!NOTE]
>Why: illegal combinations appear because each boolean is independent. The code can set `is_running = true` and `is_fault = true` at the same time, or leave the actuator marked as running while maintenance is also true. There is no single source of truth, so every `if` check has to manually enforce the rules.
>
>How: explicit state objects or a transition table prevent that by representing one valid state at a time instead of many independent flags. The system only accepts values from the allowed set, and every move must pass the domain’s transition check before it is stored. That keeps the actuator in one legal lifecycle state instead of letting impossible flag combinations exist.


10. A classmate puts HTTP status mapping or SQLAlchemy commits **inside** a concrete state class. Another state mutates a flag directly and skips `transition` / `set_state`. Explain why each is a trap.

> [!NOTE]
>Trap 1: Putting HTTP status mapping or SQLAlchemy commits inside a concrete state class is a trap because it mixes layers. The state class should describe valid lifecycle behavior in the domain, not know about FastAPI response codes or database commits. Once it starts doing API or persistence work, the domain stops being a clean business rule and becomes harder to test, reuse, and reason about.
>
>Trap 2: Mutating a flag directly and skipping `transition` / `set_state` is a trap because it bypasses the guard. The app can set an illegal state without checking whether the transition is allowed, so the invariant breaks and the database can store impossible combinations. The safe flow is always: validate in the domain, then persist through the service/repository.
