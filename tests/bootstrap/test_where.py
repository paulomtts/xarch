"""xarch where: what a path is and what code there may do, as text and as JSON, for a path that is there or not yet,
from the working folder, the project root or the app folder; and what is refused."""
import json
import shutil
from pathlib import Path

import pytest
from typer.testing import CliRunner

import xarch
from xarch.bootstrap.app import app

runner = CliRunner()
BUNDLED = Path(xarch.__file__).parent / "architectures"
DOMAIN = "app/modules/docs/domain/invoice.py"


@pytest.fixture(autouse=True)
def project(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert runner.invoke(app, ["init", "--profile", "web"]).exit_code == 0
    assert runner.invoke(app, ["new", "module", "docs"]).exit_code == 0
    (tmp_path / DOMAIN).write_text("X = 1\n")


def lines(*args: str) -> dict[str, str]:
    result = runner.invoke(app, ["where", *args])
    assert result.exit_code == 0, result.output
    return {line.split(":", 1)[0]: line.split(":", 1)[1].strip() for line in result.output.splitlines()
            if line[:1].isalpha() and ":" in line}


def document(*args: str) -> dict:
    result = runner.invoke(app, ["where", *args, "--format", "json"])
    assert result.exit_code == 0, result.output
    return json.loads(result.stdout)


def test_a_file_in_a_part_says_its_part_role_litmus_imports_libraries_forbidden_names_and_test():
    found = lines(DOMAIN)
    assert found["path"] == f"{DOMAIN} (exists)"
    assert found["part"] == "domain/ in module 'docs'"
    assert found["role"] == "entities, values (incl. ids), errors: invariants only"
    assert found["litmus"].startswith("Is it an invariant of one of this module's entities or values")
    assert found["may import"] == "its own module's `domain/`, `kernel/`"
    assert found["libraries"] == "none"
    assert found["may not use"].startswith("datetime.datetime.now, datetime.datetime.utcnow")
    assert found["tested by"] == "unit tier: tests/modules/docs/domain/test_invoice.py"


def test_a_file_that_does_not_exist_yet_is_placed_all_the_same_whichever_way_its_path_is_given(tmp_path, monkeypatch):
    new = "modules/docs/adapters/db_invoice_repo.py"
    from_root = lines(f"app/{new}")
    from_app = lines(new)
    monkeypatch.chdir(tmp_path / "app" / "modules")
    from_inside = lines("docs/adapters/db_invoice_repo.py", "--app", "../../app", "--tests", "../../tests")
    assert from_root == from_app == from_inside
    assert from_root["path"] == f"app/{new} (new)"
    assert from_root["part"] == "adapters/ in module 'docs'"
    assert from_root["libraries"] == "sqlmodel"
    assert from_root["tested by"] == "unit tier: tests/modules/docs/adapters/test_db_invoice_repo.py"


def test_a_part_that_is_one_file_has_its_test_by_use_case():
    found = lines("app/modules/docs/application/controller.py")
    assert found["tested by"] == "integration tier: tests/modules/docs/application/test_<use case>.py"


def test_a_test_file_says_its_tier_the_part_it_mirrors_what_it_may_import_and_the_fakes():
    found = lines("tests/modules/docs/application/test_publish.py")
    assert found["path"] == "tests/modules/docs/application/test_publish.py (new)"
    assert found["kind"] == "test, integration tier"
    assert found["mirrors"] == "application/controller.py in module 'docs'"
    assert found["may import"].startswith("its own module's `application/controller.py`")
    assert found["fakes"] == "may import tests/fakes/"
    assert found["tier proves"] == "one `Result` variant per path, driven through the controller"
    assert found["test code"] == "from tests/modules/docs/ only"


def test_a_unit_test_may_not_import_the_fakes():
    assert lines("tests/modules/docs/domain/test_invoice.py")["fakes"] == "may not import them"


def test_a_path_in_no_part_is_ungoverned_and_names_the_parts_near_it():
    found = lines("app/scripts/run.py")
    assert found["part"] == "none: ungoverned"
    assert found["nearest"].startswith("domain/ (app/modules/<module>/domain/), ")
    assert found["closed-tree"] == "off: `xarch check` does not read it"


def test_a_folder_of_the_layout_that_holds_the_parts_is_structure():
    found = lines("app/modules/docs")
    assert found["part"] == "none: structure"
    assert found["nearest"].startswith("domain/ (app/modules/docs/domain/)")


def test_json_gives_every_answer_as_a_field():
    found = document(DOMAIN)
    assert (found["ok"], found["profile"], found["path"], found["exists"], found["kind"]) == (
        True, "web", DOMAIN, True, "part")
    assert found["part"] == {"name": "domain", "folder": "domain/", "instance": "docs", "singular": "module",
                             "role": "entities, values (incl. ids), errors: invariants only",
                             "litmus": found["part"]["litmus"]}
    assert found["may_import"] == [
        {"part": "domain", "scope": "own", "folder": "domain/", "path": "app/modules/docs/domain/"},
        {"part": "kernel", "scope": "none", "folder": "kernel/", "path": "app/kernel/"}]
    assert found["may_import_text"] == "its own module's `domain/`, `kernel/`"
    assert found["libraries"] == [] and "builtins.open" in found["forbidden"]
    assert found["tier"]["name"] == "unit"
    assert found["test"] is None
    assert found["tested_in"] == {"folder": "tests/modules/docs/domain/", "file": "test_invoice.py"}
    assert (found["untested"], found["nearest"], found["closed_tree"], found["note"]) == (None, [], None, None)


def test_json_of_a_test_and_of_an_ungoverned_path():
    test = document("tests/modules/docs/domain/test_invoice.py")
    assert (test["kind"], test["tier"]["name"], test["part"]["name"], test["tested_in"]) == (
        "test", "unit", "domain", None)
    assert test["test"] == {"may_use_fakes": False, "fakes_path": "tests/fakes/", "types_only": [],
                            "code_from": "tests/modules/docs/"}
    stray = document("app/scripts/run.py")
    assert (stray["kind"], stray["part"], stray["closed_tree"]) == ("ungoverned", None, False)
    assert [n["part"] for n in stray["nearest"]][:2] == ["domain", "logic"]


def test_a_path_in_the_project_outside_the_app_is_ungoverned_and_exits_0(tmp_path):
    (tmp_path / "README.md").write_text("x")
    assert lines("README.md")["note"] == "it lies outside the app folder and the tests folder"


@pytest.mark.parametrize("path", ["/etc/passwd", "../elsewhere/x.py"])
def test_a_path_outside_the_project_is_refused_with_exit_2(path):
    text = runner.invoke(app, ["where", path])
    assert text.exit_code == 2 and "lies outside the project" in text.output
    result = runner.invoke(app, ["where", path, "--format", "json"])
    assert result.exit_code == 2
    assert json.loads(result.stdout) == {"ok": False, "error": json.loads(result.stdout)["error"]}
    assert "lies outside the project" in json.loads(result.stdout)["error"]


def test_a_profile_that_cannot_be_used_is_refused_with_exit_2_in_json_too():
    result = runner.invoke(app, ["where", DOMAIN, "--profile", "nowhere", "--format", "json"])
    assert result.exit_code == 2
    assert json.loads(result.stdout)["ok"] is False


def test_a_path_in_an_excluded_folder_says_it_is_excluded_and_why(tmp_path):
    shutil.copytree(BUNDLED, tmp_path / "arch")
    (tmp_path / "arch/mine.yaml").write_text((BUNDLED / "web.yaml").read_text()
                                             + "\nexcluded:\n  samples: example sources the docs show\n")
    (tmp_path / "app/samples").mkdir()
    (tmp_path / "app/samples/run.py").write_text("x = 1\n")
    found = document("app/samples/run.py", "--profile", "arch/mine.yaml")
    assert (found["kind"], found["note"], found["closed_tree"]) == (
        "ungoverned", "excluded from the checks by the profile: example sources the docs show", None)


def test_a_part_that_may_import_every_outside_package_says_so_in_words(tmp_path):
    (tmp_path / "wide.yaml").write_text("xarch: 2\nname: wide\nparts:\n  glue: {path: glue, role: the glue, libraries: everything}\n")
    (tmp_path / "app/glue").mkdir()
    assert lines("app/glue/x.py", "--profile", "wide.yaml")["libraries"] == "any outside package"
    assert document("app/glue/x.py", "--profile", "wide.yaml")["libraries"] == ["*"]
