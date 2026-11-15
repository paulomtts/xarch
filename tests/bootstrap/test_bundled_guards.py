"""The libraries and guards of the bundled profiles, loaded through the wiring."""
import pytest

from xarch.bootstrap.wiring import load_architecture
from xarch.modules.spec.domain.docs_template import fill
from xarch.modules.spec.domain.values import Fakes, NoComments, PackageOnly, ScenarioCoverage, StandIns


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
    assert load_architecture(name).guards == (PackageOnly(("contract",)),
                                              ScenarioCoverage("contract", "integration", "Result",
                                                                  ("given", "when", "then")), NoComments(),
                                              StandIns())
    assert load_architecture(name).fakes == Fakes(("tests", "fakes"), ("ports",), "Fake")


def test_the_guards_placeholder_writes_a_line_per_derived_check_and_per_guard():
    text = fill("{{guards}}", load_architecture("web"), "web.md")
    assert text.splitlines() == [
        "- `structure`: every folder and file of the layout exists, in the app and in every `modules/<name>/`.",
        "- `rules`: every import between parts is one that `rules` allows (architecture.md, section 5).",
        "- `libraries`: a part imports only the outside packages listed for it (`platform/`: sqlmodel; "
        "`adapters/`: sqlmodel; `web/`: fastapi; `bootstrap/`: sqlmodel, fastapi, uvicorn); the standard library "
        "is always allowed, and tests are not checked.",
        "- `tiers`: a test lives in the folder that mirrors its subject in the app, and imports only that part and "
        "what it may import (a test in a folder that mirrors no part, its tier's subject and what that may import); "
        "only a test whose tier tests `application/ports/` imports the fakes in `tests/fakes/`.",
        "- `types-only`: a rendering test uses `application/controller.py` only as a type: it may import it and "
        "annotate with it, and never calls it.",
        "- `test tree`: every folder below `tests/modules/` mirrors a folder of the app.",
        "- `cycles`: no `modules/<name>/` imports from another that imports, directly or through others, from it; "
        "each cycle is reported once, with the imports that close it.",
        "- `package-only`: `contract/` is imported as a package, never by its files, from outside it.",
        "- `scenario-coverage`: every variant of a union named `<Name>Result` in `contract/` is the `then` of a row "
        "of the table (columns `given`, `when`, `then`) in `test_<name>.py` among the integration tests (section "
        "5.2), or is named by a standalone test of that file; every row is a `pytest.param` with an `id`, and a "
        "table test has no `if`, `match`, `try`, `for` or `while`.",
        "- `no-comments`: no `#` comments in the app or its tests; docstrings and tool directives "
        "(`# type: ignore`, `# noqa`, `# pragma:`) stay.",
        "- `stand-ins`: every `Protocol` in `application/ports/` is fire-only (every method returns `None`) or read "
        "(any method returns a value), each method annotated; every read port `<Port>` has a fake `Fake<Port>` in "
        "`tests/fakes/`; and every mock in the integration tests names what it stands in for, `Mock(spec=<Port>)`, "
        "never a read port (section 6).",
    ]
