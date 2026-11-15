"""The cycles check on hand-made source files: no instance of a repeating folder imports, through the others, from
itself; each elementary cycle is one violation, from the instance first by name, at the first import that closes it."""
import pytest

from tests.modules.rules.builders import PROFILE, TWO, imp, profile, source
from xarch.modules.rules.application.logic.cycles import violations


def adapter(instance: str, *imports) -> object:
    return source(f"modules/{instance}/adapters/peer.py", *imports)


def uses(line: int, instance: str):
    return imp(line, f"app.modules.{instance}.contract", "X")


def problems(*files, checked=PROFILE) -> list[str]:
    return [str(v) for v in violations(list(files), checked, "app")]


def hop(instance: str, line: int, to: str, file: str = "adapters/peer.py") -> str:
    return f"app/modules/{instance}/{file}:{line} imports app.modules.{to}.contract"


@pytest.mark.parametrize("files, expected", [
    pytest.param([adapter("a", uses(1, "b")), adapter("b", uses(2, "c"))], [],
                 id="instances that depend on each other in one direction are no cycle"),
    pytest.param([adapter("b", uses(3, "a")), adapter("a", uses(1, "b"))],
                 [f"app/modules/a/adapters/peer.py:1: modules/a → modules/b → modules/a import each other in a cycle: "
                  f"{hop('a', 1, 'b')}; {hop('b', 3, 'a')} (cycles)"],
                 id="two instances importing each other are one cycle, from the first by name"),
    pytest.param([adapter("c", uses(1, "a")), adapter("b", uses(1, "c")), adapter("a", uses(1, "b"))],
                 [f"app/modules/a/adapters/peer.py:1: modules/a → modules/b → modules/c → modules/a import each other "
                  f"in a cycle: {hop('a', 1, 'b')}; {hop('b', 1, 'c')}; {hop('c', 1, 'a')} (cycles)"],
                 id="a cycle through three instances is one violation"),
    pytest.param([adapter("a", uses(1, "b"), uses(2, "c")), adapter("b", uses(1, "a")), adapter("c", uses(1, "a"))],
                 [f"app/modules/a/adapters/peer.py:1: modules/a → modules/b → modules/a import each other in a cycle: "
                  f"{hop('a', 1, 'b')}; {hop('b', 1, 'a')} (cycles)",
                  f"app/modules/a/adapters/peer.py:2: modules/a → modules/c → modules/a import each other in a cycle: "
                  f"{hop('a', 2, 'c')}; {hop('c', 1, 'a')} (cycles)"],
                 id="each elementary cycle is its own violation"),
    pytest.param([adapter("a", uses(7, "b"), uses(3, "b")), adapter("b", uses(1, "a"))],
                 [f"app/modules/a/adapters/peer.py:3: modules/a → modules/b → modules/a import each other in a cycle: "
                  f"{hop('a', 3, 'b')}; {hop('b', 1, 'a')} (cycles)"],
                 id="the import shown for a hop is the first of its file by line"),
    pytest.param([adapter("a", uses(1, "b")), source("modules/a/adapters/other.py", uses(5, "b")),
                  adapter("b", uses(1, "a"))],
                 [f"app/modules/a/adapters/other.py:5: modules/a → modules/b → modules/a import each other in a cycle: "
                  f"{hop('a', 5, 'b', 'adapters/other.py')}; {hop('b', 1, 'a')} (cycles)"],
                 id="and of the files, the first by name"),
    pytest.param([adapter("a", imp(1, "b.contract", "X", up=2)), adapter("b", uses(1, "a"))],
                 [f"app/modules/a/adapters/peer.py:1: modules/a → modules/b → modules/a import each other in a cycle: "
                  f"{hop('a', 1, 'b')}; {hop('b', 1, 'a')} (cycles)"],
                 id="a relative import makes a dependency too"),
    pytest.param([source("modules/a/domain/doc.py", imp(1, "app.modules.b.domain", "doc")),
                  source("modules/b/domain/doc.py", imp(1, "app.modules.a.domain", "doc"))],
                 ["app/modules/a/domain/doc.py:1: modules/a → modules/b → modules/a import each other in a cycle: "
                  "app/modules/a/domain/doc.py:1 imports app.modules.b.domain.doc; "
                  "app/modules/b/domain/doc.py:1 imports app.modules.a.domain.doc (cycles)"],
                 id="whatever the parts"),
    pytest.param([adapter("a", uses(1, "a"), imp(2, "", "x", up=0))], [],
                 id="an import within one instance is no dependency"),
    pytest.param([source("kernel/ids.py", uses(1, "a")), adapter("a", imp(1, "app.kernel", "ids"))], [],
                 id="a file in no instance is not the check's business"),
    pytest.param([source("modules/a/__init__.py", uses(1, "b")), adapter("b", uses(1, "a"))],
                 [f"app/modules/a/__init__.py:1: modules/a → modules/b → modules/a import each other in a cycle: "
                  f"app/modules/a/__init__.py:1 imports app.modules.b.contract; {hop('b', 1, 'a')} (cycles)"],
                 id="the package file of an instance is in it"),
    pytest.param([adapter("a", imp(1, "app.modules", "b")), adapter("b", uses(1, "a"))], [],
                 id="an import of the each root itself names no instance"),
    pytest.param([adapter("a", imp(1, "yaml")), adapter("b", imp(1, "shop.modules.a.contract", "X"))], [],
                 id="an import outside the app's package is none"),
])
def test_cycles(files, expected):
    assert problems(*files) == expected


def test_without_a_repeating_folder_there_are_no_cycles():
    assert problems(adapter("a", uses(1, "b")), adapter("b", uses(1, "a")), checked=profile(repeats=())) == []


def test_a_cycle_names_its_rule():
    assert [v.rule for v in violations([adapter("a", uses(1, "b")), adapter("b", uses(1, "a"))], PROFILE, "app")] == [
        "cycles"]


def test_a_violation_says_which_import_to_remove():
    found = violations([adapter("b", uses(3, "a")), adapter("a", uses(1, "b"))], PROFILE, "app")
    assert [(v.rule, v.fix) for v in found] == [
        ("cycles", "break the cycle: remove the import of app.modules.b.contract at "
                   "app/modules/a/adapters/peer.py:1, or move what it needs to a part that both may import")]


def hooks(instance: str, *imports) -> object:
    return source(f"plugins/{instance}/hooks/run.py", *imports)


def test_instances_of_different_repeating_folders_form_a_cycle_when_they_import_each_other():
    found = violations([adapter("a", imp(1, "app.plugins.p.hooks", "run")),
                        hooks("p", imp(4, "app.modules.a.contract", "X"))], TWO, "app")
    assert [str(v) for v in found] == [
        "app/modules/a/adapters/peer.py:1: modules/a → plugins/p → modules/a import each other in a cycle: "
        "app/modules/a/adapters/peer.py:1 imports app.plugins.p.hooks.run; "
        "app/plugins/p/hooks/run.py:4 imports app.modules.a.contract (cycles)"]


def test_a_module_and_a_plugin_of_the_same_name_are_two_instances():
    assert [str(v) for v in violations([adapter("x", imp(1, "app.plugins.x.hooks", "run")),
                                        hooks("x", imp(2, "app.kernel", "ids"))], TWO, "app")] == []


def test_instances_of_one_repeating_folder_still_form_a_cycle_beside_another_one():
    found = violations([adapter("a", uses(1, "b")), adapter("b", uses(1, "a")), hooks("p", imp(1, "app.kernel"))],
                       TWO, "app")
    assert [v.rule for v in found] == ["cycles"]
