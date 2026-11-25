"""What a part, or a tier, of a bundled profile or of xarch's own may import, must import and may import from outside
stays what it was before the import keys moved into `imports` groups: `where` says the same of a file of every part of
xarch's own profile and of a test of each of its tiers, and the rules the keys expand to are, as checks, the same text
for each profile but for the key; every list of parts under imports of each is written in references, which no other
key is; and each, written in the old forms, is refused with one problem per entry, naming the reference it held."""
import hashlib
import json
import re
from pathlib import Path

import pytest
import yaml
from typer.testing import CliRunner

from xarch.bootstrap.app import app

runner = CliRunner()
ROOT = Path(__file__).parents[2]
KEYS = {"may": "parts.imports.may", "must": "parts.imports.must", "libraries": "parts.imports.libraries"}
"""The address `profile explain` is asked for each key of the group."""
PATHS = {"domain": "xarch/modules/spec/domain/x.py", "logic": "xarch/modules/spec/application/logic/x.py",
         "ports": "xarch/modules/spec/application/ports/x.py",
         "services": "xarch/modules/spec/application/services/x.py",
         "controller": "xarch/modules/spec/application/controller.py", "adapters": "xarch/modules/spec/adapters/x.py",
         "platform": "xarch/platform/x.py", "cli": "xarch/cli/x.py", "reports": "xarch/cli/reports/x.py",
         "main": "xarch/__main__.py", "bootstrap": "xarch/bootstrap/x.py",
         "contract": "xarch/modules/spec/contract/x.py", "profile-values": "xarch/profile_values/x.py",
         "kernel-logic": "xarch/kernel/logic/x.py", "kernel": "xarch/kernel/x.py"}
"""One path of each part of xarch's own profile."""
WHERE = {
    "domain": ("its own module's `domain/`, `kernel/`, `kernel/logic/`, `profile_values/`", []),
    "logic": ("its own module's `application/logic/` and `domain/`, `kernel/`, `kernel/logic/`, `profile_values/`", []),
    "ports": ("its own module's `application/ports/` and `domain/`, `kernel/`, `kernel/logic/`, `profile_values/`", []),
    "services": ("its own module's `application/services/`, `application/logic/`, `domain/`, `application/ports/` and "
                 "`contract/`, `kernel/`, `kernel/logic/`, `profile_values/`", []),
    "controller": ("its own module's `application/controller.py`, `application/services/`, `contract/` and "
                   "`domain/errors`, `kernel/`, `kernel/logic/`, `profile_values/`", []),
    "adapters": ("its own module's `adapters/`, `application/ports/` and `domain/`, `kernel/`, `kernel/logic/`, "
                 "`profile_values/`, `platform/`, any module's `contract/`", ["ast", "tokenize"]),
    "platform": ("`platform/`, `kernel/`, `kernel/logic/`", ["yaml"]),
    "cli": ("`cli/`, `cli/reports/`, any module's `application/controller.py` and `contract/`, `kernel/`, "
            "`kernel/logic/`", ["typer"]),
    "reports": ("`cli/reports/`, any module's `contract/`, `kernel/`, `kernel/logic/`", []),
    "main": ("`__main__.py`, `bootstrap/`", []),
    "bootstrap": ("everything", []),
    "contract": ("its own module's `contract/`, `domain/values:*Id` and `domain/published`, `kernel/`, `kernel/logic/`, "
                 "`profile_values/`", []),
    "profile-values": ("`profile_values/`, `kernel/`", []),
    "kernel-logic": ("`kernel/logic/`, `kernel/`, `profile_values/`", []),
    "kernel": ("`kernel/`", []),
}
"""What `where` said of each part before the change: may_import_text and libraries."""
RULES = {
    ("cli", "may"): (12, "d1f8b82a5aad14d4"), ("cli", "must"): (1, "cb8bbbfa024c046c"),
    ("cli", "libraries"): (24, "ae1fba4a77503d1a"),
    ("web", "may"): (12, "f3ce8e2f0861c5a2"), ("web", "must"): (1, "cb8bbbfa024c046c"),
    ("web", "libraries"): (24, "058402903c045a47"),
    ("architecture.yaml", "may"): (15, "8d51891e5aa618dc"), ("architecture.yaml", "must"): (1, "cb8bbbfa024c046c"),
    ("architecture.yaml", "libraries"): (30, "27ee07b82ce0c6a6"),
}
"""For each profile and key of the group: how many rules it expands to, and the first 16 hex digits of the SHA-256 of
their checks text before the change. The rules come in the order of the parts, which became the folder tree's reading
order in 0.3.0 (`contract` after `adapters`, `kernel` before `kernel-logic`): the lines of `may` and `libraries` are the
same as before, and only their order, so only their digests, moved. In 0.3.0 the places of `must` are written as
references (`parts.<part>`), which moved only that digest. The rules of `may` then gained a `per_line` line in each
saying (one finding per import line), and nothing else: with those lines left out, each digest of `may` is the
one it was before."""
TIER_KEYS = {"types_only": "tiers.imports.types_only", "must": "tiers.imports.must",
             "also": "tiers.imports.also", "tiers": "tiers"}
