"""The `libraries` and `guards` keys of an architecture file: what each part may import from outside, and which
pre-built checks are in use."""
import pytest

from xarch.bootstrap.wiring import load_architecture
from xarch.modules.spec.domain.architecture_file import GUARDS, parse_architecture
from xarch.modules.spec.domain.docs_template import fill
from xarch.modules.spec.domain.errors import InvalidArchitecture
from xarch.modules.spec.domain.values import Fakes, NoComments, PackageOnly, ScenarioCoverage


def layered(**extra) -> dict:
    return {
        "xarch": 1, "name": "layered",
        "layout": {"src": {"singular": "module", "each": {"contract": {}, "service": {}, "store": {}}}},
        "parts": {"contract": {"path": "src/*/contract", "role": "what callers send and get back"},
                  "service": {"path": "src/*/service", "role": "business logic"},
                  "store": {"path": "src/*/store", "role": "database access"}},
        "rules": {"service": ["service@own", "store@own", "contract@own"], "store": ["store@own"]},
        **extra,
    }


def load(document):
    return parse_architecture(document, "layered.yaml", lambda relative: True)


def problems(document) -> list[str]:
    with pytest.raises(InvalidArchitecture) as caught:
        load(document)
    return list(caught.value.problems)


def test_libraries_give_each_part_its_outside_packages_and_an_unlisted_part_none():
    architecture = load(layered(libraries={"store": ["sqlmodel", "sqlalchemy"], "service": []}))
    assert architecture.libraries == {"contract": (), "service": (), "store": ("sqlmodel", "sqlalchemy")}


def test_without_libraries_outside_packages_are_not_checked():
    assert load(layered()).libraries is None


@pytest.mark.parametrize("libraries, problem", [
    ({"nowhere": ["x"]}, "libraries.nowhere: no part named 'nowhere'"),
    ({"store": "sqlmodel"}, "libraries.store: must be a list of top-level import names, such as [sqlmodel]"),
    ({"store": ["sql-model"]}, "libraries.store: 'sql-model' is not a top-level import name, such as sqlmodel"),
    ({"store": ["sqlalchemy.orm"]}, "libraries.store: 'sqlalchemy.orm' is not a top-level import name, such as sqlmodel"),
    ({"store": ["json"]}, "libraries.store: 'json' is in the standard library, which every part may import"),
    ({"store": ["x", "x"]}, "libraries.store: 'x' is listed twice"),
    (["store"], "libraries: must be a mapping of part names to lists of top-level import names"),
])
def test_a_bad_libraries_entry_is_rejected(libraries, problem):
    assert problems(layered(libraries=libraries)) == [f"layered.yaml: {problem}"]


TIERS = [{"name": "wired", "subject": ["service", "contract", "store"], "proves": "a use case", "may_touch": "all",
          "litmus": "Does it run a use case?"}]


def test_guards_name_the_pre_built_checks_in_use_with_their_parameters():
    document = layered(tiers=TIERS, guards={"no-comments": {}, "package-only": ["contract"],
                                            "scenario-coverage": {"results": "contract", "tier": "wired",
                                                                  "suffix": "Outcome"}})
    assert load(document).guards == (NoComments(), PackageOnly(("contract",)),
                                     ScenarioCoverage("contract", "wired", "Outcome"))
    assert load(layered()).guards == ()


def test_the_pre_built_checks_are_known_by_name_with_one_line_each():
    assert list(GUARDS) == ["package-only", "scenario-coverage", "no-comments"]
    assert all(text and "\n" not in text for text in GUARDS.values())


@pytest.mark.parametrize("guards, problem", [
    ({"no-comment": {}}, "guards: unknown guard 'no-comment': use package-only, scenario-coverage, no-comments"),
    ({"no-comments": {"x": 1}}, "guards.no-comments: takes no parameters: write {}"),
    (["no-comments"], "guards: must be a mapping of guard names to their parameters, such as {no-comments: {}}"),
    ({"package-only": ["nowhere"]}, "guards.package-only: no part named 'nowhere'"),
    ({"package-only": "contract"}, "guards.package-only: must be a list of part names"),
    ({"package-only": ["contract", "contract"]}, "guards.package-only: 'contract' is listed twice"),
    ({"scenario-coverage": {"results": "contract"}},
     "guards.scenario-coverage: must be a mapping {results, tier, suffix}: the part holding the result unions, "
     "the tier whose test files hold the scenarios, and how a union's name ends"),
    ({"scenario-coverage": {"results": "nowhere", "tier": "wired", "suffix": "Result"}},
     "guards.scenario-coverage.results: no part named 'nowhere'"),
    ({"scenario-coverage": {"results": "contract", "tier": "unit", "suffix": "Result"}},
     "guards.scenario-coverage.tier: no tier named 'unit'"),
    ({"scenario-coverage": {"results": "contract", "tier": "wired", "suffix": "a b"}},
     "guards.scenario-coverage.suffix: must be the end of a name, such as Result"),
])
def test_a_bad_guards_entry_is_rejected(guards, problem):
    assert problems(layered(tiers=TIERS, guards=guards)) == [f"layered.yaml: {problem}"]


