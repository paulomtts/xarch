"""Use case: create one instance of a kind, and init, on in-memory files."""
from pathlib import Path

import pytest

from tests.fakes.filesystem import FakeFiles
from tests.fakes.scaffold_skeleton import FakeSkeleton
from xarch.modules.scaffold.application.controller import ScaffoldController
from xarch.modules.scaffold.application.services.scaffolding import Scaffolding
from xarch.modules.scaffold.contract import Init, New, Refused, Report, Scaffolded

ROOT = Path("/src/app")
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


def controller(files: FakeFiles) -> ScaffoldController:
    return ScaffoldController(Scaffolding(files, SKELETON))


@pytest.mark.parametrize("given, when, then", [
    pytest.param(MODULES, New(ROOT, "module", "docs", "cli"), Scaffolded(Report(created=MODULE_FILES)),
                 id="a new module is created with its controller as a file"),
    pytest.param(set(), New(ROOT, "module", "docs", "cli"),
                 Refused(f"{ROOT / 'modules'} does not exist: run 'xarch init' first"),
                 id="a new module in an app that was not initialised is refused"),
    pytest.param(MODULES, New(ROOT, "module", "Docs", "cli"),
                 Refused("'Docs' is not a valid name: use a lowercase Python identifier, e.g. 'documents'"),
                 id="a name that is not a lowercase identifier is refused"),
    pytest.param(MODULES | {ROOT / "modules" / "docs" / "__init__.py"}, New(ROOT, "module", "docs", "cli"),
                 Refused(f"'docs' already exists at {ROOT / 'modules' / 'docs'}"),
                 id="a module that already exists is refused"),
    pytest.param(MODULES, New(ROOT, "features", "docs", "cli"),
                 Refused("no kind 'features' in the profile: use module"),
                 id="a kind the profile does not declare is refused"),
    pytest.param(MODULES, New(ROOT, "modules", "docs", "cli"),
                 Refused("no kind 'modules' in the profile: that is the folder of the kind module: write "
                         "`xarch new module <name>`"),
                 id="the folder of a kind in place of its word is refused, saying what to type"),
    pytest.param(MODULES, New(ROOT, "modules/", "docs", "cli"),
                 Refused("no kind 'modules/' in the profile: that is the folder of the kind module: write "
                         "`xarch new module <name>`"),
                 id="the folder written with a trailing slash is refused the same way"),
])
def test_new(given, when, then):
    assert controller(FakeFiles(given)).new(when) == then


def test_a_new_module_in_an_empty_folder_of_its_kind_is_created():
    result = controller(FakeFiles(dirs={ROOT / "modules"})).new(New(ROOT, "module", "docs", "cli"))
    assert result == Scaffolded(Report(created=MODULE_FILES))


def test_a_refused_new_creates_nothing():
    files = FakeFiles()
    controller(files).new(New(ROOT, "module", "Docs", "cli"))
    assert files.created == []


def test_init_creates_a_package_file_for_every_folder_then_the_docs_in_order():
    files = FakeFiles()
    result = controller(files).init(Init(ROOT, "cli"))
    expected = [ROOT / p / "__init__.py" for p in
                ["", "bootstrap", "bootstrap/migrations", "kernel", "kernel/logic", "modules", "platform", "cli",
                 "cli/commands"]]
    assert files.created == expected + [PYPROJECT] + DOC_FILES + [GUARD, MAKEFILE]
    assert result == Scaffolded(type(result.report)(created=expected + [PYPROJECT] + DOC_FILES + [GUARD, MAKEFILE],
                                                    skipped=[]))


def test_init_writes_each_doc_with_its_template():
    files = FakeFiles()
    controller(files).init(Init(ROOT, "cli"))
    assert {path: files.texts[path] for path in DOC_FILES} == {DOCS / p: f"# {p}\n" for p in DOC_PATHS}


def test_init_writes_each_project_file_beside_the_app_folder():
    files = FakeFiles()
    controller(files).init(Init(ROOT, "cli"))
    assert {path: files.texts[path] for path in (GUARD, MAKEFILE)} == {GUARD: "check app\n", MAKEFILE: "all: app\n"}


def test_init_asks_for_the_project_files_of_the_app_folder_by_its_name():
    files = FakeFiles()
    controller(files).init(Init(Path("/src/shop"), "cli"))
    assert files.texts[GUARD] == "check shop\n"


def test_init_writes_a_file_that_is_not_text_as_its_bytes_and_a_file_inside_the_app_folder():
    skeleton = FakeSkeleton([(("kernel",), True)], files={"app": [(("app", "kernel", "logo.woff"), b"\xff\x00"),
                                                                  (("app", "kernel", "a.txt"), "for app")]})
    files = FakeFiles()
    report = Scaffolding(files, skeleton).init(ROOT, "cli")
    assert files.data == {ROOT / "kernel" / "logo.woff": b"\xff\x00"}
    assert files.texts[ROOT / "kernel" / "a.txt"] == "for app"
    assert ROOT / "kernel" / "logo.woff" in report.created


def test_init_never_overwrites_a_file_of_a_preset_and_reports_it_skipped():
    skeleton = FakeSkeleton([(("kernel",), True)], files={"app": [(("app", "kernel", "logo.woff"), b"\xff\x00")]})
    files = FakeFiles({ROOT / "kernel" / "logo.woff"})
    report = Scaffolding(files, skeleton).init(ROOT, "cli")
    assert files.data == {} and ROOT / "kernel" / "logo.woff" in report.skipped


