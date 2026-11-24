"""The libraries and guards of the bundled profiles, loaded through the wiring."""
import pytest

from xarch.bootstrap.wiring import build_controllers, load_architecture
from xarch.modules.spec.contract import GuardsView
from xarch.modules.spec.domain.values import NoCallbacks
from xarch.profile_values.testing import Fakes, Fixture, Framework, Place, RowId, ScenarioCoverage, StandIns, TableForm
from xarch.profile_values.testing import TestForm as DeclaredForm


@pytest.mark.parametrize("name, expected", [
    ("web", {"platform": ("sqlmodel",), "adapters": ("sqlmodel",), "web": ("fastapi",),
             "bootstrap": ("sqlmodel", "fastapi", "uvicorn")}),
    ("cli", {"platform": ("sqlmodel",), "adapters": ("sqlmodel",), "cli": ("typer",),
             "bootstrap": ("sqlmodel", "typer")}),
])
def test_the_bundled_profiles_list_the_libraries_their_examples_use(name, expected):
    profile = build_controllers().spec.profile(name)
    assert {part: packages for part, packages in (profile.imports_libraries or {}).items() if packages} == expected


@pytest.mark.parametrize("name", ["cli", "web"])
def test_the_bundled_profiles_use_every_guard_of_their_own(name):
    mocks = ("Mock", "MagicMock", "AsyncMock", "NonCallableMock", "NonCallableMagicMock")
    form = TableForm(Place(0, "argnames"), Place(1, "argvalues"), ("pytest", "param"), RowId(keyword="id"),
                     decorator=("pytest", "mark", "parametrize"))
    profile = build_controllers().spec.profile(name)
    assert profile.guards == GuardsView(
        package_only=("contract",),
        scenarios=ScenarioCoverage("contract", "integration", "Result", ("given", "when", "then"), "test_{name:snake}.py"),
        no_comments=True,
        closed_tree=True,
        stand_ins=StandIns(tuple(("unittest", "mock", m) for m in mocks), (("unittest", "mock", "create_autospec"),),
                               ("spec", "spec_set"), (Fixture("mocker", mocks, ("create_autospec",)),), 0),
        no_duplicates=4, no_twins=3, no_twins_renamed=3, no_twins_subset=3, dead_code=True, untested=True,
        pass_through=("services", "controller", "adapters"), no_callbacks=("domain", "logic"),
        private_imports=True)
    skips = ("pytest.mark.skip", "pytest.mark.skipif", "pytest.mark.xfail", "pytest.skip", "pytest.xfail",
             "pytest.importorskip", "unittest.skip", "unittest.skipIf", "unittest.skipUnless", "unittest.expectedFailure")
    assert profile.framework == Framework(("test_*.py", "*_test.py"), (DeclaredForm(function="test_*"),),
                                              tuple(tuple(s.split(".")) for s in skips), (form,))
    assert [(file.path, file.pinned) for file in load_architecture(name).files] == [
        (("tests", "architecture", "test_rules.py"), True), (("AGENTS.md",), False), (("ruff.toml",), False)]
    assert profile.fakes == Fakes(("fakes",), ("ports",), "Fake")


@pytest.mark.parametrize("name", ["cli", "web"])
def test_the_bundled_profiles_write_no_callbacks_as_a_guard_of_domain_and_logic(name):
    architecture = load_architecture(name)
    assert [guard.parts for guard in architecture.guards if isinstance(guard, NoCallbacks)] == [("domain", "logic")]
    assert not any(hasattr(part, "no_callbacks") for part in architecture.parts.values())


PURE = ["datetime.datetime.now", "datetime.datetime.utcnow", "datetime.datetime.today", "datetime.date.today",
        "time.time", "time.time_ns", "time.monotonic", "time.perf_counter", "builtins.open", "builtins.print",
        "builtins.input", "sys.stdin", "sys.stdout", "sys.stderr", "os.environ", "os.getenv", "socket", "subprocess",
        "sqlite3", "urllib", "http", "shutil", "pathlib.Path.cwd", "pathlib.Path.absolute", "os.getcwd",
        "os.path.abspath", "os.path.realpath", "pathlib.Path.resolve", "pathlib.Path.home", "pathlib.Path.expanduser",
        "os.path.expanduser", "os.getcwdb", "os.chdir"]
