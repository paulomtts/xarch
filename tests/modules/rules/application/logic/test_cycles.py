"""The cycles check on hand-made source files: no instance of a repeating folder imports, through the others, from
itself; each group of instances that all reach each other is one violation, naming the dependencies to cut, each with
its imports, at the first import of the first of them."""
import pytest

from tests.modules.rules.builders import PROFILE, TWO, imp, profile, source
from xarch.modules.rules.application.logic.cycles import violations


def adapter(instance: str, *imports, file: str = "adapters/peer.py") -> object:
    return source(f"modules/{instance}/{file}", *imports)


def uses(line: int, instance: str):
    return imp(line, f"app.modules.{instance}.contract", "X")


def problems(*files, checked=PROFILE) -> list[str]:
    return [str(v) for v in violations(list(files), checked, "app")]


def hop(instance: str, line: int, to: str, file: str = "adapters/peer.py") -> str:
    return f"app/modules/{instance}/{file}:{line} imports app.modules.{to}.contract"


def cut(instance: str, to: str, *imports: str) -> str:
    return f"modules/{instance} → modules/{to}: {', '.join(imports)}"


def said(at: str, group: str, count: int, *cuts: str) -> str:
    many = "the one" if len(cuts) == 1 else f"the {len(cuts)}"
    return f"{at}: {group} import each other in a cycle, through {count} dependencies; {many} to cut: " \
           f"{'; '.join(cuts)} (cycles)"


AB = "modules/a and modules/b"
ABC = "modules/a, modules/b and modules/c"
PEER = "app/modules/{}/adapters/peer.py:{}"


