"""The folder tree under `parts`, walked once: a key ending in `/` is a folder, a key holding a dot a file, any other
key a key of the part; the parts in reading order, each with its own keys, the folders that are no part with their
notes, and the problems of the tree, each addressed by part name; a profile of the parts of 0.2.0 refused alone."""
import pytest

from tests.modules.spec.languages import PYTHON
from xarch.kernel.placement import EACH
from xarch.modules.spec.application.logic.parts_tree import PartsTree, TreeFolder, TreePart, parts_tree
from xarch.modules.spec.domain.values import Language

RESERVED = ("has the step `<parts>`: `<parts>` is reserved: `parts.` names a part in every instance; give the "
            "repeating folder another word")
KNOWN = "holds, imports, litmus, name, optional, package_only, role, shared, tests, untested, uses"


def walked(value):
    return parts_tree(value, PYTHON)


def test_a_folder_with_a_role_is_a_part_named_by_its_last_step_and_a_joined_key_is_its_steps():
    tree = walked({"modules/<module>/": {"domain/": {"role": "the rules", "tests": "unit"}}})
    assert tree == PartsTree(
        (TreePart("domain", ("modules", EACH, "domain"), ("module",), 0, {"role": "the rules", "tests": "unit"},
                  "modules/<module>/domain/", False),),
        (TreeFolder(("modules", EACH), ""),))


def test_the_parts_come_in_reading_order_a_part_before_the_parts_inside_it():
    tree = walked({"kernel/": {"role": "k", "logic/": {"name": "kernel-logic", "role": "kl"}},
                   "platform/": {"role": "p"}})
    assert [(part.name, part.order, part.shown) for part in tree.parts] == [
        ("kernel", 0, "kernel/"), ("kernel-logic", 1, "kernel/logic/"), ("platform", 2, "platform/")]
    assert tree.parts[0].keys == {"role": "k"} and tree.parts[1].keys == {"name": "kernel-logic", "role": "kl"}


def test_a_file_is_named_before_its_first_dot_and_name_replaces_any_name():
    tree = walked({"__main__.py": {"role": "starts"}, "cli/": {"main.tool.py": {"name": "tool", "role": "t"}}})
    assert [(part.name, part.steps, part.file) for part in tree.parts] == [
        ("__main__", ("__main__.py",), True), ("tool", ("cli", "main.tool.py"), True)]
    assert tree.folders == (TreeFolder(("cli",), ""),)


def test_a_folder_that_is_no_part_is_a_folder_with_its_note_or_none():
    tree = walked({"web/": {"role": "w", "routes/": "one file per route group", "ui/": None, "i18n/": {}}})
    assert tree.folders == (TreeFolder(("web", "routes"), "one file per route group"), TreeFolder(("web", "ui"), ""),
                            TreeFolder(("web", "i18n"), ""))
    assert [part.name for part in tree.parts] == ["web"]


def test_two_repeating_steps_on_the_way_to_a_part_are_kept_for_the_parser_to_refuse():
    assert walked({"<a>/": {"<b>/": {"c/": {"role": "r"}}}}).parts[0].words == ("a", "b")


