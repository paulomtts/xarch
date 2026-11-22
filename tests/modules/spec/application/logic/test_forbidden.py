"""A part's `uses` group, `uses: {never: <list>}`, naming one of the top-level `never` lists of the calls and modules a
part never uses, and a tier's, `uses: {apply_never: true}`, holding its tests to the list of the part they mirror: each
refused at its address when it is written wrong, and the guards section of the docs saying what the lists hold."""
import pytest

from tests.modules.spec.format_files import FILE_TYPES
from tests.modules.spec.profiles import covered, layered, parsed, problems
from xarch.kernel.violations import RULES
from xarch.modules.spec.application.logic.docs_template import fill

DOTTED = "is not a dotted name such as datetime.datetime.now, nor an import name such as socket"
METHOD = f"{DOTTED}, nor a method such as .absolute()"
LISTS = {"pure": ["socket"], "ambient": ["os.getcwd"]}
NO_NAME = "must be the name of a list under `never`"
ONE_LIST = "names one list under never: write the name of a list, such as pure"


def with_list(names, **changes) -> dict:
    """The covered profile with a list `pure` of the names, which the service part names under `uses`."""
    document = covered(never={"pure": names}, **changes)
    document["parts"]["service"]["uses"] = {"never": "pure"}
    return document


def service_uses(uses) -> dict:
    """The covered profile with the lists pure and ambient under `never`, its service part writing `uses` as given."""
    document = covered(never=LISTS)
    document["parts"]["service"]["uses"] = uses
    return document


def unit_uses(uses) -> dict:
    """The covered profile, its unit tier writing `uses` as given."""
    document = covered()
    document["tiers"]["unit"]["uses"] = uses
    return document


PART_USE = ("built_by, folders, holds, immutable, libraries, litmus, may_import, must_import, names, no_callbacks, "
            "package_only, path, role, shared, tests, types_only, untested, uses")
TIER_USE = "docs, folder, litmus, may_also_import, may_import, must_import, plain_tables, proves, types_only, uses"
FILE_USE = ("based_on, checks, docs, evals, excluded, fakes, files, guards, hints, language, layers, name, never, parts, "
            "reserved, review, testing, tiers")
LIST_MOVED = "moved in 0.3.0: write uses: {never: <list>}"
SWITCH_MOVED = "moved in 0.3.0: write uses: {apply_never: true}"
LIST_OUTSIDE = "a key of uses: write uses: {never: <list>}"
SWITCH_OUTSIDE = "a key of uses: write uses: {apply_never: true}"
NO_TIER = "no tier tests it: give it `tests: <tier>`, or `untested: <reason>`"


def service_writing(**keys) -> dict:
    """The covered profile with the lists pure and ambient under `never`, its service part writing the keys given."""
    document = covered(never=LISTS)
    document["parts"]["service"] |= keys
    return document


@pytest.mark.parametrize("name, problem", [
    pytest.param("datetime..now", f"never.pure: 'datetime..now' {METHOD}", id="a dotted name with an empty step"),
    pytest.param("2fast", f"never.pure: '2fast' {METHOD}", id="a name that starts with a digit"),
    pytest.param(3, f"never.pure: 3 {METHOD}", id="a name that is no text"),
])
def test_a_bad_forbidden_name_is_refused_saying_what_to_write(name, problem):
    assert problems(with_list([name])) == [f"layered.yaml: {problem}"]


@pytest.mark.parametrize("name, problem", [
    pytest.param("open", "never.pure: 'open' is a Python builtin, which a bare name does not ban: write "
                         "builtins.open", id="a bare builtin is rejected with the name to write instead"),
    pytest.param("print", "never.pure: 'print' is a Python builtin, which a bare name does not ban: write "
                          "builtins.print", id="another bare builtin is rejected"),
    pytest.param("__import__", "never.pure: '__import__' is a Python builtin, which a bare name does not ban: "
                               "write builtins.__import__", id="a dunder builtin is rejected"),
])
def test_a_builtin_named_bare_bans_nothing_so_it_is_rejected(name, problem):
    assert problems(with_list([name])) == [f"layered.yaml: {problem}"]


