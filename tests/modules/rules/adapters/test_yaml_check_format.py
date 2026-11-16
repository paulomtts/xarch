"""The checks of a profile written as the YAML of its `checks`: each slot as the format writes it, a default left
out, a word quoted only where the format would read it otherwise, the sayings but the last as cases, and the examples
when a check has any."""
import pytest

from xarch.kernel.logic.conditions import condition
from xarch.modules.rules.adapters.yaml_check_format import YamlCheckFormat
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

FORMAT = YamlCheckFormat(YamlWriter())


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
                  "cases:", "  - when: [{of-kind: use}]", '    message: "{where} reads {hit}"', '    fix: "f"',
                  "    once_per: [line]", 'message: "m"', 'fix: "f"'], id="dotted names, a method, and a case"),
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
    pytest.param(WrittenCheck(("class",), Scope(), Quantified("may_only", (WrittenTarget("part"),)), (Saying("m", "f"),)),
                 ["read: class", "may_only: {part: []}", 'message: "m"', 'fix: "f"'],
                 id="a kind of target that takes values is a map even with none"),
])
def test_a_check_is_written_slot_by_slot_as_a_profile_writes_it(check, lines):
    assert FORMAT.written({"x": check}) == "checks:\n  x:\n" + "".join(f"    {line}\n" for line in lines)


def test_checks_are_written_each_under_its_id_with_their_examples_when_they_have_any():
    check = WrittenCheck(("comment",), Scope(), Quantified("may_not", (WrittenTarget("exist"),)), (Saying('a "comment"', "f"),))
    shown = WrittenCheck(("comment",), Scope(), Quantified("may_not", (WrittenTarget("exist"),)), (Saying("m", "f"),),
                         flagged=(("docs/notes.py", "# TODO\n"),), clean=(("docs/notes.py", "# done\n"),))
    assert FORMAT.written({"one": check, "two": shown}) == (
        'checks:\n  one:\n    read: comment\n    may_not: exist\n    message: "a \\"comment\\""\n    fix: "f"\n'
        '  two:\n    read: comment\n    may_not: exist\n    message: "m"\n    fix: "f"\n    examples:\n'
        '      flagged: {docs/notes.py: "# TODO\\n"}\n      clean: {docs/notes.py: "# done\\n"}\n')
