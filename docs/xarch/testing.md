# Testing

How xarch is tested: which kind of test each part admits, where a test is placed, and how one is written. The tiers, their subjects and the guards below come from `architecture.yaml`, and `xarch check` holds xarch's own tests to them as it holds its source. Tests mirror the package: `tests/modules/<module>/<part>/`, `tests/kernel/`, `tests/profile_values/`, `tests/platform/`, `tests/cli/`, `tests/bootstrap/`, `tests/architecture/`. This page is generated from that file and from `docs/templates/testing.md`: edit those, never this page.

## Index

- [[#1. Tiers]]
- [[#2. Running]]
- [[#3. Placement]]
  - [[#3.1 unit]]
  - [[#3.2 integration]]
  - [[#3.3 wired]]
  - [[#3.4 guard]]
- [[#4. Examples]]
- [[#5. Files]]
  - [[#5.1 One file per]]
  - [[#5.2 Tables]]
- [[#6. Fakes]]
- [[#7. Data]]
- [[#8. Guards]]

## 1. Tiers

| Tier | Subject | Proves | May touch |
|---|---|---|---|
| unit | `domain/`, `application/logic/`, `adapters/`, `platform/`, `cli/reports/`, `profile_values/`, `kernel/logic/`, `kernel/` | a pure rule of the kernel or a module, or an adapter's translation | what the part it mirrors may import; an adapter, temporary folders |
| integration | `application/ports/`, `application/services/`, `application/controller.py`, `contract/` | a use case, through its controller around fakes | what the part it mirrors may import; `tests/fakes/` |
| wired | `cli/`, `bootstrap/` | a command, a check on real files, or what a bundled profile holds, through the app bootstrap/ wires | anything bootstrap/ wires; temporary folders |
| guard | xarch's own source tree | xarch follows the architecture it enforces | `tests/architecture/` |

`__main__.py` gets no tier of its own: a two-line shim that runs the app bootstrap/ builds; no test runs `python -m xarch`, and the wired tests drive that same app.

> [!NOTE]
> `application/ports/` and `contract/` have no behavior of their own to test: the integration tests reach them through the controller that uses them. `application/logic/` sits beside the services but holds pure functions with no port, so it is unit-tested.

## 2. Running

One command runs every tier:

```
uv run pytest tests
```

`tests/conftest.py` takes the decision model's key out of the environment for every test, so no test can send code across the network, whatever the shell running the tests holds.

## 3. Placement

Which part does the subject live in? Its row in section 1 gives the tier. When it is not obvious, run the litmus tests below in order: the first one it passes is the tier. A test imports only what the part its folder mirrors may import (architecture.md, section 5), not all that its tier may touch.

### 3.1 unit

> [!TIP]
> **Litmus test.** Does it call one part's own code directly, with nothing wired, and check its answer?

### 3.2 integration

> [!TIP]
> **Litmus test.** Does it drive a controller around fakes and check the Result it returns?

### 3.3 wired

> [!TIP]
> **Litmus test.** Does it need the whole app, as bootstrap/ wires it, to mean anything?

### 3.4 guard

> [!TIP]
> **Litmus test.** Does it run the wired check on xarch's own source?

## 4. Examples

Each example is a short version of a real test, kept in `docs/examples/tests/`. As on the architecture page, it imports from `app.`: read `app.` as `xarch.`. The unit example tests the `cycles` rule of architecture.md, section 8.5, and the guard example runs the wiring of section 6 there on xarch's own source.

```python
# unit: tests/modules/rules/application/logic/test_cycles.py
"""Cycles among modules: a module whose adapter wraps another's controller depends on it, and a ring of them is one
cycle, named from its module first by name."""
import pytest
from app.modules.rules.application.logic.cycles import cycles


@pytest.mark.parametrize("wraps, found", [
    pytest.param({"review": frozenset({"rules"}), "rules": frozenset({"spec"})}, (),
                 id="modules that wrap each other in one direction are no cycle"),
    pytest.param({"a": frozenset({"b"}), "b": frozenset({"a"})}, (("a", "b"),),
                 id="two modules that wrap each other are one cycle"),
    pytest.param({"c": frozenset({"a"}), "b": frozenset({"c"}), "a": frozenset({"b"})}, (("a", "b", "c"),),
                 id="a ring of three is one cycle, named from its module first by name"),
])
def test_cycles(wraps, found) -> None:
    assert cycles(wraps) == found

# guard: tests/architecture/test_self_check.py
"""xarch's own source follows the architecture it enforces: the one architecture.yaml at the repository root
describes."""
from pathlib import Path

import app
from app.bootstrap.wiring import build_controllers
from app.modules.rules.contract import AppChecked, CheckApp

SRC = Path(app.__file__).parent


def test_xarch_has_no_violations_in_its_own_source() -> None:
    checked = build_controllers().rules.check(CheckApp(SRC, str(SRC.parent / "architecture.yaml")))
    assert isinstance(checked, AppChecked) and checked.violations == () and checked.cycles == ()
```

The integration and wired tiers have no example here: `docs/examples/` holds no fake and no profile for one to build on. `tests/modules/layout/application/test_structure.py` is a short integration test to read instead.

## 5. Files

### 5.1 One file per

| Tier | One file per | Its cases come from |
|---|---|---|
| unit | file of the part it mirrors | a table of the rule's inputs and its answer, or of an adapter's input and what it translates it to |
| integration | use case | a Given / When / Then table: a row for every `Result` variant |
| wired | command, or feature of the profile file | what a command prints, or what a check finds in the files a test writes |
| guard | what xarch holds itself to | xarch's own source, tests and files |

### 5.2 Tables

Tests that share a shape are one table: one test function, one `pytest.param` per case, its `id` a sentence that states the outcome. A use case's test is a table with the columns `given`, `when` and `then`, and it is the integration tier's alone:

| Column | Holds |
|---|---|
| `given` | the state the fakes start with: the files of a source tree, the profiles spec would give |
| `when` | the use case's command, from the module's `contract/` |
| `then` | the `Result` variant that comes back |

The rows hold one `then` per variant at least, happy and unhappy. The body has no branch or loop: it builds the controller around `given`, calls it with `when` and asserts `== then`. A case that does not fit the shape is a standalone test beside the table, named for its outcome. A unit table names its columns for what they hold, a rule's inputs and its answer, as `test_cycles` does in section 4.

## 6. Fakes

A port is stood in for by a fake: an in-memory implementation in `tests/fakes/`, named `Fake` and the port's name, such as `FakeSourceTree` or `FakeDisk`, which takes its starting state when it is built. That state is what a row's `given` holds. A fake is not an adapter, and no integration test uses an adapter. Where a module's controller needs several fakes, `tests/modules/<module>/application/helpers.py` builds it around them the way `bootstrap/` builds the real one around adapters.

## 7. Data

A test builds the state it needs, so the reader sees all of it. No tier runs a shared seed.

| Tier | Where its data comes from |
|---|---|
| unit | built in the test; a rule's inputs are the columns of its table |
| integration | the `given` column: the state the fakes start with |
| wired | files written in a temporary folder by the test, and the bundled profiles as they ship |
| guard | none: the repository as it is |

## 8. Guards

`xarch check` runs every guard below on xarch's source and on `tests/`. `tests/architecture/test_self_check.py` runs it in the test suite, plainly and in `--strict` mode, so a broken rule fails the build.

- `structure`: every folder and file of the layout exists, in the app and in every `modules/<name>/`.
- `rules`: every import between parts is one that the `may_import` of the importing part allows (architecture.md, section 5).
- `libraries`: a part imports only the outside packages listed for it (`adapters/`: ast, tokenize; `platform/`: yaml; `cli/`: typer); the standard library is always allowed but what `reserved` names (`ast`: only the reader adapter parses the checked language, so that another language needs one new reader; `tokenize`: only the reader adapter reads the checked language's tokens), and tests are not checked.
- `never-use`: a part neither imports nor uses by name what its `uses.never` list names (`domain/`, `application/logic/`, `application/ports/`, `cli/reports/`, `profile_values/`, `kernel/logic/` and `kernel/`: `datetime.datetime.now`, `datetime.datetime.utcnow`, `datetime.datetime.today`, `datetime.date.today`, `time.time`, `time.time_ns`, `time.monotonic`, `time.perf_counter`, `builtins.open`, `builtins.print`, `builtins.input`, `sys.stdin`, `sys.stdout`, `sys.stderr`, `os.environ`, `os.getenv`, `socket`, `subprocess`, `sqlite3`, `urllib`, `http`, `shutil`, `pathlib.Path.cwd`, `pathlib.Path.absolute`, `os.getcwd`, `os.path.abspath`, `os.path.realpath`, `pathlib.Path.resolve`, `pathlib.Path.home`, `pathlib.Path.expanduser`, `os.path.expanduser`, `os.getcwdb`, `os.chdir`; `application/services/`, `application/controller.py` and `adapters/`: `pathlib.Path.cwd`, `pathlib.Path.absolute`, `pathlib.Path.resolve`, `pathlib.Path.home`, `pathlib.Path.expanduser`, `os.getcwd`, `os.getcwdb`, `os.chdir`, `os.path.abspath`, `os.path.realpath`, `os.path.expanduser`, `.absolute()`, `.resolve()`, `.expanduser()`, `.chdir()`, `os.environ`, `os.getenv`; `platform/`, `cli/` and `__main__.py`: `os.environ`, `os.getenv`; `contract/`: `datetime.datetime.now`, `datetime.datetime.utcnow`, `datetime.datetime.today`, `datetime.date.today`, `time.time`, `time.time_ns`, `time.monotonic`, `time.perf_counter`, `builtins.open`, `builtins.print`, `builtins.input`, `sys.stdin`, `sys.stdout`, `sys.stderr`, `os.environ`, `os.getenv`, `socket`, `subprocess`, `sqlite3`, `urllib`, `http`, `shutil`, `pathlib.Path.cwd`, `pathlib.Path.absolute`, `os.getcwd`, `os.path.abspath`, `os.path.realpath`, `pathlib.Path.resolve`, `pathlib.Path.home`, `pathlib.Path.expanduser`, `os.path.expanduser`, `os.getcwdb`, `os.chdir`, `typing.Any`), and neither do the unit and integration tests of those parts. It catches what is written in the part's own files, through their imports and aliases, and a method written `.name()` called on anything but the object itself and what it holds; not a name reached through a variable or `getattr`, nor I/O done on the part's behalf elsewhere.
- `tiers`: a test lives in the folder that mirrors its subject in the app, and imports only that part and what it may import (a test in a folder that mirrors no part, its tier's subject and what that may import); only a test whose tier tests `application/ports/` imports the fakes in `tests/fakes/`; it imports no other test file.
- `types-only`: a wired test uses `domain/`, `application/logic/`, `application/ports/`, `application/services/`, `application/controller.py`, `adapters/` and `platform/` only as a type: it may import it and annotate with it, and never calls it.
- `types-only`: a guard test uses `domain/`, `application/logic/`, `application/ports/`, `application/services/`, `application/controller.py`, `adapters/` and `platform/` only as a type: it may import it and annotate with it, and never calls it.
- `plain tables`: no table test of the unit and integration tests holds a branch in its body: no `if`, `match`, `try`, `for` or `while` statement and no `if` expression.
- `test tree`: every folder below `tests/modules/` mirrors a folder of the app.
- `cycles`: no `modules/<name>/` imports from another that imports, directly or through others, from it; each cycle is reported once, with the imports that close it.
- `must-import`: every file of `adapters/` imports from `platform/`, any module's `contract/`, or an outside package, or reaches one through a file of its own part; a package file and a file with no code of its own are exempt.
- `must-import`: every integration test imports from `application/controller.py`, directly or through test code that is no test file.
- `must-import`: every wired test imports from `bootstrap/`, directly or through test code that is no test file.
- `holds`: a file of `domain/`, `application/ports/`, `application/services/`, `application/controller.py`, `adapters/`, `profile_values/` and `kernel/` defines classes, never a public function at the top level; a file of `application/logic/`, `cli/reports/` and `kernel/logic/` defines functions, never a class (a private one too) but exceptions and the records its functions return; listed in the enforcement section, and fails `check --strict` only.
- `immutable`: every class of `application/logic/`, `cli/reports/` and `kernel/logic/` is an immutable record, as the Python data file marks one, or an exception; listed in the enforcement section, and fails `check --strict` only.
- `no-callbacks`: no function of `domain/` and `application/logic/` calls a parameter annotated as a callable: it is handed values, never a way to fetch them.
- `names`: every class of `application/services/` is named `*Service`.
- `names`: every class of `application/controller.py` is named `*Controller`.
- `shared`: every public name of `profile_values/` is used by at least 2 users (each instance of a repeating folder, or each part outside them; tests not read), or it belongs to the one that uses it.
- `shared`: every public name of `kernel/logic/` is used by at least 2 users (each instance of a repeating folder, or each part outside them; tests not read), or it belongs to the one that uses it.
- `shared`: every public name of `kernel/` is used by at least 2 users (each instance of a repeating folder, or each part outside them; tests not read), or it belongs to the one that uses it.
- `built-by`: only code of `bootstrap/` builds a class of `application/services/`; tests are not read.
- `built-by`: only code of `bootstrap/` builds a class of `application/controller.py`; tests are not read.
- `built-by`: only code of `bootstrap/` builds a class of `adapters/`; tests are not read.
- `package-only`: `contract/` is imported as a package, never by its files, from outside it.
- `scenario-coverage`: every variant of a union named `<Name>Result` in `contract/` is the `then` of a row of the table (columns `given`, `when`, `then`) in `test_<name>.py` among the integration tests (section 5.2), or is named by a standalone test of that file; every row is a `pytest.param` with an `id`, and a table test has no `if`, `match`, `try`, `for` or `while` statement and no `if` expression.
- `no-comments`: no `#` comments in the app or its tests; docstrings and tool directives (`# type: ignore`, `# noqa`, `# pragma:`) stay.
- `closed-tree`: every Python file of the app lies in a part, or is the package file (`__init__.py`) of a folder of the layout.
- `stand-ins`: every `Protocol` in `application/ports/` is fire-only (every method returns `None`) or read (any method returns a value), each method annotated; every read port `<Port>` has a fake `Fake<Port>` in `tests/fakes/`; and every mock in the integration tests names what it stands in for, `Mock(spec=<Port>)` (or, from a fixture, `mocker.Mock(spec=<Port>)`), never a read port (section 6).
- `no-duplicates`: no two functions of the app have the same code, names and formatting aside, when each holds at least 4 statements; tests are not compared.
- `no-twins`: no two public classes in parts of different names declare the same fields in the same order, when each declares at least 2; types and defaults aside, tests not read. Nor is one a copy of another that renames some of its fields (from 3 fields: more than half of its names kept in place, and each renamed field's type), or that keeps at least half of its fields in its order (from 3 fields). A pair is no twin when a file of `adapters/` builds one of the two through an import, imports the other, and holds one function that names both: a translation, which every check names in its enforcement section.
- `dead-code`: every `Protocol` in `application/ports/` is named by another file of the app, and every fake in `tests/fakes/` by a test; the wiring and re-exports do not count. A file of a part with a tier that no test of that tier reaches, directly or through files of parts of the same tier, is listed in the enforcement section, and fails `check --strict` only. A public class or function of the app that no other file of the app names, so that only the tests use it, or nothing does, is listed in the enforcement section, and fails `check --strict` only. `bootstrap/wiring.py:load_architecture` is accepted as only the tests' (`guards.dead-code.known`) and named in the enforcement section instead; an entry that no longer holds is listed.
- `pass-through`: a method of `application/services/`, `application/controller.py` and `adapters/` whose whole body forwards to one call on a collaborator, or returns an attribute of what that call answers, is listed in the enforcement section, and fails `check --strict` only.
- `private-imports`: no file of the app or its tests imports a name that starts with `_` from another file of them.

The other files of `tests/architecture/` hold xarch to what no key of the profile says, among them: that its code names no part of a bundled profile, that the README lists every option of every command, and that `ruff.toml` stays the bundled linter config plus the repository's own exclusions.
