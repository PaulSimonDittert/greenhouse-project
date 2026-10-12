# Phase 6 — Strategy questions

**Pattern / focus:** Strategy.

**Read first:** [Guide 06](../../materials/guides/06-strategy.md) · [Requirements](requirements.md)

## How to answer

- Use your own wording. Do not paste teaching-example types (for example shipping quotes) as if they were your greenhouse classes.
- When a question asks about *this application*, refer to irrigation (or lighting) policies, location context, and the automation API from the lab.
- Short answers are fine when the question is narrow. Write a few sentences when it asks you to explain or compare.
- Write each answer inside the matching **Your Answer** note. Replace the placeholder; leave the question text unchanged.

## A. Pattern

1. State the intent of Strategy in plain language. How does the **context** use a strategy, and why must “choose which algorithm” stay separate from “run the algorithm”?

> [!NOTE]
> Intent: Strategy enables the configuration of, for example objects, without needing to create a new one, simply by changing a specific key. A given water meassuring device can meassure the moisture level more, or less often, simply by changing a key, which then switches to a different methode. 
>Why choose and not run: There are two main reasons, first being that one huge methode with a lot of if/else statements can be avoided that way. Secondly because the context does not have to be edited, backwards compatibility and scalability are ensured. 

2. Name the participants (**strategy**, **concrete strategies**, **context**, **client**). What goes wrong when all policies live as `if/elif` inside the context (or inside an HTTP router)?

> [!NOTE]
> The strategy is `AutomationStrategy`; the concrete strategies are `ConservativeMoistureStrategy` and `AggressiveMoistureStrategy`; the context is `LocationAutomationContext`; and the client is the application service that selects a strategy and calls `decide(context)`.
>
> If the policies become `if/elif` branches in the context or router, selection and algorithm details become tangled with orchestration or HTTP handling. Adding or changing a policy then requires editing that central code, and the decision logic is harder to test independently. This would also make maintanance and backwards compatibility harder. 

3. When should you use Strategy, and when should you skip it (one algorithm only; or the variation is a **lifecycle mode** rather than a chosen policy)?

> [!NOTE]
> Use Strategy when there are multiple interchangeable policies and the application needs to select from them, for example a conservative versus aggressive data gaterhing intervall.
>Skip it when there is only one simple algorithm: an interface and multiple classes would only really bload the project.

## B. This phase of the application

4. In this lab, what does a strategy’s `decide(context)` return (action + reason)? Give a concrete difference you implemented (or were required to implement) between **conservative** and **aggressive** on the **same** moisture reading and zone thresholds.

> [!NOTE]
> `decide(context)` returns a recommendation with an action and an explanation (`reason`), not a command to operate hardware. With a low threshold of `0.25`, a high threshold of `0.45`, and moisture `0.40`, the conservative strategy returns `wait` because moisture has not fallen below the low threshold. The aggressive strategy returns `irrigate` because moisture is below the high threshold.

5. Where do the numbers in `LocationAutomationContext` (or your equivalent) come from? Latest moisture may already be in `sensor_readings` from a manual read, the simulation sampler, or MQTT translation — why does this phase not add a scheduler or a broker? Why must strategies receive a plain context object, not SQLAlchemy rows or FastAPI types? Why are thresholds read from **zones**, not hardcoded in the strategy class?

> [!NOTE]
> The application service gets each zone's low and high thresholds from the persisted zone configuration. The repository finds the latest reading from a moisture-sensor device assigned to that zone and converts its value to a plain number. If the zone has no reading, the context has no moisture value and the strategy recommends waiting.
>
> This phase uses the shared readings table; manual reads, the sampler, and translated MQTT payloads can already populate it. Adding a scheduler or broker would add a separate transport responsibility that is outside this phase.
>
> A plain context keeps domain strategies independent of persistence and web frameworks, so they can be tested directly with ordinary values. Thresholds belong to zones because they are configuration for each growing area; hardcoding them in a strategy would ignore saved settings and make policies inflexible.

6. The active `strategy_key` is **persisted** per `location_id` (for example in `automation_rules`). Why must `POST .../automation/evaluate` use the **saved** key rather than a key the client sends only in that request? What happens on the next evaluate after the operator changes strategy but moisture stays the same?

> [!NOTE]
> Evaluation should reflect the users's current, saved location policy, instead of an one-off request value that is not retained. The service loads the persisted key before choosing the strategy. After the user saves a different strategy, the next evaluation uses that key. With the same moisture and thresholds, the recommendation can therefore change. For example from conservative `wait` to aggressive `irrigate`.

7. Strategy **recommends** (irrigate / wait). It should not itself start a pump. Why keep **decide** separate from **execute**? Which later pattern is meant to carry out the action?

> [!NOTE]
> Separating decision from execution keeps the policy testable without hardware and prevents a recommendation from unexpectedly causing a physical side effect. It also allows the application to validate, log, or reject a recommendation before acting. The later Command pattern is intended to represent and carry out an action such as activating an actuator; the strategy only recommends what should happen.

## C. Compare, contrast, and scenarios

8. Contrast Strategy with **State** (Phase 8). Both delegate to an object with the same shape. Who typically **changes** the active object, and is the variation a **policy** or a **lifecycle**?

> [!NOTE]
> With Strategy, the client/user typically chooses the active policy, such as conservative or aggressive irrigation. The variation is a decision policy. 
>With State, the object or its surrounding system typically changes the active state as lifecycle events occur, such as a device moving from idle to watering or faulted; the variation represents lifecycle state.

9. Contrast Strategy with **Adapter** (Phase 5) and with **Builder** (Phase 4). Which one translates a foreign API, which one assembles a valid aggregate, and which one swaps an algorithm?

> [!NOTE]
>The Apapter translates a foreign API
>The Builder assembles a valid aggregate
>The Strategy swaps between algorithms

10. A classmate writes one “mega-strategy” that still contains `if conservative` / `if aggressive` inside a single class. Another strategy class calls the actuator adapter to water immediately. Explain why each is a trap.

> [!NOTE]
> The mega-strategy keeps the policy branches in one class, so the algorithms are not actually separated or independently replaceable.
>It recreates the conditional logic the pattern is meant to avoid. Therefore same if will be skipped while some other will be executed, even if only one was meant to be. Therefore the classmate's programm will surely often output / or recommend the wrong recommendation. 