"""Use case: create one instance of a kind, and init, on in-memory files."""
from pathlib import Path

import pytest

from tests.fakes.filesystem import FakeFiles
from tests.fakes.scaffold_skeleton import FakeSkeleton
from xarch.modules.scaffold.application.controller import ScaffoldController
from xarch.modules.scaffold.application.services.scaffolding import ScaffoldingService
from xarch.modules.scaffold.contract import InitProject, KindIsAFolder, NewInstance, NotInitialized, Refused, ReportView, Scaffolded

ROOT = Path("/src/app")
CWD = Path("/work")
"""The folder the command is run from: a value of the command, never the process's own."""
PYPROJECT = Path("/src/pyproject.toml")
DOC_PATHS = ["statement.md", "domain.md", "design.md", "architecture.md", "testing.md", "requirements.md",
             "adrs/0000-template.md", "artifacts/standards/_template.md", "artifacts/audits/_template.md",
             "artifacts/taxonomy/_template.md", "artifacts/modules/_template.md", "artifacts/guards/_template.md"]
DOCS = Path("/src/docs/project")
DOC_FILES = [DOCS / p for p in DOC_PATHS]
SKELETON = FakeSkeleton(
    [(tuple(p.split("/")), True) for p in ["bootstrap", "bootstrap/migrations", "kernel", "kernel/logic", "modules",
                                           "platform", "cli", "cli/commands"]],
    {"module": (("modules",), [(("contract",), True), (("domain",), True), (("application",), True),
                                (("application", "controller.py"), False), (("application", "services"), True),
                                (("application", "logic"), True), (("application", "ports"), True),
                                (("adapters",), True)])},
    [(("docs", "project", *p.split("/")), f"# {p}\n") for p in DOC_PATHS],
    files={"app": [(("tests", "architecture", "test_rules.py"), "check app\n"), (("Makefile",), "all: app\n")],
           "shop": [(("tests", "architecture", "test_rules.py"), "check shop\n")]})
GUARD = Path("/src/tests/architecture/test_rules.py")
MAKEFILE = Path("/src/Makefile")


MODULES = {ROOT / "modules" / "__init__.py"}
MODULE_FILES = [ROOT / "modules/docs" / p for p in
                ["__init__.py", "contract/__init__.py", "domain/__init__.py", "application/__init__.py",
                 "application/controller.py", "application/services/__init__.py", "application/logic/__init__.py",
                 "application/ports/__init__.py", "adapters/__init__.py"]]


def controller(files: FakeFiles, skeleton: FakeSkeleton = SKELETON) -> ScaffoldController:
    return ScaffoldController(ScaffoldingService(files, skeleton))


def pyproject(files: FakeFiles) -> str | None:
    found = files.pyproject(PYPROJECT.parent)
    return None if found is None else found[1]


@pytest.mark.parametrize("given, when, then", [
    pytest.param(MODULES, NewInstance(ROOT, "module", "docs", "cli"), Scaffolded(ReportView(created=MODULE_FILES)),
                 id="a new module is created with its controller as a file"),
    pytest.param(set(), NewInstance(ROOT, "module", "docs", "cli"),
                 NotInitialized(ROOT / "modules"),
                 id="a new module in an app that was not initialised is refused"),
    pytest.param(MODULES, NewInstance(ROOT, "module", "Docs", "cli"),
                 Refused("'Docs' is not a valid name: use a lowercase Python identifier, e.g. 'documents'"),
                 id="a name that is not a lowercase identifier is refused"),
    pytest.param(MODULES | {ROOT / "modules" / "docs" / "__init__.py"}, NewInstance(ROOT, "module", "docs", "cli"),
                 Refused(f"'docs' already exists at {ROOT / 'modules' / 'docs'}"),
                 id="a module that already exists is refused"),
    pytest.param(MODULES, NewInstance(ROOT, "features", "docs", "cli"),
                 Refused("no kind 'features' in the profile: use module"),
                 id="a kind the profile does not declare is refused"),
    pytest.param(MODULES, NewInstance(ROOT, "modules", "docs", "cli"),
                 KindIsAFolder("modules", "module"),
                 id="the folder of a kind in place of its word is refused, saying what to type"),
    pytest.param(MODULES, NewInstance(ROOT, "modules/", "docs", "cli"),
                 KindIsAFolder("modules/", "module"),
                 id="the folder written with a trailing slash is refused the same way"),
])
def test_new(given, when, then):
    assert controller(FakeFiles(given)).new(when) == then


