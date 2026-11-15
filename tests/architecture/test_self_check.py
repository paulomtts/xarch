"""xarch's own source follows the architecture it enforces: its package root plays the role of app/, and its
architecture is the one its pyproject.toml names, architecture.yaml at the repository root."""
import shutil
from pathlib import Path

import xarch
from xarch.bootstrap.wiring import build_controllers
from xarch.modules.layout.contract import CheckStructure
from xarch.modules.rules.contract import CheckImports, ImportsChecked
from xarch.modules.spec.contract import ProfileSelected, SelectProfile

SRC = Path(xarch.__file__).parent
TESTS = SRC.parent / "tests"


def own_architecture() -> str:
    selected = build_controllers().spec.select(SelectProfile(SRC))
    assert isinstance(selected, ProfileSelected), selected
    return selected.name


def test_xarch_checks_itself_against_its_own_architecture_file():
    assert own_architecture() == str(SRC.parent / "architecture.yaml")


def test_xarch_has_no_violations_in_its_source_or_its_tests():
    controllers = build_controllers()
    imports = controllers.rules.check(CheckImports(SRC, "xarch", own_architecture(), TESTS))
    structure = controllers.layout.check(CheckStructure(SRC, "xarch", own_architecture(), TESTS))
    assert isinstance(imports, ImportsChecked)
    assert [str(v) for v in imports.violations + structure.violations] == []


def test_xarch_is_split_into_its_four_modules():
    modules = {p.name for p in (SRC / "modules").iterdir() if p.is_dir() and not p.name.startswith("_")}
    assert modules == {"spec", "rules", "layout", "scaffold"}


def test_the_self_check_would_catch_a_broken_rule(tmp_path):
    """Guards against a vacuous pass: the same check on a copy of xarch with one forbidden import fails."""
    copy = tmp_path / "xarch"
    shutil.copytree(SRC, copy, ignore=shutil.ignore_patterns("__pycache__"))
    (copy / "modules" / "rules" / "domain" / "bad.py").write_text("from xarch.platform import filesystem\n")
    result = build_controllers().rules.check(CheckImports(copy, "xarch", own_architecture(), TESTS))
    assert [str(v) for v in result.violations] == [
        "xarch/modules/rules/domain/bad.py:1: domain/ of modules/rules may not import platform/ "
        "(xarch.platform.filesystem)"]
