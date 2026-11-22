"""A profile with two repeating folders through the real app: init, `new` for each word, a clean check, then one
violation of each kind that depends on instances, and `where` and `profile explain` on it."""
import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from xarch.bootstrap.app import app

runner = CliRunner()

PROFILE = """\
name: duo
testing: pytest
parts:
  kernel: {path: kernel, role: shared primitives, litmus: "Is it a primitive?", tests: unit}
  domain:
    path: modules/<module>/domain
    role: entities and rules of one module
    litmus: Is it an invariant of one module?
    may_import: [kernel]
    tests: unit
  contract:
    path: modules/<module>/contract
    role: what a module shows to the others
    litmus: Does another folder need it?
    may_import: [domain, kernel]
    tests: integration
    package_only: true
  adapters:
    path: modules/<module>/adapters
    role: talks to a technology
    litmus: Does it touch a technology?
    may_import: [domain, kernel, contract@any, hooks@any]
    tests: unit
  hooks:
    path: plugins/<plugin>/hooks
    role: what a plugin runs
    litmus: Does a plugin run it?
    may_import: [manifest, kernel, contract@any]
    must_import: [manifest, contract@any]
    tests: integration
  manifest:
    path: plugins/<plugin>/manifest.py
    role: what a plugin declares
    litmus: Does a plugin declare it?
    may_import: [kernel]
    tests: unit
tiers:
  unit: {proves: a rule, litmus: "Does it run with nothing outside?"}
  integration: {proves: a seam, litmus: "Does it cross a folder?"}
guards:
  closed-tree: {}
docs:
  pages:
    architecture.md: architecture.tpl.md
"""
TEMPLATE = "{{tree}}\n\n{{rules_table}}\n\n{{guards}}\n"
WORK = "def run():\n    return manifest.NAME\n"


@pytest.fixture(autouse=True)
def project(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "arch").mkdir()
    (tmp_path / "arch" / "duo.yaml").write_text(PROFILE)
    (tmp_path / "arch" / "architecture.tpl.md").write_text(TEMPLATE)
    (tmp_path / "pyproject.toml").write_text("[tool.xarch]\n")
    assert runner.invoke(app, ["init", "--profile", "arch/duo.yaml"]).exit_code == 0
    for word, name in (("module", "billing"), ("module", "shop"), ("plugin", "seo"), ("plugin", "mail")):
        assert runner.invoke(app, ["new", word, name]).exit_code == 0
    write("app/modules/billing/domain/invoice.py", "TOTAL = 1\n")
    write("app/modules/billing/contract/__init__.py", "from app.modules.billing.domain.invoice import TOTAL\n")
    write("app/plugins/seo/manifest.py", "from app.kernel import ids\n\nNAME = ids.NAME\n")
    write("app/plugins/seo/hooks/run.py",
          f"from app.plugins.seo import manifest\n\n\n{WORK}")
    write("app/kernel/ids.py", "NAME = 'x'\n")
    write("tests/modules/billing/domain/test_invoice.py", "from app.modules.billing.domain import invoice\n")
    return tmp_path


def write(path: str, text: str) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text)


def check(*args: str) -> tuple[int, list[str]]:
    result = runner.invoke(app, ["check", *args, "--format", "json"])
    document = json.loads(result.stdout)
    return result.exit_code, [f"{v['file']}:{v['line'] or 0}: {v['message']}" for v in document["violations"]]


def test_init_and_new_make_every_repeating_folder_with_its_own_parts():
    for path in ("modules/billing/domain", "modules/billing/contract", "modules/billing/adapters",
                 "plugins/seo/hooks"):
        assert Path("app", path, "__init__.py").is_file(), path
    assert Path("app/plugins/seo/manifest.py").is_file()
    assert not Path("app/plugins/seo/domain").exists() and not Path("app/modules/billing/hooks").exists()


def test_the_generated_docs_show_both_repeating_folders_in_the_tree_and_the_import_table():
    text = Path("docs/project/architecture.md").read_text()
    assert "└── <module>/" in text and "└── <plugin>/" in text
    assert "| `adapters/` | its own module's `domain/`, `kernel/`, any module's `contract/`, any plugin's `hooks/` |" in text
    assert "| `hooks/` | its own plugin's `manifest.py`, `kernel/`, any module's `contract/` |" in text


def test_a_whole_project_of_two_repeating_folders_checks_clean():
    code, found = check()
    assert (code, found) == (0, [])


def test_a_part_importing_another_instances_part_without_any_is_a_violation():
    write("app/modules/billing/adapters/db.py", "from app.modules.shop.domain import thing\n")
    code, found = check()
    assert code == 1
    assert found == ["app/modules/billing/adapters/db.py:1: adapters/ of modules/billing may not import domain/ of "
                     "modules/shop (app.modules.shop.domain)"]


def test_the_same_import_of_another_instance_is_allowed_where_the_row_says_any():
    write("app/modules/shop/contract/__init__.py", "")
    write("app/modules/billing/adapters/db.py", "from app.modules.shop.contract import thing\n")
    assert check() == (0, [])


def test_a_cross_folder_import_the_rules_do_not_allow_is_a_violation():
    write("app/plugins/seo/hooks/run.py", f"from app.plugins.seo import manifest\nfrom app.modules.billing import "
                                          f"domain\n\n\n{WORK}")
    code, found = check()
    assert code == 1
    assert found == ["app/plugins/seo/hooks/run.py:2: hooks/ of plugins/seo may not import domain/ of "
                     "modules/billing (app.modules.billing.domain)"]


def test_a_cross_folder_import_the_rules_do_not_allow_is_a_violation_the_other_way_round_too():
    write("app/modules/billing/domain/invoice.py", "from app.plugins.seo import manifest\n")
    code, found = check()
    assert code == 1
    assert found == ["app/modules/billing/domain/invoice.py:1: domain/ of modules/billing may not import "
                     "manifest/ of plugins/seo (app.plugins.seo.manifest)"]


