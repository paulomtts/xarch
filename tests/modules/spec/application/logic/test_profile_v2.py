"""A profile file in format 2: its keys, its parts and the layout they imply, what a part may import, its outside
packages, the names it may not use, and the layers."""
import pytest

from tests.modules.spec.format_files import CATALOGUE
from tests.modules.spec.profiles_v2 import layered, parsed, problems, two_folders
from xarch.modules.spec.application.logic.key_lookup import names_of
from xarch.modules.spec.application.logic.key_table import KEYS
from xarch.modules.spec.application.logic.layout_walk import docs_name, is_file
from xarch.modules.spec.domain.profile_keys import SCOPES
from xarch.modules.spec.domain.values import Part
from xarch.profile_values.placement import Repeat, Target


def test_the_smallest_profile_is_a_name_and_parts_and_checks_the_layout_and_the_imports():
    architecture = parsed({"xarch": 2, "name": "tiny", "parts": {
        "core": {"path": "core", "role": "the rules"},
        "cli": {"path": "cli", "role": "commands and output", "may_import": ["core"], "libraries": ["typer"]}}})
    assert architecture.name == "tiny"
    assert architecture.layout == {"core": {}, "cli": {}}
    assert architecture.rules == {"core": (), "cli": (Target("core"),)}
    assert architecture.libraries == {"core": (), "cli": ("typer",)}
    assert architecture.tiers == () and architecture.guards == () and architecture.framework is None
    assert architecture.repeats == ()


def test_a_profile_says_what_it_does_not_have_by_leaving_it_out():
    architecture = parsed(layered())
    assert (architecture.docs, architecture.examples, architecture.notes, architecture.layers, architecture.placement,
            architecture.naming, architecture.fakes, architecture.files, architecture.forbidden,
            architecture.excluded, architecture.hints, architecture.based_on) == (
        (), {}, {}, {}, ("api", "service", "store", "shared"), (), None, (), {}, (), {}, "")


def test_unknown_keys_are_refused_with_the_keys_that_exist_in_the_file():
    assert problems(layered(colour=1, extra=2)) == [
        "layered.yaml: unknown keys 'colour', 'extra': use based_on, checks, docs, evals, excluded, fakes, files, forbidden, guards, "
        "hints, language, layers, name, parts, reserved, review, testing, tiers, xarch"]


def test_every_unknown_key_message_reads_the_table_of_keys():
    assert {key.name for key in KEYS if key.scope == "profile"} == names_of("profile")
    assert problems(layered(colour=1))[0].split("use ")[1] == ", ".join(sorted(names_of("profile")))
    assert problems(layered(parts={"x": {"path": "x", "role": "r", "colour": 1}}))[0].split("use ")[1] == ", ".join(
        sorted(names_of("part")))


def test_every_key_of_the_table_has_a_scope_with_an_address_and_a_meaning():
    assert all(key.scope in SCOPES and CATALOGUE.texts[key.address].meaning and key.address for key in KEYS)
    assert len({key.address for key in KEYS}) == len(KEYS)


def test_the_required_keys_are_reported_together():
    assert problems({"xarch": 2}) == ["layered.yaml: missing `name`", "layered.yaml: missing `parts`"]


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
    assert problems(layered(based_on=3)) == ["layered.yaml: based_on: must be the name of a bundled profile: use cli, web"]


def test_the_layout_is_derived_from_the_paths_of_the_parts_and_a_repeating_step_is_one_star():
    architecture = parsed(layered())
    assert architecture.layout == {"src": {"*": {"api": {}, "service": {}, "store": {}}}, "shared": {}}
    assert architecture.repeats == (Repeat("module", ("src",)),)
    assert architecture.parts["api"] == Part("api", ("src", "*", "api"), "HTTP handlers")


def test_the_order_of_the_parts_is_the_placement_order():
    document = layered()
    document["parts"] = {name: document["parts"][name] for name in ("shared", "store", "api", "service")}
    assert parsed(document).placement == ("shared", "store", "api", "service")