AMBIENT = ["pathlib.Path.cwd", "pathlib.Path.absolute", "pathlib.Path.resolve", "pathlib.Path.home",
           "pathlib.Path.expanduser", "os.getcwd", "os.getcwdb", "os.chdir", "os.path.abspath", "os.path.realpath",
           "os.path.expanduser", ".absolute()", ".resolve()", ".expanduser()", ".chdir()", "os.environ", "os.getenv"]
ENVIRONMENT = ["os.environ", "os.getenv"]
PUBLISHED = PURE + ["typing.Any"]


@pytest.mark.parametrize("name", ["cli", "web"])
def test_the_bundled_profiles_forbid_the_clock_and_io_in_the_pure_parts_and_their_unit_tests(name):
    architecture = load_architecture(name)
    pure = tuple(tuple(n.split(".")) for n in PURE)
    ambient = tuple(tuple(n.split(".")) for n in AMBIENT)
    environment = tuple(tuple(n.split(".")) for n in ENVIRONMENT)
    published = tuple(tuple(n.split(".")) for n in PUBLISHED)
    assert architecture.uses_never == {"domain": pure, "logic": pure, "ports": pure, "services": ambient,
                                       "controller": ambient, "adapters": ambient, "platform": environment,
                                       name: environment, "contract": published, "kernel": pure, "kernel-logic": pure}
    assert [tier.name for tier in architecture.tiers if tier.apply_never] == ["unit"]