def test_a_new_module_in_an_empty_folder_of_its_kind_is_created():
    result = controller(FakeFiles(dirs={ROOT / "modules"})).new(NewInstance(ROOT, "module", "docs", "cli"))
    assert result == Scaffolded(ReportView(created=MODULE_FILES))


def test_a_refused_new_creates_nothing():
    files = FakeFiles()
    controller(files).new(NewInstance(ROOT, "module", "Docs", "cli"))
    assert files.kind(ROOT) is None


def test_init_creates_a_package_file_for_every_folder_then_the_docs_in_order():
    files = FakeFiles()
    result = controller(files).init(InitProject(ROOT, "cli", CWD))
    expected = [ROOT / p / "__init__.py" for p in
                ["", "bootstrap", "bootstrap/migrations", "kernel", "kernel/logic", "modules", "platform", "cli",
                 "cli/commands"]]
    assert result == Scaffolded(type(result.report)(created=expected + [PYPROJECT] + DOC_FILES + [GUARD, MAKEFILE],
                                                    skipped=[]))


def test_init_writes_each_doc_with_its_template():
    files = FakeFiles()
    controller(files).init(InitProject(ROOT, "cli", CWD))
    assert {path: files.content(path) for path in DOC_FILES} == {DOCS / p: f"# {p}\n" for p in DOC_PATHS}


def test_init_writes_each_project_file_beside_the_app_folder():
    files = FakeFiles()
    controller(files).init(InitProject(ROOT, "cli", CWD))
    assert {path: files.content(path) for path in (GUARD, MAKEFILE)} == {GUARD: "check app\n", MAKEFILE: "all: app\n"}


def test_init_asks_for_the_project_files_of_the_app_folder_by_its_name():
    files = FakeFiles()
    controller(files).init(InitProject(Path("/src/shop"), "cli", CWD))
    assert files.content(GUARD) == "check shop\n"


def test_init_writes_a_file_that_is_not_text_as_its_bytes_and_a_file_inside_the_app_folder():
    skeleton = FakeSkeleton([(("kernel",), True)], files={"app": [(("app", "kernel", "logo.woff"), b"\xff\x00"),
                                                                  (("app", "kernel", "a.txt"), "for app")]})
    files = FakeFiles()
    report = controller(files, skeleton).init(InitProject(ROOT, "cli", CWD)).report
    assert files.content(ROOT / "kernel" / "logo.woff") == b"\xff\x00"
    assert files.content(ROOT / "kernel" / "a.txt") == "for app"
    assert ROOT / "kernel" / "logo.woff" in report.created


def test_init_never_overwrites_a_file_of_a_preset_and_reports_it_skipped():
    skeleton = FakeSkeleton([(("kernel",), True)], files={"app": [(("app", "kernel", "logo.woff"), b"\xff\x00")]})
    files = FakeFiles({ROOT / "kernel" / "logo.woff"})
    report = controller(files, skeleton).init(InitProject(ROOT, "cli", CWD)).report
    assert files.content(ROOT / "kernel" / "logo.woff") == "" and ROOT / "kernel" / "logo.woff" in report.skipped


def test_init_never_overwrites_a_project_file_and_reports_it_skipped():
    files = FakeFiles({GUARD})
    report = controller(files).init(InitProject(ROOT, "cli", CWD)).report
    assert GUARD in report.skipped and GUARD not in report.created
    assert files.content(GUARD) == "" and MAKEFILE in report.created


