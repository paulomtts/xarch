"""The top-level `cycles` key: the groups of the cycles graph the profile accepts by their nodes (`accepted`), and the
nodes it leaves out of that graph (`left_out`), such as a composition root, each with why; every way of writing one
wrong is refused at its address."""
from tests.modules.spec.profiles import SOURCE as FILE
from tests.modules.spec.profiles import layered, parsed
from tests.modules.spec.profiles import problems as refused
from xarch.profile_values.placement import AcceptedCycle, LeftOut


def problems(document: dict) -> list[str]:
    return [problem.removeprefix(f"{FILE}: ") for problem in refused(document)]


def test_a_profile_without_cycles_accepts_none_and_leaves_none_out():
    architecture = parsed(layered())
    assert (architecture.cycles_accepted, architecture.cycles_left_out) == ((), ())


def test_each_entry_loads_in_the_order_written_its_nodes_by_their_path_below_the_app():
    architecture = parsed(layered(cycles={
        "accepted": [{"group": ["src/billing/", "src/orders"], "why": "billing and orders merge next"}],
        "left_out": [{"path": "src/wiring/", "why": "the composition root imports every module"}]}))
    assert architecture.cycles_accepted == (
        AcceptedCycle((("src", "billing"), ("src", "orders")), "billing and orders merge next"),)
    assert architecture.cycles_left_out == (LeftOut(("src", "wiring"), "the composition root imports every module"),)


def test_cycles_written_wrong_is_refused_at_its_address():
    assert problems(layered(cycles=[])) == ["cycles: must be a map {accepted, left_out}"]
    assert problems(layered(cycles={"kept": []})) == ["cycles: unknown key 'kept': use accepted, left_out"]
    assert problems(layered(cycles={"accepted": {}})) == [
        "cycles.accepted: must be a list of {group, why}, such as [{group: [<node>, <node>], why: <the reason>}]"]
    assert problems(layered(cycles={"left_out": []})) == [
        "cycles.left_out: must be a list of {path, why}, such as [{path: <node>, why: <the reason>}]"]


def test_an_entry_written_wrong_is_refused_at_its_index():
    def accepted(*entries) -> list[str]:
        return problems(layered(cycles={"accepted": list(entries)}))

    assert accepted({"group": ["src/a", "src/b"]}) == ["cycles.accepted.0: missing `why`"]
    assert accepted({"group": ["src/a"], "why": "w"}) == [
        "cycles.accepted.0.group: must list two nodes or more, each once: a cycle runs between nodes"]
    assert accepted({"group": ["src/a", "src/a/"], "why": "w"}) == [
        "cycles.accepted.0.group: must list two nodes or more, each once: a cycle runs between nodes"]
    assert accepted({"group": ["src/a", "shared"], "why": "w"}) == [
        "cycles.accepted.0.group.1: shared is no node of the cycles graph: a node is an instance of a repeating "
        "folder, or a folder the layout names beside them, such as src/<module>"]
    left = problems(layered(cycles={"left_out": [{"path": "src/a/api", "why": "w"}]}))
    assert left == ["cycles.left_out.0.path: src/a/api is no node of the cycles graph: a node is an instance of a "
                    "repeating folder, or a folder the layout names beside them, such as src/<module>"]
