"""What the bundled profiles and xarch's own find by `holds` stays what they found when `holds` was one word: for each
part, the rule its kinds expand to is, as a check, the rule of the word it wrote, the sentence of a part of functions
aside, which now says the three kinds it lists; the names and built-by rules read the classes they read, keyed by the
nested keys; and immutable, now under records, reads the records of a part of functions alone."""
import json

import pytest
from typer.testing import CliRunner

from xarch.bootstrap.app import app

runner = CliRunner()
CLASSES = ('  holds-{part}:\n    read: function\n    in: {{part: {part}, where: [not package-file]}}\n'
           '    keep: [top-level, public]\n    may_not: exist\n    mode: list\n'
           '    message: "{{name}} is a function at the top level, but {{where}} holds classes ({{key}})"\n'
           '    fix: "make {{name}} a method of the class whose rule it is, or move it to {{parts_holding_functions}}"\n')
"""The rule of `holds: classes`, as a check."""
FUNCTIONS = ('  holds-{part}:\n    read: class\n    in: {{part: {part}, where: [not package-file]}}\n    may_not: exist\n'
             '    except: [exception, record]\n    mode: list\n'
             '    message: "{{name}} is a class, but {{where}} holds functions, records and exceptions ({{key}})"\n'
             '    fix: "move {{name}} to {{parts_holding_classes}}, or make what it does functions"\n')
"""The rule of `holds: functions`, as a check, but for its sentence, which says the three kinds."""
NAMES = ('  names-{part}:\n    read: class\n    in: {{part: {part}}}\n    keep: [public]\n'
         '    may_only: {{name: ["{pattern}"]}}\n'
         '    message: "{{name}} does not match {{targets}}, as every class of {{where}} must ({{key}})"\n'
         '    fix: "rename {{name}} to match {{targets}}, or move it to the part whose kind of class it is"\n')
BUILT_BY = ('checks:\n  built-by:\n    read: construction\n    may_not: {part: [services, controller, adapters]}\n'
            '    except: [{target-allows-under: built_by}]\n'
            '    message: "{where} builds {name}, a class of {target_part}, which only {built_by} may build '
            '(parts.{target_part_name}.holds.classes.built_by)"\n'
            '    fix: "take {name} as a parameter of the constructor, and build it in {built_by}"\n')
IMMUTABLE = ('  immutable-{part}:\n    read: class\n    in: {{part: {part}, where: [not package-file]}}\n'
             '    keep: [record]\n    may_not: exist\n    except: [exception, immutable]\n    mode: list\n'
             '    message: "{{name}} is a record that is not immutable, but every record of {{where}} is one ({{key}})"\n'
             "    fix: \"make {{name}} an immutable record (the {{language}} data file's `immutable` says how), or move "
             'it to {{parts_holding_classes}}"\n')
BUNDLED = "domain C logic F ports C services C controller C adapters C kernel-logic F"
PARTS = {"cli": BUNDLED, "web": BUNDLED,
         "architecture.yaml": "domain C logic F ports C services C controller C adapters C reports F profile-values C "
                              "kernel-logic F kernel C"}
"""Each part a profile writes `holds` for, in its order, with the one word it wrote: C classes, F functions."""


def checks(key: str, profile: str) -> str:
    found = json.loads(runner.invoke(app, ["profile", "explain", key, "--rule", "--profile", profile, "--format",
                                           "json"]).output)
    return found["checks"]


def written(template: str, parts: list[str], **fields: str) -> str:
    return "checks:\n" + "".join(template.format(part=part, **fields) for part in parts)


@pytest.mark.parametrize("profile", list(PARTS))
def test_each_part_s_holds_is_the_rule_of_the_word_it_wrote(profile):
    words = PARTS[profile].split()
    assert checks("parts.holds", profile) == "checks:\n" + "".join(
        (CLASSES if kind == "C" else FUNCTIONS).format(part=part) for part, kind in zip(words[::2], words[1::2]))


@pytest.mark.parametrize("profile", list(PARTS))
def test_the_names_and_built_by_rules_read_the_classes_they_read_keyed_by_the_nested_keys(profile):
    assert checks("parts.holds.classes.names", profile) == "checks:\n" + NAMES.format(
        part="services", pattern="*Service") + NAMES.format(part="controller", pattern="*Controller")
    assert checks("parts.holds.classes.built_by", profile) == BUILT_BY


@pytest.mark.parametrize("profile", list(PARTS))
def test_immutable_reads_the_records_of_each_part_of_functions(profile):
    words = PARTS[profile].split()
    assert checks("parts.holds.records.immutable", profile) == written(
        IMMUTABLE, [part for part, kind in zip(words[::2], words[1::2]) if kind == "F"])
