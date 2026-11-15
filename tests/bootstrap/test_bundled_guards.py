"""The libraries and guards of the bundled profiles, loaded through the wiring."""
import pytest

from xarch.bootstrap.wiring import build_architectures, load_architecture
from xarch.modules.spec.contract import (
    CaseTable,
    DeadCode,
    Fixture,
    Framework,
    NoComments,
    NoDuplicates,
    PackageOnly,
    PassThrough,
    ScenarioCoverage,
    StandIns,
)


@pytest.mark.parametrize("name, expected", [
    ("web", {"platform": ("sqlmodel",), "adapters": ("sqlmodel",), "web": ("fastapi",),
             "bootstrap": ("sqlmodel", "fastapi", "uvicorn")}),
    ("cli", {"platform": ("sqlmodel",), "adapters": ("sqlmodel",), "cli": ("typer",),
             "bootstrap": ("sqlmodel", "typer")}),
])
def test_the_bundled_profiles_list_the_libraries_their_examples_use(name, expected):
    architecture = load_architecture(name)
    assert {part: packages for part, packages in (architecture.libraries or {}).items() if packages} == expected


@pytest.mark.parametrize("name", ["cli", "web"])
def test_the_bundled_profiles_use_every_guard_of_their_own(name):
    mocks = ("Mock", "MagicMock", "AsyncMock", "NonCallableMock", "NonCallableMagicMock")
    table = CaseTable(("pytest", "mark", "parametrize"), ("pytest", "param"), "id", ("argnames", "argvalues"))
    assert load_architecture(name).guards == (
        PackageOnly(("contract",)),
        ScenarioCoverage("contract", "integration", "Result", ("given", "when", "then"), table, "test_{name}.py"),
        NoComments(),
        StandIns(tuple(("unittest", "mock", m) for m in mocks), (("unittest", "mock", "create_autospec"),),
                 ("spec", "spec_set"), (Fixture("mocker", mocks, ("create_autospec",)),)),
        NoDuplicates(4), DeadCode(), PassThrough(("services",)))
    skips = ("pytest.mark.skip", "pytest.mark.skipif", "pytest.mark.xfail", "pytest.skip", "pytest.xfail",
             "pytest.importorskip", "unittest.skip", "unittest.skipIf", "unittest.skipUnless", "unittest.expectedFailure")
    assert load_architecture(name).framework == Framework(("test_*.py", "*_test.py"), "test_*",
                                                          tuple(tuple(s.split(".")) for s in skips))
    assert [(file.path, file.pinned) for file in load_architecture(name).files] == [
        (("tests", "architecture", "test_rules.py"), True), (("AGENTS.md",), False), (("ruff.toml",), False)]
    fakes = load_architecture(name).fakes
    assert fakes is not None and (fakes.folder, fakes.stand_in_for, fakes.prefix) == (("fakes",), ("ports",), "Fake")


PURE = ["datetime.datetime.now", "datetime.datetime.utcnow", "datetime.datetime.today", "datetime.date.today",
        "time.time", "time.time_ns", "time.monotonic", "time.perf_counter", "builtins.open", "builtins.print",
        "builtins.input", "sys.stdin", "sys.stdout", "sys.stderr", "os.environ", "os.getenv", "socket", "subprocess",
        "sqlite3", "urllib", "http", "shutil"]


@pytest.mark.parametrize("name", ["cli", "web"])
def test_the_bundled_profiles_forbid_the_clock_and_io_in_the_pure_parts_and_their_unit_tests(name):
    architecture = load_architecture(name)
    pure = tuple(tuple(n.split(".")) for n in PURE)
    assert architecture.forbidden == {part: pure for part in ("domain", "logic", "kernel", "ports", "contract")}
    assert [tier.name for tier in architecture.tiers if tier.forbidden] == ["unit"]


