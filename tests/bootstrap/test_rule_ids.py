"""Every violation names the stable id of the check that found it and tells what to do, on a throwaway web project with
one violation planted at a time; and no rule id can produce one without a fix."""
import shutil
from pathlib import Path

import pytest

import xarch
from tests.bootstrap.project import APP, TESTS, write
from xarch.bootstrap.wiring import build_controllers
from xarch.kernel.violations import RULES, Violation
from xarch.modules.layout.contract import CheckStructure
from xarch.modules.rules.contract import CheckImports, ImportsChecked

CONTROLLER = "app.modules.docs.application.controller"
MODULES = {"modules/mod/__init__.py": "", "modules/mod/contract/__init__.py": "",
           "modules/docs/adapters/mod_review.py": "from app.modules.mod.contract import Clean\n",
           "modules/mod/adapters/docs_review.py": "from app.modules.docs.contract import Published\n"}
PORT = "from typing import Protocol\n\nclass Repo(Protocol):\n    def get(self) -> int: ...\n"
NOTIFIER = "from typing import Protocol\n\n\nclass Notifier(Protocol):\n    def send(self) -> None: ...\n"
COPY = "def copy(a):\n    b = a + 1\n    c = b * 2\n    d = c - 3\n    return d\n"
BUNDLED = Path(xarch.__file__).parent / "architectures"


def found(tmp_path: Path, app: dict[str, str], tests: dict[str, str]) -> list[Violation]:
    result = build_controllers().rules.check(CheckImports(write(tmp_path / "app", {**APP, **app}), "app", "web",
                                                          write(tmp_path / "tests", {**TESTS, **tests})))
    assert isinstance(result, ImportsChecked)
    return list(result.violations)


CASES = [
    pytest.param({"kernel/x.py": "from app.platform import sql\n"}, {}, "rules",
                 "import only kernel/ in kernel/ (parts.kernel.may_import), or move this code to adapters/, which may import it",
                 id="rules"),
    pytest.param({"kernel/x.py": "import requests\n"}, {}, "libraries",
                 "use the standard library or a package listed in parts.kernel.libraries, since requests is listed for "
                 "no part", id="libraries"),
    pytest.param({"kernel/x.py": "import socket\n"}, {}, "forbidden",
                 "do what needs socket outside kernel/, and hand kernel/ the result", id="forbidden"),
    pytest.param({}, {"modules/docs/domain/test_document.py": f"from {CONTROLLER} import C\n"}, "tiers",
                 "import here only what domain/ may; test controller/ of modules/docs from the folder that mirrors it",
                 id="tiers: an import"),
    pytest.param({}, {"misc/test_x.py": ""}, "tiers",
                 "move it to the folder that mirrors its subject's path in the app, or into a tier's `folder`",
                 id="tiers: no tier"),
    pytest.param({}, {"web/conftest.py": f"from {CONTROLLER} import DocumentController\nDocumentController(None)\n"},
                 "types-only", "use controller/ here only as a type, and drive what you test through web/ "
                               "(rendering tests may touch: a fake controller, injected; the real controller's class "
                               "only as a type, never called)", id="types-only"),
    pytest.param(MODULES, {}, "cycles",
                 "break the cycle: remove the import of app.modules.mod.contract at "
                 "app/modules/docs/adapters/mod_review.py:1, or move what it needs to a part that both may import",
                 id="cycles"),
    pytest.param({"web/routes/docs.py": "from app.modules.docs.contract.results import Published\n"}, {},
                 "package-only", "import from app.modules.docs.contract", id="package-only"),
    pytest.param({}, {"modules/docs/application/test_publish.py": "def test_publish():\n    assert True\n"},
                 "scenario-coverage", "add a table test whose parameters are given, when, then",
                 id="scenario-coverage"),
    pytest.param({"kernel/x.py": "x = 1  # why\n"}, {}, "no-comments",
                 "say it in a docstring or a name, and delete the comment", id="no-comments"),
    pytest.param({"modules/docs/application/ports/repo.py": PORT}, {}, "stand-ins",
                 "write FakeRepo under tests/fakes/", id="stand-ins"),
    pytest.param({"modules/docs/adapters/x.py": "from app.modules.docs.application.ports.repo import Repo\n\n\n"
                                                 "def size(repo: Repo):\n    return 1\n"}, {}, "must-import",
                 "import what it wraps from platform/ or contract/, or an outside package, or move its code to a part that needs no "
                 "technology", id="must-import"),
    pytest.param({"kernel/a.py": COPY, "kernel/b.py": COPY}, {}, "no-duplicates",
                 "keep one of the two and import it where the other is, or move it to a part both may import when they "
                 "cannot import each other", id="no-duplicates"),
    pytest.param({"modules/docs/application/ports/notifier.py": NOTIFIER}, {}, "dead-code",
                 "delete Notifier and its fake, or write the service step that uses it", id="dead-code: a port"),
    pytest.param({}, {"fakes/notifier.py": "class FakeNotifier:\n    def send(self) -> None: ...\n"}, "dead-code",
                 "delete FakeNotifier, or write the test that uses it", id="dead-code: a fake"),
    pytest.param({"kernel/x.py": "def (:\n"}, {}, "syntax", "correct the syntax so that the file can be read",
                 id="syntax"),
]


