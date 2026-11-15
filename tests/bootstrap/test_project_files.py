"""The files a bundled profile has `init` write beside the app: the guard test is written, passes, and fails on a
violation, whatever the app folder is called."""
import subprocess
import sys
from pathlib import Path

import pytest

from xarch.bootstrap.wiring import build_controllers
from xarch.modules.layout.contract import CheckStructure
from xarch.modules.rules.contract import CheckImports
from xarch.modules.scaffold.contract import Init, Scaffolded

GUARD = Path("tests/architecture/test_rules.py")
PROFILES = ["cli", "web"]


def init(app: Path, profile: str) -> Scaffolded:
    result = build_controllers().scaffold.init(Init(app, profile))
    assert isinstance(result, Scaffolded)
    return result


def pytest_in(project: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", str(GUARD)], cwd=project,
                          capture_output=True, text=True)


@pytest.mark.parametrize("profile", PROFILES)
def test_init_writes_the_guard_test_beside_the_app_and_a_second_init_skips_it(tmp_path, profile):
    first = init(tmp_path / "app", profile).report
    second = init(tmp_path / "app", profile).report
    assert tmp_path / GUARD in first.created and tmp_path / GUARD not in first.skipped
    assert tmp_path / GUARD in second.skipped and tmp_path / GUARD not in second.created


@pytest.mark.parametrize("profile", PROFILES)
def test_the_written_guard_test_passes_the_check_of_its_own_project(tmp_path, profile):
    app = tmp_path / "app"
    init(app, profile)
    controllers = build_controllers()
    imports = controllers.rules.check(CheckImports(app, "app", profile, tmp_path / "tests")).violations
    structure = controllers.layout.check(CheckStructure(app, "app", profile, tmp_path / "tests")).violations
    assert imports + structure == ()


@pytest.mark.parametrize("profile", PROFILES)
def test_the_written_guard_test_runs_and_passes(tmp_path, profile):
    init(tmp_path / "app", profile)
    result = pytest_in(tmp_path)
    assert result.returncode == 0, result.stdout + result.stderr


def test_the_written_guard_test_fails_with_the_violation_as_its_message(tmp_path):
    init(tmp_path / "app", "web")
    (tmp_path / "app" / "kernel" / "bad.py").write_text("X = 1  # a comment\n")
    result = pytest_in(tmp_path)
    assert result.returncode == 1
    assert "app/kernel/bad.py:1:" in result.stdout and "1 violation(s) in 1 file(s)" in result.stdout


def test_the_written_guard_test_checks_an_app_folder_with_another_path_and_name(tmp_path):
    init(tmp_path / "src" / "shop", "web")
    assert (tmp_path / "src" / GUARD).is_file()
    (tmp_path / "src" / "shop" / "kernel" / "bad.py").write_text("X = 1  # a comment\n")
    result = pytest_in(tmp_path / "src")
    assert result.returncode == 1
    assert "shop/kernel/bad.py:1:" in result.stdout


@pytest.mark.parametrize("profile", PROFILES)
def test_the_guard_example_of_the_testing_doc_is_the_file_init_writes(tmp_path, profile):
    init(tmp_path / "app", profile)
    written = (tmp_path / GUARD).read_text()
    testing = next(f.template for f in build_controllers().spec.docs(profile).files if f.path == ("testing.md",))
    assert f"# guard: {GUARD.as_posix()} (written by `xarch init`)\n{written}" in testing