def test_the_testing_doc_writes_a_line_per_derived_check_and_per_guard():
    testing = next(f.template for f in build_architectures().docs("web").files if f.path == ("testing.md",))
    section = testing.split("\n\n## 9. Guards\n\n", 1)[1].split("\n\n")[1]
    assert section == "\n".join([
        "- `structure`: every folder and file of the layout exists, in the app and in every `modules/<name>/`.",
        "- `rules`: every import between parts is one that the `may_import` of the importing part allows "
        "(architecture.md, section 5).",
        "- `libraries`: a part imports only the outside packages listed for it (`adapters/`: sqlmodel; "
        "`platform/`: sqlmodel; `web/`: fastapi; `bootstrap/`: sqlmodel, fastapi, uvicorn); the standard library "
        "is always allowed, and tests are not checked.",
        "- `forbidden`: a part neither imports nor uses by name what is listed for it (`domain/`, "
        "`application/logic/`, `application/ports/`, `contract/` and `kernel/`: " + ", ".join(f"`{n}`" for n in PURE)
        + "), and neither do the unit tests of those parts. It catches what is written in the part's own files, "
        "through their imports and aliases, not a name reached through a variable or `getattr`, nor I/O done on the "
        "part's behalf elsewhere.",
        "- `tiers`: a test lives in the folder that mirrors its subject in the app, and imports only that part and "
        "what it may import (a test in a folder that mirrors no part, its tier's subject and what that may import); "
        "only a test whose tier tests `application/ports/` imports the fakes in `tests/fakes/`.",
        "- `types-only`: a rendering test uses `application/controller.py` only as a type: it may import it and "
        "annotate with it, and never calls it.",
        "- `test tree`: every folder below `tests/modules/` mirrors a folder of the app.",
        "- `cycles`: no `modules/<name>/` imports from another that imports, directly or through others, from it; "
        "each cycle is reported once, with the imports that close it.",
        "- `must-import`: every file of `adapters/` imports from `platform/`, any module's `contract/`, or an outside "
        "package, or reaches one through a file of its own part, so that it touches technology; a package file and "
        "a file with no code of its own are exempt.",
        "- `package-only`: `contract/` is imported as a package, never by its files, from outside it.",
        "- `scenario-coverage`: every variant of a union named `<Name>Result` in `contract/` is the `then` of a row "
        "of the table (columns `given`, `when`, `then`) in `test_<name>.py` among the integration tests (section "
        "5.2), or is named by a standalone test of that file; every row is a `pytest.param` with an `id`, and a "
        "table test has no `if`, `match`, `try`, `for` or `while`.",
        "- `no-comments`: no `#` comments in the app or its tests; docstrings and tool directives "
        "(`# type: ignore`, `# noqa`, `# pragma:`) stay.",
        "- `stand-ins`: every `Protocol` in `application/ports/` is fire-only (every method returns `None`) or read "
        "(any method returns a value), each method annotated; every read port `<Port>` has a fake `Fake<Port>` in "
        "`tests/fakes/`; and every mock in the integration tests names what it stands in for, `Mock(spec=<Port>)` "
        "(or, from a fixture, `mocker.Mock(spec=<Port>)`), never a read port (section 6).",
        "- `no-duplicates`: no two functions of the app have the same code, names and formatting aside, when each "
        "holds at least 4 statements; tests are not compared.",
        "- `dead-code`: every `Protocol` in `application/ports/` is named by another file of the app, and every fake "
        "in `tests/fakes/` by a test; the wiring and re-exports do not count.",
        "- `pass-through`: a method of `application/services/` whose whole body forwards to one call on a "
        "collaborator is listed in the enforcement section, and fails `check --strict` only.",
    ])


@pytest.mark.parametrize("name", ["cli", "web"])
def test_the_bundled_profiles_say_that_an_adapter_reaches_the_platform_or_wraps_another_module_s_contract(name):
    architecture = load_architecture(name)
    assert {n: [(t.part, t.scope) for t in p.must_import] for n, p in architecture.parts.items() if p.must_import} == {
        "adapters": [("platform", "none"), ("contract", "any")]}
