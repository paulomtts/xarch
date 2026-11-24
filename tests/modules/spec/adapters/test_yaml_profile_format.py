"""Spec's ProfileFormat as YAML: the content of a profile file is the document as YAML, in UTF-8, and a copy's text is
named for the copy and based on what it was copied from. The checks of a profile are written as the YAML of its
`checks`: each slot as the format writes it, a default left out, a word quoted only where the format would read it
otherwise, the sayings but the last as cases, a target as it was written (its kind alone, or a map of its values), and
the examples when a check has any."""
import json
from pathlib import Path

import pytest
import yaml

from xarch.kernel.logic.conditions import condition
from xarch.modules.spec.adapters.yaml_profile_format import YamlProfileFormat
from xarch.platform.yaml_writer import YamlWriter
from xarch.profile_values.checks import (
    STRUCTURE,
    TESTS,
    Condition,
    Quantified,
    Saying,
    Scope,
    WrittenCheck,
    WrittenTarget,
)

FORMAT = YamlProfileFormat(YamlWriter())
ROOT = Path(__file__).parents[4]


def test_a_profile_is_written_as_yaml_in_utf_8():
    assert YamlProfileFormat(YamlWriter()).written({"name": "cafés"}) == "name: \"cafés\"\n".encode()


ORIGINAL = "# a comment\nname: web\nlanguage: python\n\nparts:\n  name: not this one\n"


def test_the_copy_is_named_and_based_on_the_original_and_keeps_everything_else_as_written():
    assert FORMAT.renamed(ORIGINAL, "mine", "web") == (
        "# a comment\nname: mine\nbased_on: web\nlanguage: python\n\nparts:\n  name: not this one\n")


def test_a_based_on_the_original_already_had_is_replaced_not_repeated():
    text = FORMAT.renamed("name: web\nbased_on: cli\n", "mine", "web")
    assert text == "name: mine\nbased_on: web\n"


def test_a_profile_with_no_name_line_cannot_be_copied():
    assert FORMAT.renamed("parts: {}\n", "mine", "web") is None


def c(*texts: str) -> tuple[Condition, ...]:
    return tuple(condition(text) for text in texts)


@pytest.mark.parametrize("check, lines", [
    pytest.param(WrittenCheck(("class",), Scope(part="store"), Quantified("may_only", (WrittenTarget("name", ("*Store",)),)),
                              (Saying("{name} is not {targets}", "rename {name}"),), keep=c("public")),
                 ["read: class", "in: {part: store}", "keep: [public]", 'may_only: {name: ["*Store"]}',
                  'message: "{name} is not {targets}"', 'fix: "rename {name}"'], id="a check of a part"),
    pytest.param(WrittenCheck(("file",), Scope(TESTS, where=c("not tiered", "below fakes")),
                              Quantified("may_not", (WrittenTarget("exist"),)), (Saying("m", "f"),), mode="list"),
                 ["read: file", "in: {files: tests, where: [not tiered, {below: fakes}]}", "may_not: exist",
                  "mode: list", 'message: "m"', 'fix: "f"'], id="a scope of the tests, its filters and a mode"),
    pytest.param(WrittenCheck(("use", "method-call"), Scope(part=STRUCTURE),
                              Quantified("may_not", (WrittenTarget("path", ("time.time", ".absolute()")),)),
                              (Saying("{where} reads {hit}", "f", c("of-kind use"), ("line",)), Saying("m", "f"))),
                 ["read: [use, method-call]", "in: {part: structure}", 'may_not: {path: [time.time, ".absolute()"]}',
                  'message: "m"', 'fix: "f"', "cases:", "  - when: [{of-kind: use}]", '    message: "{where} reads {hit}"',
                  '    fix: "f"', "    once_per: [line]"], id="dotted names, a method, and a case"),
    pytest.param(WrittenCheck(("import", "import-into-app"), Scope(part="store"),
                              Quantified("must_reach", (WrittenTarget("place", ("core", "api@any/v1")),
                                                        WrittenTarget("outside")),
                                         ("import-into-app",), c("target-in-own-part")), (Saying("m", "f"),)),
                 ["read: [import, import-into-app]", "in: {part: store}", "must_reach:",
                  "  targets: [{place: [core, api@any/v1]}, outside]", "  through: import-into-app",
                  "  through_only: [target-in-own-part]", 'message: "m"', 'fix: "f"'], id="a reach to targets"),
    pytest.param(WrittenCheck(("class",), Scope(part="ports"),
                              Quantified("must_be_reached", (), ("names-mentioned",), (),
                                         Scope(where=c("not package-file")), ("class",), True),
                              (Saying("{name}", "f"),), keep=c("interface")),
                 ["read: class", "in: {part: ports}", "keep: [interface]", "must_be_reached:",
                  "  from: {files: app, where: [not package-file]}", "  through: names-mentioned", "  then_through: class",
                  "  by_another_file: true", 'message: "{name}"', 'fix: "f"'], id="a reach from roots"),
    pytest.param(WrittenCheck(("class",), Scope(), Quantified("may_only", (WrittenTarget("part", ()),)), (Saying("m", "f"),)),
                 ["read: class", "may_only: {part: []}", 'message: "m"', 'fix: "f"'],
                 id="a target written with an empty list of values is a map with none"),
    pytest.param(WrittenCheck(("class",), Scope(), Quantified("may_only", (WrittenTarget("part"),)), (Saying("m", "f"),)),
                 ["read: class", "may_only: part", 'message: "m"', 'fix: "f"'],
                 id="a target written alone is its kind alone"),
])
def test_a_check_is_written_slot_by_slot_as_a_profile_writes_it(check, lines):
    assert FORMAT.checks({"x": check}) == "checks:\n  x:\n" + "".join(f"    {line}\n" for line in lines)