def test_scenario_coverage_needs_its_tier_to_test_the_results_part():
    tiers = [dict(TIERS[0], subject=["service", "store"]),
             {"name": "api", "subject": ["contract"], "proves": "x", "may_touch": "y", "litmus": "z"}]
    guards = {"scenario-coverage": {"results": "contract", "tier": "wired", "suffix": "Result"}}
    assert problems(layered(tiers=tiers, guards=guards)) == [
        "layered.yaml: guards.scenario-coverage.tier: tier 'wired' does not test part 'contract'"]


def test_fakes_name_their_folder_and_the_parts_they_stand_in_for():
    assert load(layered(fakes={"path": "tests/fakes", "for": ["store"]})).fakes == Fakes(("tests", "fakes"), ("store",))
    assert load(layered()).fakes is None


@pytest.mark.parametrize("fakes, problem", [
    ({"path": "tests/fakes"}, "fakes: must be a mapping {path, for}: the folder of the fakes, such as tests/fakes, "
                              "and the parts they stand in for"),
    ({"path": "fakes", "for": ["store"]}, "fakes.path: must be a folder below the tests root, such as tests/fakes"),
    ({"path": "tests/fakes", "for": ["nowhere"]}, "fakes.for: no part named 'nowhere'"),
])
def test_a_bad_fakes_entry_is_rejected(fakes, problem):
    assert problems(layered(fakes=fakes)) == [f"layered.yaml: {problem}"]


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
def test_the_bundled_profiles_use_every_guard(name):
    assert load_architecture(name).guards == (PackageOnly(("contract",)),
                                              ScenarioCoverage("contract", "integration", "Result"), NoComments())
    assert load_architecture(name).fakes == Fakes(("tests", "fakes"), ("ports",))


def test_the_guards_placeholder_writes_a_line_per_derived_check_and_per_guard():
    text = fill("{{guards}}", load_architecture("web"), "web.md")
    assert text.splitlines() == [
        "- `structure`: every folder and file of the layout exists, in the app and in every `modules/<name>/`.",
        "- `rules`: every import between parts is one that `rules` allows (architecture.md, section 5).",
        "- `libraries`: a part imports only the outside packages listed for it (`platform/`: sqlmodel; "
        "`adapters/`: sqlmodel; `web/`: fastapi; `bootstrap/`: sqlmodel, fastapi, uvicorn); the standard library "
        "is always allowed, and tests are not checked.",
        "- `tiers`: a test lives in the folder that mirrors its subject in the app, and imports only its tier's "
        "subject and what that subject may import; only a test whose tier tests `application/ports/` imports the "
        "fakes in `tests/fakes/`.",
        "- `test tree`: every folder below `tests/modules/` mirrors a folder of the app.",
        "- `package-only`: `contract/` is imported as a package, never by its files, from outside it.",
        "- `scenario-coverage`: every variant of a union named `<Name>Result` in `contract/` has a scenario in the "
        "header of `test_<name>.py` among the integration tests (section 5.2), and every scenario has a test of "
        "the same name.",
        "- `no-comments`: no `#` comments in the app or its tests; docstrings and tool directives "
        "(`# type: ignore`, `# noqa`, `# pragma:`) stay.",
    ]


def test_the_guards_placeholder_leaves_out_what_the_architecture_does_not_check():
    text = fill("{{guards}}", load(layered()), "layered.md")
    assert text.splitlines() == [
        "- `structure`: every folder and file of the layout exists, in the app and in every `src/<name>/`.",
        "- `rules`: every import between parts is one that `rules` allows (architecture.md, section 5).",
        "- `test tree`: every folder below `tests/src/` mirrors a folder of the app."]
