# Testing

How the system is tested: which kind of test each part admits, where a test is placed, and how one is written. Each ring admits one kind of test, so a test's tier follows from the ring its subject lives in (architecture.md, section 2). Tests mirror the app: `tests/modules/<module>/<part>/`, `tests/web/`, `tests/architecture/`.

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
  - [[#5.2 Tables]]
  - [[#5.3 Tables in the other tiers]]
- [[#6. Fakes and mocks]]
- [[#7. Data]]
- [[#8. How a test is written]]
  - [[#8.1 Where helpers live]]
  - [[#8.2 How tests are named]]
  - [[#8.3 What a conftest.py may hold]]
  - [[#8.4 How a fake stays honest]]
- [[#9. Guards]]
  - [[#9.1 The enforcement section]]

## 1. Tiers

| Tier | Subject | Proves | May touch |
|---|---|---|---|
| unit | `domain/`, `application/logic/`, `adapters/`, `kernel/logic/`, `kernel/` | an invariant, a value rule, a state transition, a pure rule, an adapter's translation | nothing: no I/O, no clock (checked by `uses.never` for the pure parts), no fakes; an adapter gets a stub of its `platform/` client |
| integration | `application/controller.py`, with the services behind it | one `Result` variant per path, driven through the controller | real controllers only; their ports are `tests/fakes/`, or `Mock(spec=<Port>)` for fire-only ports |
| rendering | `web/` | what the page shows for each `Result`; never a business outcome | a fake controller, injected; the real controller's class only as a type, never called |
| guard | the source tree | a rule of the architecture holds | `tests/architecture/` |

`platform/` gets no tier of its own: it wraps outside technology; adapters are tested against a stub of it.

`bootstrap/` gets no tier of its own: it wires the app and holds no rule; it has no test of its own.

> [!NOTE]
> `application/logic/` sits in the application ring but holds pure functions with no port, so it is unit-tested.

## 2. Running

One command runs every tier. It appears here and nowhere else.

- unit, integration, rendering, guard: `<command>`

The project also ships a linter config, `ruff.toml`, for the rules that are the same in every file (imports sorted and absolute, a return type on public functions, no `print`, no naive datetime, pytest style). What differs by part, such as which imports, names and outside packages a part may use, lives in the profile and is checked by `xarch check`, not in the linter config.

## 3. Placement

Which ring does the subject live in? That is the tier. When it is not obvious, run the litmus tests in the order of the table in section 1. The first one it passes is where the test goes.

A test imports only what the part its folder mirrors may import (architecture.md, section 5), not all that its tier may touch: a test in `tests/modules/<module>/domain/` imports no adapter, though the unit tier tests both. A test in `tests/modules/<module>/application/` mirrors `application/controller.py`, so it imports what the controller may. A tier may name more with `may_also_import`, such as the values a test builds its fakes' answers with; `profile check` lists each target the bundled profile does not give as looser.

### 3.1 unit

> [!TIP]
> **Litmus test.** Does it prove a rule, value or transition by building the object and asking it, or by calling a pure function from `logic/`, or by handing an adapter a stub client and checking what it translates, with no port in sight? If yes, it is a unit test. If it needs a port to get an answer, it is an integration test. If it asserts how a port was called, it is testing nothing.

### 3.2 integration

> [!TIP]
> **Litmus test.** Does it drive one use case through its real controller, from the state in `given` with the command in `when`, and assert the `Result` in `then`? If yes, it is an integration test. If it asserts what a fake holds instead of the `Result`, check first that the `Result` would not already say it. If it asserts how a row is stored or read back, it is a unit test of the adapter. If it mocks a repo to assert it was called, fake the repo and assert the `Result`.

### 3.3 rendering

> [!TIP]
> **Litmus test.** Does it prove what the page shows for one `Result`, with a fake controller injected, asserting only what is shown and never a status code? If yes, it is a rendering test. If it asserts what the use case did, or needs the real controller to mean anything, it is an integration test wearing a screen.

### 3.4 guard

> [!TIP]
> **Litmus test.** Does it read the source tree and fail on a rule of architecture.md, whatever the app does? If yes, it is a guard. If it runs the app, it is not a guard.

## 4. Examples

One module, `documents`, with a use case `publish` (architecture.md, section 8). Each tier has its test here, holding only what its row allows. Where a tier's cases share a shape, the test is a table (section 5.2).

The guard test is the one example that is a real file: `xarch init` writes it as shown, with the app folder's name in place of `app`.

```python
# unit: tests/modules/documents/application/logic/test_staleness.py
@pytest.mark.parametrize("published_at, now, stale", [
    pytest.param(None, NOW, False, id="a draft is never stale"),
    pytest.param(NOW - timedelta(days=365), NOW, False, id="a document published a year ago is not stale"),
    pytest.param(NOW - timedelta(days=366), NOW, True, id="a document published over a year ago is stale"),
])
def test_is_stale(published_at, now, stale):
    assert is_stale(a_document(published_at=published_at), now) is stale

# an invariant that raises is its own test: tests/modules/documents/domain/test_document.py
def test_a_document_without_a_title_cannot_be_published():
    with pytest.raises(DocumentIncomplete):
        a_document(title="").publish(NOW)

# an adapter's translation: tests/modules/documents/adapters/test_db_document_repo.py
def test_a_row_is_translated_to_a_document():
    session = Mock(get=lambda model, id: DocumentRow(id=A_ID, title="Hello", published_at=None))
    doc = DbDocumentRepo(session).get(A_ID)
    assert (doc.id, doc.title, doc.published_at) == (A_ID, "Hello", None)

# integration: tests/modules/documents/application/test_publish.py (its table is in section 5.2)
"""Use case: publish a document."""

@pytest.mark.parametrize("given, when, then", [
    pytest.param([a_document(title="Hello")], PublishDocument(A_ID), Published(DocumentView(A_ID, "Hello")),
                 id="a document with a title is published"),
    pytest.param([],                          PublishDocument(A_ID), Missing(),
                 id="a document that does not exist is missing"),
    pytest.param([a_document(title="")],      PublishDocument(A_ID), Rejected("The document needs a title."),
                 id="a document without a title is rejected"),
])
def test_publish(given, when, then):
    assert controller(given).publish(when) == then

# rendering: tests/web/test_publish.py
@pytest.mark.parametrize("result, shown", [
    pytest.param(Published(DocumentView(A_ID, "Hello")), "Hello", id="a published document shows its title"),
    pytest.param(Missing(), t("documents.missing"), id="a missing document says so"),
    pytest.param(Rejected("The document needs a title."), "The document needs a title.",
                 id="a rejected document shows the reason"),
])
def test_publish(client, result, shown):
    page = client(Mock(publish=lambda cmd: result)).post(f"/documents/{A_ID}/publish")
    assert shown in page.text

# guard: tests/architecture/test_rules.py (written by `xarch init`)
import subprocess
import sys
from pathlib import Path

PROJECT = Path(__file__).parents[2]


def test_the_architecture_holds():
    check = subprocess.run([sys.executable, "-m", "xarch", "check", "--app", str(PROJECT / "app")],
                           capture_output=True, text=True)
    assert check.returncode == 0, check.stdout + check.stderr
```

## 5. Files

### 5.1 One file per

| Tier | One file per | Its cases come from |
|---|---|---|
| unit | domain object or rule | the invariants in the module doc; a rule's cases are a table of its inputs and its answer |
| integration | use case | a Given / When / Then table: a row for every `Result` variant, happy and unhappy |
| rendering | command or page | a table of the `Result` and what is shown, a row for every variant it shows |
| guard | project, since one test runs every guard | the guards of section 9 |

### 5.2 Tables

A table is the standard way to write tests that share a shape: one test function, one row per case. A use case's test is a table with the columns Given / When / Then, one row per path through it, and it is the integration tier's alone. A unit test proves a rule or a translation, and neither has a Given (section 5.3). The table is the list of scenarios: a row is a scenario, and its `id` is the scenario's name. The example in section 4 is such a table.

| Column | Holds |
|---|---|
| `given` | the state the fakes start with: the documents a repo holds, the answer a review gives |
| `when` | the use case's command, from the module's `contract/` |
| `then` | the `Result` variant that comes back |

Every row is a `pytest.param(..., id="<a sentence stating the outcome>")`, and the `id` is the row's name: a bare tuple has none and is reported. The columns are named by the first argument of `parametrize`, so no comment labels them. The rows hold one `then` per `Result` variant at least, happy and unhappy, so a variant with neither a row nor a standalone test is an untested path, and a row whose `then` is not a variant is a missing `Result`.

The body has no `if`, `match`, `try`, `for` or `while`: it arranges from `given`, acts with `when` and asserts `== then`.

> [!TIP]
> **Litmus test.** Can the case be written as the state the fakes start with, a command, and the `Result` that comes back, with the same body as every other row? If yes, it is a row. If its body needs a branch, a loop or another assertion, it has its own test next to the table.

A case that is not state in, command, `Result` out gets its own standalone test beside the table, named for its outcome (section 8.2). Two cases are typical:

- A fire-only port (section 6) has nothing to put in `given` and nothing to read back: the test asserts the call on a `Mock(spec=<Port>)`.
- A `Result` that carries a generated value, such as a fresh id, cannot be written as a value in `then`: the test asserts what it can, such as the title.

When a use case needs the state of more than one port, `given` holds the keyword arguments of the module's `controller(...)` helper (section 8.1), and the body is `controller(**given)`:

```python
# tests/modules/documents/application/test_create.py
"""Use case: create a document."""

@pytest.mark.parametrize("given, when, then", [
    pytest.param(dict(review=Denied("spam")), CreateDocument("Buy now"), Rejected("spam"),
                 id="a title the review denies is rejected"),
])
def test_create(given, when, then):
    assert controller(**given).create(when) == then

def test_a_created_document_comes_back_with_its_title():
    result = controller().create(CreateDocument("Hello"))
    assert isinstance(result, Created) and result.view.title == "Hello"
```

> [!IMPORTANT]
> `xarch check` reads the table from the file, never runs it. The test file `test_<use case>.py` holds a test parametrized over the columns `given`, `when` and `then`, whose rows are literal `pytest.param(...)` calls with an `id`: written in the decorator, or as a list assigned once at the top of the file. A row's `then` is a variant of the use case's union, called or bare, and every variant is the `then` of a row or is named in a standalone test of the file. A branch in the body of the table test is reported (section 9).

### 5.3 Tables in the other tiers

A unit test and a rendering test use the same table when their cases share a shape. Given, When and Then belong to a use case, so their columns are named for what they hold.

- A unit table's columns are the rule's inputs and its answer, as in `test_is_stale`: a row is one input and what the rule says of it.
- A rendering table's columns are the `Result` and what the user sees, the page or the terminal output. Only what is shown is asserted: no status-code or exit-code column, since what the use case decided is the `Result`'s to say.

The same rules hold: every row is a `pytest.param` with an `id` that states the outcome, the body has no branch, and a test whose case does not share the shape, such as an invariant that raises, stands alone.

## 6. Fakes and mocks

A port is faked or mocked by what the use case does with it, and its signatures say which: the return annotations of its `Protocol`'s methods.

| The use case | Port kind | Its methods | Stand-in | Example |
|---|---|---|---|---|
| reads back what it wrote | read (stateful) | at least one returns a value | a fake: an in-memory implementation in `tests/fakes/`, named `Fake<Port>`, one per port | a repo, a clock, a blob store |
| only fires and never reads | fire-only | every one returns `None` | a mock that names the port, `Mock(spec=<Port>)`, asserting the call and its payload, since the call is the contract | send an email, publish an event |

> [!TIP]
> **Litmus test.** Does the use case ever read back through this port what it or anything else wrote, or branch on its answer? If yes, fake it: a mock would script the answer, and the test would prove only what it was told. If the use case only calls it and never looks at it again, mock it: the call is the outcome, and a fake would be ceremony. A port that is written and then read back is a read port, whatever its writing methods return: fake it. A port that carries two unrelated needs, such as a store and a notification, is split in two: that is a review judgment, and `check` does not report it.

> [!IMPORTANT]
> `xarch check` holds every port to its kind (section 9). A port with any method that returns a value is a read port, and one whose methods all return `None` is fire-only. A method with no return annotation is reported, since the kind follows from it. A read port with no `Fake<Port>` in `tests/fakes/` is reported. In an integration test, a mock that names nothing, such as `Mock()`, is reported, and so is one that names a read port: that port has a fake.

A fake is a working implementation of the port that keeps its state in memory, not a recording of calls. It takes its starting state when it is built, which is what a row's `given` holds.

```python
class DocumentRepo(Protocol):                       # the port, in application/ports/
    def get(self, id: DocumentId) -> Document | None: ...
    def save(self, doc: Document) -> None: ...

class DbDocumentRepo:                              # the adapter, in adapters/: talks to the database
    ...

class FakeDocumentRepo:                             # the fake, in tests/fakes/: a dict standing in for the table
    def __init__(self, docs: Iterable[Document] = ()): self.docs = {d.id: d for d in docs}
    def get(self, id): return self.docs.get(id)
    def save(self, doc): self.docs[doc.id] = doc

class FakeContentReview:                            # the fake of a port that answers: it gives the answer it starts with
    def __init__(self, outcome: Allowed | Denied = Allowed()): self.outcome = outcome
    def review(self, title): return self.outcome

class FakeClock:                                    # the fake of kernel's Clock: it tells the time it starts with
    def __init__(self, now: datetime): self._now = now
    def now(self): return self._now
```

The fakes are shared by every integration test. A fake is not an adapter, and a mock is not a fake.

## 7. Data

A test builds the state it needs, so the reader sees all of it: in an integration test it is the `given` column of its table, row by row. No tier runs a shared seed.

| Tier | Where its data comes from |
|---|---|
| unit | built in the test; a rule's inputs are the columns of its table |
| integration | the `given` column: the state the fakes start with; a builder per aggregate for the common shape, never a shared dataset |
| rendering | none: the `result` column is what the fake controller returns |
| guard | none |

> [!NOTE]
> The seed is product code. It lives in `bootstrap/`, the only part that sees every module, and the demo environment runs it.

## 8. How a test is written

The tier says where a test goes. This section says how one is written: where its helpers live, how it is named, what a `conftest.py` may hold and how a fake is kept honest against its port.

### 8.1 Where helpers live

| Helper | Lives in | What it is |
|---|---|---|
| builders, such as `a_document(...)` | `tests/modules/<module>/builders.py` | one builder per aggregate, each argument defaulted so a test names only what it cares about; the constants a test does not care about (`NOW`, `A_ID`) live beside them |
| `controller(...)` | `tests/modules/<module>/application/helpers.py` | assembles the real controller and service around fakes, each built from the starting state it is given: a row's `given`, or its keyword arguments; a port the test does not name starts empty |
| `client` | `tests/web/conftest.py` | a fixture that builds the entry point around the fake controller it is given |
| fakes | `tests/fakes/` | one per port (section 6) |

```python
# tests/modules/documents/builders.py
NOW = datetime(2026, 1, 1)
A_ID = DocumentId(UUID(int=1))

def a_document(id: DocumentId = A_ID, title: str = "Hello", published_at: datetime | None = None) -> Document:
    return Document(id, title, published_at)

# tests/modules/documents/application/helpers.py
def controller(repo: Iterable[Document] = (), review: Allowed | Denied = Allowed(), now: datetime = NOW) -> DocumentController:
    # each argument is a fake's start state
    service = DocumentService(FakeDocumentRepo(repo), FakeContentReview(review), FakeClock(now))
    return DocumentController(service)

# tests/web/conftest.py
@pytest.fixture
def client():
    def build(controller: DocumentController) -> TestClient:
        app = FastAPI()
        app.include_router(router)
        # the route gets the fake controller
        app.dependency_overrides[documents_controller] = lambda: controller
        return TestClient(app)
    return build
```

> [!NOTE]
> `controller` is a plain function, not a fixture, so the test calls it directly. A test of one port passes its `given` as the first argument, `controller(given)`, and a test of several passes `controller(**given)`, so both forms of section 5.2 read the same. It follows the service of architecture.md, section 8.4: `DocumentService(repo, review, clock)`.

### 8.2 How tests are named

A test file is `test_<subject>.py`, in the folder that mirrors the subject's path in the app. What a test function is called depends on whether it is a table or stands alone.

- A table test is named for the use case or the rule it covers: `test_publish`, `test_is_stale`. The outcome is in the rows: each row's `id` is a sentence that states it, and pytest reports the row as `test_publish[a document without a title is rejected]`.
- A standalone test is named for its outcome, never for the method under test.

```python
def test_publish(given, when, then): ...                    # a table: the use case; every row's id states an outcome
def test_a_created_document_comes_back_with_its_title(): ...   # standalone: the outcome
def test_create(): ...                                      # standalone, and the method under test: never
```

> [!TIP]
> **Litmus test.** When the test fails, does its report tell what broke without opening the file? If yes, it states an outcome: the row's `id` for a table, the name for a standalone test. If it only names the method under test, it says what was called, not what should be true.

### 8.3 What a conftest.py may hold

A `conftest.py` holds fixtures that build things, such as a client. It never holds data, a shared seed or a fake's state. A test folder that needs one has one, beside its tests, and there is no catch-all at the root of `tests/`.

> [!IMPORTANT]
> A `conftest.py` that holds data or a fake's state is the shared seed of section 7 under another name, and a test could no longer show all the state it depends on.

### 8.4 How a fake stays honest

A fake is checked against its port twice. `xarch check` requires it to exist: every read port `<Port>` has a class `Fake<Port>` in `tests/fakes/`, found by its name. The type checker checks its shape: `controller(...)` hands each fake to the service, whose parameters are typed with the port `Protocol`s. When a port changes and its fake does not, that call no longer type-checks, and the build fails.

> [!WARNING]
> The type checker proves that the fake has the port's shape, not that it behaves like the adapter. A fake that drifts in behavior is caught in review, and that risk is accepted.

## 9. Guards

`xarch check` runs every guard below on the app and on `tests/`. `xarch init` writes the guard test, `tests/architecture/test_rules.py` (section 4): it runs `xarch check` on the app, and it is what runs every guard with the project's test suite, so a broken rule fails the build. `xarch check` can also run in CI or in a pre-commit hook. The ones named for a key of the architecture file follow from it; the others are switched on by name in its `guards`.

- `structure`: every folder and file of the layout exists, in the app and in every `modules/<name>/`.
- `may-import`: every import between parts is one that the `imports.may` of the importing part allows (architecture.md, section 5).
- `libraries`: a part imports only the outside packages listed for it (`adapters/`: sqlmodel; `platform/`: sqlmodel; `web/`: fastapi; `bootstrap/`: sqlmodel, fastapi, uvicorn); the standard library is always allowed, and tests are not checked.
- `never-use`: a part neither imports nor uses by name what its `uses.never` list names (`domain/`, `application/logic/`, `application/ports/`, `kernel/logic/` and `kernel/`: `datetime.datetime.now`, `datetime.datetime.utcnow`, `datetime.datetime.today`, `datetime.date.today`, `time.time`, `time.time_ns`, `time.monotonic`, `time.perf_counter`, `builtins.open`, `builtins.print`, `builtins.input`, `sys.stdin`, `sys.stdout`, `sys.stderr`, `os.environ`, `os.getenv`, `socket`, `subprocess`, `sqlite3`, `urllib`, `http`, `shutil`, `pathlib.Path.cwd`, `pathlib.Path.absolute`, `os.getcwd`, `os.path.abspath`, `os.path.realpath`, `pathlib.Path.resolve`, `pathlib.Path.home`, `pathlib.Path.expanduser`, `os.path.expanduser`, `os.getcwdb`, `os.chdir`; `application/services/`, `application/controller.py` and `adapters/`: `pathlib.Path.cwd`, `pathlib.Path.absolute`, `pathlib.Path.resolve`, `pathlib.Path.home`, `pathlib.Path.expanduser`, `os.getcwd`, `os.getcwdb`, `os.chdir`, `os.path.abspath`, `os.path.realpath`, `os.path.expanduser`, `.absolute()`, `.resolve()`, `.expanduser()`, `.chdir()`, `os.environ`, `os.getenv`; `platform/` and `web/`: `os.environ`, `os.getenv`; `contract/`: `datetime.datetime.now`, `datetime.datetime.utcnow`, `datetime.datetime.today`, `datetime.date.today`, `time.time`, `time.time_ns`, `time.monotonic`, `time.perf_counter`, `builtins.open`, `builtins.print`, `builtins.input`, `sys.stdin`, `sys.stdout`, `sys.stderr`, `os.environ`, `os.getenv`, `socket`, `subprocess`, `sqlite3`, `urllib`, `http`, `shutil`, `pathlib.Path.cwd`, `pathlib.Path.absolute`, `os.getcwd`, `os.path.abspath`, `os.path.realpath`, `pathlib.Path.resolve`, `pathlib.Path.home`, `pathlib.Path.expanduser`, `os.path.expanduser`, `os.getcwdb`, `os.chdir`, `typing.Any`), and neither do the unit tests of those parts. It catches what is written in the part's own files, through their imports and aliases, and a method written `.name()` called on anything but the object itself and what it holds; not a name reached through a variable or `getattr`, nor I/O done on the part's behalf elsewhere.
- `tiers`: a test lives in the folder that mirrors its subject in the app, and imports only that part and what it may import (a test in a folder that mirrors no part, its tier's subject and what that may import); only a test whose tier tests `application/ports/` imports the fakes in `tests/fakes/`; it imports no other test file.
- `types-only`: a rendering test uses `application/controller.py` only as a type: it may import it and annotate with it, and never calls it.
- `test tree`: every folder below `tests/modules/` mirrors a folder of the app.
- `cycles`: no `modules/<name>/` imports from another that imports, directly or through others, from it; each cycle is reported once, with the imports that close it.
- `must-import`: every file of `adapters/` imports from `platform/`, any module's `contract/`, or an outside package, or reaches one through a file of its own part; a package file and a file with no code of its own are exempt.
- `holds`: a file of `domain/`, `application/ports/`, `application/services/`, `application/controller.py` and `adapters/` defines classes, never a public function at the top level; a file of `application/logic/` and `kernel/logic/` defines functions, never a class (a private one too) but exceptions and the records its functions return; listed in the enforcement section, and fails `check --strict` only.
- `immutable`: every record of `application/logic/` and `kernel/logic/` is an immutable record, as the Python data file marks one; listed in the enforcement section, and fails `check --strict` only.
- `names`: every class of `application/services/` is named `*Service`.
- `names`: every class of `application/controller.py` is named `*Controller`.
- `built-by`: only code of `bootstrap/` builds a class of `application/services/`; tests are not read.
- `built-by`: only code of `bootstrap/` builds a class of `application/controller.py`; tests are not read.
- `built-by`: only code of `bootstrap/` builds a class of `adapters/`; tests are not read.
- `package-only`: `contract/` is imported as a package, never by its files, from outside it.
- `scenario-coverage`: every variant of a union named `<Name>Result` in `contract/` is the `then` of a row of the table (columns `given`, `when`, `then`) in `test_<name>.py` among the integration tests (section 5.2), or is named by a standalone test of that file; every row is a `pytest.param` with an `id`, and a table test has no `if`, `match`, `try`, `for` or `while` statement and no `if` expression.
- `no-comments`: no `#` comments in the app or its tests; docstrings and tool directives (`# type: ignore`, `# noqa`, `# pragma:`) stay.
- `closed-tree`: every Python file of the app lies in a part, or is the package file (`__init__.py`) of a folder of the layout.
- `stand-ins`: every `Protocol` in `application/ports/` is fire-only (every method returns `None`) or read (any method returns a value), each method annotated; every read port `<Port>` has a fake `Fake<Port>` in `tests/fakes/`; and every mock in the integration tests names what it stands in for, `Mock(spec=<Port>)` (or, from a fixture, `mocker.Mock(spec=<Port>)`), never a read port (section 6).
- `no-duplicates`: no two functions of the app have the same code, names and formatting aside, when each holds at least 4 statements; tests are not compared.
- `no-twins`: no two public classes in parts of different names declare the same fields in the same order, when each declares at least 3; types and defaults aside, tests not read. Nor is one a copy of another that renames some of its fields (from 3 fields: more than half of its names kept in place, and each renamed field's type), or that keeps at least half of its fields in its order (from 3 fields).
- `dead-code`: every `Protocol` in `application/ports/` is named by another file of the app, and every fake in `tests/fakes/` by a test; the wiring and re-exports do not count. A file of a part with a tier that no test of that tier reaches, directly or through files of parts of the same tier, is listed in the enforcement section, and fails `check --strict` only.
- `pass-through`: a method of `application/services/`, `application/controller.py` and `adapters/` whose whole body forwards to one call on a collaborator, or returns an attribute of what that call answers, is listed in the enforcement section, and fails `check --strict` only.
- `no-callbacks`: no function of `domain/` and `application/logic/` calls a parameter annotated as a callable: it is handed values, never a way to fetch them.
- `private-imports`: no file of the app or its tests imports a name that starts with `_` from another file of them.

One line per guard. A guard the project adds itself is a check of its own under `tests/architecture/`, written up from `artifacts/guards/_template.md`.

### 9.1 The enforcement section

After the violations, `xarch check` prints an `enforcement` section: the state of its own enforcement, so that a clean check reached by weakening it shows. It names the profile in force, a bundled one or a custom file with the bundled profile it most resembles (the one sharing the most parts), and the guards it leaves off; for a custom file, every way it is looser than that profile: an `imports.may` target or an `imports.libraries` package added to a part, a `types_only` mark dropped from an entry of a part's `imports.may`, an `imports.must` target added to a part or the key dropped, a `uses.never` name dropped, a part newly marked `untested`, a part redefined without the `litmus` the bundled profile gives it, a tier that lost a `types_only` part or its `uses.apply_never`, a target a tier's tests may also import (`may_also_import`), a name dropped from `testing.skips`, a file of `files` no longer `pinned`, a name `reserved` no longer holds, a public name `guards.dead-code.known` accepts as only the tests', a part `guards.no-twins.translated` lists. Then the pairs of classes `no-twins` accepts as translations, each with the function that translates; the Python files of the app that no part and no folder of the layout governs, which no check reads; the files `xarch init` writes that are missing, or, for a pinned one such as the guard test, changed from what `init` would write now; the tests skipped or expected to fail; the dynamic imports (`importlib.import_module`, `__import__`), whose targets the import rules cannot see; and the checks met to the letter only, as `weak`: a fake that does not define every method its port declares, a `Result` variant credited to a standalone test whose body holds no `assert`, and what the guards of section 9 list without failing (`holds`, `immutable`, `pass-through`, and `dead-code`'s untested files and names only the tests use, but those `guards.dead-code.known` accepts, which it names apart). `xarch check --format json` gives the same as one JSON document.

The section never changes the exit code. `xarch check --strict` fails on every finding in it except the guards that the bundled profile in force, or the one a custom profile is compared with, also leaves off (none here), and except the ways a custom profile is looser, which are information, but for a part left without the `litmus` the bundled profile gives it, which fails too. The guard test runs `xarch check` without `--strict`, and is pinned, so editing it is itself reported: a project opts in by running `xarch check --strict` in CI or in a pre-commit hook.