def test_a_second_init_skips_every_project_file():
    files = FakeFiles()
    controller(files).init(InitProject(ROOT, "cli", CWD))
    report = controller(files).init(InitProject(ROOT, "cli", CWD)).report
    assert {GUARD, MAKEFILE} <= set(report.skipped) and report.created == []


def test_init_never_overwrites_a_doc_and_reports_it_skipped():
    existing = DOCS / "architecture.md"
    files = FakeFiles({existing, DOCS / ".obsidian" / "app.json"}, dirs={DOCS / "adrs"})
    report = controller(files).init(InitProject(ROOT, "cli", CWD)).report
    assert report.skipped == [existing]
    assert files.content(existing) == ""
    assert DOCS / "adrs" / "0000-template.md" in report.created


def test_a_second_init_creates_nothing():
    files = FakeFiles()
    controller(files).init(InitProject(ROOT, "cli", CWD))
    report = controller(files).init(InitProject(ROOT, "cli", CWD)).report
    assert report.created == [] and report.updated == [] and DOC_FILES[0] in report.skipped


@pytest.mark.parametrize("app, docs", [
    pytest.param(Path("app"), Path("docs/project"), id="an app folder named alone has its docs beside it"),
    pytest.param(Path("elsewhere/app"), Path("elsewhere/docs/project"), id="an app folder in a folder has them there"),
])
def test_the_docs_go_beside_the_app_folder(app, docs):
    files = FakeFiles()
    report = controller(files).init(InitProject(app, "cli", CWD)).report
    assert docs / "statement.md" in report.created


def test_the_docs_of_the_current_folder_go_beside_it_in_its_parent():
    files = FakeFiles()
    report = controller(files).init(InitProject(Path("."), "cli", CWD)).report
    assert CWD.parent / "docs" / "project" / "statement.md" in report.created


def test_new_does_not_touch_the_docs():
    files = FakeFiles({ROOT / "modules" / "__init__.py"})
    report = controller(files).new(NewInstance(ROOT, "module", "docs", "cli")).report
    assert files.kind(DOCS) is None and files.kind(PYPROJECT) is None
    assert not [p for p in report.created if "docs" in p.parts and "modules" not in p.parts]


def test_init_skips_what_exists():
    files = FakeFiles({ROOT / "kernel" / "__init__.py"})
    report = controller(files).init(InitProject(ROOT, "cli", CWD)).report
    assert report.skipped == [ROOT / "kernel" / "__init__.py"]
    assert ROOT / "kernel" / "__init__.py" not in report.created


def test_init_records_the_profile_in_a_new_pyproject_beside_the_app():
    files = FakeFiles()
    controller(files).init(InitProject(ROOT, "web", CWD))
    assert pyproject(files) == '[tool.xarch]\nprofile = "web"\n'


def test_init_adds_the_profile_to_the_pyproject_of_the_project():
    files = FakeFiles(texts={PYPROJECT: '[project]\nname = "x"\n'})
    report = controller(files).init(InitProject(ROOT, "web", CWD)).report
    assert pyproject(files) == '[project]\nname = "x"\n\n[tool.xarch]\nprofile = "web"\n'
    assert report.updated == [PYPROJECT] and PYPROJECT not in report.created


def test_init_adds_the_profile_to_an_existing_tool_xarch_table():
    files = FakeFiles(texts={PYPROJECT: '[tool.xarch]\ntests = "t"\n\n[tool.other]\n'})
    controller(files).init(InitProject(ROOT, "web", CWD))
    assert pyproject(files) == '[tool.xarch]\nprofile = "web"\ntests = "t"\n\n[tool.other]\n'


def test_init_never_changes_a_recorded_profile():
    text = '[tool.xarch]\nprofile = "cli"\n'
    files = FakeFiles(texts={PYPROJECT: text})
    report = controller(files).init(InitProject(ROOT, "web", CWD)).report
    assert pyproject(files) == text and PYPROJECT in report.skipped



