# Testing

How the system is tested: which kind of test each part admits, where a test is placed, and how one is written. Each ring admits one kind of test, so a test's tier follows from the ring its subject lives in (architecture.md, section 2). Tests mirror the app: `tests/modules/<module>/<part>/`, `tests/{{entry}}/`, `tests/architecture/`.

## Index

- [[#1. Tiers]]
- [[#2. Running]]
- [[#3. Placement]]
{{tier_index:3}}
- [[#4. Examples]]
- [[#5. Files]]
  - [[#5.1 One file per]]
  - [[#5.2 Scenarios]]
- [[#6. Fakes and mocks]]
- [[#7. Data]]
- [[#8. How a test is written]]
  - [[#8.1 Where helpers live]]
  - [[#8.2 How tests are named]]
  - [[#8.3 What a conftest.py may hold]]
  - [[#8.4 How a fake stays honest]]
- [[#9. Guards]]

## 1. Tiers

{{tiers}}

{{untested}}

> [!NOTE]
> `application/logic/` sits in the application ring but holds pure functions with no port, so it is unit-tested.

## 2. Running

One command runs every tier. It appears here and nowhere else.

- unit, integration, rendering, guard: `<command>`

## 3. Placement

Which ring does the subject live in? That is the tier. When it is not obvious, run the litmus tests in the order of the table in section 1. The first one it passes is where the test goes.

{{tier_litmus:3}}

## 4. Examples

One module, `documents`, with a use case `publish` (architecture.md, section 8). Each tier has one test here, holding only what its row allows.

{{tier_examples}}

## 5. Files

### 5.1 One file per

{{tier_files}}

### 5.2 Scenarios

Scenarios belong to the integration tier only. There a test is one path through one use case, which is what a scenario names. A unit test proves a rule or a translation, and neither has a Given.

An integration file opens with its scenarios, one per `Result` variant of the use case in `contract/`. A scenario's name is its test's name, so the header and the tests cannot drift apart. A variant with no scenario is an untested path, and a scenario with no variant is a missing `Result`.

```python
"""Use case: publish a document.

Scenario: a document with a title is published
  Given a document with a title   When it is published   Then the Result is Published
Scenario: a document that does not exist is missing
  Given no such document          When it is published   Then the Result is Missing
Scenario: a document without a title is rejected
  Given a document with no title  When it is published   Then the Result is Rejected("The document needs a title.")
"""

def test_a_document_with_a_title_is_published(): ...
def test_a_document_that_does_not_exist_is_missing(): ...
def test_a_document_without_a_title_is_rejected(): ...
```

## 6. Fakes and mocks

A port is faked or mocked by what the use case does with it.

| The use case | Port kind | Stand-in | Example |
|---|---|---|---|
| reads back what it wrote | stateful | a fake: an in-memory implementation in `tests/fakes/`, one per port | a repo, a clock, a blob store |
| only fires and never reads | fire-only | a mock asserting the call and its payload, since the call is the contract | send an email, publish an event |

> [!TIP]
> **Litmus test.** Does the use case ever read back through this port what it or anything else wrote, or branch on its answer? If yes, fake it: a mock would script the answer, and the test would prove only what it was told. If the use case only calls it and never looks at it again, mock it: the call is the outcome, and a fake would be ceremony. If a port does both, split the port: one that is written and read is not the same need as one that only fires.

A fake is a working implementation of the port that keeps its state in memory, not a recording of calls.

```python
class DocumentRepo(Protocol):                       # the port, in application/ports/
    def get(self, id: DocumentId) -> Document | None: ...
    def save(self, doc: Document) -> None: ...

class DbDocumentRepo:                              # the adapter, in adapters/: talks to the database
    ...

class FakeDocumentRepo:                             # the fake, in tests/fakes/: a dict standing in for the table
    def __init__(self): self.docs = {}
    def get(self, id): return self.docs.get(id)
    def save(self, doc): self.docs[doc.id] = doc
```

The fakes are shared by every integration test. A fake is not an adapter, and a mock is not a fake.

## 7. Data

A test builds the state it needs, so the reader sees all of it. No tier runs a shared seed.

{{tier_data}}

> [!NOTE]
> The seed is product code. It lives in `bootstrap/`, the only part that sees every module, and the demo environment runs it.

## 8. How a test is written

The tier says where a test goes. This section says how one is written: where its helpers live, how it is named, what a `conftest.py` may hold and how a fake is kept honest against its port.

### 8.1 Where helpers live

| Helper | Lives in | What it is |
|---|---|---|
| builders, such as `a_document(...)` | `tests/modules/<module>/builders.py` | one builder per aggregate, each argument defaulted so a test names only what it cares about; the constants a test does not care about (`NOW`, `A_ID`) live beside them |
| `controller(repo)` | `tests/modules/<module>/application/helpers.py` | assembles the real controller and service around fakes; a port the test does not name defaults to a fake |
| `client` | `tests/{{entry}}/conftest.py` | a fixture that builds the entry point around the fake controller it is given |
| fakes | `tests/fakes/` | one per port (section 6) |

{{tier_helpers}}

> [!NOTE]
> `controller` is a plain function, not a fixture, so the test calls it directly and the type checker sees the fake it is handed (section 8.4). It follows the service of architecture.md, section 8.4: `DocumentService(repo, review, clock)`.

### 8.2 How tests are named

A test file is `test_<subject>.py`, in the folder that mirrors the subject's path in the app. A test's name is a sentence that states the outcome, never the method under test. An integration test's name is its scenario's name (section 5.2).

```python
def test_a_document_without_a_title_is_rejected(): ...      # the outcome
def test_publish(): ...                                     # the method under test: never
```

> [!TIP]
> **Litmus test.** When the test fails, does its name tell what broke without opening the file? If yes, it states an outcome. If it only names the method under test, it says what was called, not what should be true.

### 8.3 What a conftest.py may hold

A `conftest.py` holds fixtures that build things, such as a client. It never holds data, a shared seed or a fake's state. A test folder that needs one has one, beside its tests, and there is no catch-all at the root of `tests/`.

> [!IMPORTANT]
> A `conftest.py` that holds data or a fake's state is the shared seed of section 7 under another name, and a test could no longer show all the state it depends on.

### 8.4 How a fake stays honest

A fake is checked against its port by the type checker. It is annotated as the port where it is handed over: the parameters of `controller(...)` are typed with the port `Protocol`s. When a port changes and its fake does not, the call that hands the fake over no longer type-checks, and the build fails.

> [!WARNING]
> The type checker proves that the fake has the port's shape, not that it behaves like the adapter. A fake that drifts in behavior is caught in review, and that risk is accepted.

## 9. Guards

`xarch check` runs every guard below on the app and on `tests/`, and a test under `tests/architecture/` runs `xarch check`, so a broken rule fails the build. The ones named for a key of the architecture file follow from it; the others are switched on by name in its `guards`.

{{guards}}

One line per guard. Each has a file under `artifacts/guards/`.
