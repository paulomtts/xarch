"""A part's `uses` group, `uses: {never: <list>}`, naming one of the top-level `never` lists of the calls and modules a
part never uses, and a tier's, `uses: {apply_never: true}`, holding its tests to the list of the part they mirror: each
refused at its address when it is written wrong, and the guards section of the docs saying what the lists hold."""
import pytest

from tests.modules.spec.format_files import FILE_TYPES
from tests.modules.spec.languages import BRACE
from tests.modules.spec.profiles import covered, layered, parsed, problems
from xarch.kernel.violations import RULES
from xarch.modules.spec.application.logic.docs_template import fill

METHOD = "is not an outside name such as <package>.<name>, nor a package, nor a method such as .<name>()"
LISTS = {"pure": ["socket"], "ambient": ["os.getcwd"]}
NO_NAME = "must be the name of a list under `never`"
ONE_LIST = "names one list under never: write the name of a list, such as pure; a list may include others"


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


EMPTY = ("must be a non-empty list of outside names, packages or methods, such as [<package>.<name>, <package>, "
         ".<name>()]")
TIME_SOCKET = (("time", "time"), ("socket",))


def standard(name: str, title: str = "Python") -> str:
    """The refusal of a list named like a package of the language's standard library."""
    return (f"never.{name}: a list may not take the name of a package of the {title} standard library, since an entry "
            f"{name} would name the list: rename it")


def named(name: str, key: str) -> str:
    """The refusal of a list named like a package the profile names at key."""
    return f"never.{name}: a list may not take the name of a package this profile names ({key}): rename it"


def naming(never, uses) -> dict:
    """The covered profile with the lists given under `never`, its service part naming the list uses."""
    document = covered(never=never)
    document["parts"]["service"]["uses"] = {"never": uses}
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
    assert parsed(with_list([name])).uses_never == {"service": (tuple(name.split(".")),)}


def test_a_method_written_with_a_leading_dot_and_parentheses_is_kept_as_written():
    assert parsed(with_list([".absolute()", "pathlib.Path.cwd"])).uses_never == {
        "service": (("", "absolute()"), ("pathlib", "Path", "cwd"))}