SHOP = Path("/src/shop")


@pytest.mark.parametrize("given, then", [
    pytest.param({}, ('[tool.xarch]\nprofile = "web"\napp = "shop"\n', (True, False, False)),
                 id="a new pyproject records an app folder that is not the default, after the profile"),
    pytest.param({PYPROJECT: '[project]\nname = "x"\n'},
                 ('[project]\nname = "x"\n\n[tool.xarch]\nprofile = "web"\napp = "shop"\n', (False, True, False)),
                 id="a pyproject with no table gets it with both"),
    pytest.param({PYPROJECT: '[tool.xarch]\nprofile = "cli"\napp = "other"\n'},
                 ('[tool.xarch]\nprofile = "cli"\napp = "other"\n', (False, False, True)),
                 id="a profile and an app folder already recorded are never rewritten"),
])
def test_init_records_an_app_folder_that_is_not_the_default_and_never_rewrites_a_value(given, then):
    files = FakeFiles(texts=given)
    report = controller(files).init(InitProject(SHOP, "web", CWD)).report
    assert (pyproject(files), (PYPROJECT in report.created, PYPROJECT in report.updated,
                               PYPROJECT in report.skipped)) == then


def test_the_app_folder_is_recorded_relative_to_the_pyproject_found_above_it_as_posix():
    files = FakeFiles(texts={PYPROJECT: '[project]\nname = "x"\n'})
    controller(files).init(InitProject(Path("/src/services/shop"), "web", CWD))
    assert pyproject(files).endswith('[tool.xarch]\nprofile = "web"\napp = "services/shop"\n')
    assert pyproject(files).startswith('[project]\nname = "x"\n')


TWO_KINDS = FakeSkeleton([], {"module": (("modules",), [(("domain",), True)]),
                              "plugin": (("plugins",), [(("hooks",), True), (("manifest.py",), False)])})


def test_every_kind_of_a_profile_with_several_repeating_folders_is_made_in_its_own_folder():
    files = FakeFiles(dirs={ROOT / "modules", ROOT / "plugins"})
    two = controller(files, TWO_KINDS)
    assert two.new(NewInstance(ROOT, "module", "docs", "cli")) == Scaffolded(
        ReportView(created=[ROOT / "modules/docs/__init__.py", ROOT / "modules/docs/domain/__init__.py"]))
    assert two.new(NewInstance(ROOT, "plugin", "seo", "cli")) == Scaffolded(
        ReportView(created=[ROOT / "plugins/seo/__init__.py", ROOT / "plugins/seo/hooks/__init__.py",
                        ROOT / "plugins/seo/manifest.py"]))


@pytest.mark.parametrize("kind, refused", [
    pytest.param("feature", Refused("no kind 'feature' in the profile: use module, plugin"),
                 id="an unknown kind lists every word"),
    pytest.param("plugins", KindIsAFolder("plugins", "plugin"), id="the folder of the second kind names its word"),
])
def test_a_kind_the_profile_does_not_declare_is_refused_listing_every_word(kind, refused):
    two = controller(FakeFiles(dirs={ROOT / "modules"}), TWO_KINDS)
    assert two.new(NewInstance(ROOT, kind, "docs", "cli")) == refused


def test_the_language_of_the_profile_is_named_in_the_refusal_of_a_name_and_the_package_file_is_the_one_it_has():
    pascal = FakeSkeleton([(("kernel",), True)], SKELETON.kinds("cli"), package_file="unit.pas", language="Pascal")
    files = FakeFiles({ROOT / "modules" / "unit.pas"})
    assert controller(files, pascal).new(NewInstance(ROOT, "module", "Docs", "cli")) == Refused(
        "'Docs' is not a valid name: use a lowercase Pascal identifier, e.g. 'documents'")
    assert controller(files, pascal).init(InitProject(ROOT, "cli", CWD)).report.created[0] == ROOT / "unit.pas"