def test_a_last_step_with_a_dot_is_a_file_and_a_part_may_sit_inside_another_ones_folder():
    document = layered()
    document["parts"]["entry"] = {"path": "src/<module>/entry.py", "role": "the entry"}
    document["parts"]["sql"] = {"path": "src/<module>/store/sql", "role": "queries"}
    architecture = parsed(document)
    assert architecture.layout["src"]["*"]["entry.py"] is None
    assert architecture.layout["src"]["*"]["store"] == {"sql": {}}
    assert is_file(architecture.layout, ("src", "*", "entry.py")) and not is_file(architecture.layout, ("src", "*", "store"))


def test_a_top_level_file_is_a_file():
    document = layered()
    document["parts"]["main"] = {"path": "__main__.py", "role": "starts the app"}
    assert parsed(document).layout["__main__.py"] is None


def test_the_folders_of_a_part_are_in_the_layout_with_their_notes_as_the_notes_of_the_layout():
    document = layered()
    document["parts"]["shared"]["folders"] = {"text": "string helpers", "io/disk": "what touches the disk"}
    document["parts"]["api"]["folders"] = ["v1"]
    architecture = parsed(document)
    assert architecture.layout["shared"] == {"text": {}, "io": {"disk": {}}}
    assert architecture.layout["src"]["*"]["api"] == {"v1": {}}
    assert architecture.notes == {("shared", "text"): "string helpers", ("shared", "io", "disk"): "what touches the disk"}


@pytest.mark.parametrize("folders, expected", [
    pytest.param(3, "layered.yaml: parts.shared.folders: must be a mapping of folder paths to one line of text, or a "
                    "list of folder paths", id="not a mapping or a list"),
    pytest.param({"../x": "n"}, "layered.yaml: parts.shared.folders: '../x' is not a folder below the part: write "
                                "a path of plain names such as io/disk", id="a path climbing out"),
    pytest.param({"a": "two\nlines"}, "layered.yaml: parts.shared.folders.a: must be one line of text",
                 id="a note of two lines"),
    pytest.param({"a": 3}, "layered.yaml: parts.shared.folders.a: must be one line of text", id="a note that is no text"),
    pytest.param(["a", "a"], "layered.yaml: parts.shared.folders: 'a' is listed twice", id="a folder twice"),
])
def test_a_bad_folders_entry_is_refused(folders, expected):
    document = layered()
    document["parts"]["shared"]["folders"] = folders
    assert problems(document) == [expected]


def test_a_part_that_is_a_file_has_no_folders():
    document = layered()
    document["parts"]["main"] = {"path": "main.py", "role": "x", "folders": ["a"]}
    assert problems(document) == ["layered.yaml: parts.main.folders: a file has no folders: drop the key"]


def test_a_folder_that_is_a_part_is_refused_since_its_note_is_its_role():
    document = layered()
    document["parts"]["shared"]["folders"] = {"text": "helpers"}
    document["parts"]["text"] = {"path": "shared/text", "role": "text helpers"}
    assert problems(document) == ["layered.yaml: parts.shared.folders.text: 'text' is part 'text', whose note is its "
                                  "role: drop it from `folders`"]


