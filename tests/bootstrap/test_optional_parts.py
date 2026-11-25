"""Optional parts through the real app: a part, a file of a repeating folder or a folder with what it holds, marked
`optional: true`, whose absence is no `structure` finding and whose presence is checked as any part's; and a repeating
folder beside loose files and named folders of its own folder, none of which is an instance."""
import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from xarch.bootstrap.app import app

runner = CliRunner()

PROFILE = """\
name: sparse
parts:
  kernel/: {role: shared primitives}
  modules/<module>/:
    domain/:
      role: the rules of one module
      imports: {may: [parts.kernel]}
    config.py:
      role: the module's settings
      optional: true
      imports: {may: [parts.kernel]}
    application/:
      controller.py: {role: the module's facade, imports: {may: [module.domain, module.config]}}
      webhook_controller.py:
        role: the facade of a webhook, which few modules have
        optional: true
        imports: {may: [module.domain]}
  api/:
    role: an optional surface
    optional: true
    imports: {may: [parts.kernel]}
    routes.py: {role: its routes, imports: {may: [parts.kernel]}}
  sql/:
    role: the engine and what every store shares
    imports: {may: [parts.kernel, parts.engine]}
    engine.py: {role: the engine, imports: {may: [parts.kernel]}}
    <store>/:
      name: store
      role: one store's repositories
      imports: {may: [parts.sql, parts.engine]}
"""


@pytest.fixture(autouse=True)
def project(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    Path("sparse.yaml").write_text(PROFILE)
    for path, text in {
        "app/__init__.py": "", "app/kernel/__init__.py": "", "app/kernel/ids.py": "NAME = 'x'\n",
        "app/modules/__init__.py": "",
        "app/modules/docs/__init__.py": "", "app/modules/docs/domain/__init__.py": "",
        "app/modules/docs/application/__init__.py": "",
        "app/modules/docs/application/controller.py": "from app.modules.docs import config\n",
        "app/modules/docs/config.py": "from app.kernel import ids\n",
        "app/modules/docs/application/webhook_controller.py": "from app.modules.docs.domain import rules\n",
        "app/modules/users/__init__.py": "", "app/modules/users/domain/__init__.py": "",
        "app/modules/users/application/__init__.py": "", "app/modules/users/application/controller.py": "",
        "app/sql/__init__.py": "", "app/sql/engine.py": "from app.kernel import ids\n",
        "app/sql/schema.py": "from app.sql import engine\n",
        "app/sql/docs/__init__.py": "", "app/sql/docs/repo.py": "from app.sql import engine, schema\n",
        "app/sql/users/__init__.py": "", "app/sql/users/repo.py": "from app.sql.engine import x\n",
    }.items():
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(text)
    Path("tests").mkdir()


def write(path: str, text: str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(text)


def check() -> list[str]:
    result = runner.invoke(app, ["check", "--profile", "sparse.yaml", "--format", "json"])
    document = json.loads(result.stdout)
    return [f"{v['file']}:{v['line'] or 0}: {v['message']}" for v in document["violations"]]


def test_an_optional_part_some_instances_lack_and_an_optional_folder_left_out_give_no_finding():
    assert check() == []


def test_an_optional_part_that_is_there_is_checked_as_any_part():
    write("app/modules/users/config.py", "from app.modules.docs.domain import rules\n")
    assert check() == ["app/modules/users/config.py:1: config/ of modules/users may not import domain/ of "
                       "modules/docs (app.modules.docs.domain)"]


def test_what_an_optional_folder_holds_is_required_once_the_folder_is_there():
    write("app/api/__init__.py", "")
    assert check() == ["app:0: missing api/routes.py"]
    write("app/api/routes.py", "")
    assert check() == []


def test_a_part_that_is_not_optional_is_still_required_in_every_instance():
    Path("app/modules/users/application/controller.py").unlink()
    assert check() == ["app/modules/users:0: missing application/controller.py"]


def test_a_loose_file_beside_the_instances_is_no_instance_and_lies_in_the_folder_s_part():
    write("app/sql/schema.py", "from app.modules.docs.domain import rules\n")
    assert check() == ["app/sql/schema.py:1: sql/ may not import domain/ of modules/docs (app.modules.docs.domain)"]


def test_an_instance_beside_loose_files_is_still_held_to_its_own_rule():
    write("app/sql/docs/other.py", "from app.sql.users import repo\n")
    assert check() == ["app/sql/docs/other.py:1: store/ of sql/docs may not import store/ of sql/users "
                       "(app.sql.users.repo)"]


def test_where_places_a_loose_file_in_the_folder_s_part_and_a_named_file_in_its_own():
    for path, part in (("app/sql/schema.py", "sql"), ("app/sql/engine.py", "engine"), ("app/sql/docs/repo.py", "store")):
        result = runner.invoke(app, ["where", path, "--profile", "sparse.yaml", "--format", "json"])
        assert json.loads(result.stdout)["part"]["name"] == part, path


def test_new_leaves_the_optional_parts_out():
    assert runner.invoke(app, ["new", "module", "billing", "--profile", "sparse.yaml"]).exit_code == 0
    assert Path("app/modules/billing/application/controller.py").is_file()
    assert not Path("app/modules/billing/config.py").exists()
    assert not Path("app/modules/billing/application/webhook_controller.py").exists()
