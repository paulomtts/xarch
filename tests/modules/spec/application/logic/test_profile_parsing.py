"""A profile file: its keys, its parts and the layout they imply, what a part may import, its outside
packages, the names it may not use, and the layers."""
from copy import deepcopy

import pytest

from tests.modules.spec.format_files import CATALOGUE
from tests.modules.spec.profiles import TESTING, covered, layered, parsed, part_of, problems, two_folders
from xarch.modules.spec.application.logic.key_lookup import names_of
from xarch.modules.spec.application.logic.layout_walk import docs_name, is_file
from xarch.modules.spec.application.logic.profile_parsing import parse_profile
from xarch.modules.spec.domain.errors import InvalidArchitecture
from xarch.modules.spec.domain.key_table import KEYS
from xarch.modules.spec.domain.profile_keys import SCOPES
from xarch.modules.spec.domain.values import Part
from xarch.profile_values.placement import Repeat, Target


def test_a_document_that_is_no_mapping_is_refused():
    with pytest.raises(InvalidArchitecture) as caught:
        parse_profile([1], "layered.yaml")
    assert caught.value.problems == ("layered.yaml: must be a mapping of keys",)


def test_the_smallest_profile_is_a_name_and_parts_and_checks_the_layout_and_the_imports():
    architecture = parsed({"name": "tiny", "parts": {
        "core/": {"role": "the rules"},
        "cli/": {"role": "commands and output", "imports": {"may": ["parts.core"], "libraries": ["typer"]}}}})
    assert architecture.name == "tiny"
    assert architecture.layout == {"core": {}, "cli": {}}
    assert architecture.rules == {"core": (), "cli": (Target("core"),)}
    assert architecture.imports_libraries == {"core": (), "cli": ("typer",)}
    assert architecture.tiers == () and architecture.guards == () and architecture.framework is None
    assert architecture.repeats == ()


def test_a_profile_says_what_it_does_not_have_by_leaving_it_out():
    architecture = parsed(layered())
    assert (architecture.docs, architecture.examples, architecture.notes, architecture.layers, architecture.placement,
            architecture.naming, architecture.fakes, architecture.files, architecture.uses_never,
            architecture.excluded, architecture.hints, architecture.based_on) == (
        (), {}, {}, {}, ("api", "service", "store", "shared"), (), None, (), {}, (), {}, "")


def test_unknown_keys_are_refused_with_the_keys_that_exist_in_the_file():
    assert problems(layered(colour=1, extra=2)) == [
        "layered.yaml: unknown keys 'colour', 'extra': use based_on, checks, docs, evals, excluded, fakes, files, guards, "
        "hints, language, layers, name, never, parts, reserved, review, testing, tiers"]


def test_every_unknown_key_message_reads_the_table_of_keys():
    assert {key.name for key in KEYS if key.scope == "profile"} == names_of("profile")
    assert problems(layered(colour=1))[0].split("use ")[1] == ", ".join(sorted(names_of("profile")))
    assert problems(layered(parts={"x/": {"role": "r", "colour": 1}}))[0].split("use ")[1] == ", ".join(
        sorted(names_of("part")))


def test_every_key_of_the_table_has_a_scope_with_an_address_and_a_meaning():
    assert all(key.scope in SCOPES and CATALOGUE.texts[key.address].meaning and key.address for key in KEYS)
    assert len({key.address for key in KEYS}) == len(KEYS)


def test_the_required_keys_are_reported_together():
    assert problems({}) == ["layered.yaml: missing `name`", "layered.yaml: missing `parts`"]


@pytest.mark.parametrize("name", ["", "  ", 3, None])
def test_a_name_must_be_text(name):
    assert problems(layered(name=name)) == ["layered.yaml: `name` must be a non-empty string"]


def test_python_is_the_default_and_the_only_language():
    assert parsed(layered(language="python")).name == "layered"
    assert problems(layered(language="ruby")) == ["layered.yaml: language: 'ruby' is not a language xarch reads: use python"]
    assert problems(layered(language=3)) == ["layered.yaml: language: 3 is not a language xarch reads: use python"]