@pytest.mark.parametrize("name, problem", [
    pytest.param(".absolute", "never.pure: '.absolute' is neither an outside name nor a method: write .absolute() for "
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
    assert parsed(service_uses({"never": "ambient"})).uses_never == {"service": (("os", "getcwd"),)}
    assert parsed(covered(never=LISTS)).uses_never == {}


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
    assert [tier.apply_never for tier in parsed(document).tiers] == [True, False]


def test_apply_never_false_is_the_same_tier_as_no_uses():
    assert parsed(unit_uses({"apply_never": False})).tiers == parsed(covered()).tiers


def test_the_guards_section_shows_a_method_as_written_and_says_what_it_does_not_see():
    document = with_list([".resolve()", "os.getcwd"])
    lines = fill("{{guards}}", parsed(document), "layered.md", file_types=FILE_TYPES).splitlines()
    assert lines[3] == (
        "- `never-use`: a part neither imports nor uses by name what its `uses.never` list names (`service/`: "
        "`.resolve()`, `os.getcwd`). It catches what is written in the part's own files, through their imports and "
        "aliases, and a method written `.name()` called on anything but the object itself and what it holds; not a name "
        "reached through a variable or `getattr`, nor I/O done on the part's behalf elsewhere.")


def test_the_guards_section_lists_the_names_each_part_never_uses_and_says_what_it_does_not_see():
    document = covered(never={"clock": ["time.time", "socket"], "printing": ["builtins.print"]})
    document["parts"]["service"]["uses"] = {"never": "clock"}
    document["parts"]["store"]["uses"] = {"never": "clock"}
    document["parts"]["api"]["uses"] = {"never": "printing"}
    document["tiers"]["unit"]["uses"] = {"apply_never": True}
    lines = fill("{{guards}}", parsed(document), "layered.md", file_types=FILE_TYPES).splitlines()
    assert lines[3] == (
        "- `never-use`: a part neither imports nor uses by name what its `uses.never` list names (`api/`: "
        "`builtins.print`; `service/` and `store/`: `time.time`, `socket`), and neither do the "
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


BRACED = {"brace": BRACE}


def brace_document(ambient=("node:fs#readFileSync", "globalThis#fetch", ".toISOString()"),
                   libraries=("lodash-es", "@scope/pkg")) -> dict:
    """The layered profile as an app in the brace language writes it: its store's outside packages by the language's
    package names, and a list of outside names under `never`, which its service part never uses."""
    document = layered(never={"ambient": list(ambient)})
    document["parts"]["store"]["libraries"] = list(libraries)
    document["parts"]["service"]["uses"] = {"never": "ambient"}
    return document


def test_outside_names_are_read_by_the_package_pattern_and_the_member_of_the_language():
    architecture = parsed(brace_document(), languages=BRACED)
    assert (architecture.libraries["store"], architecture.uses_never) == (
        ("lodash-es", "@scope/pkg"),
        {"service": (("node:fs", "readFileSync"), ("globalThis", "fetch"), ("", "toISOString()"))})


def test_the_same_outside_names_are_refused_under_a_language_whose_patterns_do_not_allow_them():
    assert problems(brace_document()) == [
        f"layered.yaml: never.ambient: 'node:fs#readFileSync' {METHOD}",
        f"layered.yaml: never.ambient: 'globalThis#fetch' {METHOD}",
        "layered.yaml: parts.store.libraries: 'lodash-es' is not a package name the language Python allows",
        "layered.yaml: parts.store.libraries: '@scope/pkg' is not a package name the language Python allows"]


def test_a_bare_builtin_is_told_to_be_written_in_the_namespace_with_the_member_of_the_language():
    assert problems(brace_document(ambient=["fetch"]), languages=BRACED) == [
        "layered.yaml: never.ambient: 'fetch' is a Brace builtin, which a bare name does not ban: write globalThis#fetch"]


@pytest.mark.parametrize("entry", [
    pytest.param("node:fs#", id="a member with nothing after it"),
    pytest.param("#readFileSync", id="nothing before the member"),
    pytest.param("Fs#readFileSync", id="a head that is neither a package nor the namespace"),
])
def test_an_outside_name_the_language_s_patterns_refuse_is_refused_under_that_language(entry):
    assert problems(brace_document(ambient=[entry]), languages=BRACED) == [
        f"layered.yaml: never.ambient: '{entry}' is not an outside name such as <package>#<name>, nor a package, nor a "
        "method such as .<name>()"]


def test_an_outside_name_listed_twice_is_refused_once_under_a_member_that_is_not_a_dot():
    assert problems(brace_document(ambient=["node:fs#readFileSync", "node:fs#readFileSync"]), languages=BRACED) == [
        "layered.yaml: never.ambient: 'node:fs#readFileSync' is listed twice"]


def test_a_package_is_never_the_namespace_of_the_language():
    assert problems(brace_document(libraries=["globalThis"]), languages=BRACED) == [
        "layered.yaml: parts.store.libraries: 'globalThis' is not a package name the language Brace allows"]


def test_the_guards_section_writes_an_outside_name_with_the_member_of_the_language():
    text = fill("{{guards}}", parsed(brace_document(), languages=BRACED), "layered.md", file_types=FILE_TYPES)
    assert "(`service/`: `node:fs#readFileSync`, `globalThis#fetch`, `.toISOString()`)" in text


@pytest.mark.parametrize("never, uses, found", [
    pytest.param({"pure": ["time.time", "socket"], "published": ["pure", "typing.Any"]}, "published",
                 (*TIME_SOCKET, ("typing", "Any")), id="an include, then a name"),
    pytest.param({"pure": ["time.time", "socket"], "published": ["typing.Any", "pure", "os.getenv"]}, "published",
                 (("typing", "Any"), *TIME_SOCKET, ("os", "getenv")), id="an include between two names"),
    pytest.param({"a": ["b", "x.one"], "b": ["c", "x.two"], "c": ["x.three"]}, "a",
                 (("x", "three"), ("x", "two"), ("x", "one")), id="a chain of three lists"),
    pytest.param({"published": ["pure", "typing.Any"], "pure": ["time.time", "socket"]}, "published",
                 (*TIME_SOCKET, ("typing", "Any")), id="the included list written below"),
    pytest.param(LISTS | {"both": ["pure", "ambient"]}, "both", (("socket",), ("os", "getcwd")),
                 id="a list of only includes"),
    pytest.param({"pure": ["published"]}, "pure", (("published",),),
                 id="a bare word that is no list name is a package"),
    pytest.param({"pure": ["socket"], "published": ["Pure"]}, "published", (("Pure",),),
                 id="an entry differing from a list name by case is a package"),
])
def test_an_entry_naming_a_list_puts_that_list_s_names_in_its_place(never, uses, found):
    assert parsed(naming(never, uses)).uses_never == {"service": found}


def test_a_list_including_another_reads_as_the_same_names_written_out():
    included = parsed(naming({"pure": ["time.time", "socket"], "published": ["pure", "typing.Any"]}, "published"))
    written = parsed(naming({"pure": ["time.time", "socket"], "published": ["time.time", "socket", "typing.Any"]},
                            "published"))
    assert included.uses_never == written.uses_never


@pytest.mark.parametrize("never, found", [
    pytest.param({"a": ["a", "x.one"]}, ["never.a: includes itself"], id="a list writing itself"),
    pytest.param({"a": ["b"], "b": ["a"]}, ["never.a: includes itself, through never.b: drop one of the two"],
                 id="two lists including each other, said at the one written first"),
    pytest.param({"b": ["a"], "a": ["b"]}, ["never.b: includes itself, through never.a: drop one of the two"],
                 id="said at whichever is written first"),
    pytest.param({"a": ["b"], "b": ["c"], "c": ["a"]},
                 ["never.a: includes itself, through never.b, never.c: drop one of the includes"],
                 id="three lists in a loop"),
    pytest.param({"top": ["a"], "a": ["b"], "b": ["a"]},
                 ["never.a: includes itself, through never.b: drop one of the two"],
                 id="a list including a list of a loop gets no problem for it"),
    pytest.param({"pure": ["os.environ"], "published": ["pure", "os.environ"]},
                 ["never.published: 'os.environ' is listed in never.pure, which never.published includes: drop it "
                  "here"], id="a name written after an include holding it"),
    pytest.param({"pure": ["os.environ"], "published": ["os.environ", "pure"]},
                 ["never.published: 'os.environ' is listed in never.pure, which never.published includes: drop it "
                  "here"], id="a name written before an include holding it"),
    pytest.param({"pure": ["os.environ"], "mid": ["pure"], "top": ["mid", "os.environ"]},
                 ["never.top: 'os.environ' is listed in never.pure, which never.top includes: drop it here"],
                 id="a name held by a list included through another, naming the list holding it"),
    pytest.param({"pure": ["os.environ"], "ambient": ["os.environ"], "both": ["pure", "ambient"]},
                 ["never.both: 'os.environ' is listed in never.pure and in never.ambient, which never.both includes: "
                  "drop it from one"], id="a name reached through two includes"),
    pytest.param({"pure": ["socket"], "both": ["pure", "pure"]}, ["never.both: includes never.pure twice"],
                 id="a list included twice"),
    pytest.param({"pure": ["socket"], "mid": ["pure"], "both": ["pure", "mid"]},
                 ["never.both: includes never.pure twice"],
                 id="a list included directly and through another, and its names not said again"),
    pytest.param({"pure": ["os.environ"], "mid": ["pure", "os.environ"], "top": ["mid"]},
                 ["never.mid: 'os.environ' is listed in never.pure, which never.mid includes: drop it here"],
                 id="a repeat said once, at the lowest list where it meets"),
    pytest.param({"pure": ["datetime..now"], "published": ["pure"]}, [f"never.pure: 'datetime..now' {METHOD}"],
                 id="a bad entry of an included list said once, under that list"),
    pytest.param({"pure": [], "published": ["pure", "x.one"]}, [f"never.pure: {EMPTY}"],
                 id="an included list that is empty"),
    pytest.param({"pure": "socket", "published": ["pure", "x.one"]}, [f"never.pure: {EMPTY}"],
                 id="an included list that is no list"),
    pytest.param({"a b": ["x.one"], "c": ["a b"]},
                 ["never: 'a b' is not a list name: use letters, digits, '_' and '-'", f"never.c: 'a b' {METHOD}"],
                 id="a key refused as a list name is no list"),
    pytest.param({1: ["x.one"], "c": ["pure", 3]},
                 ["never: 1 is not a list name: use letters, digits, '_' and '-'", f"never.c: 3 {METHOD}"],
                 id="a key that is no text, and an entry that is no text beside a name"),
    pytest.param({"pure": ["socket"], "published": [" pure"]}, [f"never.published: ' pure' {METHOD}"],
                 id="an entry with a space around a list name is no include"),
    pytest.param({"pure": ["os.environ"], "published": ["pure", "os.environ", "2fast"]},
                 [f"never.published: '2fast' {METHOD}",
                  "never.published: 'os.environ' is listed in never.pure, which never.published includes: drop it "
                  "here"], id="a list's entry problems before its include problems"),
])
def test_an_include_written_wrong_is_refused_at_the_list_it_is_about(never, found):
    assert problems(covered(never=never)) == [f"layered.yaml: {problem}" for problem in found]


def test_a_part_naming_a_list_of_a_loop_adds_no_problem_of_its_own():
    assert problems(naming({"a": ["b"], "b": ["a"]}, "b")) == [
        "layered.yaml: never.a: includes itself, through never.b: drop one of the two"]


def test_a_chain_and_a_loop_of_many_lists_are_read_whole():
    count = 1500
    chain = {f"l{i}": [f"l{i + 1}"] for i in range(count)} | {f"l{count}": ["x.one"]}
    assert parsed(naming(chain, "l0")).uses_never == {"service": (("x", "one"),)}
    loop = {f"l{i}": [f"l{(i + 1) % count}"] for i in range(count)}
    found = problems(naming(loop, "l0"))
    assert len(found) == 1
    assert found[0].startswith("layered.yaml: never.l0: includes itself, through never.l1, never.l2, never.l3, ")
    assert found[0].endswith(f", never.l{count - 1}: drop one of the includes")


def test_a_list_named_like_a_standard_package_is_refused_and_an_entry_of_that_name_still_includes_it():
    assert problems(covered(never={"pure": ["socket"], "socket": ["time.time"]})) == [
        f"layered.yaml: {standard('socket')}"]


def test_the_standard_library_a_list_may_not_be_named_from_is_the_language_s():
    document = layered(never={"fs": ["lodash"], "pure": ["fs"]})
    document["parts"]["service"]["uses"] = {"never": "pure"}
    assert problems(document, languages={"brace": BRACE}) == [
        f"layered.yaml: {standard('fs', 'Brace')}"]
    assert parsed(document).uses_never == {"service": (("lodash",),)}


def test_a_list_named_like_a_package_a_part_lists_is_refused_naming_the_first_part_that_lists_it():
    assert problems(covered(never={"sqlmodel": ["x.one"]})) == [
        f"layered.yaml: {named('sqlmodel', 'parts.store.libraries')}"]
    document = covered(never={"sqlmodel": ["x.one"]})
    document["parts"]["service"]["libraries"] = ["sqlmodel"]
    assert problems(document) == [f"layered.yaml: {named('sqlmodel', 'parts.service.libraries')}"]


def test_a_list_named_like_a_reserved_module_is_refused_once_as_a_standard_package():
    document = covered(never={"ast": ["x.one"]}, reserved={"ast": "only the reader parses the language"})
    assert problems(document) == [f"layered.yaml: {standard('ast')}"]


def test_a_part_whose_libraries_are_everything_names_no_package():
    document = covered(never={"sqlmodel": ["x.one"]})
    document["parts"]["store"]["libraries"] = "everything"
    assert parsed(document).uses_never == {}


def test_a_part_naming_a_list_refused_for_its_name_adds_no_problem_of_its_own():
    assert problems(naming({"socket": ["time.time"]}, "socket")) == [f"layered.yaml: {standard('socket')}"]


def test_a_list_s_name_problem_comes_first_then_its_entries_then_its_includes():
    document = covered(never={"pure": ["os.environ"], "socket": ["pure", "os.environ", "2fast"]})
    assert problems(document) == [
        f"layered.yaml: {standard('socket')}",
        f"layered.yaml: never.socket: '2fast' {METHOD}",
        "layered.yaml: never.socket: 'os.environ' is listed in never.pure, which never.socket includes: drop it here"]


def test_never_reserved_and_libraries_are_said_once_each_in_their_own_place():
    document = covered(never={"pure": ["datetime..now"]}, reserved={"json": ""})
    document["parts"]["store"]["libraries"] = ["2fast"]
    assert problems(document) == [
        f"layered.yaml: never.pure: 'datetime..now' {METHOD}",
        "layered.yaml: reserved.json: must say in one line why it is reserved",
        "layered.yaml: parts.store.libraries: '2fast' is not a package name the language Python allows"]