@pytest.mark.parametrize("files, expected", [
    pytest.param([adapter("a", uses(1, "b")), adapter("b", uses(2, "c"))], [],
                 id="instances that depend on each other in one direction are no cycle"),
    pytest.param([adapter("b", uses(3, "a")), adapter("a", uses(1, "b"))],
                 [said(PEER.format("b", 3), AB, 2, cut("b", "a", hop("b", 3, "a")))],
                 id="two instances importing each other once each are one group, cut back to the first by name"),
    pytest.param([adapter("c", uses(1, "a")), adapter("b", uses(1, "c")), adapter("a", uses(1, "b"))],
                 [said(PEER.format("c", 1), ABC, 3, cut("c", "a", hop("c", 1, "a")))],
                 id="a cycle through three instances is one violation, with one dependency to cut"),
    pytest.param([adapter("a", uses(1, "b"), uses(2, "c")), adapter("b", uses(1, "a")), adapter("c", uses(1, "a"))],
                 [said(PEER.format("b", 1), ABC, 4, cut("b", "a", hop("b", 1, "a")), cut("c", "a", hop("c", 1, "a")))],
                 id="the cycles of one group of instances are one violation, not one each"),
    pytest.param([adapter("a", uses(1, "b")), adapter("b", uses(1, "c"), uses(2, "a")), adapter("c", uses(1, "a"))],
                 [said(PEER.format("a", 1), ABC, 4, cut("a", "b", hop("a", 1, "b")))],
                 id="one dependency that every cycle runs through is the only one to cut"),
    pytest.param([adapter("a", uses(1, "b"), uses(2, "b")), adapter("b", uses(1, "a"))],
                 [said(PEER.format("b", 1), AB, 2, cut("b", "a", hop("b", 1, "a")))],
                 id="the dependency to cut is the one made by fewer imports"),
    pytest.param([adapter("a", uses(1, "b")), adapter("b", uses(1, "a"), uses(2, "a"))],
                 [said(PEER.format("a", 1), AB, 2, cut("a", "b", hop("a", 1, "b")))],
                 id="whichever way it goes"),
    pytest.param([adapter("a", uses(1, "b")), adapter("b", uses(1, "a")),
                  adapter("c", uses(4, "d")), adapter("d", uses(5, "c"))],
                 [said(PEER.format("b", 1), AB, 2, cut("b", "a", hop("b", 1, "a"))),
                  said(PEER.format("d", 5), "modules/c and modules/d", 2, cut("d", "c", hop("d", 5, "c")))],
                 id="two groups that do not reach each other are two violations"),
    pytest.param([adapter("a", uses(1, "b")), adapter("b", uses(1, "a"), uses(2, "c")), adapter("c", uses(1, "d"))],
                 [said(PEER.format("b", 1), AB, 2, cut("b", "a", hop("b", 1, "a")))],
                 id="an instance the group only reaches is not in it"),
    pytest.param([adapter("a", uses(3, "b"), uses(7, "b")), adapter("b", uses(4, "a"), uses(1, "a"))],
                 [said(PEER.format("b", 1), AB, 2, cut("b", "a", hop("b", 1, "a"), hop("b", 4, "a")))],
                 id="every import of a dependency to cut is listed, by line"),
    pytest.param([adapter("a", uses(1, "b"), uses(2, "b")), adapter("b", uses(1, "a")),
                  adapter("b", uses(5, "a"), file="adapters/other.py")],
                 [said("app/modules/b/adapters/other.py:5", AB, 2,
                       cut("b", "a", hop("b", 5, "a", "adapters/other.py"), hop("b", 1, "a")))],
                 id="and by file first"),
    pytest.param([adapter("a", uses(1, "b")), adapter("b", imp(2, "app.modules.a.contract", "X", "Y"))],
                 [said(PEER.format("b", 2), AB, 2, cut("b", "a", hop("b", 2, "a")))],
                 id="an import taking several names from one place is listed once"),
    pytest.param([adapter("a", imp(1, "b.contract", "X", up=2)), adapter("b", uses(1, "a"))],
                 [said(PEER.format("b", 1), AB, 2, cut("b", "a", hop("b", 1, "a")))],
                 id="a relative import makes a dependency too"),
    pytest.param([source("modules/a/domain/doc.py", imp(1, "app.modules.b.domain", "doc")),
                  source("modules/b/domain/doc.py", imp(1, "app.modules.a.domain", "doc"))],
                 [said("app/modules/b/domain/doc.py:1", AB, 2,
                       "modules/b → modules/a: app/modules/b/domain/doc.py:1 imports app.modules.a.domain.doc")],
                 id="whatever the parts"),
    pytest.param([adapter("a", uses(1, "a"), imp(2, "", "x", up=0))], [],
                 id="an import within one instance is no dependency"),
    pytest.param([source("kernel/ids.py", uses(1, "a")), adapter("a", imp(1, "app.kernel", "ids"))], [],
                 id="a file in no instance is not the check's business"),
    pytest.param([adapter("a", uses(1, "b")), source("modules/b/__init__.py", uses(1, "a"))],
                 [said("app/modules/b/__init__.py:1", AB, 2,
                       "modules/b → modules/a: app/modules/b/__init__.py:1 imports app.modules.a.contract")],
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


def fixes(*files) -> list[str | None]:
    return [v.fix for v in violations(list(files), PROFILE, "app")]


def test_a_violation_says_which_dependency_to_cut():
    assert fixes(adapter("b", uses(3, "a")), adapter("a", uses(1, "b"))) == [
        "break the cycle: remove the imports of modules/b → modules/a the message lists, or move what they need to a "
        "part that both may import"]


def test_a_violation_with_several_dependencies_to_cut_names_each():
    assert fixes(adapter("a", uses(1, "b"), uses(2, "c")), adapter("b", uses(1, "a")), adapter("c", uses(1, "a"))) == [
        "break the cycles: remove the imports of modules/b → modules/a and modules/c → modules/a the message lists, "
        "or move what each needs to a part that both of its ends may import"]


def hooks(instance: str, *imports) -> object:
    return source(f"plugins/{instance}/hooks/run.py", *imports)


def test_instances_of_different_repeating_folders_form_a_cycle_when_they_import_each_other():
    found = violations([adapter("a", imp(1, "app.plugins.p.hooks", "run")),
                        hooks("p", imp(4, "app.modules.a.contract", "X"))], TWO, "app")
    assert [str(v) for v in found] == [
        "app/plugins/p/hooks/run.py:4: modules/a and plugins/p import each other in a cycle, through 2 dependencies; "
        "the one to cut: plugins/p → modules/a: app/plugins/p/hooks/run.py:4 imports app.modules.a.contract (cycles)"]


def test_a_module_and_a_plugin_of_the_same_name_are_two_instances():
    assert [str(v) for v in violations([adapter("x", imp(1, "app.plugins.x.hooks", "run")),
                                        hooks("x", imp(2, "app.kernel", "ids"))], TWO, "app")] == []


def test_instances_of_one_repeating_folder_still_form_a_cycle_beside_another_one():
    found = violations([adapter("a", uses(1, "b")), adapter("b", uses(1, "a")), hooks("p", imp(1, "app.kernel"))],
                       TWO, "app")
    assert [v.rule for v in found] == ["cycles"]