def test_based_on_names_a_bundled_profile_and_nothing_else():
    assert parsed(layered(based_on="web")).based_on == "web"
    assert problems(layered(based_on="mine")) == ["layered.yaml: based_on: no bundled profile 'mine': use cli, web"]
    assert problems(layered(based_on=3)) == [
        "layered.yaml: based_on: must be the name of a bundled profile or the path of a profile file: use cli, web"]
    assert problems(layered(based_on="")) == [
        "layered.yaml: based_on: must be the name of a bundled profile or the path of a profile file: use cli, web"]
    assert problems(layered(based_on=3), bundled=()) == [
        "layered.yaml: based_on: must be the name of a bundled profile or the path of a profile file"]


@pytest.mark.parametrize("path", ["../team.yaml", "team.yaml", "base/team.json"])
def test_based_on_a_path_is_kept_as_written_without_reading_any_file(path):
    assert parsed(layered(based_on=path)).based_on == path


def test_the_layout_is_derived_from_the_paths_of_the_parts_and_a_repeating_step_is_one_star():
    architecture = parsed(layered())
    assert architecture.layout == {"src": {"*": {"api": {}, "service": {}, "store": {}}}, "shared": {}}
    assert architecture.repeats == (Repeat("module", ("src",)),)
    assert architecture.parts["api"] == Part("api", ("src", "*", "api"), "HTTP handlers")


def test_a_nested_tree_and_the_same_tree_joined_parse_to_one_architecture():
    nested = layered(parts={"src/": {"<module>/": {"api/": {"role": "HTTP handlers", "imports": {"may": ["module.service"]}},
                                                   "service/": {"role": "business logic",
                                                                "imports": {"may": ["module.store", "parts.shared"]}},
                                                   "store/": {"role": "database access",
                                                              "imports": {"may": ["parts.shared"],
                                                                          "libraries": ["sqlmodel"]}}}},
                            "shared/": {"role": "shared code"}})
    one, other = parsed(layered()), parsed(nested)
    assert (one.parts, one.layout, one.notes, one.repeats, one.placement) == (
        other.parts, other.layout, other.notes, other.repeats, other.placement)


def test_the_reading_order_of_the_tree_is_the_placement_order_a_part_before_the_parts_inside_it():
    architecture = parsed(layered(parts={
        "src/<module>/": {"contract/": {"role": "c"}, "api/": {"role": "a"}},
        "platform/": {"role": "p"},
        "kernel/": {"role": "k", "logic/": {"name": "kernel-logic", "role": "kl"}}}))
    assert architecture.placement == ("contract", "api", "platform", "kernel", "kernel-logic")
    assert architecture.placement == tuple(architecture.parts)
    assert architecture.parts["kernel-logic"].path == ("kernel", "logic")


def test_a_file_part_is_a_file_of_the_layout_and_a_part_may_sit_inside_another():
    document = layered()
    document["parts"]["src/<module>/"]["entry.py"] = {"role": "the entry"}
    part_of(document, "store")["sql/"] = {"role": "queries"}
    document["parts"]["__main__.py"] = {"name": "main", "role": "starts the app"}
    architecture = parsed(document)
    assert architecture.layout["src"]["*"]["entry.py"] is None and architecture.layout["__main__.py"] is None
    assert architecture.layout["src"]["*"]["store"] == {"sql": {}}
    assert architecture.parts["sql"].path == ("src", "*", "store", "sql")
    assert architecture.parts["main"].path == ("__main__.py",)
    assert is_file(architecture.layout, architecture.parts["entry"].path)
    assert not is_file(architecture.layout, ("src", "*", "store"))


def test_a_folder_with_a_note_or_with_nothing_is_a_folder_of_the_layout_and_its_note_a_note():
    document = layered()
    part_of(document, "shared")["text/"] = "text helpers"
    part_of(document, "shared")["io/"] = None
    part_of(document, "shared")["disk/"] = {}
    architecture = parsed(document)
    assert architecture.layout["shared"] == {"text": {}, "io": {}, "disk": {}}
    assert architecture.notes == {("shared", "text"): "text helpers"}


