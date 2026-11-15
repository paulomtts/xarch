"""Use case: create one instance of a kind, and init, on in-memory files.

Scenario: new creates controller as a file
  Given an app after init         When a new one is made    Then the Result is Scaffolded
Scenario: refusals carry the reason and create nothing
  Given no app, or a bad name     When a new one is made    Then the Result is Refused
"""
from pathlib import Path

import pytest

from xarch.bootstrap.wiring import build_spec
from xarch.modules.scaffold.adapters.spec_skeleton import SpecSkeleton
from xarch.modules.scaffold.application.controller import ScaffoldController
from xarch.modules.scaffold.application.services.scaffolding import Scaffolding
from xarch.modules.scaffold.contract import Init, New, Refused, Scaffolded
from tests.fakes.filesystem import FakeFiles

ROOT = Path("/src/app")
PYPROJECT = Path("/src/pyproject.toml")


def controller(files: FakeFiles) -> ScaffoldController:
    return ScaffoldController(Scaffolding(files, SpecSkeleton(build_spec())))


DOCS = Path("/src/docs/project")
DOC_FILES = [DOCS / p for p in ["statement.md", "domain.md", "design.md", "architecture.md", "testing.md",
                                "requirements.md", "adrs/0000-template.md", "artifacts/standards/_template.md",
                                "artifacts/audits/_template.md", "artifacts/taxonomy/_template.md",
                                "artifacts/modules/_template.md", "artifacts/guards/_template.md"]]


def test_init_creates_a_package_file_for_every_folder_then_the_docs_in_order():
    files = FakeFiles()
    result = controller(files).init(Init(ROOT, "cli"))
    expected = [ROOT / p / "__init__.py" for p in
                ["", "bootstrap", "bootstrap/migrations", "kernel", "kernel/logic", "modules", "platform", "cli",
                 "cli/commands"]]
    assert files.created == expected + [PYPROJECT] + DOC_FILES
    assert result == Scaffolded(type(result.report)(created=expected + [PYPROJECT] + DOC_FILES, skipped=[]))


@pytest.mark.parametrize("profile", ["cli", "web"])
def test_init_writes_each_doc_with_its_template_in_every_profile(profile):
    files = FakeFiles()
    controller(files).init(Init(ROOT, profile))
    docs = build_spec().docs(profile)
    assert {path: files.texts[path] for path in DOC_FILES} == {
        DOCS.joinpath(*f.path): f.template for f in docs.files}


def test_init_never_overwrites_a_doc_and_reports_it_skipped():
    existing = DOCS / "architecture.md"
    files = FakeFiles({existing, DOCS / "adrs", DOCS / ".obsidian" / "app.json"})
    report = controller(files).init(Init(ROOT, "cli")).report
    assert report.skipped == [existing]
    assert existing not in files.texts
    assert DOCS / "adrs" / "0000-template.md" in report.created


def test_a_second_init_creates_nothing():
    files = FakeFiles()
    controller(files).init(Init(ROOT, "cli"))
    report = controller(files).init(Init(ROOT, "cli")).report
    assert report.created == [] and report.updated == [] and DOC_FILES[0] in report.skipped


@pytest.mark.parametrize("app, docs", [(Path("app"), Path("docs/project")),
                                       (Path("elsewhere/app"), Path("elsewhere/docs/project")),
                                       (Path("."), Path.cwd().parent / "docs" / "project")])
def test_the_docs_go_beside_the_app_folder(app, docs):
    files = FakeFiles()
    controller(files).init(Init(app, "cli"))
    assert docs / "statement.md" in files.created


def test_new_does_not_touch_the_docs():
    files = FakeFiles({ROOT / "modules" / "__init__.py"})
    controller(files).new(New(ROOT, "modules", "docs", "cli"))
    assert files.texts == {}
    assert not [p for p in files.created if "docs" in p.parts and "modules" not in p.parts]


def test_init_skips_what_exists():
    files = FakeFiles({ROOT / "kernel" / "__init__.py"})
    report = controller(files).init(Init(ROOT, "cli")).report
    assert report.skipped == [ROOT / "kernel" / "__init__.py"]
    assert ROOT / "kernel" / "__init__.py" not in files.created


def test_new_creates_controller_as_a_file():
    files = FakeFiles({ROOT / "modules" / "__init__.py"})
    controller(files).new(New(ROOT, "modules", "docs", "cli"))
    assert ROOT / "modules/docs/application/controller.py" in files.created
    assert ROOT / "modules/docs/application/controller.py/__init__.py" not in files.created


def test_refusals_carry_the_reason_and_create_nothing():
    files = FakeFiles()
    assert controller(files).new(New(ROOT, "modules", "docs", "cli")) == Refused(
        f"{ROOT / 'modules'} does not exist: run 'xarch init' first")
    assert controller(files).new(New(ROOT, "modules", "Docs", "cli")) == Refused(
        "'Docs' is not a valid name: use a lowercase Python identifier, e.g. 'documents'")
    assert files.created == []


def test_an_existing_module_is_refused():
    files = FakeFiles({ROOT / "modules" / "docs" / "__init__.py"})
    assert controller(files).new(New(ROOT, "modules", "docs", "cli")) == Refused(
        f"'docs' already exists at {ROOT / 'modules' / 'docs'}")


def test_new_refuses_a_kind_the_profile_does_not_declare():
    files = FakeFiles({ROOT / "modules" / "__init__.py"})
    assert controller(files).new(New(ROOT, "features", "docs", "cli")) == Refused(
        "no kind 'features' in the profile: use modules")
    assert files.created == []


def test_init_records_the_profile_in_a_new_pyproject_beside_the_app():
    files = FakeFiles()
    controller(files).init(Init(ROOT, "web"))
    assert files.texts[PYPROJECT] == '[tool.xarch]\nprofile = "web"\n'


def test_init_adds_the_profile_to_the_pyproject_of_the_project():
    files = FakeFiles(texts={PYPROJECT: '[project]\nname = "x"\n'})
    report = controller(files).init(Init(ROOT, "web")).report
    assert files.texts[PYPROJECT] == '[project]\nname = "x"\n\n[tool.xarch]\nprofile = "web"\n'
    assert report.updated == [PYPROJECT] and PYPROJECT not in report.created


def test_init_adds_the_profile_to_an_existing_tool_xarch_table():
    files = FakeFiles(texts={PYPROJECT: '[tool.xarch]\ntests = "t"\n\n[tool.other]\n'})
    controller(files).init(Init(ROOT, "web"))
    assert files.texts[PYPROJECT] == '[tool.xarch]\nprofile = "web"\ntests = "t"\n\n[tool.other]\n'


def test_init_never_changes_a_recorded_profile():
    text = '[tool.xarch]\nprofile = "cli"\n'
    files = FakeFiles(texts={PYPROJECT: text})
    report = controller(files).init(Init(ROOT, "web")).report
    assert PYPROJECT not in files.texts and PYPROJECT in report.skipped

