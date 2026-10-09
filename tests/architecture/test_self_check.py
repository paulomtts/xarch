"""xarch's own source follows the architecture it enforces: its package root plays the role of app/."""
import shutil
from pathlib import Path

import xarch
from xarch.bootstrap.wiring import build_controllers
from xarch.modules.layout.contract import CheckStructure
from xarch.modules.rules.contract import CheckImports, ImportsChecked

SRC = Path(xarch.__file__).parent


def test_xarch_has_no_import_or_structure_violations():
    controllers = build_controllers()
    imports = controllers.rules.check(CheckImports(SRC, package="xarch"))
    structure = controllers.layout.check(CheckStructure(SRC, package="xarch"))
    assert isinstance(imports, ImportsChecked)
    assert [str(v) for v in imports.violations + structure.violations] == []


def test_xarch_is_split_into_its_four_modules():
    modules = {p.name for p in (SRC / "modules").iterdir() if p.is_dir() and not p.name.startswith("_")}
    assert modules == {"spec", "rules", "layout", "scaffold"}


def test_the_self_check_would_catch_a_broken_rule(tmp_path):
    # Guards against a vacuous pass: the same check on a copy of xarch with one forbidden import fails.
    copy = tmp_path / "xarch"
    shutil.copytree(SRC, copy, ignore=shutil.ignore_patterns("__pycache__"))
    (copy / "modules" / "rules" / "domain" / "bad.py").write_text("from xarch.platform import filesystem\n")
    result = build_controllers().rules.check(CheckImports(copy, package="xarch"))
    assert [str(v) for v in result.violations] == [
        "xarch/modules/rules/domain/bad.py:1: domain/ of module 'rules' may not import platform/ "
        "(xarch.platform.filesystem)"]