def test_a_part_s_own_folders_follow_the_parts_in_the_layout_as_today():
    architecture = parsed(layered(parts={"cli/": {"role": "c", "commands/": {}, "reports/": {"role": "r"}}}))
    assert list(architecture.layout["cli"]) == ["reports", "commands"]


@pytest.mark.parametrize("parts, expected", [
    pytest.param({"x/": {"role": 3, "litmus": 4}},
                 ["layered.yaml: parts.x.role: must be a string", "layered.yaml: parts.x.litmus: must be a string"],
                 id="texts that are no strings"),
    pytest.param({"x/": {"role": "r", "package_only": "yes"}},
                 ["layered.yaml: parts.x.package_only: must be true or false"], id="package_only that is no boolean"),
    pytest.param({"x/": {"role": "r", "optional": "yes"}},
                 ["layered.yaml: parts.x.optional: must be true or false"], id="optional that is no boolean"),
    pytest.param({"x/": {"role": "r", "untested": "two\nlines"}},
                 ["layered.yaml: parts.x.untested: must be one line of text: why no tier tests the part"],
                 id="an untested reason of two lines"),
])
def test_a_bad_part_is_refused_with_every_problem(parts, expected):
    assert problems(layered(parts=parts)) == expected


@pytest.mark.parametrize("written, optional", [
    pytest.param({"optional": True}, True, id="a part marked optional"),
    pytest.param({"optional": False}, False, id="a part marked not optional"),
    pytest.param({}, False, id="a part that does not say"),
])
def test_a_part_is_optional_only_when_it_says_so(written, optional):
    assert parsed(layered(parts={"x/": {"role": "r", **written}})).parts["x"].optional is optional


def test_two_repeating_steps_on_the_way_to_a_part_are_refused():
    assert problems(layered(parts={"<a>/": {"<b>/": {"c/": {"role": "r"}}}})) == [
        "layered.yaml: parts.c: '<a>/<b>/c/' has two repeating steps, <a> and <b>: a repeating folder cannot sit "
        "inside another, so give each its own folder"]


def test_two_words_may_not_share_a_parent():
    document = layered(parts={"src/": {"<module>/": {"api/": {"role": "a"}}, "<doc>/": {"x/": {"role": "r"}}}})
    assert problems(document) == [
        "layered.yaml: parts.x: 'src/<doc>/x/' calls the repeating folder <doc>, but part 'api' called it <module> in "
        "the same folder 'src': two words may not share a parent, use one word"]


def test_one_word_repeats_in_one_folder_only():
    document = layered()
    document["parts"]["other/<module>/"] = {"y/": {"role": "r"}}
    assert problems(document) == [
        "layered.yaml: parts.y: 'other/<module>/y/' repeats <module> below 'other', but part 'api' repeats it below "
        "'src': one word repeats in one folder, so give this one a word of its own"]


def test_a_profile_may_hold_several_repeating_folders_each_with_its_word_and_parent():
    architecture = parsed(two_folders())
    assert architecture.repeats == (Repeat("module", ("src",)), Repeat("plugin", ("ext",)))
    assert architecture.layout == {"src": {"*": {"api": {}, "service": {}, "store": {}}},
                                   "shared": {}, "ext": {"*": {"hooks": {}, "manifest.py": None}}}
    assert architecture.parts["hooks"].path == ("ext", "*", "hooks")
    assert architecture.parts["manifest"].path == ("ext", "*", "manifest.py")
    assert architecture.top_level_tree() == {"src": {}, "shared": {}, "ext": {}}
    assert architecture.instance_tree(architecture.repeats[1]) == {"hooks": {}, "manifest.py": None}


def test_a_part_is_shown_below_its_own_repeating_folder():
    architecture = parsed(two_folders())
    assert [docs_name(architecture, architecture.parts[name]) for name in ("api", "hooks", "manifest", "shared")] == [
        "api/", "hooks/", "manifest.py", "shared/"]


