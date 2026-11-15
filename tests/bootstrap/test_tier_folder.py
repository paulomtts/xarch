"""Where a test with no part to mirror lives is a tier's `folder`, wired: the example of a tier is for the docs and
decides nothing `check` does, so no example, however it is written, can switch the "lies in no tier" report off."""
import pytest

from xarch.bootstrap.wiring import build_controllers
from xarch.modules.rules.contract import CheckImports, ImportsChecked

NO_TIER = ("tests/scripts/test_x.py: lies in no tier: no part's folder and no tier's `folder` is mirrored here; "
           "fix: move it to the folder that mirrors its subject's path in the app, or into a tier's `folder`")

PROFILE = """\
xarch: 1
name: min
layout: {{sub: {{}}}}
parts: {{sub: {{path: sub, role: "the only part"}}}}
rules: {{}}
tests: {{files: ["test_*.py"], functions: "test_*"}}
tiers:
  - name: unit
    subject: [sub]
    proves: a rule
    may_touch: nothing
    litmus: Does it decide?
{tier}
"""


def check(tmp_path, tier: str, tests: tuple[str, ...]) -> list[str]:
    (tmp_path / "app" / "sub").mkdir(parents=True)
    (tmp_path / "app" / "sub" / "a.py").write_text("x = 1\n")
    (tmp_path / "x.py").write_text("x = 1\n")
    for name in tests:
        (tmp_path / "tests" / name).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / "tests" / name).write_text("x = 1\n")
    (tmp_path / "min.yaml").write_text(PROFILE.format(tier=tier))
    result = build_controllers().rules.check(CheckImports(tmp_path / "app", "app", str(tmp_path / "min.yaml"),
                                                          tmp_path / "tests"))
    assert isinstance(result, ImportsChecked)
    return [f"{v}; fix: {v.fix}" for v in result.violations]


@pytest.mark.parametrize("tier, tests, expected", [
    pytest.param("    folder: architecture", ("scripts/test_x.py", "architecture/test_x.py"), [NO_TIER],
                 id="a test in a tier's folder has that tier and one outside every folder has none"),
    pytest.param("    folder: architecture\n    example: {path: tests/architecture/test_x.py, file: x.py}",
                 ("scripts/test_x.py", "architecture/test_x.py"), [NO_TIER],
                 id="an example inside the tier's folder changes nothing"),
    pytest.param("    example: {path: tests/scripts/test_x.py, file: x.py}", ("scripts/test_x.py",), [NO_TIER],
                 id="an example with no folder places no test, even where it says it would live"),
    pytest.param("    example: {path: tests/test_x.py, file: x.py}", ("scripts/test_x.py",), [NO_TIER],
                 id="an example directly below the tests folder does not make every test placed"),
    pytest.param("    example: {path: test_x.py, file: x.py}", ("scripts/test_x.py",), [NO_TIER],
                 id="an example with no tests folder in its path does not make every test placed"),
])
def test_a_test_with_no_part_to_mirror_is_placed_only_by_a_tier_folder(tmp_path, tier, tests, expected):
    assert check(tmp_path, tier, tests) == expected
