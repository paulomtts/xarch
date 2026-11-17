"""xarch's own source follows the architecture it enforces: the one architecture.yaml at the repository root
describes."""
from pathlib import Path

import app
from app.bootstrap.wiring import build_controllers
from app.modules.rules.contract import AppChecked, CheckApp

SRC = Path(app.__file__).parent


def test_xarch_has_no_violations_in_its_own_source() -> None:
    checked = build_controllers().rules.check(CheckApp(SRC, str(SRC.parent / "architecture.yaml")))
    assert isinstance(checked, AppChecked) and checked.violations == () and checked.cycles == ()