def test_a_part_names_a_part_of_its_own_repeating_folder_by_its_word_and_one_of_another_with_parts():
    document = two_folders()
    part_of(document, "hooks").setdefault("imports", {})["may"] = ["plugin.manifest", "parts.service", "parts.shared"]
    part_of(document, "service").setdefault("imports", {})["may"] = ["module.store", "parts.shared", "parts.hooks"]
    rules = parsed(document).rules
    assert rules["hooks"] == (Target("manifest", "own"), Target("service", "any"), Target("shared"))
    assert rules["service"] == (Target("store", "own"), Target("shared"), Target("hooks", "any"))


REMOVED = "was removed in 0.3.0: write"
NOT_A_REFERENCE = ("is not a reference: write parts.<part> or <word>.<part>, optionally followed by /<path> and "
                   ":<pattern>")


@pytest.mark.parametrize("importer, name, expected", [
    pytest.param("hooks", "service", f"layered.yaml: parts.hooks.imports.may: 'service': a bare part name {REMOVED} "
                                     "parts.service", id="a plugin part names a module part bare"),
    pytest.param("service", "hooks", f"layered.yaml: parts.service.imports.may: 'hooks': a bare part name {REMOVED} "
                                     "parts.hooks", id="a module part names a plugin part bare"),
    pytest.param("hooks", "service@own", f"layered.yaml: parts.hooks.imports.may: 'service@own': @own {REMOVED} "
                                         "parts.service", id="a plugin part names a module part as its own"),
])
def test_a_part_in_another_repeating_folder_has_no_own_instance_so_an_old_form_is_told_parts(importer, name, expected):
    document = two_folders()
    part_of(document, importer).setdefault("imports", {})["may"] = [name]
    assert problems(document) == [expected]


def test_a_must_import_in_an_old_form_is_refused_once_with_its_reference():
    document = two_folders()
    part_of(document, "hooks").setdefault("imports", {})["may"] = ["parts.service"]
    part_of(document, "hooks").setdefault("imports", {})["must"] = ["service"]
    assert problems(document) == [
        f"layered.yaml: parts.hooks.imports.must: 'service': a bare part name {REMOVED} parts.service"]


@pytest.mark.parametrize("targets, rules", [
    pytest.param(["module.service"], (Target("service", "own"),),
                 id="a part of the repeating folder by its word is the importer's own"),
    pytest.param(["parts.service"], (Target("service", "any"),), id="parts is any instance"),
    pytest.param(["parts.shared"], (Target("shared"),), id="a part outside the repeating folder"),
    pytest.param(["parts.shared/text", "module.service/rules"], (Target("shared", "none", ("text",)),
                                                                 Target("service", "own", ("rules",))),
                 id="only a path below the part"),
    pytest.param(["parts.api"], (Target("api", "any"),), id="another instance of the part itself is allowed"),
    pytest.param([], (), id="nothing"),
])
def test_what_a_part_of_the_repeating_folder_may_import(targets, rules):
    document = layered()
    part_of(document, "store").setdefault("imports", {})["may"] = targets
    assert parsed(document).rules["store"] == rules


def test_a_part_outside_the_repeating_folder_reaches_into_it_with_parts():
    document = layered()
    part_of(document, "shared").setdefault("imports", {})["may"] = ["parts.api", "parts.service/rules"]
    assert parsed(document).rules["shared"] == (Target("api", "any"), Target("service", "any", ("rules",)))


def test_everything_is_a_part_that_may_import_everything_and_the_rest_a_part_with_no_may_import_imports_itself_only():
    document = layered()
    part_of(document, "shared").setdefault("imports", {})["may"] = "everything"
    architecture = parsed(document)
    assert architecture.rules["shared"] == (Target("*"),)
    assert architecture.rules["api"] == (Target("service", "own"),)
    assert parsed(layered()).rules["shared"] == ()