def test_instances_of_the_two_folders_that_import_each_other_form_a_cycle():
    write("app/modules/billing/adapters/db.py", "from app.plugins.seo.hooks import run\n")
    write("app/plugins/seo/hooks/run.py",
          f"from app.plugins.seo import manifest\nfrom app.modules.billing.contract import TOTAL\n\n\n{WORK}")
    code, found = check()
    assert code == 1 and len(found) == 1
    assert found[0].startswith("app/modules/billing/adapters/db.py:1: modules/billing → plugins/seo → modules/billing "
                               "import each other in a cycle")


def test_a_missing_part_is_found_in_each_repeating_folder_by_its_own_parts():
    Path("app/plugins/mail/manifest.py").unlink()
    Path("app/modules/shop/contract/__init__.py").unlink()
    Path("app/modules/shop/contract").rmdir()
    code, found = check()
    assert code == 1
    assert found == ["app/modules/shop:0: missing contract/", "app/plugins/mail:0: missing manifest.py"]


def test_a_test_folder_that_mirrors_no_folder_is_found_below_each_repeating_folder():
    write("tests/plugins/seo/hooks/test_run.py", "from app.plugins.seo.hooks import run\n")
    write("tests/plugins/ghost/helpers.py", "")
    write("tests/modules/ghost/helpers.py", "")
    code, found = check()
    assert code == 1
    assert sorted(found) == [
        "tests/modules/ghost:0: mirrors no folder of the app (app/modules/ghost)",
        "tests/plugins/ghost:0: mirrors no folder of the app (app/plugins/ghost)"]


def test_a_test_below_the_second_repeating_folder_imports_only_what_its_part_may():
    write("tests/plugins/seo/hooks/test_run.py", "from app.plugins.seo.hooks import run\nfrom app.modules.billing."
                                                  "contract import TOTAL\n")
    assert check() == (0, [])
    write("tests/plugins/seo/hooks/test_run.py", "from app.modules.billing.domain import invoice\n")
    code, found = check()
    assert code == 1
    assert found == [
        "tests/plugins/seo/hooks/test_run.py:1: a test of hooks/ (integration tier) may not import domain/ of "
        "modules/billing (app.modules.billing.domain.invoice): it imports only what hooks/ may "
        "(parts.hooks.may_import)"]


def test_a_file_of_a_part_that_must_import_reaches_it_through_a_sibling_of_its_own_instance_only():
    write("app/plugins/seo/hooks/helper.py", "from app.plugins.seo import manifest\n")
    write("app/plugins/seo/hooks/run.py", f"from app.plugins.seo.hooks import helper\n\n\n{WORK}")
    assert check() == (0, [])
    write("app/plugins/seo/hooks/run.py", f"from app.plugins.mail.hooks import helper\n\n\n{WORK}")
    write("app/plugins/mail/hooks/helper.py", "from app.plugins.mail import manifest\n")
    code, found = check()
    assert code == 1
    assert [line.split(": ", 1)[0] for line in found] == ["app/plugins/seo/hooks/run.py:0",
                                                          "app/plugins/seo/hooks/run.py:1"]


def test_a_file_in_no_part_of_either_folder_is_a_closed_tree_violation():
    write("app/plugins/seo/stray.py", "")
    write("app/modules/billing/stray.py", "")
    code, found = check()
    assert code == 1
    assert [line.split(": ", 1)[0] for line in found] == ["app/modules/billing/stray.py:0",
                                                          "app/plugins/seo/stray.py:0"]


def test_where_names_each_path_by_the_word_of_its_own_repeating_folder():
    plugin = json.loads(runner.invoke(app, ["where", "app/plugins/seo/hooks/run.py", "--format", "json"]).stdout)
    module = json.loads(runner.invoke(app, ["where", "app/modules/billing/domain/invoice.py", "--format", "json"]).stdout)
    assert (plugin["part"]["name"], plugin["part"]["instance"], plugin["part"]["singular"]) == ("hooks", "seo", "plugin")
    assert (module["part"]["name"], module["part"]["instance"], module["part"]["singular"]) == (
        "domain", "billing", "module")
    paths = {entry["part"]: entry["path"] for entry in plugin["may_import"]}
    assert paths == {"hooks": "app/plugins/seo/hooks/", "manifest": "app/plugins/seo/manifest.py",
                     "kernel": "app/kernel/", "contract": "app/modules/<module>/contract/"}


def test_where_a_test_of_the_second_repeating_folder_says_which_file_it_mirrors():
    result = runner.invoke(app, ["where", "tests/plugins/seo/hooks/test_run.py"])
    assert result.exit_code == 0, result.output
    assert "mirrors:        hooks/ in plugin 'seo'" in result.output
    assert "its own plugin's `hooks/` and `manifest.py`, `kernel/`, any module's `contract/`" in result.output


def test_new_refuses_a_word_the_profile_does_not_have_listing_all_of_them():
    result = runner.invoke(app, ["new", "feature", "x"])
    assert result.exit_code == 2
    assert "no kind 'feature' in the profile: use module, plugin" in result.output


def test_profile_explain_and_profile_check_work_on_a_profile_with_two_repeating_folders():
    shown = runner.invoke(app, ["profile", "explain", "--profile", "arch/duo.yaml"])
    assert shown.exit_code == 0, shown.output
    assert "└── <module>/" in shown.output and "└── <plugin>/" in shown.output
    checked = runner.invoke(app, ["profile", "check", "arch/duo.yaml"])
    assert checked.exit_code == 0, checked.output
    assert "loads: ok" in checked.output
