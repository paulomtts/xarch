"""The `forbidden` key of an architecture file: the calls and modules each part may not use, and the tiers whose
tests are held to the list of the part they mirror."""
import pytest

from xarch.modules.spec.domain.architecture_file import parse_architecture
from xarch.modules.spec.domain.docs_template import fill
from xarch.modules.spec.domain.errors import InvalidArchitecture

TIER = {"name": "unit", "subject": ["service", "contract", "store"], "proves": "a rule", "may_touch": "nothing",
        "litmus": "Does it call a rule?"}


def layered(**extra) -> dict:
    return {
        "xarch": 1, "name": "layered",
        "layout": {"src": {"singular": "module", "each": {"contract": {}, "service": {}, "store": {}}}},
        "parts": {"contract": {"path": "src/*/contract", "role": "what callers send and get back"},
                  "service": {"path": "src/*/service", "role": "business logic"},
                  "store": {"path": "src/*/store", "role": "database access"}},
        "rules": {},
        **extra,
    }


def load(document):
    return parse_architecture(document, "layered.yaml", lambda relative: True)


def problems(document) -> list[str]:
    with pytest.raises(InvalidArchitecture) as caught:
        load(document)
    return list(caught.value.problems)


def test_forbidden_gives_each_listed_part_its_dotted_names_and_modules():
    architecture = load(layered(forbidden={"service": ["datetime.datetime.now", "builtins.open", "socket"]}))
    assert architecture.forbidden == {"service": (("datetime", "datetime", "now"), ("builtins", "open"), ("socket",))}


def test_without_forbidden_no_part_has_a_list():
    assert load(layered()).forbidden == {}


@pytest.mark.parametrize("forbidden, problem", [
    ({"nowhere": ["socket"]}, "forbidden.nowhere: no part named 'nowhere'"),
    ({"service": "socket"}, "forbidden.service: must be a non-empty list of dotted names or import names, such as "
                            "[datetime.datetime.now, socket]"),
    ({"service": []}, "forbidden.service: must be a non-empty list of dotted names or import names, such as "
                      "[datetime.datetime.now, socket]"),
    ({"service": ["datetime..now"]}, "forbidden.service: 'datetime..now' is not a dotted name such as "
                                     "datetime.datetime.now, nor an import name such as socket"),
    ({"service": ["2fast"]}, "forbidden.service: '2fast' is not a dotted name such as datetime.datetime.now, nor an "
                             "import name such as socket"),
    ({"service": [3]}, "forbidden.service: 3 is not a dotted name such as datetime.datetime.now, nor an import name "
                       "such as socket"),
    ({"service": ["socket", "socket"]}, "forbidden.service: 'socket' is listed twice"),
    (["service"], "forbidden: must be a mapping of part names to lists of dotted names, such as "
                  "{<part>: [datetime.datetime.now, socket]}"),
])
def test_a_bad_forbidden_entry_is_rejected(forbidden, problem):
    assert problems(layered(forbidden=forbidden)) == [f"layered.yaml: {problem}"]


def test_a_tier_may_hold_its_tests_to_the_list_of_the_part_they_mirror():
    tests = {"files": ["test_*.py"], "functions": "test_*"}
    architecture = load(layered(tiers=[{**TIER, "forbidden": True}], tests=tests,
                                forbidden={"service": ["socket"]}))
    assert architecture.tiers[0].forbidden is True
    assert load(layered(tiers=[TIER], tests=tests)).tiers[0].forbidden is False


def test_a_tier_s_forbidden_is_true_or_false():
    tests = {"files": ["test_*.py"], "functions": "test_*"}
    assert problems(layered(tiers=[{**TIER, "forbidden": "yes"}], tests=tests)) == [
        "layered.yaml: tiers[0].forbidden: must be true or false: whether its tests are held to the `forbidden` list "
        "of the part they mirror"]


def test_the_guards_section_lists_the_names_each_part_may_not_use_and_says_what_it_does_not_see():
    tests = {"files": ["test_*.py"], "functions": "test_*"}
    architecture = load(layered(tiers=[{**TIER, "forbidden": True}], tests=tests,
                                forbidden={"service": ["time.time", "socket"], "store": ["time.time", "socket"],
                                           "contract": ["builtins.print"]}))
    lines = fill("{{guards}}", architecture, "layered.md").splitlines()
    assert lines[2] == (
        "- `forbidden`: a part neither imports nor uses by name what is listed for it (`service/` and `store/`: "
        "`time.time`, `socket`; `contract/`: `builtins.print`), and neither do the "
        "unit tests of those parts. It catches what is written in the part's own files, through their imports and "
        "aliases, not a name reached through a variable or `getattr`, nor I/O done on the part's behalf elsewhere.")
