# Testing

How the system is tested: which kind of test each part admits, where a test is placed, and how one is written. Each ring admits one kind of test, so a test's tier follows from the ring its subject lives in (architecture.md, section 2). Tests mirror the app: `tests/modules/<module>/<part>/`, `tests/cli/`, `tests/architecture/`.

## Index

- [[#1. Tiers]]
- [[#2. Running]]
- [[#3. Placement]]
  - [[#3.1 unit]]
  - [[#3.2 integration]]
  - [[#3.3 rendering]]
  - [[#3.4 guard]]
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

| Tier | Subject | Proves | May touch |
|---|---|---|---|
| unit | `kernel/` and `kernel/logic/`, `domain/`, `application/logic/`, `adapters/` | an invariant, a value rule, a state transition, a pure rule, an adapter's translation | nothing: no I/O, no clock, no fakes; an adapter gets a stub of its `platform/` client |
| integration | `application/controller.py`, with the services behind it | one `Result` variant per path, driven through the controller | real controllers only; their ports are `tests/fakes/`, or mocks for fire-only ports |
| rendering | `cli/` | what the terminal output shows for each `Result`; never a business outcome | a fake controller, injected |
| guard | the source tree | a rule of the architecture holds | `tests/architecture/` |

`platform/` gets no tier of its own: it wraps outside technology; adapters are tested against a stub of it.

`bootstrap/` gets no tier of its own: it wires the app and holds no rule; it has no test of its own.

> [!NOTE]
> `application/logic/` sits in the application ring but holds pure functions with no port, so it is unit-tested.

## 2. Running

One command runs every tier. It appears here and nowhere else.

- unit, integration, rendering, guard: `<command>`

## 3. Placement

Which ring does the subject live in? That is the tier. When it is not obvious, run the litmus tests in the order of the table in section 1. The first one it passes is where the test goes.

### 3.1 unit

> [!TIP]
> **Litmus test.** Does it prove a rule, value or transition by building the object and asking it, or by calling a pure function from `logic/`, or by handing an adapter a stub client and checking what it translates, with no port in sight? If yes, it is a unit test. If it needs a port to get an answer, it is an integration test. If it asserts how a port was called, it is testing nothing.

### 3.2 integration

> [!TIP]
> **Litmus test.** Does it drive one use case through its real controller and assert one `Result` variant? If yes, it is an integration test. If it asserts what a fake holds instead of the `Result`, check first that the `Result` would not already say it. If it asserts how a row is stored or read back, it is a unit test of the adapter. If it mocks a repo to assert it was called, fake the repo and assert the `Result`.

### 3.3 rendering

> [!TIP]
> **Litmus test.** Does it prove what the terminal output shows for one `Result`, with a fake controller injected? If yes, it is a rendering test. If it asserts what the use case did, or needs the real controller to mean anything, it is an integration test wearing a screen.

### 3.4 guard

> [!TIP]
> **Litmus test.** Does it read the source tree and fail on a rule of architecture.md, whatever the app does? If yes, it is a guard, and it has a file under `artifacts/guards/`. If it runs the app, it is not a guard.

## 4. Examples

One module, `documents`, with a use case `publish` (architecture.md, section 8). Each tier has one test here, holding only what its row allows.

```python
# unit: tests/modules/documents/domain/test_document.py
def test_a_document_without_a_title_cannot_be_published():
    with pytest.raises(DocumentIncomplete):
        a_document(title="").publish(NOW)

# an adapter's translation: tests/modules/documents/adapters/test_db_document_repo.py
def test_a_row_is_translated_to_a_document():
    session = Mock(get=lambda model, id: DocumentRow(id=A_ID, title="Hello", published_at=None))
    doc = DbDocumentRepo(session).get(A_ID)
    assert (doc.id, doc.title, doc.published_at) == (A_ID, "Hello", None)

# integration: tests/modules/documents/application/test_publish.py (its header is in section 5.2)
def test_a_document_without_a_title_is_rejected():
    repo = FakeDocumentRepo()
    repo.save(doc := a_document(title=""))
    assert controller(repo).publish(PublishDocument(doc.id)) == Rejected("The document needs a title.")

# rendering: tests/cli/test_publish.py
def test_publish_prints_the_title(client):
    controller = Mock(publish=lambda cmd: Published(DocumentView(cmd.id, "Hello")))
    result = client(controller)(["documents", "publish", str(A_ID)])
    assert "Published Hello" in result.output

# guard: tests/architecture/test_rules.py
def test_the_dependency_rules_hold():
    assert check(Path("app")).violations == []
```

## 5. Files

### 5.1 One file per

| Tier | One file per | Its cases come from |
|---|---|---|
| unit | domain object or rule | the invariants in the module doc |
| integration | use case, headed by its scenarios | the scenarios: one per `Result` variant, happy and unhappy |
| rendering | command or page | the `Result` variants it shows |
| guard | rule | the standard it enforces |

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

| Tier | Where its data comes from |
|---|---|
| unit | built in the test |
| integration | the test loads the fake before acting; a builder per aggregate for the common shape, never a shared dataset |
| rendering | none: the fake controller returns the `Result` under test |
| guard | none |

> [!NOTE]
> The seed is product code. It lives in `bootstrap/`, the only part that sees every module, and the demo environment runs it.

## 8. How a test is written

The tier says where a test goes. This section says how one is written: where its helpers live, how it is named, what a `conftest.py` may hold and how a fake is kept honest against its port.

### 8.1 Where helpers live

| Helper | Lives in | What it is |
|---|---|---|
| builders, such as `a_document(...)` | `tests/modules/<module>/builders.py` | one builder per aggregate, each argument defaulted so a test names only what it cares about; the constants a test does not care about (`NOW`, `A_ID`) live beside them |
| `controller(repo)` | `tests/modules/<module>/application/helpers.py` | assembles the real controller and service around fakes; a port the test does not name defaults to a fake |
| `client` | `tests/cli/conftest.py` | a fixture that builds the entry point around the fake controller it is given |
| fakes | `tests/fakes/` | one per port (section 6) |

```python
# tests/modules/documents/builders.py
NOW = datetime(2026, 1, 1)
A_ID = DocumentId(UUID(int=1))

def a_document(id: DocumentId = A_ID, title: str = "Hello", published_at: datetime | None = None) -> Document:
    return Document(id, title, published_at)

# tests/modules/documents/application/helpers.py
def controller(repo: DocumentRepo, review: ContentReview | None = None, clock: Clock | None = None) -> DocumentController:
    service = DocumentService(repo, review or FakeContentReview(), clock or FakeClock(NOW))   # what the test omits is a fake
    return DocumentController(service)

# tests/cli/conftest.py
@pytest.fixture
def client():
    def build(controller: DocumentController):
        cli = Typer()
        cli.add_typer(documents_commands.app, name="documents")
        return partial(CliRunner().invoke, cli, obj=App(cli=cli, documents=controller))   # the command gets the fake controller
    return build
```

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

- `structure`: every folder and file of the layout exists, in the app and in every `modules/<name>/`.
- `rules`: every import between parts is one that `rules` allows (architecture.md, section 5).
- `libraries`: a part imports only the outside packages listed for it (`platform/`: sqlmodel; `adapters/`: sqlmodel; `cli/`: typer; `bootstrap/`: sqlmodel, typer); the standard library is always allowed, and tests are not checked.
- `tiers`: a test lives in the folder that mirrors its subject in the app, and imports only its tier's subject and what that subject may import; only a test whose tier tests `application/ports/` imports the fakes in `tests/fakes/`.
- `test tree`: every folder below `tests/modules/` mirrors a folder of the app.
- `package-only`: `contract/` is imported as a package, never by its files, from outside it.
- `scenario-coverage`: every variant of a union named `<Name>Result` in `contract/` has a scenario in the header of `test_<name>.py` among the integration tests (section 5.2), and every scenario has a test of the same name.
- `no-comments`: no `#` comments in the app or its tests; docstrings and tool directives (`# type: ignore`, `# noqa`, `# pragma:`) stay.

One line per guard. Each has a file under `artifacts/guards/`.