@pytest.mark.parametrize("part, targets, expected", [
    pytest.param("store", 3, "layered.yaml: parts.store.imports.may: must be a list of targets such as [parts.core, "
                              "unit.store/schema], or everything", id="not a list"),
    pytest.param("store", "all", "layered.yaml: parts.store.imports.may: must be a list of targets such as [parts.core, "
                                 "unit.store/schema], or everything", id="a string that is not everything"),
    pytest.param("store", ["repo"], "layered.yaml: parts.store.imports.may: 'repo' names no part 'repo'", id="no such part"),
    pytest.param("store", [3], f"layered.yaml: parts.store.imports.may: 3 {NOT_A_REFERENCE}", id="not text"),
    pytest.param("store", [""], f"layered.yaml: parts.store.imports.may: '' {NOT_A_REFERENCE}", id="empty"),
    pytest.param("store", ["service@own"], f"layered.yaml: parts.store.imports.may: 'service@own': @own {REMOVED} "
                                           "module.service", id="@own"),
    pytest.param("shared", ["api@own"], f"layered.yaml: parts.shared.imports.may: 'api@own': @own {REMOVED} parts.api",
                 id="@own from outside"),
    pytest.param("store", ["service@all"], f"layered.yaml: parts.store.imports.may: 'service@all' {NOT_A_REFERENCE}",
                 id="an unknown scope"),
    pytest.param("store", ["shared@any"], f"layered.yaml: parts.store.imports.may: 'shared@any': @any {REMOVED} "
                                          "parts.shared", id="@any on a part outside"),
    pytest.param("shared", ["api"], f"layered.yaml: parts.shared.imports.may: 'api': a bare part name {REMOVED} "
                                    "parts.api", id="a bare part inside, from outside"),
    pytest.param("store", ["service"], f"layered.yaml: parts.store.imports.may: 'service': a bare part name {REMOVED} "
                                       "module.service (this module's) or parts.service (any module's)",
                 id="a bare part inside, from inside"),
    pytest.param("store", ["parts.shared/../x"], "layered.yaml: parts.store.imports.may: 'parts.shared/../x' has an "
                                                 "invalid path after the part", id="a climbing path"),
    pytest.param("store", ["parts.shared/"], "layered.yaml: parts.store.imports.may: 'parts.shared/' has an invalid "
                                             "path after the part", id="a trailing slash"),
    pytest.param("store", ["store"], "layered.yaml: parts.store.imports.may: 'store' is implied: a part may always "
                                     "import itself, its own instance of the repeating folder; remove it "
                                     "(parts.store, another instance's too, stays allowed)",
                 id="itself in an instance"),
    pytest.param("shared", ["shared"], "layered.yaml: parts.shared.imports.may: 'shared' is implied: a part may always "
                                       "import itself; remove it", id="itself outside the instances"),
    pytest.param("store", ["everything"], "layered.yaml: parts.store.imports.may: 'everything' stands alone: write "
                                          "`everything` in place of the list", id="everything inside a list"),
])
def test_a_bad_target_is_refused_saying_what_to_write(part, targets, expected):
    document = layered()
    part_of(document, part).setdefault("imports", {})["may"] = targets
    assert problems(document) == [expected]


def test_libraries_are_strict_by_default_and_a_part_lists_what_it_may_import():
    libraries = parsed(layered()).imports_libraries
    assert libraries == {"api": (), "service": (), "store": ("sqlmodel",), "shared": ()}


def test_a_part_may_leave_libraries_unchecked_with_everything():
    document = layered()
    part_of(document, "shared").setdefault("imports", {})["libraries"] = "everything"
    assert parsed(document).imports_libraries["shared"] == (Target("*").part,)


@pytest.mark.parametrize("libraries, expected", [
    pytest.param(3, "layered.yaml: parts.store.imports.libraries: must be a list of top-level import names such as "
                    "[sqlmodel], or everything", id="not a list"),
    pytest.param("all", "layered.yaml: parts.store.imports.libraries: must be a list of top-level import names such as "
                        "[sqlmodel], or everything", id="a string that is not everything"),
    pytest.param(["json"], "layered.yaml: parts.store.imports.libraries: 'json' is in the standard library, which every part "
                           "may import unless `reserved` names it", id="the standard library"),
    pytest.param(["a.b"], "layered.yaml: parts.store.imports.libraries: 'a.b' is not a package name the language Python allows",
                 id="a dotted name"),
    pytest.param(["x", "x"], "layered.yaml: parts.store.imports.libraries: 'x' is listed twice", id="twice"),
])
def test_bad_libraries_are_refused(libraries, expected):
    document = layered()
    part_of(document, "store").setdefault("imports", {})["libraries"] = libraries
    assert problems(document) == [expected]