def test_the_testing_doc_writes_a_line_per_derived_check_and_per_guard():
    testing = next(f.template for f in build_controllers().spec.docs("web").files if f.path == ("testing.md",))
    section = testing.split("\n\n## 9. Guards\n\n", 1)[1].split("\n\n")[1]
    assert section == "\n".join([
        "- `structure`: every folder and file of the layout exists, in the app and in every `modules/<name>/`.",
        "- `may-import`: every import between parts is one that the `imports.may` of the importing part allows "
        "(architecture.md, section 5).",
        "- `libraries`: a part imports only the outside packages listed for it (`adapters/`: sqlmodel; "
        "`platform/`: sqlmodel; `web/`: fastapi; `bootstrap/`: sqlmodel, fastapi, uvicorn); the standard library "
        "is always allowed, and tests are not checked.",
        "- `never-use`: a part neither imports nor uses by name what its `uses.never` list names (`domain/`, "
        "`application/logic/`, `application/ports/`, `kernel/logic/` and `kernel/`: "
        + ", ".join(f"`{n}`" for n in PURE) + "; `application/services/`, `application/controller.py` and `adapters/`: "
        + ", ".join(f"`{n}`" for n in AMBIENT) + "; `platform/` and `web/`: "
        + ", ".join(f"`{n}`" for n in ENVIRONMENT) + "; `contract/`: "
        + ", ".join(f"`{n}`" for n in PUBLISHED)
        + "), and neither do the unit tests of those parts. It catches what is written in the part's own files, "
        "through their imports and aliases, and a method written `.name()` called on anything but the object itself "
        "and what it holds; not a name reached through a variable or `getattr`, nor I/O done on the part's behalf "
        "elsewhere.",
        "- `tiers`: a test lives in the folder that mirrors its subject in the app, and imports only that part and "
        "what it may import (a test in a folder that mirrors no part, its tier's subject and what that may import); "
        "only a test whose tier tests `application/ports/` imports the fakes in `tests/fakes/`; it imports no other "
        "test file.",
        "- `types-only`: a rendering test uses `application/controller.py` only as a type: it may import it and "
        "annotate with it, and never calls it.",
        "- `test tree`: every folder below `tests/modules/` mirrors a folder of the app.",
        "- `cycles`: no `modules/<name>/` imports from another that imports, directly or through others, from it; "
        "each cycle is reported once, with the imports that close it.",
        "- `must-import`: every file of `adapters/` imports from `platform/`, any module's `contract/`, or an outside "
        "package, or reaches one through a file of its own part; a package file and a file with no code of its own "
        "are exempt.",
        "- `holds`: a file of `domain/`, `application/ports/`, `application/services/`, `application/controller.py` "
        "and `adapters/` defines classes, never a public function at the top level; a file of `application/logic/` "
        "and `kernel/logic/` defines functions, never a class (a private one too) but exceptions and the records its "
        "functions return; listed in the enforcement section, and fails `check --strict` only.",
        "- `immutable`: every record of `application/logic/` and `kernel/logic/` is an immutable record, as the Python "
        "data file marks one; listed in the enforcement section, and fails `check --strict` only.",
        "- `names`: every class of `application/services/` is named `*Service`.",
        "- `names`: every class of `application/controller.py` is named `*Controller`.",
        "- `built-by`: only code of `bootstrap/` builds a class of `application/services/`; tests are not read.",
        "- `built-by`: only code of `bootstrap/` builds a class of `application/controller.py`; tests are not read.",
        "- `built-by`: only code of `bootstrap/` builds a class of `adapters/`; tests are not read.",
        "- `package-only`: `contract/` is imported as a package, never by its files, from outside it.",
        "- `scenario-coverage`: every variant of a union named `<Name>Result` in `contract/` is the `then` of a row "
        "of the table (columns `given`, `when`, `then`) in `test_<name>.py` among the integration tests (section "
        "5.2), or is named by a standalone test of that file; every row is a `pytest.param` with an `id`, and a "
        "table test has no `if`, `match`, `try`, `for` or `while` statement and no `if` expression.",
        "- `no-comments`: no `#` comments in the app or its tests; docstrings and tool directives "
        "(`# type: ignore`, `# noqa`, `# pragma:`) stay.",
        "- `closed-tree`: every Python file of the app lies in a part, or is the package file (`__init__.py`) of a "
        "folder of the layout.",
        "- `stand-ins`: every `Protocol` in `application/ports/` is fire-only (every method returns `None`) or read "
        "(any method returns a value), each method annotated; every read port `<Port>` has a fake `Fake<Port>` in "
        "`tests/fakes/`; and every mock in the integration tests names what it stands in for, `Mock(spec=<Port>)` "
        "(or, from a fixture, `mocker.Mock(spec=<Port>)`), never a read port (section 6).",
        "- `no-duplicates`: no two functions of the app have the same code, names and formatting aside, when each "
        "holds at least 4 statements; tests are not compared.",
        "- `no-twins`: no two public classes in parts of different names declare the same fields in the same order, "
        "when each declares at least 3; types and defaults aside, tests not read. Nor is one a copy of another that "
        "renames some of its fields (from 3 fields: more than half of its names kept in place, and each renamed "
        "field's type), or that keeps at least half of its fields in its order (from 3 fields).",
        "- `dead-code`: every `Protocol` in `application/ports/` is named by another file of the app, and every fake "
        "in `tests/fakes/` by a test; the wiring and re-exports do not count. A file of a part with a tier that no "
        "test of that tier reaches, directly or through files of parts of the same tier, is listed in the "
        "enforcement section, and fails `check --strict` only.",
        "- `pass-through`: a method of `application/services/`, `application/controller.py` and `adapters/` whose "
        "whole body forwards to one call on a collaborator, or returns an attribute of what that call answers, is "
        "listed in the enforcement section, and fails `check --strict` only.",
        "- `no-callbacks`: no function of `domain/` and `application/logic/` calls a parameter annotated as a "
        "callable: it is handed values, never a way to fetch them.",
        "- `private-imports`: no file of the app or its tests imports a name that starts with `_` from another file "
        "of them.",
    ])


@pytest.mark.parametrize("name", ["cli", "web"])
def test_the_bundled_profiles_say_that_an_adapter_reaches_the_platform_or_wraps_another_module_s_contract(name):
    architecture = load_architecture(name)
    assert {n: [(t.part, t.scope) for t in p.imports_must] for n, p in architecture.parts.items() if p.imports_must} == {
        "adapters": [("platform", "none"), ("contract", "any")]}
