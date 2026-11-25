"""Where a test with no part to mirror lives is a tier's `folder`, wired: the example of a tier is for the docs and
decides nothing `check` does, so no example, however it is written, can switch the "lies in no tier" report off."""
import pytest

from tests.bootstrap.project import source_check

NO_TIER = ("tests/scripts/test_x.py: lies in no tier: no part's folder and no tier's `folder` is mirrored here; "
           "fix: move it to the folder that mirrors its subject's path in the app, or into a tier's `folder`")

PROFILE = """\
name: min
testing: pytest
parts:
  sub/: {{role: "the only part", tests: unit}}
tiers:
  unit:
    proves: a rule
    litmus: Does it decide?
{tier}
docs: {{examples: [ex]}}
"""
EXAMPLES = ("tests/architecture/test_x.py", "tests/scripts/test_x.py", "tests/test_x.py", "test_x.py")


def check(tmp_path, tier: str, tests: tuple[str, ...]) -> list[str]:
    (tmp_path / "app" / "sub").mkdir(parents=True)
    (tmp_path / "app" / "sub" / "a.py").write_text("x = 1\n")
    for example in EXAMPLES:
        (tmp_path / "ex" / example).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / "ex" / example).write_text("x = 1\n")
    for name in tests:
        (tmp_path / "tests" / name).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / "tests" / name).write_text("x = 1\n")
    (tmp_path / "min.yaml").write_text(PROFILE.format(tier=tier))
    result = source_check(tmp_path / "app", str(tmp_path / "min.yaml"), tmp_path / "tests")
    return [f"{v}; fix: {v.fix}" for v in result.violations]


@pytest.mark.parametrize("tier, tests, expected", [
    pytest.param("    folder: architecture", ("scripts/test_x.py", "architecture/test_x.py"), [NO_TIER],
                 id="a test in a tier's folder has that tier and one outside every folder has none"),
    pytest.param("    folder: architecture\n    docs: {example: tests/architecture/test_x.py}",
                 ("scripts/test_x.py", "architecture/test_x.py"), [NO_TIER],
                 id="an example inside the tier's folder changes nothing"),
    pytest.param("    docs: {example: tests/scripts/test_x.py}", ("scripts/test_x.py",), [NO_TIER],
                 id="an example with no folder places no test, even where it says it would live"),
    pytest.param("    docs: {example: tests/test_x.py}", ("scripts/test_x.py",), [NO_TIER],
                 id="an example directly below the tests folder does not make every test placed"),
    pytest.param("    docs: {example: test_x.py}", ("scripts/test_x.py",), [NO_TIER],
                 id="an example with no tests folder in its path does not make every test placed"),
])
def test_a_test_with_no_part_to_mirror_is_placed_only_by_a_tier_folder(tmp_path, tier, tests, expected):
    assert check(tmp_path, tier, tests) == expected


TIER_FIRST = """\
name: tierfirst
testing: {{preset: pytest{shared}}}
parts:
  sub/: {{role: "the only part", untested: "its tests lie tier first"}}
tiers:
{tiers}
{fakes}"""
UNIT = "  unit:\n    proves: a rule\n    folder: unit\n    imports:\n      may: everything\n"


def tier_first(tmp_path, tests: dict[str, str], shared: str = "", tiers: str = UNIT, fakes: str = "") -> list[str]:
    """The tiers findings of a project whose tests lie tier first, tests/<tier>/, each test file with the text given."""
    (tmp_path / "app" / "sub").mkdir(parents=True)
    (tmp_path / "app" / "sub" / "a.py").write_text("x = 1\n")
    for name, text in tests.items():
        (tmp_path / "tests" / name).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / "tests" / name).write_text(text)
    (tmp_path / "tf.yaml").write_text(TIER_FIRST.format(shared=shared, tiers=tiers, fakes=fakes))
    result = source_check(tmp_path / "app", str(tmp_path / "tf.yaml"), tmp_path / "tests")
    return [f"{v}" for v in result.violations if v.rule == "tiers"]


SHARING = {"support/__init__.py": "", "support/clock.py": "x = 1\n", "helpers.py": "x = 1\n",
           "other/builders.py": "x = 1\n",
           "unit/modules/docs/test_a.py": "from tests.support import clock\nfrom tests.helpers import x\n"
                                          "from tests.other.builders import x as y\n"}


def test_a_tier_first_test_imports_the_shared_test_code_and_nothing_else_outside_its_folder(tmp_path):
    assert tier_first(tmp_path, SHARING, shared=", shared: [support, helpers.py]") == [
        "tests/unit/modules/docs/test_a.py:3: a test may import test code only from its own folder tests/unit/ or the "
        "shared support/, helpers.py (testing.shared) (tests.other.builders)"]


def test_without_shared_the_tier_first_test_is_held_to_its_own_folder(tmp_path):
    assert tier_first(tmp_path, SHARING) == [
        f"tests/unit/modules/docs/test_a.py:{line}: a test may import test code only from its own folder tests/unit/ "
        f"({target})" for line, target in ((1, "tests.support.clock"), (2, "tests.helpers"), (3, "tests.other.builders"))]


FAKING = {"fakes/__init__.py": "", "fakes/repo.py": "x = 1\n", "unit/test_a.py": "from tests.fakes.repo import x\n"}


def test_a_tier_first_test_of_a_tier_fakes_tiers_lists_imports_the_fakes(tmp_path):
    assert tier_first(tmp_path, FAKING, fakes="fakes: {folder: fakes, for: [sub], tiers: [unit]}\n") == []


def test_without_fakes_tiers_a_tier_first_test_may_not_import_the_fakes(tmp_path):
    assert tier_first(tmp_path, FAKING, fakes="fakes: {folder: fakes, for: [sub]}\n") == [
        "tests/unit/test_a.py:1: a unit test may not import the fakes (tests.fakes.repo): only a tier that tests sub "
        "may"]
