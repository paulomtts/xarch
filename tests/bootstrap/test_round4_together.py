"""The features of one round together through the real app, on one small project of modules: a check under `unique`
compared per instance of the repeating folder (a class of billing named as another of billing is a finding, one of
shipping named so is not), a check whose finding in one function is accepted by `function:` under
`checks.<id>.accepted` while the same call in another function of the file is still found, the wiring module left out
of the cycles graph by `cycles.left_out`, a part written as a package file whose stray sibling closed-tree reports,
and a closure that follows a name through the package file re-exporting it by `import-to-definition`, so only the
file that takes the name defined beside sqlalchemy reaches it."""
import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from xarch.bootstrap.app import app

runner = CliRunner()

PROFILE = """\
name: together
parts:
  modules/:
    <module>/:
      application/:
        __init__.py:
          name: facade
          role: the module's facade
          optional: true
          untested: a scratch project
          imports: {may: everything}
        services/:
          name: services
          role: the module's services
          optional: true
          untested: a scratch project
          imports: {may: everything, libraries: [sqlalchemy]}
      domain/:
        name: domain
        role: the module's rules
        optional: true
        untested: a scratch project
        imports: {may: everything}
guards:
  closed-tree: {}
cycles:
  left_out:
    - {path: modules/wiring/, why: the composition root wires every module}
checks:
  domain-names-once:
    read: class
    in: {part: domain}
    unique: {field: name, per: instance}
    message: "{name} at {file}:{line} is named as the class at {first}"
    fix: rename {name}
    examples:
      flagged: {modules/a/domain/x.py: "class A: ...\\n", modules/a/domain/y.py: "class A: ...\\n"}
      clean: {modules/a/domain/x.py: "class A: ...\\n", modules/b/domain/y.py: "class A: ...\\n"}
  one-claim:
    read: method-call
    in: {part: services}
    keep: [{named: with_for_update}]
    may_not: exist
    message: "{file} claims rows at line {line}, in '{function}'"
    fix: claim them through the shared claim
    accepted:
      - {file: modules/billing/application/services/claims.py, function: fail_expired, why: it claims what expired}
    examples:
      flagged: {modules/a/application/services/x.py: "def f(q):\\n    q.with_for_update()\\n"}
      clean: {modules/a/application/services/x.py: "def f(q):\\n    q.all()\\n"}
  domain-never-sql:
    read: import
    in: {part: domain}
    must_not_reach: {targets: [{package: [sqlalchemy]}], through: import-to-definition}
    message: "{file} reaches sqlalchemy at line {line}: {chain}"
    fix: take what it needs through a port
    examples:
      flagged: {modules/a/domain/x.py: "import sqlalchemy\\n"}
      clean: {modules/a/domain/x.py: "import json\\n"}
"""
FACADE = "from .services.invoices import Invoices\nfrom .services.sql import Repo\n"
FILES = {
    "app/__init__.py": "", "app/modules/__init__.py": "",
    "app/modules/wiring/__init__.py": "", "app/modules/wiring/application/__init__.py": "",
    "app/modules/wiring/application/services/__init__.py": "",
    "app/modules/wiring/application/services/build.py": "from app.modules.billing.application import Invoices\n",
    "app/modules/billing/__init__.py": "",
    "app/modules/billing/application/__init__.py": FACADE,
    "app/modules/billing/application/helpers.py": "",
    "app/modules/billing/application/services/__init__.py": "",
    "app/modules/billing/application/services/invoices.py": "class Invoices: ...\n",
    "app/modules/billing/application/services/sql.py": "import sqlalchemy\n\nclass Repo: ...\n",
    "app/modules/billing/application/services/claims.py": (
        "from app.modules.wiring.application.services.build import Invoices\n\n"
        "def fail_expired(q):\n    q.with_for_update()\n\n"
        "def claim(q):\n    q.with_for_update()\n"),
    "app/modules/billing/domain/__init__.py": "",
    "app/modules/billing/domain/invoice.py": "class Invoice: ...\n",
    "app/modules/billing/domain/legacy.py": "class Invoice: ...\n",
    "app/modules/shipping/__init__.py": "", "app/modules/shipping/application/__init__.py": "",
    "app/modules/shipping/domain/__init__.py": "",
    "app/modules/shipping/domain/parcel.py": "from app.modules.billing.application import Invoices\n\nclass Invoice: ...\n",
    "app/modules/shipping/domain/stock.py": "from app.modules.billing.application import Repo\n",
}


@pytest.fixture(autouse=True)
def project(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    Path("together.yaml").write_text(PROFILE)
    for path, text in FILES.items():
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(text)
    Path("tests").mkdir()


def where(path: str) -> dict:
    result = runner.invoke(app, ["where", path, "--profile", "together.yaml", "--format", "json"])
    assert result.exit_code == 0, result.output
    return json.loads(result.stdout)


def test_unique_per_instance_an_accepted_function_a_left_out_root_a_package_file_part_and_a_re_export_together():
    checked = runner.invoke(app, ["profile", "check", "together.yaml"])
    assert checked.exit_code == 0, checked.output

    result = runner.invoke(app, ["check", "--profile", "together.yaml", "--format", "json"])
    document = json.loads(result.stdout)
    assert result.exit_code == 1
    assert [(v["rule"], v["file"], v["line"] or 0, v["message"]) for v in document["violations"]
            if v["rule"] != "closed-tree"] == [
        ("one-claim", "app/modules/billing/application/services/claims.py", 7,
         "app/modules/billing/application/services/claims.py claims rows at line 7, in 'claim'"),
        ("domain-names-once", "app/modules/billing/domain/legacy.py", 1,
         "Invoice at app/modules/billing/domain/legacy.py:1 is named as the class at "
         "app/modules/billing/domain/invoice.py:1"),
        ("domain-never-sql", "app/modules/shipping/domain/stock.py", 1,
         "app/modules/shipping/domain/stock.py reaches sqlalchemy at line 1: "
         "app.modules.billing.application.services.sql -> sqlalchemy")]
    assert [v["file"] for v in document["violations"] if v["rule"] == "closed-tree"] == [
        "app/modules/billing/application/helpers.py"]
    assert [(item["key"], item["file"]) for item in document["enforcement"]["accepted_findings"]] == [
        ("cycles.left_out", "app/modules/wiring"),
        ("checks.one-claim.accepted", "app/modules/billing/application/services/claims.py")]

    assert where("app/modules/billing/application/__init__.py")["part"]["name"] == "facade"
    assert (where("app/modules/billing/application/helpers.py")["kind"],
            where("app/modules/billing/application/helpers.py")["part"]) == ("ungoverned", None)
