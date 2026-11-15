"""The enforcement section of a check, on a throwaway web project: what the profile is, what no rule governs, the
init files, the skipped tests, the dynamic imports and the checks met to the letter only."""
from pathlib import Path

from tests.bootstrap.project import APP, TABLE, TESTS, write
from xarch.bootstrap.wiring import build_controllers
from xarch.modules.rules.contract import AtView, CheckImports, DriftView, EnforcementView, ImportsChecked, OriginView, WeakView

PORTS = "modules/docs/application/ports/"
REPO = ("from typing import Protocol\n\nclass Repo(Protocol):\n    def get(self, id: int) -> str: ...\n"
        "    def save(self, text: str) -> None: ...\n    @property\n    def size(self) -> int: ...\n")


def enforcement(tmp_path: Path, app: dict[str, str] | None = None, tests: dict[str, str | None] | None = None,
                profile: str = "web") -> EnforcementView:
    guard, *others = build_controllers().spec.files("web", "app")
    for file in others:
        (tmp_path.joinpath(*file.path)).parent.mkdir(parents=True, exist_ok=True)
        tmp_path.joinpath(*file.path).write_text(file.content)
    tests = {**TESTS, "architecture/test_rules.py": guard.content, **(tests or {})}
    result = build_controllers().rules.check(CheckImports(
        write(tmp_path / "app", {**APP, **(app or {})}), "app", profile,
        write(tmp_path / "tests", {k: v for k, v in tests.items() if v is not None})))
    assert isinstance(result, ImportsChecked)
    return result.enforcement


def test_a_clean_project_on_a_bundled_profile_reports_only_the_guards_it_ships_off(tmp_path):
    assert enforcement(tmp_path) == EnforcementView(OriginView("web", True, None, ("closed-tree",), ("closed-tree",), ()))


def test_a_python_file_no_part_governs_is_listed(tmp_path):
    found = enforcement(tmp_path, {"scripts/run.py": "", "scripts/__init__.py": "", "kernel/x.py": ""})
    assert found.ungoverned == ("app/scripts/__init__.py", "app/scripts/run.py")


def test_a_missing_or_edited_guard_test_is_listed(tmp_path):
    assert enforcement(tmp_path, tests={"architecture/test_rules.py": None}).init_files == (
        DriftView("tests/architecture/test_rules.py", "missing"),)
    assert enforcement(tmp_path, tests={"architecture/test_rules.py": "def test_nothing():\n    pass\n"}).init_files == (
        DriftView("tests/architecture/test_rules.py", "changed"),)


def test_skipped_tests_and_dynamic_imports_are_listed_where_they_are(tmp_path):
    tests = {"modules/docs/domain/test_document.py": "import pytest\n\n@pytest.mark.skip\ndef test_x():\n    pass\n"
                                                     "\n@pytest.mark.xfail(reason='later')\ndef test_y():\n    pass\n"}
    app = {"kernel/dyn.py": "import importlib\n\nplugin = importlib.import_module('app.' + 'x')\n"}
    found = enforcement(tmp_path, app, tests)
    assert found.skipped == (AtView("tests/modules/docs/domain/test_document.py", 3),
                             AtView("tests/modules/docs/domain/test_document.py", 7))
    assert found.dynamic == (AtView("app/kernel/dyn.py", 3),)


def test_a_fake_that_defines_less_than_its_port_declares_is_weak(tmp_path):
    fakes = {"fakes/repo.py": "class FakeRepo:\n    def get(self, id):\n        return ''\n"}
    assert enforcement(tmp_path, {PORTS + "repo.py": REPO}, fakes).weak == (
        WeakView("stand-ins", "tests/fakes/repo.py", 1,
             "FakeRepo does not define save, size, which Repo declares (app/modules/docs/application/ports/repo.py)"),)


def test_a_fake_that_defines_every_method_or_sets_it_as_an_attribute_is_not_weak(tmp_path):
    fakes = {"fakes/repo.py": "class FakeRepo:\n    size = 0\n    def get(self, id):\n        return ''\n"
                              "    def save(self, text):\n        self.saved = text\n"}
    assert enforcement(tmp_path, {PORTS + "repo.py": REPO}, fakes).weak == ()


def test_a_variant_credited_to_a_standalone_test_with_no_assert_is_weak(tmp_path):
    three = "class Published: ...\nclass Missing: ...\nclass Gone: ...\n\nPublishResult = Published | Missing | Gone\n"
    body = TABLE + "\n\ndef test_a_gone_document_is_gone():\n    Gone()\n\ndef test_also_gone():\n    run(Gone)\n"
    found = enforcement(tmp_path, {"modules/docs/contract/results.py": three},
                        {"modules/docs/application/test_publish.py": body})
    assert found.weak == (
        WeakView("scenario-coverage", "tests/modules/docs/application/test_publish.py", 20,
             "PublishResult variant Gone is credited to test_a_gone_document_is_gone, test_also_gone by name only: "
             "no assert in their bodies"),)
    asserted = body + "\ndef test_gone_for_real():\n    assert run(Gone) == Gone()\n"
    assert enforcement(tmp_path, {"modules/docs/contract/results.py": three},
                       {"modules/docs/application/test_publish.py": asserted}).weak == ()


def test_a_fake_that_defines_every_method_of_one_port_of_its_name_is_not_weak(tmp_path):
    other = "from typing import Protocol\n\nclass Repo(Protocol):\n    def find(self) -> str: ...\n"
    app = {PORTS + "repo.py": REPO, "modules/mod/__init__.py": "", "modules/mod/application/ports/repo.py": other}
    fakes = {"fakes/repo.py": "class FakeRepo:\n    size = 0\n    def get(self, id):\n        return ''\n"
                              "    def save(self, text):\n        pass\n",
             "fakes/mod_repo.py": "class FakeRepo:\n    def find(self):\n        return ''\n"}
    assert enforcement(tmp_path, app, fakes).weak == ()