def test_checks_are_written_each_under_its_id_with_their_examples_when_they_have_any():
    check = WrittenCheck(("comment",), Scope(), Quantified("may_not", (WrittenTarget("exist"),)), (Saying('a "comment"', "f"),))
    shown = WrittenCheck(("comment",), Scope(), Quantified("may_not", (WrittenTarget("exist"),)), (Saying("m", "f"),),
                         flagged=(("docs/notes.py", "# TODO\n"),), clean=(("docs/notes.py", "# done\n"),))
    assert FORMAT.checks({"one": check, "two": shown}) == (
        'checks:\n  one:\n    read: comment\n    may_not: exist\n    message: "a \\"comment\\""\n    fix: "f"\n'
        '  two:\n    read: comment\n    may_not: exist\n    message: "m"\n    fix: "f"\n    examples:\n'
        '      flagged: {docs/notes.py: "# TODO\\n"}\n      clean: {docs/notes.py: "# done\\n"}\n')


def parts_written(parts: dict) -> str:
    """The text written for a document of only parts, without the `parts:` line."""
    return FORMAT.written({"parts": parts}).decode().split("parts:\n", 1)[1]


def test_a_chain_of_folders_that_are_no_part_is_written_as_one_joined_key():
    assert parts_written({"modules/": {"<module>/": {"domain/": {"role": "the rules"},
                                                     "adapters/": {"role": "the repos"}}}}) == (
        "  modules/<module>/:\n"
        "    domain/:\n      role: the rules\n"
        "    adapters/:\n      role: the repos\n")


def test_a_part_s_own_keys_come_first_in_the_fixed_order_then_its_folders_and_files():
    assert parts_written({"cli/": {"reports/": {"role": "r"}, "tests": "unit", "commands/": {}, "imports": {"may": ["x"]},
                                   "role": "c", "name": "cli"}}) == (
        "  cli/:\n    name: cli\n    role: c\n    imports:\n      may: [x]\n    tests: unit\n"
        "    reports/:\n      role: r\n    commands/: {}\n")


def test_a_part_folder_with_one_folder_inside_it_is_written_nested_never_joined():
    assert parts_written({"kernel/": {"role": "k", "logic/": {"name": "kernel-logic", "role": "l"}}}) == (
        "  kernel/:\n    role: k\n    logic/:\n      name: kernel-logic\n      role: l\n")


def test_a_joined_part_key_is_split_and_written_under_its_folder():
    assert parts_written({"kernel/": {"role": "k"}, "lib/logic/": {"role": "l"}}) == (
        "  kernel/:\n    role: k\n  lib/logic/:\n    role: l\n")
    assert parts_written({"a/": {"b/": {"role": "x"}, "c.py": {"role": "z"}}}) == (
        "  a/:\n    b/:\n      role: x\n    c.py:\n      role: z\n")


@pytest.mark.parametrize("value", [None, {}], ids=["null", "an empty map"])
def test_a_folder_with_neither_note_nor_children_is_written_as_an_empty_map(value):
    assert parts_written({"web/": {"role": "w", "ui/": value}}) == "  web/:\n    role: w\n    ui/: {}\n"


def test_a_note_is_written_as_the_folder_s_string():
    assert parts_written({"web/": {"role": "w", "routes/": "one file per route group"}}) == (
        "  web/:\n    role: w\n    routes/: one file per route group\n")


def test_a_lone_folder_holding_one_file_is_joined_with_it():
    assert parts_written({"bin/": {"run.py": {"role": "starts it"}}}) == "  bin/run.py:\n    role: starts it\n"


def test_the_rest_of_the_document_is_written_as_before():
    document = {"name": "x", "parts": {"core/": {"role": "r"}}, "layers": {"a": ["core"]}}
    assert yaml.safe_load(FORMAT.written(document)) == document


@pytest.mark.parametrize("path", ["xarch/architectures/web.yaml", "xarch/architectures/cli.yaml", "architecture.yaml",
                                  "tests/bootstrap/corpora/7cc6111.yaml", "tests/bootstrap/corpora/df537ca.yaml",
                                  "tests/bootstrap/corpora/stress.yaml"])
def test_each_profile_shipped_or_archived_is_its_tree_as_the_writer_writes_it(path):
    document = yaml.safe_load((ROOT / path).read_text(encoding="utf-8"))
    written = yaml.safe_load(FORMAT.written(document))["parts"]
    assert written == document["parts"]
    assert json.dumps(written) == json.dumps(document["parts"])
    assert all(key.endswith("/") or "." in key for key in document["parts"])
