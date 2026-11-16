"""Every violation names the stable id of the check that found it and tells what to do, on a throwaway web project with
one violation planted at a time; and no rule id can produce one without a fix. Where a check's unit tests own the
wording of its fix, word for word, a test here says only that the finding carries one (OWNED); the other rows keep
the fix's wording, which no unit test pins as the real profile says it (CASES)."""
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
TWIN = "class Doc:\n    title: str\n    body: str\n    author: str\n"
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
    pytest.param({}, {"web/conftest.py": f"from {CONTROLLER} import DocumentController\nDocumentController(None)\n"},
                 "types-only", "use controller/ here only as a type, and drive what you test through web/ "
                               "(rendering tests may touch: a fake controller, injected; the real controller's class "
                               "only as a type, never called)", id="types-only"),
    pytest.param(MODULES, {}, "cycles",
                 "break the cycle: remove the import of app.modules.mod.contract at "
                 "app/modules/docs/adapters/mod_review.py:1, or move what it needs to a part that both may import",
                 id="cycles"),
    pytest.param({"modules/docs/domain/document.py": TWIN, "modules/docs/contract/views.py": TWIN.replace("Doc", "DocView")},
                 {}, "no-twins", "keep one of the two and import it from a part both may import, or give DocView the "
                                 "fields its reader needs instead of a copy of Doc's", id="no-twins"),
    pytest.param({"modules/docs/application/ports/notifier.py": NOTIFIER}, {}, "dead-code",
                 "delete Notifier and its fake, or add the code that uses it", id="dead-code: a port"),
    pytest.param({}, {"fakes/notifier.py": "class FakeNotifier:\n    def send(self) -> None: ...\n"}, "dead-code",
                 "delete FakeNotifier, or write the test that uses it", id="dead-code: a fake"),
    pytest.param({}, {"modules/docs/domain/test_x.py": "from tests.modules.docs.domain.test_document import X\n"},
                 "tiers", "move what tests.modules.docs.domain.test_document holds that this test needs into test code "
                          "of its folder that is no test file, and import it from there", id="tiers: a test file"),
    pytest.param({"modules/docs/domain/rule.py": "from typing import Callable\n\n\nclass Rule:\n"
                                                 "    def ok(self, has: Callable[[str], bool]):\n"
                                                 "        return has('x')\n"}, {}, "no-callbacks",
                 "have the caller call has first and pass ok the answer as a value", id="no-callbacks"),
    pytest.param({"modules/docs/application/services/doc.py": "class Publisher: ...\n"}, {}, "names",
                 "rename Publisher to match *Service, or move it to the part whose kind of class it is", id="names"),
    pytest.param({"kernel/x.py": "from app.kernel.y import _z\n"}, {}, "private-imports",
                 "make _z public where it is defined (drop the `_`), or move it to a file both may import",
                 id="private-imports"),
]
"""The rules whose fix the wired tier pins word for word: no unit test asserts it as it is said here."""
OWNED = [
    pytest.param({}, {"modules/docs/domain/test_document.py": f"from {CONTROLLER} import C\n"}, "tiers", id="tiers: an import"),
    pytest.param({}, {"misc/test_x.py": ""}, "tiers", id="tiers: no tier"),
    pytest.param({"web/routes/docs.py": "from app.modules.docs.contract.results import Published\n"}, {},
                 "package-only", id="package-only"),
    pytest.param({}, {"modules/docs/application/test_publish.py": "def test_publish():\n    assert True\n"},
                 "scenario-coverage", id="scenario-coverage"),
    pytest.param({"kernel/x.py": "x = 1  # why\n"}, {}, "no-comments", id="no-comments"),
    pytest.param({"modules/docs/application/ports/repo.py": PORT}, {}, "stand-ins", id="stand-ins"),
    pytest.param({"modules/docs/adapters/x.py": "from app.modules.docs.application.ports.repo import Repo\n\n\n"
                                                 "def size(repo: Repo):\n    return 1\n"}, {}, "must-import", id="must-import"),
    pytest.param({"kernel/a.py": COPY, "kernel/b.py": COPY}, {}, "no-duplicates", id="no-duplicates"),
    pytest.param({"kernel/x.py": "def (:\n"}, {}, "syntax", id="syntax"),
    pytest.param({"modules/docs/contract/ids.py": "from app.modules.docs.domain.values import Document\n"}, {}, "rules",
                 id="rules: a name the pattern does not match"),
    pytest.param({"modules/docs/application/services/doc.py": "class DocService: ...\n",
                  "modules/docs/application/controller.py":
                      "from app.modules.docs.application.services.doc import DocService\n\nDocService()\n"},
                 {}, "built-by", id="built-by"),
]


"""The rules whose fix a unit test of the check asserts word for word: here a finding only has to carry one."""


@pytest.mark.parametrize("app, tests, rule, fix", CASES)
def test_a_violation_names_its_rule_and_carries_its_fix(tmp_path, app, tests, rule, fix):
    assert [(v.rule, v.fix) for v in found(tmp_path, app, tests)] == [(rule, fix)]


@pytest.mark.parametrize("app, tests, rule", OWNED)
def test_a_violation_whose_fix_a_unit_test_owns_names_its_rule_and_carries_a_fix(tmp_path, app, tests, rule):
    assert [(v.rule, bool(v.fix)) for v in found(tmp_path, app, tests)] == [(rule, True)]


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
    cases = {case.values[2] for case in (*CASES, *OWNED)}
    assert cases | {"structure", "test-tree", "closed-tree", "pass-through", "holds", "shared"} == set(RULES)