@pytest.mark.parametrize("parts, expected", [
    pytest.param(3, ["layered.yaml: parts: must be a mapping of part names to {path, role, ...}"], id="not a mapping"),
    pytest.param({3: {"path": "x", "role": "r"}, "a b": {"path": "y", "role": "r"}},
                 ["layered.yaml: parts: 3 is not a part name: use letters, digits, '_' and '-'",
                  "layered.yaml: parts: 'a b' is not a part name: use letters, digits, '_' and '-'"],
                 id="bad names"),
    pytest.param({"x": 3}, ["layered.yaml: parts.x: must be a mapping with `path` and `role`"], id="a part that is no mapping"),
    pytest.param({"x": {}}, ["layered.yaml: parts.x: missing `path`", "layered.yaml: parts.x: missing `role`"],
                 id="a part with nothing"),
    pytest.param({"x": {"path": "x", "role": 3, "litmus": 4}},
                 ["layered.yaml: parts.x.role: must be a string", "layered.yaml: parts.x.litmus: must be a string"],
                 id="texts that are no strings"),
    pytest.param({"x": {"path": "x", "role": "r", "colour": 1}},
                 ["layered.yaml: parts.x: unknown key 'colour': use built_by, folders, forbidden, holds, immutable, libraries, litmus, "
                  "may_import, must_import, names, no_callbacks, package_only, path, role, shared, tier, types_only, untested"],
                 id="an unknown key"),
    pytest.param({"x": {"path": "x", "role": "r", "package_only": "yes"}},
                 ["layered.yaml: parts.x.package_only: must be true or false"], id="package_only that is no boolean"),
    pytest.param({"x": {"path": "x", "role": "r", "untested": "two\nlines"}},
                 ["layered.yaml: parts.x.untested: must be one line of text: why no tier tests the part"],
                 id="an untested reason of two lines"),
])
def test_a_bad_part_is_refused_with_every_problem(parts, expected):
    assert problems(layered(parts=parts)) == expected


@pytest.mark.parametrize("path, expected", [
    pytest.param(3, "layered.yaml: parts.x.path: must be a path such as 'src/<name>/api'", id="no text"),
    pytest.param("", "layered.yaml: parts.x.path: must be a path such as 'src/<name>/api'", id="empty"),
    pytest.param("a//b", "layered.yaml: parts.x.path: 'a//b' has an empty, `.` or `..` step", id="an empty step"),
    pytest.param("a/../b", "layered.yaml: parts.x.path: 'a/../b' has an empty, `.` or `..` step", id="a step climbing"),
    pytest.param("a/*/b", "layered.yaml: parts.x.path: 'a/*/b' has a `*` step: write the repeating folder as "
                          "one word between `<` and `>`", id="a star in a path"),
    pytest.param("a/<mo dule>/b", "layered.yaml: parts.x.path: 'a/<mo dule>/b' has a step with `<` or `>` that is not "
                                  "one word between them: write the "
                                  "repeating folder as `<name>`", id="a bracket that holds no word"),
    pytest.param("a/<x>b", "layered.yaml: parts.x.path: 'a/<x>b' has a step with `<` or `>` that is not "
                           "one word between them: write the repeating folder as `<name>`", id="a bracket inside a name"),
    pytest.param("<a>/<b>/c", "layered.yaml: parts.x.path: '<a>/<b>/c' has two repeating steps, <a> and <b>: a "
                              "repeating folder cannot sit inside another, so give each its own folder",
                 id="two repeating steps"),
    pytest.param("shared", "layered.yaml: parts.x.path: 'shared' is already claimed by part 'shared'", id="a path twice"),
    pytest.param("shared/", "layered.yaml: parts.x.path: 'shared' is already claimed by part 'shared'",
                 id="a path twice with a slash"),
])
def test_a_bad_part_path_is_refused(path, expected):
    document = layered()
    document["parts"]["x"] = {"path": path, "role": "r"}
    assert problems(document) == [expected]


def test_two_words_may_not_share_a_parent():
    document = layered()
    document["parts"]["x"] = {"path": "src/<doc>/x", "role": "r"}
    assert problems(document) == [
        "layered.yaml: parts.x.path: 'src/<doc>/x' calls the repeating folder <doc>, but part 'api' called it "
        "<module> in the same folder 'src': two words may not share a parent, use one word"]


def test_one_word_repeats_in_one_folder_only():
    document = layered()
    document["parts"]["y"] = {"path": "other/<module>/y", "role": "r"}
    assert problems(document) == [
        "layered.yaml: parts.y.path: 'other/<module>/y' repeats <module> below 'other', but part 'api' repeats it "
        "below 'src': one word repeats in one folder, so give this one a word of its own"]


