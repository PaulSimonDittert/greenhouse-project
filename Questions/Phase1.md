# Phase 1 — Skeleton questions

**Pattern / focus:** Course intro and an empty-but-running three-tier skeleton (no GoF pattern this phase).

**Read first:** [Guide 01](../../materials/guides/01-course-patterns-and-skeleton.md) · [Requirements](requirements.md)

## How to answer

- Use your own wording. Do not paste textbook definitions or teaching-example class names as if they were your greenhouse types.
- When a question asks about *this application*, refer to what you built (or what the lab required): layers, routes, and tooling.
- Short answers are fine when the question is narrow. Write a few sentences when it asks you to explain or compare.
- Write each answer inside the matching **Your Answer** note. Replace the placeholder; leave the question text unchanged.

## A. Pattern

1. In your own words, what is a design pattern? What is it *not*?

> [!NOTE]
>A design pattern describes a reusable approach to a typical object-oriented design problem. These approaches, for example, include specific ways to structure classes and code and can therefore not simply be installed and added to a project like a library. The Architect must implement them by hand.

2. Name the three GoF pattern families. For each family, give one-sentence: what kind of design problem it addresses. Then place **Factory Method** and **Strategy** into the correct family.

> [!NOTE]
>The three GoF (Gang of Four) families include:
>Creational, Structural and Behavioral.
>
>Creational: Creational patterns describe how, where and when Objects should be created, to simplify and manage processes.
>This family includes the Factory Method pattern.
>
>Structural: Structural patterns describe how Objects should be establishing relations to one another.
>
>Behavioral: Behavioral patterns describe how communication between Objects should be handled. Communication in a sense that this pattern describes the way entities interact and distribute responsibilities in a system.
>This family includes the Strategy pattern.

3. A teammate wants to add a pattern “because it is on the course list,” even though the feature is small and unlikely to grow. When should you **skip** a pattern? What risk do you take if you apply one too early?

> [!NOTE]
>Implementing a pattern should be skipped when YAGNI applies (The feature is small and unlikely to grow), or when patterns are applied by “name” (“it simply fits”) rather than actual “pain” (need), or when a plain function or data structure can take care of the problem in less complexity.
>
>Some of the risks of applying a pattern too early are:
>Patterns also come with tradeoffs, for example structure which will have >unforeseen cost and influence on an incubation project: unwanted >complexity.
>
>Patterns may be implemented on a guested basis; this can lead to wrong >abstraction.
>
>Patterns may also be implemented with little to no effects for the >project: Wasted time and effort.

## B. This phase of the application

4. Why does Phase 1 ship a vertical slice that does almost no greenhouse business logic? What does “empty but running” prove that a folder of unimplemented classes would not?

> [!NOTE]
>The vertical slice proves that the plumbing/pipeline actually works. By having an “empty but running system” one can verify that the CORS, Database, Environment, Docker and frontend-to-backend actually functions, way before writing any code that would end up wasted. A folder of unimplemented classes only proves that the project can compile and therefore hides setup and deployment failures.

5. List the four backend layer packages used in this course (`domain`, `application`, `infrastructure`, `interfaces/api`). For each, state what belongs there and give one example of something that must **not** live in `domain`.

> [!NOTE]
>Domain: core business entities and rules. MUST not live here: DB queries, FastAPI HTTP, SQLAlchemy
>
>Application: use cases and orchestration
>
>Infrastructure: external, like db connections
>
>Interfaces: routing, controllers and HTTP endpoints

6. What does `GET /health` return, and why does it check the database instead of only reporting that the HTTP process is up? Why is API documentation served at `/scalar`, and why is `/docs` disabled?

> [!NOTE]
>GET /health returns: "status": "ok", "db": "ok"} (or "degraded" and "fail" if down)
>
>Why we check the database: because an HTTP only check could falsely >report healthy, even though it cannot read/write on the db, because only >the HTTP response is checked.
>Course requires modern Scalar UI
>Disabling the /docs forces a single, intentional “source of truth” for the API

7. Phase 1 requires Alembic (or equivalent) with a **baseline** migration and **no** business tables such as `devices`. Why introduce the migration toolchain before any product schema? What would go wrong if you created tables by hand in Postgres and only added migrations later?

> [!NOTE]
>Introducing with a baseline secures that the db shema is version controlled, as well as making the db reproducible. Creating tables by hand could cause desync of local db instances, which would become even more important when working with teammates. The biggest reason though is that trying to add Alembic later after creating tables manually causes conflicts, because Alembic would not know the history of the db. 

## C. Compare, contrast, and scenarios

8. Explain **dependency direction** in this skeleton: which layers may import which? Why must domain code not import FastAPI, SQLAlchemy, or Pydantic models used as HTTP schemas?

> [!NOTE]
>The dependencies direction is always pointing inwards. The API and Infrastructure layer can be imported from the Application and Domain layers. The Application layer can only import from the Domain layer, and the Domain layer itself cannot import from any other layer.
>
>Keeping the Domain layer isolated helps with ensuring business logic remains easy to test, stay reusable and immune to breaking if later for some reason the db and/or API might change.

9. The frontend cannot show a healthy badge. A classmate blames “the patterns.” What should you check first (stack, CORS/proxy, health JSON), and why is that a Phase 1 concern rather than a later pattern concern?

> [!NOTE]
>I would check whether the backend is running on the correct ports and making sure that GET /health returns the correct JSON shape.
>
>Blaming a pattern is insensible because no business logic or any pattern has even been implemented yet.  It is therefore a Phase 1 Infrastructure and plumbing/pipeline failure.

10. Course completion is at **Phase 12**, not Phase 1. What is still missing after a successful skeleton, and how do later phases add behaviour without rewriting the foundations you laid here?

> [!NOTE]
>Still missing business logic, db tables and entries, use cases for the Application and any pattern must be implemented yet.
>
>Since we have constructed a solid skeleton, new behavior (code) can be easily added. From now on the skeleton will never change, therefore the application can safely grow.