@pytest.mark.parametrize("app, tests, rule, fix", CASES)
def test_a_violation_names_its_rule_and_carries_its_fix(tmp_path, app, tests, rule, fix):
    assert [(v.rule, v.fix) for v in found(tmp_path, app, tests)] == [(rule, fix)]


def structural(tmp_path: Path) -> list[Violation]:
    app, tests = write(tmp_path / "app", APP), write(tmp_path / "tests", TESTS)
    (tests / "modules/ghost").mkdir()
    return list(build_controllers().layout.check(CheckStructure(app, "app", "web", tests)).violations)


def test_the_layout_checks_name_their_rule_and_carry_their_fix(tmp_path):
    violations = structural(tmp_path)
    assert [(v.rule, v.fix) for v in violations if v.rule == "test-tree"] == [
        ("test-tree", "create app/modules/ghost/ in the app, or move what it holds to the folder that mirrors its "
                      "subject, or remove it")]
    assert ("structure", "create app/bootstrap/") in [(v.rule, v.fix) for v in violations]


def test_a_closed_tree_names_its_rule_and_its_fix(tmp_path):
    shutil.copytree(BUNDLED, tmp_path / "arch")
    text = (BUNDLED / "web.yaml").read_text().replace("  no-comments: {}\n",
                                                       "  no-comments: {}\n  closed-tree: {}\n")
    (tmp_path / "arch/closed.yaml").write_text(text)
    write(tmp_path / "app", {"stray.py": ""})
    result = build_controllers().rules.check(CheckImports(tmp_path / "app", "app", str(tmp_path / "arch/closed.yaml")))
    assert isinstance(result, ImportsChecked)
    assert [(v.rule, v.fix) for v in result.violations] == [
        ("closed-tree", "move app/stray.py into the part that fits it (run xarch where app/stray.py), or add its "
                        "folder to the layout")]


def test_every_rule_id_has_a_case_here_that_produces_a_violation_with_a_fix():
    cases = {case.values[2] for case in CASES}
    assert cases | {"structure", "test-tree", "closed-tree", "pass-through"} == set(RULES)


def test_a_pass_through_is_listed_as_weak_with_its_fix_and_is_no_violation(tmp_path):
    service = ("class DocService:\n    def __init__(self, repo):\n        self.repo = repo\n\n"
               "    def get(self, id):\n        return self.repo.get(id)\n")
    app = write(tmp_path / "app", {**APP, "modules/docs/application/services/doc.py": service})
    result = build_controllers().rules.check(CheckImports(app, "app", "web", write(tmp_path / "tests", TESTS)))
    assert isinstance(result, ImportsChecked)
    assert [(w.rule, w.line, w.fix) for w in result.enforcement.weak] == [
        ("pass-through", 5, "have the caller use self.repo.get, or keep it as a deliberate plain forward: it stays listed and fails "
                            "only `check --strict`")]
    assert [f.detail for f in result.enforcement.strict if f.key == "weak"] == [
        "app/modules/docs/application/services/doc.py:5: DocService.get only passes its arguments on to self.repo.get"]
    assert [v.rule for v in result.violations] == []


def test_every_violation_of_a_check_names_a_rule(tmp_path):
    body = ("import pytest\n\n@pytest.mark.parametrize('given, when, then', [(1, 2, Published)])\n"
            "def test_publish(given, when, then):\n    if given:\n        pass\n")
    violations = found(tmp_path, {}, {"modules/docs/application/test_publish.py": body})
    assert {v.rule for v in violations} == {"scenario-coverage"}
    assert [v.fix for v in violations] == [
        "arrange from given, act with when, assert == then, and give the odd case its own test",
        'write pytest.param(..., id="<a sentence stating the outcome>")',
        "add a row whose then is Missing, or a standalone test naming it"]