def test_a_profile_may_hold_several_repeating_folders_each_with_its_word_and_parent():
    architecture = parsed(two_folders())
    assert architecture.repeats == (Repeat("module", ("src",)), Repeat("plugin", ("ext",)))
    assert architecture.layout == {"src": {"*": {"api": {}, "service": {}, "store": {}}},
                                   "ext": {"*": {"hooks": {}, "manifest.py": None}}, "shared": {}}
    assert architecture.parts["hooks"].path == ("ext", "*", "hooks")
    assert architecture.top_level_tree() == {"src": {}, "ext": {}, "shared": {}}
    assert architecture.instance_tree(architecture.repeats[1]) == {"hooks": {}, "manifest.py": None}


def test_a_part_is_shown_below_its_own_repeating_folder():
    architecture = parsed(two_folders())
    assert [docs_name(architecture, architecture.parts[name]) for name in ("api", "hooks", "manifest", "shared")] == [
        "api/", "hooks/", "manifest.py", "shared/"]


def test_a_part_names_a_part_of_its_own_repeating_folder_bare_and_one_of_another_with_any():
    document = two_folders()
    document["parts"]["hooks"]["may_import"] = ["manifest", "service@any", "shared"]
    document["parts"]["service"]["may_import"] = ["store", "shared", "hooks@any"]
    rules = parsed(document).rules
    assert rules["hooks"] == (Target("manifest", "own"), Target("service", "any"), Target("shared"))
    assert rules["service"] == (Target("store", "own"), Target("shared"), Target("hooks", "any"))


@pytest.mark.parametrize("importer, name, expected", [
    pytest.param("hooks", "service", "layered.yaml: parts.hooks.may_import: 'service' lies in another repeating "
                                     "folder than part 'hooks', which has no own instance of it: write service@any",
                 id="a plugin part names a module part bare"),
    pytest.param("service", "hooks", "layered.yaml: parts.service.may_import: 'hooks' lies in another repeating "
                                     "folder than part 'service', which has no own instance of it: write hooks@any",
                 id="a module part names a plugin part bare"),
])
def test_a_part_in_another_repeating_folder_has_no_own_instance_so_a_bare_name_is_refused(importer, name, expected):
    document = two_folders()
    document["parts"][importer]["may_import"] = [name]
    assert problems(document) == [expected]


def test_a_part_in_another_repeating_folder_may_not_be_said_as_own():
    document = two_folders()
    document["parts"]["hooks"]["may_import"] = ["service@own"]
    assert problems(document) == [
        "layered.yaml: parts.hooks.may_import: 'service@own' lies in another repeating folder than part 'hooks', "
        "which has no own instance of it: write service@any"]


def test_a_must_import_names_a_part_of_another_repeating_folder_with_any_as_well():
    document = two_folders()
    document["parts"]["hooks"]["may_import"] = ["service@any"]
    document["parts"]["hooks"]["must_import"] = ["service"]
    assert problems(document) == [
        "layered.yaml: parts.hooks.must_import: 'service' lies in another repeating folder than part 'hooks', which "
        "has no own instance of it: write service@any"]


def test_a_file_cannot_hold_a_part_below_it():
    document = layered()
    document["parts"]["f"] = {"path": "notes.txt", "role": "r"}
    document["parts"]["g"] = {"path": "notes.txt/x", "role": "r"}
    assert problems(document) == [
        "layered.yaml: parts.g.path: 'notes.txt/x' lies below 'notes.txt', which part 'f' makes a file"]


def test_a_folder_that_holds_a_part_cannot_also_be_a_file():
    document = layered()
    document["parts"]["f"] = {"path": "a.b/x", "role": "r"}
    document["parts"]["g"] = {"path": "a.b", "role": "r"}
    assert problems(document) == [
        "layered.yaml: parts.g.path: 'a.b' is a file, since its last step holds a dot, but part 'f' lies below it: "
        "rename one of them"]