def test_a_pass_through_is_listed_as_weak_with_its_fix_and_is_no_violation(tmp_path):
    service = ("class DocService:\n    def __init__(self, repo):\n        self.repo = repo\n\n"
               "    def get(self, id):\n        return self.repo.get(id)\n")
    app = write(tmp_path / "app", {**APP, "modules/docs/application/services/doc.py": service})
    result = build_controllers().rules.check(CheckImports(app, "app", "web", write(tmp_path / "tests", TESTS)))
    assert isinstance(result, ImportsChecked)
    assert [(w.rule, w.line, bool(w.fix)) for w in result.enforcement.weak if w.rule == "pass-through"] == [
        ("pass-through", 5, True)]
    assert [f.detail for f in result.enforcement.strict if f.key == "weak" and "pass" in f.detail] == [
        "app/modules/docs/application/services/doc.py:5: DocService.get only passes its arguments on to self.repo.get"]
    assert [v.rule for v in result.violations] == []


def test_every_violation_of_a_check_names_a_rule(tmp_path):
    body = ("import pytest\n\n@pytest.mark.parametrize('given, when, then', [(1, 2, Published)])\n"
            "def test_publish(given, when, then):\n    if given:\n        pass\n")
    violations = found(tmp_path, {}, {"modules/docs/application/test_publish.py": body})
    assert {v.rule for v in violations} == {"scenario-coverage"}
    assert [(v.line, bool(v.fix)) for v in violations] == [(5, True), (3, True), (3, True)]


def test_a_function_of_a_part_that_holds_classes_is_listed_as_weak_with_its_fix_and_is_no_violation(tmp_path):
    app = write(tmp_path / "app", {**APP, "modules/docs/domain/rule.py": "def clean():\n    return 1\n"})
    result = build_controllers().rules.check(CheckImports(app, "app", "web", write(tmp_path / "tests", TESTS)))
    assert isinstance(result, ImportsChecked)
    assert [(w.rule, w.line, bool(w.fix)) for w in result.enforcement.weak if w.rule == "holds"] == [("holds", 1, True)]
    assert [v.rule for v in result.violations] == []


def test_a_test_that_reaches_nothing_its_tier_must_reach_names_its_rule_and_its_fix(tmp_path):
    shutil.copytree(BUNDLED, tmp_path / "arch")
    text = (BUNDLED / "web.yaml").read_text().replace(
        "  integration:\n", "  integration:\n    must_import: [controller]\n", 1)
    (tmp_path / "arch/reach.yaml").write_text(text)
    tests = {**TESTS, "modules/docs/application/test_other.py": "def test_other():\n    assert 1\n"}
    result = build_controllers().rules.check(CheckImports(write(tmp_path / "app", APP), "app",
                                                          str(tmp_path / "arch/reach.yaml"),
                                                          write(tmp_path / "tests", tests)))
    assert isinstance(result, ImportsChecked)
    assert [(v.file, v.rule, bool(v.fix)) for v in result.violations] == [
        ("tests/modules/docs/application/test_other.py", "must-import", True)]


def test_a_file_no_test_of_its_tier_reaches_is_listed_as_weak_with_its_fix(tmp_path):
    app = write(tmp_path / "app", {**APP, "modules/docs/domain/rule.py": "class Rule:\n    def ok(self):\n"
                                                                        "        return 1\n"})
    result = build_controllers().rules.check(CheckImports(app, "app", "web", write(tmp_path / "tests", TESTS)))
    assert isinstance(result, ImportsChecked)
    assert [(w.file, bool(w.fix)) for w in result.enforcement.weak if w.rule == "dead-code"] == [
        ("app/modules/docs/domain/rule.py", True)]


def test_a_shared_part_names_its_rule_and_its_fix(tmp_path):
    shutil.copytree(BUNDLED, tmp_path / "arch")
    text = (BUNDLED / "web.yaml").read_text().replace("  kernel:\n    path: kernel\n",
                                                       "  kernel:\n    path: kernel\n    shared: 2\n")
    (tmp_path / "arch/shared.yaml").write_text(text)
    write(tmp_path / "app", {"kernel/__init__.py": "", "kernel/ids.py": "PREFIX = 'doc'\n",
                             "modules/docs/domain/values.py": "from app.kernel.ids import PREFIX\n\nNAME = PREFIX\n"})
    result = build_controllers().rules.check(CheckImports(tmp_path / "app", "app", str(tmp_path / "arch/shared.yaml")))
    assert isinstance(result, ImportsChecked)
    assert [(v.rule, v.fix) for v in result.violations if v.rule == "shared"] == [
        ("shared", "move PREFIX to modules/docs, its one user, or to the published types of modules/docs if others "
                   "read it through them")]


def test_a_part_used_only_as_a_type_names_its_rule_and_its_fix(tmp_path):
    """No bundled profile holds a part to types_only now that services build their module's contract types, so the
    web profile is given one."""
    shutil.copytree(BUNDLED, tmp_path / "arch")
    services = "    may_import: [logic, domain, ports, contract, kernel, kernel-logic]\n    holds: classes\n"
    text = (BUNDLED / "web.yaml").read_text()
    assert text.count(services) == 1
    (tmp_path / "arch/typed.yaml").write_text(text.replace(services, services + "    types_only: [contract]\n"))
    app = write(tmp_path / "app", {**APP, "modules/docs/application/services/doc.py":
                                   "from app.modules.docs.contract import Published\n\n\nclass DocService:\n"
                                   "    def run(self):\n        return Published()\n"})
    result = build_controllers().rules.check(CheckImports(app, "app", str(tmp_path / "arch/typed.yaml"),
                                                          write(tmp_path / "tests", TESTS)))
    assert isinstance(result, ImportsChecked)
    assert [(v.rule, v.line, bool(v.fix)) for v in result.violations] == [("types-only", 6, True)]