"""The address `profile explain` is asked for each key of a tier's group that rules are keyed by, and for `tiers`,
whose rule a tier's `also` keys too."""
TIER_RULES = {
    ("cli", "types_only"): (1, "29bdb75af0440d40"), ("cli", "must"): (0, "e3b0c44298fc1c14"),
    ("cli", "also"): (0, "e3b0c44298fc1c14"), ("cli", "tiers"): (3, "07ebde882b66c963"),
    ("web", "types_only"): (1, "29bdb75af0440d40"), ("web", "must"): (0, "e3b0c44298fc1c14"),
    ("web", "also"): (0, "e3b0c44298fc1c14"), ("web", "tiers"): (3, "07ebde882b66c963"),
    ("architecture.yaml", "types_only"): (2, "329ba93378533550"), ("architecture.yaml", "must"): (2, "0083c4a5a67770c5"),
    ("architecture.yaml", "also"): (1, "297bcd04b21ab4d8"), ("architecture.yaml", "tiers"): (3, "07ebde882b66c963"),
}
"""For each profile and key of a tier: how many rules it expands to, and the first 16 hex digits of the SHA-256 of
their checks text before the change."""
TESTS = {"unit": "tests/modules/spec/domain/test_x.py", "integration": "tests/modules/spec/application/test_x.py",
         "wired": "tests/bootstrap/test_x.py", "guard": "tests/architecture/test_x.py",
         "wired, of cli": "tests/cli/test_x.py"}
"""A test of each tier of xarch's own profile, the wired one twice: once below bootstrap/, once mirroring cli/."""
TYPES = ["domain", "logic", "ports", "services", "controller", "adapters", "platform"]
TIER_WHERE = {
    "unit": ("unit", "its own module's `domain/`, `kernel/`, `kernel/logic/`, `profile_values/`", [], "5e0f441d9899ecd1"),
    "integration": ("integration", "its own module's `application/controller.py`, `application/services/`, `contract/` "
                    "and `domain/errors`, `kernel/`, `kernel/logic/`, `profile_values/`, its own module's "
                    "`domain/values`, `domain/profile`, `domain/parsed` and `domain/outcomes`", [], "ae600445e22537b0"),
    "wired": ("wired", "everything", TYPES, "2a05a9860791084b"),
    "guard": ("guard", "everything", TYPES, "4f53cda18c2baa0c"),
    "wired, of cli": ("wired", "`cli/`, `cli/reports/`, any module's `application/controller.py` and `contract/`, "
                      "`kernel/`, `kernel/logic/`", TYPES, "46205533adc1e5b6"),
}
"""What `where` said of each test before the change: its tier, may_import_text, test.types_only, and the first 16 hex
digits of the SHA-256 of its may_import list."""


def explained(address: str, profile: str) -> tuple[int, str]:
    found = json.loads(runner.invoke(app, ["profile", "explain", address, "--rule", "--profile", profile,
                                           "--format", "json"]).output)
    text = found["checks"].replace(".imports.libraries)", ".libraries)")
    return found["rules"], hashlib.sha256(text.encode()).hexdigest()[:16]