@pytest.mark.parametrize("value, expected", [
    pytest.param(3, "parts: must be the folder tree of the app: folders ending in /, files with their extension",
                 id="1 parts not a map"),
    pytest.param({"rol": "x"}, "parts: unknown key 'rol': a key under parts is a folder ending in / or a file ending "
                 "in .py", id="2 a typo directly under parts"),
    pytest.param({"core/": {"litmus": "q"}}, "parts.core: missing `role`", id="3 a folder with a part key, no role"),
    pytest.param({"main.py": "x"}, "parts.main: a file is a part: write it as a map with role", id="4 a file no map"),
    pytest.param({"main.py": {}}, "parts.main: missing `role`", id="5 a file with no role"),
    pytest.param({"notes.txt": {"role": "r"}}, "parts.notes: 'notes.txt' is a file, since its key holds a dot, but it "
                 "does not end in .py: write a folder as notes.txt/", id="6 a file of another extension"),
    pytest.param({"application/": {"logic/": {"role": "a"}}, "kernel/": {"logic/": {"role": "b"}}},
                 "parts.logic: 'application/logic/' and 'kernel/logic/' are both named logic: write name: <part name> "
                 "on one of them", id="7 two parts of one name, no name invented"),
    pytest.param({"kernel/": {"role": "k"}, "kernel/logic/": {"role": "l"}},
                 "parts: the folder 'kernel/' is written twice, in 'kernel/' and 'kernel/logic/': write it once and "
                 "nest what lies in it", id="8 a part folder beside a key below it"),
    pytest.param({"modules/<module>/domain/": {"role": "d"}, "modules/<module>/adapters/": {"role": "a"}},
                 "parts: the folder 'modules/<module>/' is written twice, in 'modules/<module>/domain/' and "
                 "'modules/<module>/adapters/': write it once and nest what lies in it", id="8 a joined folder twice"),
    pytest.param({"core/": {"role": "r", "rol": "x"}}, f"parts.core: unknown key 'rol': use {KNOWN}",
                 id="9 a typo inside a folder is never a folder"),
    pytest.param({"core/": {"role": "r", "path": "core"}}, "parts.core: unknown key 'path': moved in 0.3.0: a part "
                 f"is the folder or file it is written as under parts: drop it; use {KNOWN}", id="10 path in a node"),
    pytest.param({"core/": {"role": "r", "folders": {"a": "n"}}}, "parts.core: unknown key 'folders': moved in "
                 "0.3.0: write each folder below the part as a key ending in /, with its note as its value; use "
                 f"{KNOWN}", id="11 folders in a node"),
    pytest.param({"src/<module>/": {"role": "r"}}, "parts: 'src/<module>/' is named '<module>', which is not a part "
                 "name: write name: with letters, digits, '_' and '-'", id="12 a name from the folder"),
    pytest.param({"core/": {"name": "a b", "role": "r"}}, "parts: 'core/' is named 'a b', which is not a part name: "
                 "write name: with letters, digits, '_' and '-'", id="12 a name from name"),
    pytest.param({"docs/": "two\nlines"}, "parts: 'docs/': a folder is a map, one line of text (its note), or nothing",
                 id="13 a note of two lines"),
    pytest.param({"docs/": ["a"]}, "parts: 'docs/': a folder is a map, one line of text (its note), or nothing",
                 id="13 a list"),
    pytest.param({"docs/": 3}, "parts: 'docs/': a folder is a map, one line of text (its note), or nothing",
                 id="13 a number"),
    pytest.param({"main.py": {"role": "r", "x/": {}}}, "parts.main: 'main.py' is a file and holds nothing below it",
                 id="14 a folder below a file"),
    pytest.param({"a//b/": {"role": "r"}}, "parts: 'a//b/' has an empty, `.` or `..` step", id="15 an empty step"),
    pytest.param({"a/../b/": {"role": "r"}}, "parts: 'a/../b/' has an empty, `.` or `..` step", id="15 climbing"),
    pytest.param({"a/*/b/": {"role": "r"}}, "parts: 'a/*/b/' has a `*` step: write the repeating folder as one word "
                 "between `<` and `>`", id="15 a star step"),
    pytest.param({"a/<mo dule>/b/": {"role": "r"}}, "parts: 'a/<mo dule>/b/' has a step with `<` or `>` that is not "
                 "one word between them: write the repeating folder as `<name>`", id="15 a bracket that is no word"),
    pytest.param({"a/<x>b/": {"role": "r"}}, "parts: 'a/<x>b/' has a step with `<` or `>` that is not one word "
                 "between them: write the repeating folder as `<name>`", id="15 a bracket inside a name"),
    pytest.param({"units/<parts>/store/": {"role": "r"}}, f"parts: 'units/<parts>/store/' {RESERVED}",
                 id="15 the word parts in a joined key"),
    pytest.param({"units/": {"<parts>/": {"store/": {"role": "r"}}}}, f"parts: '<parts>/' {RESERVED}",
                 id="15 the word parts in a nested key"),
    pytest.param({"<parts>/x.py": {"role": "r"}}, f"parts: '<parts>/x.py' {RESERVED}",
                 id="15 the word parts at the top"),
    pytest.param({"modules/<module>/": {}}, "parts: 'modules/<module>/' is a repeating folder with no part below it: "
                 "write a part in it, or drop it", id="17 a repeating folder with no part"),
])
def test_each_refusal_of_the_tree_says_where_and_what_to_write(value, expected):
    assert walked(value).problems == (expected,)