@pytest.mark.parametrize("name", [
    pytest.param("builtins.open", id="a builtin written as builtins.<name> is a dotted name"),
    pytest.param("socket", id="a module that is no builtin stays an import name"),
    pytest.param("time", id="a module whose name only resembles a builtin's stays an import name"),
    pytest.param("open.read", id="a dotted name starting with a builtin's is not a bare name"),
    pytest.param("Open", id="a name that differs from a builtin by case is no builtin"),
])
def test_a_name_that_is_no_bare_builtin_is_kept(name):
    assert parsed(with_list([name])).forbidden == {"service": (tuple(name.split(".")),)}


def test_a_method_written_with_a_leading_dot_and_parentheses_is_kept_as_written():
    assert parsed(with_list([".absolute()", "pathlib.Path.cwd"])).forbidden == {
        "service": (("", "absolute()"), ("pathlib", "Path", "cwd"))}


@pytest.mark.parametrize("name, problem", [
    pytest.param(".absolute", "never.pure: '.absolute' is neither a dotted name nor a method: write .absolute() for "
                              "a method called on anything", id="a method without its parentheses"),
    pytest.param("path.absolute()", f"never.pure: 'path.absolute()' {METHOD}", id="a dotted name with parentheses"),
    pytest.param(".a.b()", f"never.pure: '.a.b()' {METHOD}", id="a method of more than one step"),
    pytest.param(".__init__()", "never.pure: '.__init__()' is a special method, which no code calls by name",
                 id="a special method of the language"),
])
def test_a_bad_method_is_refused_saying_what_to_write(name, problem):
    assert problems(with_list([name])) == [f"layered.yaml: {problem}"]


@pytest.mark.parametrize("uses, problem", [
    pytest.param("pure", "parts.service.uses: must be a mapping {never}, such as {never: pure}",
                 id="a uses that is no mapping"),
    pytest.param([{"never": "pure"}], "parts.service.uses: must be a mapping {never}, such as {never: pure}",
                 id="a uses written as a list"),
    pytest.param({}, "parts.service.uses: says nothing: write never, or drop it", id="a uses that says nothing"),
    pytest.param({"only": ["x"]}, "parts.service.uses: unknown key 'only': use never", id="a key uses does not have"),
    pytest.param({"forbidden": "pure"}, "parts.service.uses: unknown key 'forbidden': use never",
                 id="the old name, under uses"),
    pytest.param({"apply_never": True}, "parts.service.uses: unknown key 'apply_never': use never",
                 id="the switch of a tier, under a part's uses"),
    pytest.param({"never": ["pure", "ambient"]}, f"parts.service.uses.never: {ONE_LIST}", id="a list of list names"),
    pytest.param({"never": ["socket"]}, f"parts.service.uses.never: {ONE_LIST}", id="a list of names"),
    pytest.param({"never": 3}, f"parts.service.uses.never: {NO_NAME}", id="a number"),
    pytest.param({"never": True}, f"parts.service.uses.never: {NO_NAME}", id="true"),
    pytest.param({"never": False}, f"parts.service.uses.never: {NO_NAME}", id="false"),
    pytest.param({"never": None}, f"parts.service.uses.never: {NO_NAME}", id="null"),
    pytest.param({"never": {"pure": True}}, f"parts.service.uses.never: {NO_NAME}", id="a mapping"),
    pytest.param({"never": "nope"}, "parts.service.uses.never: no list named 'nope': use ambient, pure, or write it "
                                    "under `never`", id="a list that is not there"),
])
def test_a_part_s_uses_written_wrong_is_refused_at_its_address(uses, problem):
    assert problems(service_uses(uses)) == [f"layered.yaml: {problem}"]


@pytest.mark.parametrize("changes", [
    pytest.param({}, id="a file with no never"),
    pytest.param({"never": {}}, id="a never that holds no list"),
])
def test_a_part_naming_a_list_the_file_does_not_hold_is_told_to_write_it_under_never(changes):
    document = layered(**changes)
    document["parts"]["service"]["uses"] = {"never": "pure"}
    assert problems(document) == ["layered.yaml: parts.service.uses.never: no list named 'pure': write it under "
                                  "`never`"]