def test_init_never_overwrites_a_project_file_and_reports_it_skipped():
    files = FakeFiles({GUARD})
    report = controller(files).init(Init(ROOT, "cli")).report
    assert GUARD in report.skipped and GUARD not in report.created
    assert GUARD not in files.texts and MAKEFILE in report.created


def test_a_second_init_skips_every_project_file():
    files = FakeFiles()
    controller(files).init(Init(ROOT, "cli"))
    report = controller(files).init(Init(ROOT, "cli")).report
    assert {GUARD, MAKEFILE} <= set(report.skipped) and report.created == []


def test_init_never_overwrites_a_doc_and_reports_it_skipped():
    existing = DOCS / "architecture.md"
    files = FakeFiles({existing, DOCS / ".obsidian" / "app.json"}, dirs={DOCS / "adrs"})
    report = controller(files).init(Init(ROOT, "cli")).report
    assert report.skipped == [existing]
    assert existing not in files.texts
    assert DOCS / "adrs" / "0000-template.md" in report.created


def test_a_second_init_creates_nothing():
    files = FakeFiles()
    controller(files).init(Init(ROOT, "cli"))
    report = controller(files).init(Init(ROOT, "cli")).report
    assert report.created == [] and report.updated == [] and DOC_FILES[0] in report.skipped


@pytest.mark.parametrize("app, docs", [
    pytest.param(Path("app"), Path("docs/project"), id="an app folder named alone has its docs beside it"),
    pytest.param(Path("elsewhere/app"), Path("elsewhere/docs/project"), id="an app folder in a folder has them there"),
])
def test_the_docs_go_beside_the_app_folder(app, docs):
    files = FakeFiles()
    controller(files).init(Init(app, "cli"))
    assert docs / "statement.md" in files.created


def test_the_docs_of_the_current_folder_go_beside_it_in_its_parent():
    files = FakeFiles()
    controller(files).init(Init(Path("."), "cli"))
    assert Path.cwd().parent / "docs" / "project" / "statement.md" in files.created


def test_new_does_not_touch_the_docs():
    files = FakeFiles({ROOT / "modules" / "__init__.py"})
    controller(files).new(New(ROOT, "module", "docs", "cli"))
    assert files.texts == {}
    assert not [p for p in files.created if "docs" in p.parts and "modules" not in p.parts]


def test_init_skips_what_exists():
    files = FakeFiles({ROOT / "kernel" / "__init__.py"})
    report = controller(files).init(Init(ROOT, "cli")).report
    assert report.skipped == [ROOT / "kernel" / "__init__.py"]
    assert ROOT / "kernel" / "__init__.py" not in files.created


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



SHOP = Path("/src/shop")


@pytest.mark.parametrize("root, text, written, where", [
    pytest.param(SHOP, None, '[tool.xarch]\nprofile = "web"\napp = "shop"\n', "created",
                 id="a new pyproject records an app folder that is not the default, after the profile"),
    pytest.param(SHOP, '[project]\nname = "x"\n', '[project]\nname = "x"\n\n[tool.xarch]\nprofile = "web"\n'
                 'app = "shop"\n', "updated", id="a pyproject with no table gets it with both"),
    pytest.param(SHOP, '[tool.xarch]\ntests = "t"\n\n[tool.other]\n',
                 '[tool.xarch]\nprofile = "web"\napp = "shop"\ntests = "t"\n\n[tool.other]\n', "updated",
                 id="an existing table gets both at its top"),
    pytest.param(SHOP, '[tool.xarch]\nprofile = "web"\n', '[tool.xarch]\nprofile = "web"\napp = "shop"\n',
                 "updated", id="a recorded profile is left, and the app folder is still recorded"),
    pytest.param(SHOP, '[tool.xarch]\napp = "other"\n', '[tool.xarch]\nprofile = "web"\napp = "other"\n', "updated",
                 id="a recorded app folder is left, and the profile is still recorded"),
    pytest.param(SHOP, '[tool.xarch]\nprofile = "cli"\napp = "other"\n', None, "skipped",
                 id="a profile and an app folder already recorded are never rewritten"),
    pytest.param(ROOT, None, '[tool.xarch]\nprofile = "web"\n', "created",
                 id="the default app folder is not recorded"),
    pytest.param(ROOT, '[tool.xarch]\nprofile = "web"\n', None, "skipped",
                 id="the default app folder with a recorded profile has nothing to record"),
])
def test_init_records_an_app_folder_that_is_not_the_default_and_never_rewrites_a_value(root, text, written, where):
    files = FakeFiles(texts={PYPROJECT: text} if text is not None else None)
    report = controller(files).init(Init(root, "web")).report
    assert files.texts.get(PYPROJECT) == written
    assert PYPROJECT in getattr(report, where)
    assert (PYPROJECT in report.created) == (where == "created")


def test_the_app_folder_is_recorded_relative_to_the_pyproject_found_above_it_as_posix():
    files = FakeFiles(texts={PYPROJECT: '[project]\nname = "x"\n'})
    controller(files).init(Init(Path("/src/services/shop"), "web"))
    assert files.texts[PYPROJECT].endswith('[tool.xarch]\nprofile = "web"\napp = "services/shop"\n')
    assert files.texts[PYPROJECT].startswith('[project]\nname = "x"\n')
