"""xarch's own source follows the architecture it enforces: its package root plays the role of app/, and its
architecture is the one its pyproject.toml names, architecture.yaml at the repository root."""
import json
import shutil
from pathlib import Path

import pytest
from typer.testing import CliRunner

import xarch
from xarch.bootstrap.app import app
from xarch.bootstrap.wiring import build_controllers
from xarch.modules.layout.contract import CheckStructure
from xarch.modules.rules.contract import CheckImports, ImportsChecked
from xarch.modules.spec.contract import AppChosen, ChooseApp, ProfileSelected, SelectProfile

SRC = Path(xarch.__file__).parent
TESTS = SRC.parent / "tests"
REFACTOR_PENDING = pytest.mark.xfail(
    strict=True,
    reason="branch refactor/profile-consistency, second round: the checks that close the loopholes the audits found "
           "(pass-through on a returned attribute of a forwarded call) are on in architecture.yaml, and xarch's own "
           "code breaks them until it is refactored. Remove this mark once `uv run xarch check --strict` passes on "
           "xarch.")


def own_architecture() -> str:
    selected = build_controllers().spec.select(SelectProfile(SRC))
    assert isinstance(selected, ProfileSelected), selected
    return selected.name


def test_xarch_checks_itself_against_its_own_architecture_file():
    assert own_architecture() == str(SRC.parent / "architecture.yaml")


def test_xarch_records_its_own_app_folder_so_a_bare_check_runs_here():
    assert build_controllers().spec.choose_app(ChooseApp(SRC.parent)) == AppChosen(SRC)


def test_xarch_has_no_violations_in_its_source_or_its_tests():
    controllers = build_controllers()
    imports = controllers.rules.check(CheckImports(SRC, "xarch", own_architecture(), TESTS))
    structure = controllers.layout.check(CheckStructure(SRC, "xarch", own_architecture(), TESTS))
    assert isinstance(imports, ImportsChecked)
    assert [str(v) for v in imports.violations + structure.violations] == []


@REFACTOR_PENDING
def test_xarch_passes_its_own_check_in_strict_mode_leaving_nothing_unenforced():
    result = CliRunner().invoke(app, ["check", "--app", str(SRC), "--strict", "--format", "json"])
    document = json.loads(result.stdout)
    assert (document["violations"], document["enforcement"]["strict_failures"]) == ([], [])
    assert (result.exit_code, document["ok"], document["strict"]) == (0, True, True)
    assert [item["folder"] for item in document["enforcement"]["excluded"]] == ["xarch/architectures/examples"]
    assert document["enforcement"]["profile"]["guards_off"] == []


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