def test_a_never_that_is_no_mapping_is_the_one_problem_and_the_parts_naming_it_add_none():
    document = service_uses({"never": "nope"})
    document["never"] = ["pure"]
    assert problems(document) == ["layered.yaml: never: must be a mapping of list names to lists of dotted names, such "
                                  "as {pure: [datetime.datetime.now, socket]}"]


def test_a_part_naming_a_list_under_uses_never_uses_its_names_and_a_part_without_uses_none():
    assert parsed(service_uses({"never": "ambient"})).forbidden == {"service": (("os", "getcwd"),)}
    assert parsed(covered(never=LISTS)).forbidden == {}


@pytest.mark.parametrize("uses, problem", [
    pytest.param("yes", "tiers.unit.uses: must be a mapping {apply_never}, such as {apply_never: true}",
                 id="a uses that is no mapping"),
    pytest.param({}, "tiers.unit.uses: says nothing: write apply_never, or drop it", id="a uses that says nothing"),
    pytest.param({"never": True}, "tiers.unit.uses: unknown key 'never': use apply_never",
                 id="never under a tier's uses"),
    pytest.param({"apply_never": "yes-please"}, "tiers.unit.uses.apply_never: must be true or false: whether its "
                                                "tests are held to the `uses.never` list of the part they mirror",
                 id="an apply_never that is no boolean"),
])
def test_a_tier_s_uses_written_wrong_is_refused_at_its_address(uses, problem):
    assert problems(unit_uses(uses)) == [f"layered.yaml: {problem}"]


def test_a_tier_may_hold_its_tests_to_the_list_of_the_part_they_mirror():
    document = with_list(["socket"])
    document["tiers"]["unit"]["uses"] = {"apply_never": True}
    assert [tier.forbidden for tier in parsed(document).tiers] == [True, False]


def test_apply_never_false_is_the_same_tier_as_no_uses():
    assert parsed(unit_uses({"apply_never": False})).tiers == parsed(covered()).tiers


def test_the_guards_section_shows_a_method_as_written_and_says_what_it_does_not_see():
    document = with_list([".resolve()", "os.getcwd"])
    lines = fill("{{guards}}", parsed(document), "layered.md", file_types=FILE_TYPES).splitlines()
    assert lines[3] == (
        "- `forbidden`: a part neither imports nor uses by name what is listed for it (`service/`: `.resolve()`, "
        "`os.getcwd`). It catches what is written in the part's own files, through their imports and aliases, and a "
        "method written `.name()` called on anything but the object itself and what it holds; not a name reached "
        "through a variable or `getattr`, nor I/O done on the part's behalf elsewhere.")


def test_the_guards_section_lists_the_names_each_part_may_not_use_and_says_what_it_does_not_see():
    document = covered(never={"clock": ["time.time", "socket"], "printing": ["builtins.print"]})
    document["parts"]["service"]["uses"] = {"never": "clock"}
    document["parts"]["store"]["uses"] = {"never": "clock"}
    document["parts"]["api"]["uses"] = {"never": "printing"}
    document["tiers"]["unit"]["uses"] = {"apply_never": True}
    lines = fill("{{guards}}", parsed(document), "layered.md", file_types=FILE_TYPES).splitlines()
    assert lines[3] == (
        "- `forbidden`: a part neither imports nor uses by name what is listed for it (`api/`: `builtins.print`; "
        "`service/` and `store/`: `time.time`, `socket`), and neither do the "
        "unit tests of those parts. It catches what is written in the part's own files, through their imports and "
        "aliases, not a name reached through a variable or `getattr`, nor I/O done on the part's behalf elsewhere.")


def test_a_part_writing_forbidden_is_told_the_list_moved_under_uses():
    assert problems(service_writing(forbidden="pure")) == [
        f"layered.yaml: parts.service: unknown key 'forbidden': {LIST_MOVED}; use {PART_USE}"]