def test_a_part_refers_to_a_list_under_never_by_its_name():
    document = layered(never={"pure": ["datetime.datetime.now", "builtins.open", "socket"]})
    part_of(document, "service")["uses"] = {"never": "pure"}
    part_of(document, "shared")["uses"] = {"never": "pure"}
    uses_never = parsed(document).uses_never
    assert uses_never == {"service": (("datetime", "datetime", "now"), ("builtins", "open"), ("socket",)),
                          "shared": (("datetime", "datetime", "now"), ("builtins", "open"), ("socket",))}


def test_a_part_that_names_no_list_forbids_nothing():
    assert parsed(layered(never={"pure": ["socket"]})).uses_never == {}


@pytest.mark.parametrize("never, part, expected", [
    pytest.param(3, "pure", ["layered.yaml: never: must be a mapping of list names to lists of dotted names, such "
                             "as {pure: [datetime.datetime.now, socket]}"], id="not a mapping"),
    pytest.param({"pure": []}, "pure", ["layered.yaml: never.pure: must be a non-empty list of outside names, packages "
                                        "or methods, such as [<package>.<name>, <package>, .<name>()]"], id="an empty list"),
    pytest.param({"pure": ["open"]}, "pure", ["layered.yaml: never.pure: 'open' is a Python builtin, which a bare "
                                              "name does not ban: write builtins.open"], id="a bare builtin"),
    pytest.param({"pure": ["socket", "socket"]}, "pure", ["layered.yaml: never.pure: 'socket' is listed twice"],
                 id="a name twice"),
    pytest.param({"a b": ["socket"]}, "pure", ["layered.yaml: never: 'a b' is not a list name: use letters, "
                                               "digits, '_' and '-'",
                                               "layered.yaml: parts.service.uses.never: no list named 'pure': write "
                                               "it under `never`"], id="a bad list name"),
    pytest.param({"pure": ["socket"]}, "impure", ["layered.yaml: parts.service.uses.never: no list named 'impure': "
                                                  "use pure, or write it under `never`"], id="no such list"),
    pytest.param({"pure": ["socket"]}, 3, ["layered.yaml: parts.service.uses.never: must be the name of a list "
                                           "under `never`"], id="a part naming no text"),
])
def test_bad_forbidden_lists_are_refused(never, part, expected):
    document = layered(never=never)
    part_of(document, "service")["uses"] = {"never": part}
    assert problems(document) == expected


def test_layers_are_chains_of_parts_checked_against_what_the_parts_may_import():
    document = layered(layers={"app": ["shared", "store", "service", "api"]})
    assert parsed(document).layers == {"app": ("shared", "store", "service", "api")}
    document = layered(layers={"app": ["api", "service"]})
    assert problems(document) == ["layered.yaml: layers.app: 'api' imports 'service', which is outward of it"]
    assert problems(layered(layers={"app": ["api", "repo"]})) == ["layered.yaml: layers.app: no part named 'repo'"]


def test_a_part_that_is_package_only_makes_the_guard_with_its_parts_in_the_order_of_the_parts():
    document = layered()
    part_of(document, "store")["package_only"] = True
    part_of(document, "api")["package_only"] = True
    part_of(document, "shared")["package_only"] = False
    assert [(type(guard).__name__, guard.parts) for guard in parsed(document).guards] == [
        ("PackageOnly", ("api", "store"))]


def test_every_problem_of_a_profile_is_reported_at_once():
    document = layered(colour=1, language="ruby", layout={})
    part_of(document, "store").setdefault("imports", {})["may"] = ["repo"]
    assert problems(document) == [
        "layered.yaml: unknown keys 'colour', 'layout': use based_on, checks, docs, evals, excluded, fakes, files, guards, "
        "hints, language, layers, name, never, parts, reserved, review, testing, tiers",
        "layered.yaml: language: 'ruby' is not a language xarch reads: use python",
        "layered.yaml: parts.store.imports.may: 'repo' names no part 'repo'"]