@pytest.mark.parametrize("targets, rules", [
    pytest.param(["service"], (Target("service", "own"),), id="a part of the repeating folder, by its bare name, is the importer's own"),
    pytest.param(["service@any"], (Target("service", "any"),), id="@any is any instance"),
    pytest.param(["shared"], (Target("shared"),), id="a part outside the repeating folder"),
    pytest.param(["shared/text", "service/rules"], (Target("shared", "none", ("text",)),
                                                    Target("service", "own", ("rules",))),
                 id="only a path below the part"),
    pytest.param(["api@any"], (Target("api", "any"),), id="another instance of the part itself is allowed"),
    pytest.param([], (), id="nothing"),
])
def test_what_a_part_of_the_repeating_folder_may_import(targets, rules):
    document = layered()
    document["parts"]["store"]["may_import"] = targets
    assert parsed(document).rules["store"] == rules


def test_a_part_outside_the_repeating_folder_reaches_into_it_with_any():
    document = layered()
    document["parts"]["shared"]["may_import"] = ["api@any", "service@any/rules"]
    assert parsed(document).rules["shared"] == (Target("api", "any"), Target("service", "any", ("rules",)))


def test_everything_is_a_part_that_may_import_everything_and_the_rest_a_part_with_no_may_import_imports_itself_only():
    document = layered()
    document["parts"]["shared"]["may_import"] = "everything"
    architecture = parsed(document)
    assert architecture.rules["shared"] == (Target("*"),)
    assert architecture.rules["api"] == (Target("service", "own"),)
    assert parsed(layered()).rules["shared"] == ()


@pytest.mark.parametrize("part, targets, expected", [
    pytest.param("store", 3, "layered.yaml: parts.store.may_import: must be a list of targets such as [<part>, "
                              "shared/text, api@any], or everything", id="not a list"),
    pytest.param("store", "all", "layered.yaml: parts.store.may_import: must be a list of targets such as [<part>, "
                                 "shared/text, api@any], or everything", id="a string that is not everything"),
    pytest.param("store", ["repo"], "layered.yaml: parts.store.may_import: 'repo' names no part 'repo'", id="no such part"),
    pytest.param("store", [3], "layered.yaml: parts.store.may_import: 3 is not a target: use <part>, <part>@any, "
                               "optionally followed by /<path>", id="not text"),
    pytest.param("store", [""], "layered.yaml: parts.store.may_import: '' is not a target: use <part>, <part>@any, "
                                "optionally followed by /<path>", id="empty"),
    pytest.param("store", ["service@own"], "layered.yaml: parts.store.may_import: 'service@own' says what a bare name "
                                           "already says: write service", id="@own is the default"),
    pytest.param("shared", ["api@own"], "layered.yaml: parts.shared.may_import: 'api@own' lies in the repeating "
                                        "folder, which shared is not in: say api@any", id="@own from outside"),
    pytest.param("store", ["service@all"], "layered.yaml: parts.store.may_import: 'service@all' has an unknown scope "
                                           "'@all': the only scope is @any, any instance of the repeating folder",
                 id="an unknown scope"),
    pytest.param("store", ["shared@any"], "layered.yaml: parts.store.may_import: 'shared@any' does not lie in the "
                                          "repeating folder: drop '@any'", id="@any on a part outside"),
    pytest.param("shared", ["api"], "layered.yaml: parts.shared.may_import: 'api' lies in the repeating folder, which "
                                    "shared is not in: say api@any", id="a bare part inside, from outside"),
    pytest.param("store", ["shared/../x"], "layered.yaml: parts.store.may_import: 'shared/../x' has an invalid path "
                                           "after the part", id="a climbing path"),
    pytest.param("store", ["shared/"], "layered.yaml: parts.store.may_import: 'shared/' has an invalid path after the "
                                       "part", id="a trailing slash"),
    pytest.param("store", ["store"], "layered.yaml: parts.store.may_import: 'store' is implied: a part may always "
                                     "import itself, its own instance of the repeating folder; remove it (store@any, "
                                     "another instance's too, stays allowed)", id="itself in an instance"),
    pytest.param("shared", ["shared"], "layered.yaml: parts.shared.may_import: 'shared' is implied: a part may always "
                                       "import itself; remove it", id="itself outside the instances"),
    pytest.param("store", ["everything"], "layered.yaml: parts.store.may_import: 'everything' stands alone: write "
                                          "`everything` in place of the list", id="everything inside a list"),
])
def test_a_bad_target_is_refused_saying_what_to_write(part, targets, expected):
    document = layered()
    document["parts"][part]["may_import"] = targets
    assert problems(document) == [expected]