@pytest.mark.parametrize("part", list(PATHS))
def test_where_says_what_each_part_of_xarch_may_import_as_before(part):
    found = json.loads(runner.invoke(app, ["where", PATHS[part], "--format", "json"]).output)
    assert found["part"]["name"] == part
    assert (found["may_import_text"], found["libraries"]) == WHERE[part]


@pytest.mark.parametrize("profile, key", list(RULES))
def test_each_key_of_the_group_expands_to_the_rules_of_before(profile, key):
    assert explained(KEYS[key], profile) == RULES[profile, key]


@pytest.mark.parametrize("profile", ["cli", "web", "architecture.yaml"])
def test_the_places_a_part_must_import_are_written_as_references(profile):
    found = json.loads(runner.invoke(app, ["profile", "explain", "parts.imports.must", "--rule", "--profile", profile,
                                           "--format", "json"]).output)
    assert "targets: [{place: [parts.platform, parts.contract]}, outside]" in found["checks"]
    assert "@any" not in found["checks"]


@pytest.mark.parametrize("test", list(TESTS))
def test_where_says_what_a_test_of_each_tier_of_xarch_may_import_as_before(test):
    found = json.loads(runner.invoke(app, ["where", TESTS[test], "--format", "json"]).output)
    reached = hashlib.sha256(json.dumps(found["may_import"], sort_keys=True).encode()).hexdigest()[:16]
    assert (found["tier"]["name"], found["may_import_text"], found["test"]["types_only"], reached) == TIER_WHERE[test]


@pytest.mark.parametrize("profile, key", list(TIER_RULES))
def test_each_key_of_a_tier_s_group_expands_to_the_rules_of_before(profile, key):
    assert explained(TIER_KEYS[key], profile) == TIER_RULES[profile, key]


SHIPPED = {"cli": ROOT / "xarch" / "architectures" / "cli.yaml", "web": ROOT / "xarch" / "architectures" / "web.yaml",
           "architecture.yaml": ROOT / "architecture.yaml"}
"""Each profile the rules above are asked of, by the name they are asked for, as a file."""
LISTS = ("may", "must", "also", "types_only")
"""The lists of parts under an `imports` group, a part's or a tier's, which take references."""


def nodes(node, path=()):
    """Every value of a document, each with the keys and indexes that lead to it."""
    yield path, node
    children = node.items() if isinstance(node, dict) else enumerate(node) if isinstance(node, list) else ()
    for key, value in children:
        yield from nodes(value, (*path, key))


def entries(document) -> list:
    """Every entry of a list of parts under an `imports` group, a marked one by the reference it marks."""
    return [next(iter(entry)) if isinstance(entry, dict) else entry for path, value in nodes(document)
            if path[-2:-1] == ("imports",) and path[-1] in LISTS and isinstance(value, list) for entry in value]


def texts(document) -> list[str]:
    """Every text a document writes, as a value or as a key."""
    return [text for _, value in nodes(document)
            for text in (value if isinstance(value, dict) else [value]) if isinstance(text, str)]


@pytest.mark.parametrize("profile", list(SHIPPED))
def test_every_list_of_parts_under_imports_is_written_in_references_and_no_other_key_is(profile):
    document = yaml.safe_load(SHIPPED[profile].read_text(encoding="utf-8"))
    listed = entries(document)
    assert listed
    assert [entry for entry in listed if entry != "everything" and "." not in re.split("[/:]", entry, maxsplit=1)[0]] == []
    assert sum(entry.startswith("parts.") for entry in listed) == sum(text.startswith("parts.") for text in texts(document))


REPEATING = re.compile(r"<[^>]+>")
"""A step of a folder key that repeats, `<word>`."""