def test_a_part_says_what_its_files_must_import_with_the_targets_of_may_import():
    document = layered()
    part_of(document, "store").setdefault("imports", {})["must"] = ["parts.shared"]
    part_of(document, "api").setdefault("imports", {})["must"] = ["module.service"]
    architecture = parsed(document)
    assert architecture.parts["store"].imports_must == (Target("shared"),)
    assert architecture.parts["api"].imports_must == (Target("service", "own"),)
    assert architecture.parts["shared"].imports_must == ()


@pytest.mark.parametrize("value, expected", [
    pytest.param("everything", "layered.yaml: parts.store.imports.must: must be a list of targets such as "
                               "[parts.<part>, <word>.<part>]", id="no everything"),
    pytest.param([], "layered.yaml: parts.store.imports.must: must be a list of targets such as [parts.<part>, <word>.<part>]",
                 id="an empty list"),
    pytest.param(["ghost"], "layered.yaml: parts.store.imports.must: 'ghost' names no part 'ghost'", id="no such part"),
    pytest.param(["module.api"], "layered.yaml: parts.store.imports.must: 'module.api' is not in imports.may, so no "
                                 "file could import it: add it there, or name a part the part may import",
                 id="a part it may not import"),
    pytest.param(["module.store"], "layered.yaml: parts.store.imports.must: 'module.store' is implied: a part may "
                                   "always import itself, its own instance of the repeating folder; remove it "
                                   "(parts.store, another instance's too, stays allowed)", id="the part itself"),
    pytest.param(["api"], f"layered.yaml: parts.store.imports.must: 'api': a bare part name {REMOVED} module.api (this "
                          "module's) or parts.api (any module's)", id="an old form, refused once"),
])
def test_a_bad_must_import_is_refused(value, expected):
    document = layered()
    part_of(document, "store").setdefault("imports", {})["must"] = value
    assert problems(document) == [expected]


def test_a_part_that_may_import_everything_may_be_asked_to_reach_any_part():
    document = layered()
    part_of(document, "store").setdefault("imports", {})["may"] = "everything"
    part_of(document, "store").setdefault("imports", {})["must"] = ["module.api"]
    assert parsed(document).parts["store"].imports_must == (Target("api", "own"),)


def referencing(services: dict, guard: dict) -> dict:
    """A profile of modules/<module>/ (domain, services) and kernel/, services tested by a tier guard in the folder
    architecture and the other parts untested: services writes the imports given, and the guard the keys given beside
    its folder."""
    return {"name": "refs", "testing": deepcopy(TESTING), "parts": {
        "modules/<module>/": {
            "domain/": {"role": "the rules", "untested": "read through services"},
            "services/": {"role": "the use cases", "tests": "guard", "imports": services}},
        "kernel/": {"role": "shared code", "untested": "too small to test"}},
        "tiers": {"guard": {"folder": "architecture"} | guard}}


def test_references_reach_every_target_spec_reads_and_the_old_forms_are_each_refused_with_one():
    new = parsed(referencing({"may": ["module.domain", "parts.kernel", {"parts.domain": "types_only"}],
                              "must": ["parts.kernel"]},
                             {"imports": {"may": ["parts.kernel"], "also": ["module.domain/values"]}}))
    old = referencing({"may": ["domain", "kernel", {"domain@any": "types_only"}], "must": ["kernel"]},
                      {"imports": {"may": ["kernel"], "also": ["domain/values"]}})
    services, (guard,) = new.parts["services"], new.tiers
    assert (new.rules["services"], services.imports_must, services.imports_types_only) == (
        (Target("domain", "own"), Target("kernel"), Target("domain", "any")), (Target("kernel"),),
        (Target("domain", "any"),))
    assert (guard.imports_may, guard.imports_also) == ((Target("kernel"),), (Target("domain", "own", ("values",)),))
    own = f"a bare part name {REMOVED} module.domain (this module's) or parts.domain (any module's)"
    assert problems(old) == [
        f"layered.yaml: parts.services.imports.may: 'domain': {own}",
        f"layered.yaml: parts.services.imports.may: 'kernel': a bare part name {REMOVED} parts.kernel",
        f"layered.yaml: parts.services.imports.may: 'domain@any': @any {REMOVED} parts.domain",
        f"layered.yaml: parts.services.imports.must: 'kernel': a bare part name {REMOVED} parts.kernel",
        f"layered.yaml: tiers.guard.imports.may: 'kernel': a bare part name {REMOVED} parts.kernel",
        f"layered.yaml: tiers.guard.imports.also: 'domain/values': a bare part name {REMOVED} module.domain/values "
        "(this module's) or parts.domain/values (any module's)"]