def test_libraries_are_strict_by_default_and_a_part_lists_what_it_may_import():
    libraries = parsed(layered()).libraries
    assert libraries == {"api": (), "service": (), "store": ("sqlmodel",), "shared": ()}


def test_a_part_may_leave_libraries_unchecked_with_everything():
    document = layered()
    document["parts"]["shared"]["libraries"] = "everything"
    assert parsed(document).libraries["shared"] == (Target("*").part,)


@pytest.mark.parametrize("libraries, expected", [
    pytest.param(3, "layered.yaml: parts.store.libraries: must be a list of top-level import names such as "
                    "[sqlmodel], or everything", id="not a list"),
    pytest.param("all", "layered.yaml: parts.store.libraries: must be a list of top-level import names such as "
                        "[sqlmodel], or everything", id="a string that is not everything"),
    pytest.param(["json"], "layered.yaml: parts.store.libraries: 'json' is in the standard library, which every part "
                           "may import unless `reserved` names it", id="the standard library"),
    pytest.param(["a.b"], "layered.yaml: parts.store.libraries: 'a.b' is not a top-level import name, such as sqlmodel",
                 id="a dotted name"),
    pytest.param(["x", "x"], "layered.yaml: parts.store.libraries: 'x' is listed twice", id="twice"),
])
def test_bad_libraries_are_refused(libraries, expected):
    document = layered()
    document["parts"]["store"]["libraries"] = libraries
    assert problems(document) == [expected]


def test_a_part_refers_to_a_list_of_forbidden_names_by_its_name():
    document = layered(forbidden={"pure": ["datetime.datetime.now", "builtins.open", "socket"]})
    document["parts"]["service"]["forbidden"] = "pure"
    document["parts"]["shared"]["forbidden"] = "pure"
    forbidden = parsed(document).forbidden
    assert forbidden == {"service": (("datetime", "datetime", "now"), ("builtins", "open"), ("socket",)),
                         "shared": (("datetime", "datetime", "now"), ("builtins", "open"), ("socket",))}


def test_a_part_that_names_no_list_forbids_nothing():
    assert parsed(layered(forbidden={"pure": ["socket"]})).forbidden == {}


@pytest.mark.parametrize("forbidden, part, expected", [
    pytest.param(3, "pure", ["layered.yaml: forbidden: must be a mapping of list names to lists of dotted names, such "
                             "as {pure: [datetime.datetime.now, socket]}"], id="not a mapping"),
    pytest.param({"pure": []}, "pure", ["layered.yaml: forbidden.pure: must be a non-empty list of dotted names or "
                                        "import names, such as [datetime.datetime.now, socket]"], id="an empty list"),
    pytest.param({"pure": ["open"]}, "pure", ["layered.yaml: forbidden.pure: 'open' is a Python builtin, which a bare "
                                              "name does not ban: write builtins.open"], id="a bare builtin"),
    pytest.param({"pure": ["socket", "socket"]}, "pure", ["layered.yaml: forbidden.pure: 'socket' is listed twice"],
                 id="a name twice"),
    pytest.param({"a b": ["socket"]}, "pure", ["layered.yaml: forbidden: 'a b' is not a list name: use letters, "
                                               "digits, '_' and '-'",
                                               "layered.yaml: parts.service.forbidden: no list named 'pure': write "
                                               "it under `forbidden`"], id="a bad list name"),
    pytest.param({"pure": ["socket"]}, "impure", ["layered.yaml: parts.service.forbidden: no list named 'impure': "
                                                  "use pure, or write it under `forbidden`"], id="no such list"),
    pytest.param({"pure": ["socket"]}, 3, ["layered.yaml: parts.service.forbidden: must be the name of a list under "
                                           "`forbidden`"], id="a part naming no text"),
])
def test_bad_forbidden_lists_are_refused(forbidden, part, expected):
    document = layered(forbidden=forbidden)
    document["parts"]["service"]["forbidden"] = part
    assert problems(document) == expected