@pytest.mark.parametrize("value, names", [
    pytest.param({"units/<partsx>/store/": {"role": "r"}}, ["store"], id="a word that starts with parts"),
    pytest.param({"units/<sub-parts>/store/": {"role": "r"}}, ["store"], id="a word that ends with parts"),
    pytest.param({"parts/": {"store/": {"role": "r"}}}, ["store"], id="a plain folder named parts"),
    pytest.param({"parts/": {"role": "r"}}, ["parts"], id="a part named parts"),
])
def test_only_the_repeating_word_parts_is_reserved(value, names):
    tree = walked(value)
    assert (tree.problems, [part.name for part in tree.parts]) == ((), names)


def test_a_typo_alone_in_a_folder_leaves_it_a_folder_and_no_part():
    tree = walked({"core/": {"rol": "x"}})
    assert (tree.parts, tree.folders, tree.problems) == ((), (TreeFolder(("core",), ""),),
                                                         (f"parts.core: unknown key 'rol': use {KNOWN}",))


def test_a_file_of_another_extension_is_checked_only_when_the_language_lists_any():
    assert parts_tree({"notes.txt": {"role": "r"}}, Language()).problems == ()


def test_a_refused_part_still_counts_as_a_part_below_its_repeating_folder():
    assert walked({"src/<module>/": {"core/": {"name": "a b", "role": "r"}}}).problems == (
        "parts: 'src/<module>/core/' is named 'a b', which is not a part name: write name: with letters, digits, "
        "'_' and '-'",)


def test_several_problems_of_one_tree_are_all_listed():
    assert walked({"rol": 1, "core/": {"rol": 2}, "main.py": "x"}).problems == (
        "parts: unknown key 'rol': a key under parts is a folder ending in / or a file ending in .py",
        f"parts.core: unknown key 'rol': use {KNOWN}",
        "parts.main: a file is a part: write it as a map with role")


def test_an_old_flat_part_is_refused_alone_with_where_to_write_it():
    tree = walked({"domain": {"path": "modules/<module>/domain", "role": "r"}, "core/": {"rol": 1},
                   "kernel-logic": {"path": "kernel/logic", "role": "r"}, "main": {"path": "__main__.py", "role": "r"},
                   "x": {"path": 3, "role": "r"}})
    assert (tree.parts, tree.folders, tree.problems) == ((), (), ())
    assert tree.old == (
        "parts.domain: unknown key 'path': moved in 0.3.0: write the part as the folder domain/: under the folder it "
        f"lies in (modules/<module>/); use {KNOWN}",
        "parts.kernel-logic: unknown key 'path': moved in 0.3.0: write the part as the folder logic/: with name: "
        f"kernel-logic, under the folder it lies in (kernel/); use {KNOWN}",
        "parts.main: unknown key 'path': moved in 0.3.0: write the part as the file __main__.py: with name: main, at "
        f"the top of parts; use {KNOWN}",
        f"parts.x: unknown key 'path': moved in 0.3.0: write the part as a folder ending in /; use {KNOWN}")