@pytest.mark.parametrize("services, guard, problem", [
    pytest.param({"may": ["module.kernel"]}, {},
                 "layered.yaml: parts.services.imports.may: 'module.kernel': part 'kernel' lies in no <module> folder: "
                 "write parts.kernel", id="a part's may"),
    pytest.param({"may": ["parts.kernel"], "must": ["module.kernel"]}, {},
                 "layered.yaml: parts.services.imports.must: 'module.kernel': part 'kernel' lies in no <module> folder: "
                 "write parts.kernel", id="a part's must"),
    pytest.param({"may": ["parts.kernel"]}, {"imports": {"also": ["module.kernel"]}},
                 "layered.yaml: tiers.guard.imports.also: 'module.kernel': part 'kernel' lies in no <module> folder: "
                 "write parts.kernel", id="a tier's also"),
    pytest.param({"may": ["parts.kernel"]}, {"imports": {"may": ["module.domain"]}},
                 "layered.yaml: tiers.guard.imports.may: 'module.domain': a tier's folder lies in no <module> folder, "
                 "so it has no own module: write parts.domain", id="a tier's may"),
])
def test_a_reference_written_wrong_is_refused_at_its_address(services, guard, problem):
    assert problems(referencing(services, guard)) == [problem]


def built_by(names: list) -> dict:
    document = layered()
    part_of(document, "service")["holds"] = {"classes": {"built_by": names}}
    return document


OUTSIDE = "names a part outside imports: write"


@pytest.mark.parametrize("document, problem", [
    pytest.param(built_by(["parts.store"]), f"parts.service.holds.classes.built_by: 'parts.store': {OUTSIDE} store",
                 id="holds.classes.built_by"),
    pytest.param(covered(fakes={"folder": "fakes", "for": ["parts.store"]}),
                 f"fakes.for: 'parts.store': {OUTSIDE} store", id="fakes.for"),
    pytest.param(covered(guards={"no-twins": {"translated": ["module.store"]}}),
                 f"guards.no-twins.translated: 'module.store': {OUTSIDE} store", id="guards.no-twins.translated"),
    pytest.param(covered(guards={"pass-through": {"parts": ["parts.service"]}}),
                 f"guards.pass-through.parts: 'parts.service': {OUTSIDE} service", id="guards.pass-through.parts"),
    pytest.param(covered(guards={"no-callbacks": {"parts": ["module.service/x"]}}),
                 f"guards.no-callbacks.parts: 'module.service/x': {OUTSIDE} service", id="a path dropped"),
    pytest.param(layered(layers={"app": ["parts.store", "api"]}), f"layers.app: 'parts.store': {OUTSIDE} store",
                 id="layers"),
    pytest.param(layered(docs={"entry": "module.api"}), f"docs.entry: 'module.api': {OUTSIDE} api", id="docs.entry"),
    pytest.param(layered(docs={"entry": "orders.api"}), "docs.entry: no part named 'orders.api'",
                 id="a prefix that is no word keeps the reader's text"),
    pytest.param(covered(fakes={"folder": "fakes", "for": ["parts.nope"]}), "fakes.for: no part named 'parts.nope'",
                 id="a part not declared keeps the reader's text"),
])
def test_a_key_outside_imports_refuses_a_prefixed_name_with_the_plain_one(document, problem):
    assert problems(document) == [f"layered.yaml: {problem}"]