def test_layers_are_chains_of_parts_checked_against_what_the_parts_may_import():
    document = layered(layers={"app": ["shared", "store", "service", "api"]})
    assert parsed(document).layers == {"app": ("shared", "store", "service", "api")}
    document = layered(layers={"app": ["api", "service"]})
    assert problems(document) == ["layered.yaml: layers.app: 'api' imports 'service', which is outward of it"]
    assert problems(layered(layers={"app": ["api", "repo"]})) == ["layered.yaml: layers.app: no part named 'repo'"]


def test_a_part_that_is_package_only_makes_the_guard_with_its_parts_in_the_order_of_the_parts():
    document = layered()
    document["parts"]["store"]["package_only"] = True
    document["parts"]["api"]["package_only"] = True
    document["parts"]["shared"]["package_only"] = False
    assert [(type(guard).__name__, guard.parts) for guard in parsed(document).guards] == [
        ("PackageOnly", ("api", "store"))]


def test_every_problem_of_a_profile_is_reported_at_once():
    document = layered(colour=1, language="ruby", layout={})
    document["parts"]["store"]["may_import"] = ["repo"]
    assert problems(document) == [
        "layered.yaml: unknown keys 'colour', 'layout': use based_on, checks, docs, evals, excluded, fakes, files, forbidden, "
        "guards, hints, language, layers, name, parts, reserved, review, testing, tiers, xarch",
        "layered.yaml: language: 'ruby' is not a language xarch reads: use python",
        "layered.yaml: parts.store.may_import: 'repo' names no part 'repo'"]


def test_a_part_says_what_its_files_must_import_with_the_targets_of_may_import():
    document = layered()
    document["parts"]["store"]["must_import"] = ["shared"]
    document["parts"]["api"]["must_import"] = ["service"]
    architecture = parsed(document)
    assert architecture.parts["store"].must_import == (Target("shared"),)
    assert architecture.parts["api"].must_import == (Target("service", "own"),)
    assert architecture.parts["shared"].must_import == ()


@pytest.mark.parametrize("value, expected", [
    pytest.param("everything", "layered.yaml: parts.store.must_import: must be a list of targets such as "
                               "[<part>, <part>@any]", id="no everything"),
    pytest.param([], "layered.yaml: parts.store.must_import: must be a list of targets such as [<part>, <part>@any]",
                 id="an empty list"),
    pytest.param(["ghost"], "layered.yaml: parts.store.must_import: 'ghost' names no part 'ghost'", id="no such part"),
    pytest.param(["api"], "layered.yaml: parts.store.must_import: 'api' is not in `may_import`, so no file could "
                          "import it: add it there, or name a part the part may import", id="a part it may not import"),
    pytest.param(["store"], "layered.yaml: parts.store.must_import: 'store' is implied: a part may always import "
                            "itself, its own instance of the repeating folder; remove it (store@any, another "
                            "instance's too, stays allowed)", id="the part itself"),
])
def test_a_bad_must_import_is_refused(value, expected):
    document = layered()
    document["parts"]["store"]["must_import"] = value
    assert problems(document) == [expected]


def test_a_part_that_may_import_everything_may_be_asked_to_reach_any_part():
    document = layered()
    document["parts"]["store"]["may_import"] = "everything"
    document["parts"]["store"]["must_import"] = ["api"]
    assert parsed(document).parts["store"].must_import == (Target("api", "own"),)