def repeating_parts(node, repeats=False, found=None) -> dict[str, bool]:
    """Each part of a `parts` tree, by its name (its `name`, else its last step before the first dot), and whether its
    path holds a repeating step."""
    found = {} if found is None else found
    for key, value in node.items() if isinstance(node, dict) else ():
        if not isinstance(key, str) or not ("/" in key or "." in key):
            continue
        steps = key.rstrip("/").split("/")
        inside = repeats or any(REPEATING.fullmatch(step) for step in steps)
        if isinstance(value, dict) and any(isinstance(k, str) and "/" not in k and "." not in k for k in value):
            found[value.get("name") or steps[-1].split(".")[0]] = inside
        repeating_parts(value, inside, found)
    return found


def old_form(reference: str, whole: bool, repeats: dict[str, bool]) -> str:
    """The form a reference was written in before 0.3.0: `parts.X` as `X@any` when X repeats, else `X`; `<word>.X` as
    `X`; whole, for a tier's must and types_only, the part's name alone."""
    prefix, _, rest = reference.partition(".")
    name = re.split("[/:]", rest, maxsplit=1)[0]
    if whole:
        return name
    return f"{name}@any{rest[len(name):]}" if prefix == "parts" and repeats[name] else rest


def inverted(document) -> list[str]:
    """Writes every entry of a list of parts under an `imports` group in its old form, in place; the references it
    held, in the order of the document."""
    repeats = repeating_parts(document["parts"])
    found: list[str] = []
    for path, value in list(nodes(document)):
        if path[-2:-1] != ("imports",) or path[-1] not in LISTS or not isinstance(value, list):
            continue
        whole = path[0] == "tiers" and path[-1] in ("must", "types_only")
        for i, entry in enumerate(value):
            marked = isinstance(entry, dict)
            reference = next(iter(entry)) if marked else entry
            if reference == "everything":
                continue
            found.append(reference)
            old = old_form(reference, whole, repeats)
            value[i] = {old: entry[reference]} if marked else old
    return found


def written_instead(problem: str) -> str:
    """The first reference a problem of a removed form says to write; any other problem as it is said."""
    _, removed, instead = problem.partition("was removed in 0.3.0: write ")
    return instead.split(" (")[0] if removed else problem


def beside(source: Path, folder: Path, text: str) -> Path:
    """The file text as if it sat where source does: folder holds a link to every other file next to source."""
    for item in source.parent.iterdir():
        if item.name != source.name:
            (folder / item.name).symlink_to(item)
    written = folder / source.name
    written.write_text(text, encoding="utf-8")
    return written


@pytest.mark.parametrize("profile", list(SHIPPED))
def test_each_profile_written_in_the_old_forms_is_refused_one_problem_per_entry_each_naming_its_reference(profile,
                                                                                                         tmp_path):
    document = yaml.safe_load(SHIPPED[profile].read_text(encoding="utf-8"))
    references = inverted(document)
    written = beside(SHIPPED[profile], tmp_path, yaml.safe_dump(document, sort_keys=False))
    result = runner.invoke(app, ["profile", "check", str(written)])
    said = [line.strip() for line in result.output.splitlines() if line.strip().startswith(f"{written}:")]
    assert result.exit_code != 0
    assert references
    assert sorted(written_instead(problem) for problem in said) == sorted(references)


def test_an_inline_profile_with_several_old_forms_says_one_problem_per_line(tmp_path):
    written = tmp_path / "tiny.yaml"
    written.write_text("name: tiny\nparts:\n  modules/<module>/:\n    domain/: {role: the rules}\n    services/:\n"
                       "      role: the use cases\n      imports:\n        may:\n          - domain\n"
                       "          - kernel@any\n          - domain@own\n  kernel/: {role: shared code}\n",
                       encoding="utf-8")
    result = runner.invoke(app, ["profile", "check", str(written)])
    assert result.exit_code != 0
    assert [line.strip() for line in result.output.splitlines() if line.strip().startswith(f"{written}:")] == [
        f"{written}: parts.services.imports.may: 'domain': a bare part name was removed in 0.3.0: write module.domain "
        "(this module's) or parts.domain (any module's)",
        f"{written}: parts.services.imports.may: 'kernel@any': @any was removed in 0.3.0: write parts.kernel",
        f"{written}: parts.services.imports.may: 'domain@own': @own was removed in 0.3.0: write module.domain"]