def test_the_list_a_part_wrote_under_forbidden_is_in_no_problem():
    found = problems(service_writing(forbidden="secret-list"))
    assert found == [f"layered.yaml: parts.service: unknown key 'forbidden': {LIST_MOVED}; use {PART_USE}"]
    assert not any("secret-list" in problem for problem in found)


def test_a_part_writing_never_outside_uses_is_told_it_is_a_key_of_uses():
    assert problems(service_writing(never="pure")) == [
        f"layered.yaml: parts.service: unknown key 'never': {LIST_OUTSIDE}; use {PART_USE}"]


def test_apply_never_under_a_part_s_uses_is_only_unknown_there():
    assert problems(service_writing(uses={"never": "pure", "apply_never": True})) == [
        "layered.yaml: parts.service.uses: unknown key 'apply_never': use never"]


def test_a_part_of_an_old_profile_writing_forbidden_and_tier_gets_both_in_sorted_order_then_no_tier_tests_it():
    document = service_writing(forbidden="pure", tier="unit")
    document["parts"]["service"].pop("tests")
    assert problems(document) == [
        f"layered.yaml: parts.service: unknown key 'forbidden': {LIST_MOVED}; use {PART_USE}",
        f"layered.yaml: parts.service: unknown key 'tier': renamed in 0.3.0: write tests; use {PART_USE}",
        f"layered.yaml: parts.service: {NO_TIER}"]


def test_a_part_writing_forbidden_beside_uses_is_refused_for_forbidden_and_its_uses_read_as_written():
    assert problems(service_writing(forbidden="pure", uses={"never": "nope"})) == [
        f"layered.yaml: parts.service: unknown key 'forbidden': {LIST_MOVED}; use {PART_USE}",
        "layered.yaml: parts.service.uses.never: no list named 'nope': use ambient, pure, or write it under `never`"]


def test_a_tier_writing_apply_forbidden_is_told_the_switch_moved_under_uses():
    document = covered()
    document["tiers"]["unit"]["apply_forbidden"] = True
    assert problems(document) == [
        f"layered.yaml: tiers.unit: unknown key 'apply_forbidden': {SWITCH_MOVED}; use {TIER_USE}"]


def test_a_tier_writing_apply_never_outside_uses_is_told_it_is_a_key_of_uses():
    document = covered()
    document["tiers"]["unit"]["apply_never"] = True
    assert problems(document) == [
        f"layered.yaml: tiers.unit: unknown key 'apply_never': {SWITCH_OUTSIDE}; use {TIER_USE}"]


def test_a_file_writing_the_block_forbidden_is_told_it_is_renamed_never_and_its_parts_once_each():
    document = covered(forbidden=LISTS)
    document["parts"]["service"]["forbidden"] = "pure"
    document["parts"]["store"]["forbidden"] = "pure"
    assert problems(document) == [
        f"layered.yaml: unknown key 'forbidden': renamed in 0.3.0: write never; use {FILE_USE}",
        f"layered.yaml: parts.service: unknown key 'forbidden': {LIST_MOVED}; use {PART_USE}",
        f"layered.yaml: parts.store: unknown key 'forbidden': {LIST_MOVED}; use {PART_USE}"]


@pytest.mark.parametrize("never, after", [
    pytest.param(LISTS, [], id="a never that loads adds no problem"),
    pytest.param(["pure"], ["layered.yaml: never: must be a mapping of list names to lists of dotted names, such as "
                            "{pure: [datetime.datetime.now, socket]}"], id="a never written wrong adds its own"),
])
def test_a_file_writing_forbidden_beside_never_is_refused_for_forbidden_and_never_read_as_written(never, after):
    document = service_uses({"never": "pure"}) | {"forbidden": LISTS, "never": never}
    assert problems(document) == [
        f"layered.yaml: unknown key 'forbidden': renamed in 0.3.0: write never; use {FILE_USE}", *after]


def test_a_hint_for_the_rule_id_forbidden_is_told_it_is_renamed_never_use():
    assert problems(layered(hints={"forbidden": "see the docs"})) == [
        "layered.yaml: hints.forbidden: unknown rule id 'forbidden': renamed in 0.3.0: write never-use; use "
        f"{', '.join(sorted(RULES))}"]
