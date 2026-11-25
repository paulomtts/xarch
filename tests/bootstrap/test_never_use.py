"""The never-use check on a throwaway web project, as the bundled profile lists it: the pure parts may not read the
clock or do I/O by name, and neither may the unit tests of those parts."""
import shutil
from pathlib import Path

import pytest

import xarch
from tests.bootstrap.project import APP, PURE, TESTS, problems, source_check, write
from xarch.modules.rules.contract import DYNAMIC, At, FindingView

BUNDLED = Path(xarch.__file__).parent / "architectures"
DOMAIN = "modules/docs/domain/document.py"


@pytest.mark.parametrize("path, body, problem", [
    (DOMAIN, "from datetime import datetime as dt\n\ndef stamp():\n    return dt.now()\n",
     f"app/{DOMAIN}:4: domain/ of modules/docs may not use datetime.datetime.now (parts.domain.uses.never)"),
    (DOMAIN, "import datetime\n\nTODAY = datetime.date.today()\n",
     f"app/{DOMAIN}:3: domain/ of modules/docs may not use datetime.date.today (parts.domain.uses.never)"),
    (DOMAIN, "def load(path):\n    return open(path).read()\n",
     f"app/{DOMAIN}:2: domain/ of modules/docs may not use builtins.open (parts.domain.uses.never)"),
    ("modules/docs/application/logic/rule.py", "import subprocess\n",
     "app/modules/docs/application/logic/rule.py:1: logic/ of modules/docs may not import subprocess "
     "(parts.logic.uses.never)"),
    ("kernel/clock.py", "from time import time\n",
     "app/kernel/clock.py:1: kernel/ may not import time.time (parts.kernel.uses.never)"),
    (DOMAIN, "def show(print):\n    print('x')\n", None),
    ("platform/clock.py", "from datetime import datetime\n\ndef now():\n    return datetime.now()\n", None),
])
def test_a_pure_part_never_uses_what_the_bundled_profile_lists_for_it(tmp_path, path, body, problem):
    assert problems(tmp_path, app={path: body}) == ([problem] if problem else [])


def test_a_unit_test_of_a_pure_part_is_held_to_its_list(tmp_path):
    body = "from app.modules.docs.domain.document import Document\nimport time\n\ndef test_x():\n    time.time()\n"
    assert problems(tmp_path, tests={"modules/docs/domain/test_document.py": body}) == [
        "tests/modules/docs/domain/test_document.py:5: a test of domain/ (unit tier) may not use time.time "
        "(parts.domain.uses.never; tiers.unit.uses.apply_never)"]


@pytest.mark.parametrize("imported, problem", [
    pytest.param("from app.kernel.clock import now",
                 f"app/{DOMAIN}:1: domain/ of modules/docs may not import app.kernel.clock.now (parts.domain.uses.never)",
                 id="imported from the top: found at the import, which names it in full"),
    pytest.param("from ....kernel.clock import now",
                 f"app/{DOMAIN}:4: domain/ of modules/docs may not use app.kernel.clock.now (parts.domain.uses.never)",
                 id="imported relatively: found at the use, since the import names it from the file's folder"),
])
def test_a_name_of_the_app_on_a_never_list_is_found_however_it_is_imported(tmp_path, imported, problem):
    """No bundled list names a name of the app, which is all a relative import reaches, so the web profile's pure list
    is given one."""
    shutil.copytree(BUNDLED, tmp_path / "arch")
    text = (BUNDLED / "web.yaml").read_text()
    listed = "  pure: [datetime.datetime.now,"
    assert text.count(listed) == 1
    (tmp_path / "arch/clocked.yaml").write_text(text.replace(listed, "  pure: [app.kernel.clock.now, datetime.datetime.now,"))
    body = f"{imported}\n\ndef stamp():\n    return now()\n"
    assert problems(tmp_path, app={"kernel/clock.py": "def now(): ...\n", DOMAIN: body},
                    profile=str(tmp_path / "arch/clocked.yaml")) == [problem]


def test_a_contract_file_is_found_the_same_whether_published_includes_pure_or_writes_its_names_out(tmp_path):
    shutil.copytree(BUNDLED, tmp_path / "arch")
    text = (BUNDLED / "web.yaml").read_text()
    included = "\n  published: [pure, typing.Any]\n"
    assert text.count(included) == 1
    written = tmp_path / "arch/written.yaml"
    written.write_text(text.replace(included, f"\n  published: [{', '.join((*PURE, 'typing.Any'))}]\n"))
    body = "from typing import Any\nimport datetime\n\nSTAMP = datetime.datetime.now()\n"
    contract = "modules/docs/contract/commands.py"
    found = problems(tmp_path / "included", app={contract: body})
    assert found == problems(tmp_path / "written", app={contract: body}, profile=str(written))
    assert found == [
        f"app/{contract}:1: contract/ of modules/docs may not import typing.Any (parts.contract.uses.never)",
        f"app/{contract}:4: contract/ of modules/docs may not use datetime.datetime.now (parts.contract.uses.never)"]
    assert not any("pure" in line or "published" in line for line in found)


@pytest.mark.parametrize("body, problem", [
    pytest.param("from datetime import datetime as D\n\nclock = D\n\n\ndef stamp():\n    return clock.now()\n",
                 f"app/{DOMAIN}:7: domain/ of modules/docs may not use datetime.datetime.now (parts.domain.uses.never)",
                 id="a name bound to an imported name, then used under the new name"),
    pytest.param("import time as t\n\n\ndef stamp():\n    tick = t\n    return tick.time()\n",
                 f"app/{DOMAIN}:6: domain/ of modules/docs may not use time.time (parts.domain.uses.never)",
                 id="the same rebinding in a function"),
])
def test_a_plain_rebinding_in_the_same_file_is_followed(tmp_path, body, problem):
    assert [p for p in problems(tmp_path, profile="cli", app={DOMAIN: body}) if "uses.never" in p] == [problem]


@pytest.mark.parametrize("body, line", [
    pytest.param('import time as t\n\n\ndef stamp():\n    return getattr(t, "time")()\n', 5,
                 id="getattr on a module an import binds"),
    pytest.param('import importlib\n\n\ndef stamp():\n    return importlib.import_module("time").time()\n', 5,
                 id="importlib.import_module"),
    pytest.param('def stamp():\n    return __import__("time").time()\n', 2, id="__import__"),
])
def test_a_name_read_by_a_name_worked_out_at_run_time_is_no_violation_but_is_listed_as_dynamic(tmp_path, body, line):
    """never-use cannot follow it, so it is listed in the enforcement section, which `--strict` fails on."""
    app_files = {k: v for k, v in {**APP, DOMAIN: body}.items() if v is not None}
    result = source_check(write(tmp_path / "app", app_files), "cli", write(tmp_path / "tests", TESTS))
    assert [v for v in result.violations if v.rule == "never-use"] == []
    assert At(f"app/{DOMAIN}", line) in result.enforcement.dynamic
    assert FindingView(DYNAMIC, f"app/{DOMAIN}:{line}") in result.enforcement.strict


def test_a_getattr_of_anything_no_import_binds_is_not_listed(tmp_path):
    body = 'class Doc:\n    title = ""\n\n    def get(self, name):\n        return getattr(self, name)\n'
    app_files = {k: v for k, v in {**APP, DOMAIN: body}.items() if v is not None}
    result = source_check(write(tmp_path / "app", app_files), "cli", write(tmp_path / "tests", TESTS))
    assert [at for at in result.enforcement.dynamic if at.file == f"app/{DOMAIN}"] == []
