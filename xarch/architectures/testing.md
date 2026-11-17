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

{{tiers}}

{{untested}}

> [!NOTE]
> `application/logic/` sits in the application ring but holds pure functions with no port, so it is unit-tested.

## 2. Running

One command runs every tier. It appears here and nowhere else.

- unit, integration, rendering, guard: `<command>`

The project also ships a linter config, `ruff.toml`, for the rules that are the same in every file (imports sorted and absolute, a return type on public functions, no `print`, no naive datetime, pytest style). What differs by part, such as which imports, names and outside packages a part may use, lives in the profile and is checked by `xarch check`, not in the linter config.

## 3. Placement

Which ring does the subject live in? That is the tier. When it is not obvious, run the litmus tests in the order of the table in section 1. The first one it passes is where the test goes.

A test imports only what the part its folder mirrors may import (architecture.md, section 5), not all that its tier may touch: a test in `tests/modules/<module>/domain/` imports no adapter, though the unit tier tests both. A test in `tests/modules/<module>/application/` mirrors `application/controller.py`, so it imports what the controller may. A tier may name more with `may_also_import`, such as the values a test builds its fakes' answers with; `profile check` lists each target the bundled profile does not give as looser.

{{tier_litmus:3}}

## 4. Examples

One module, `documents`, with a use case `publish` (architecture.md, section 8). Each tier has its test here, holding only what its row allows. Where a tier's cases share a shape, the test is a table (section 5.2).

The guard test is the one example that is a real file: `xarch init` writes it as shown, with the app folder's name in place of `app`.

{{tier_examples}}

## 5. Files

### 5.1 One file per

{{tier_files}}

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

{{tier_data}}

> [!NOTE]
> The seed is product code. It lives in `bootstrap/`, the only part that sees every module, and the demo environment runs it.

## 8. How a test is written

The tier says where a test goes. This section says how one is written: where its helpers live, how it is named, what a `conftest.py` may hold and how a fake is kept honest against its port.

### 8.1 Where helpers live

| Helper | Lives in | What it is |
|---|---|---|
| builders, such as `a_document(...)` | `tests/modules/<module>/builders.py` | one builder per aggregate, each argument defaulted so a test names only what it cares about; the constants a test does not care about (`NOW`, `A_ID`) live beside them |
| `controller(...)` | `tests/modules/<module>/application/helpers.py` | assembles the real controller and service around fakes, each built from the starting state it is given: a row's `given`, or its keyword arguments; a port the test does not name starts empty |
| `client` | `tests/{{entry}}/conftest.py` | a fixture that builds the entry point around the fake controller it is given |
| fakes | `tests/fakes/` | one per port (section 6) |

{{tier_helpers}}

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

{{guards}}

One line per guard. A guard the project adds itself is a check of its own under `tests/architecture/`, written up from `artifacts/guards/_template.md`.

### 9.1 The enforcement section

After the violations, `xarch check` prints an `enforcement` section: the state of its own enforcement, so that a clean check reached by weakening it shows. It names the profile in force, a bundled one or a custom file with the bundled profile it most resembles (the one sharing the most parts), and the guards it leaves off; for a custom file, every way it is looser than that profile: a `may_import` target or a `libraries` package added to a part, a `must_import` target added to a part or the key dropped, a `forbidden` name dropped, a part newly marked `untested`, a part redefined without the `litmus` the bundled profile gives it, a tier that lost a `types_only` part or its `apply_forbidden`, a target a tier's tests may also import (`may_also_import`), a name dropped from `testing.skips`, a file of `files` no longer `pinned`, a name `reserved` no longer holds, a public name `guards.dead-code.known` accepts as only the tests', a part `guards.no-twins.translated` lists. Then the pairs of classes `no-twins` accepts as translations, each with the function that translates; the Python files of the app that no part and no folder of the layout governs, which no check reads; the files `xarch init` writes that are missing, or, for a pinned one such as the guard test, changed from what `init` would write now; the tests skipped or expected to fail; the dynamic imports (`importlib.import_module`, `__import__`), whose targets the import rules cannot see; and the checks met to the letter only, as `weak`: a fake that does not define every method its port declares, a `Result` variant credited to a standalone test whose body holds no `assert`, and what the guards of section 9 list without failing (`holds`, `immutable`, `pass-through`, and `dead-code`'s untested files and names only the tests use, but those `guards.dead-code.known` accepts, which it names apart). `xarch check --format json` gives the same as one JSON document.

The section never changes the exit code. `xarch check --strict` fails on every finding in it except the guards that the bundled profile in force, or the one a custom profile is compared with, also leaves off (none here), and except the ways a custom profile is looser, which are information, but for a part left without the `litmus` the bundled profile gives it, which fails too. The guard test runs `xarch check` without `--strict`, and is pinned, so editing it is itself reported: a project opts in by running `xarch check --strict` in CI or in a pre-commit hook.
