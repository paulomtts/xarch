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
  sub: {{path: sub, role: "the only part", tier: unit}}
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
