"""How a profile writes a target, read against the parts by their paths, the part that writes it and the profile's
repeating folders: the old forms (a bare name, @any, /<path>, :<pattern>) as before, and the references parts.<part>
and <word>.<part>, each read or refused with its one problem."""
import pytest

from xarch.kernel.logic.targets import target
from xarch.profile_values.placement import Repeat, Target

PARTS = {"domain": ("modules", "*", "domain"), "services": ("modules", "*", "services"), "kernel": ("kernel",),
         "kernel-logic": ("kernel", "logic"), "store": ("units", "*", "store"), "cli": ("cli",)}
REPEATS = (Repeat("module", ("modules",)), Repeat("unit", ("units",)))
SERVICES = ("services", PARTS["services"])
DOMAIN = ("domain", PARTS["domain"])
CLI = ("cli", PARTS["cli"])
KERNEL = ("kernel", PARTS["kernel"])
LEDGER = ("ledger", ("units", "*", "ledger"))
NOT_A_REFERENCE = "is not a reference: write parts.<part> or <word>.<part>, optionally followed by /<path> and :<pattern>"


def read(written, owner, parts=PARTS, repeats=REPEATS, patterns=True, mirrored=False, place=False,
         alone="a tier's folder", declared=None):
    problems: list[str] = []
    found = target(written, owner, parts, parts if declared is None else declared, "at", problems, patterns, mirrored,
                   alone=alone, repeats=repeats, place=place)
    return found, problems


READ = [
    pytest.param("domain", SERVICES, Target("domain", "own"), id="a bare name in the importer's repeating folder is its own instance"),
    pytest.param("domain@any/values", SERVICES, Target("domain", "any", ("values",)), id="any instance, and a path below"),
    pytest.param("kernel:*Id", SERVICES, Target("kernel", "none", (), "*Id"), id="a part outside, narrowed by a name pattern"),
    pytest.param("domain@any", None, Target("domain", "any"), id="a scope of no part reaches an instance only by @any"),
]


@pytest.mark.parametrize("written, owner, found", READ)
def test_a_target_is_read_from_its_written_form(written, owner, found):
    problems: list[str] = []
    assert (target(written, owner, PARTS, PARTS, "at", problems, patterns=True, alone="a tier's folder",
                   repeats=REPEATS), problems) == (found, [])


@pytest.mark.parametrize("written, owner, problem", [
    pytest.param("nowhere", SERVICES, "at: 'nowhere' names no part 'nowhere'", id="a part the profile has not"),
    pytest.param("domain", None, "at: 'domain' lies in the repeating folder, which a tier's folder is not in: say "
                                 "domain@any", id="an instance asked for from outside the repeating folder"),
    pytest.param("services", SERVICES, "at: 'services' is implied: a part may always import itself, its own instance "
                                       "of the repeating folder; remove it (services@any, another instance's too, stays "
                                       "allowed)", id="the part itself"),
    pytest.param("kernel:*Id", SERVICES, "at: 'kernel:*Id' has a name pattern, which this key does not take: drop "
                                         "':*Id'", id="a name pattern where none is allowed"),
    pytest.param("everything", SERVICES, "at: 'everything' names no part 'everything'",
                 id="everything is no part: the key that takes it alone says so"),
])
def test_a_target_that_is_not_one_is_none_with_its_problem(written, owner, problem):
    problems: list[str] = []
    assert (target(written, owner, PARTS, PARTS, "at", problems, alone="a tier's folder", repeats=REPEATS),
            problems) == (None, [problem])


@pytest.mark.parametrize("written, found, problem", [
    pytest.param("domain/values", Target("domain", "own", ("values",)), [],
                 id="a bare name in the repeating folder is the instance the test mirrors"),
    pytest.param("domain@any", Target("domain", "any"), [], id="any instance stays any"),
    pytest.param("kernel", Target("kernel"), [], id="a part outside the repeating folder is in no instance"),
    pytest.param("domain@own", None, ["at: 'domain@own' says what a bare name already says: write domain"],
                 id="the mirrored instance written out is refused"),
])
def test_a_target_a_test_reads_is_read_from_the_instance_it_mirrors(written, found, problem):
    problems: list[str] = []
    assert (target(written, None, PARTS, PARTS, "at", problems, mirrored=True, alone="a tier's folder", repeats=REPEATS),
            problems) == (found, problem)


@pytest.mark.parametrize("pattern", [
    pytest.param("*Id", id="letters and a star"),
    pytest.param("$*", id="a mark another language starts its names with"),
    pytest.param("%Doc*", id="another such mark"),
    pytest.param("Détail*", id="a letter that is not ascii"),
])
def test_a_name_pattern_is_any_text_but_whitespace_and_the_separators_of_a_target(pattern):
    assert target(f"kernel:{pattern}", SERVICES, PARTS, PARTS, "at", [], patterns=True, alone="a tier's folder",
                  repeats=REPEATS) == Target("kernel", "none", (), pattern)


@pytest.mark.parametrize("written", ["kernel:a b", "kernel:a@b", "kernel:a:b"])
def test_a_name_pattern_with_whitespace_or_a_separator_is_refused(written):
    problems: list[str] = []
    assert (target(written, SERVICES, PARTS, PARTS, "at", problems, patterns=True, alone="a tier's folder",
                   repeats=REPEATS), problems) == (
        None, [f"at: {written!r} has a name pattern that is not one: write it with no space, `@`, `/` or `:`, `*` "
               "standing for any text"])


def test_what_names_no_part_is_named_in_the_callers_words():
    problems: list[str] = []
    target("domain", None, PARTS, PARTS, "at", problems, alone="a check that names no part", repeats=REPEATS)
    assert problems == ["at: 'domain' lies in the repeating folder, which a check that names no part is not in: say "
                        "domain@any"]


@pytest.mark.parametrize("written, owner, found", [
    pytest.param("parts.domain", CLI, Target("domain", "any"), id="parts, a part that repeats, is every instance"),
    pytest.param("parts.kernel", SERVICES, Target("kernel", "none"), id="parts, a part that does not repeat"),
    pytest.param("module.domain", SERVICES, Target("domain", "own"), id="a word, the importer's own instance"),
    pytest.param("module.services/schema", DOMAIN, Target("services", "own", ("schema",)), id="a path below"),
    pytest.param("parts.domain:*Id", SERVICES, Target("domain", "any", (), "*Id"), id="a name pattern"),
    pytest.param("parts.domain/values:*Id", CLI, Target("domain", "any", ("values",), "*Id"),
                 id="parts, a path and a pattern"),
    pytest.param("module.domain/values:*Id", SERVICES, Target("domain", "own", ("values",), "*Id"),
                 id="a word, a path and a pattern"),
    pytest.param("parts.domain/published", CLI, Target("domain", "any", ("published",)), id="parts, a path"),
    pytest.param("unit.store", LEDGER, Target("store", "own"), id="a second word"),
    pytest.param("parts.kernel-logic", SERVICES, Target("kernel-logic", "none"), id="a name with a dash"),
    pytest.param("parts.services", SERVICES, Target("services", "any"), id="the part itself in every instance"),
    pytest.param("parts.domain", None, Target("domain", "any"), id="a tier's folder, every instance"),
])
def test_a_reference_is_read(written, owner, found):
    assert read(written, owner) == (found, [])


@pytest.mark.parametrize("written, owner, patterns, problem", [
    pytest.param("module.kernel", SERVICES, True,
                 "at: 'module.kernel': part 'kernel' lies in no <module> folder: write parts.kernel",
                 id="a word for a part in no repeating folder"),
    pytest.param("module.domain", CLI, True,
                 "at: 'module.domain': part 'cli' lies in no <module> folder, so it has no own module: write "
                 "parts.domain", id="a word from an importer in no repeating folder"),
    pytest.param("module.domain", None, True,
                 "at: 'module.domain': a tier's folder lies in no <module> folder, so it has no own module: write "
                 "parts.domain", id="a word from what names no part"),
    pytest.param("module.store", SERVICES, True,
                 "at: 'module.store': part 'store' lies in the <unit> folder, not <module>: write parts.store",
                 id="a word for a part in another word's folder"),
    pytest.param("unit.store", DOMAIN, True,
                 "at: 'unit.store': part 'domain' lies in no <unit> folder: write parts.store",
                 id="a word from an importer in another word's folder"),
    pytest.param("orders.services", DOMAIN, True,
                 "at: 'orders.services': 'orders' is neither parts nor a word of this profile (module, unit): a "
                 "profile names no instance; write module.services or parts.services", id="an instance named"),
    pytest.param("<module>.services", DOMAIN, True,
                 "at: '<module>.services': write the word without brackets: module.services", id="the word in brackets"),
    pytest.param("parts.nope", SERVICES, True, "at: 'parts.nope' names no part 'nope'", id="a part the profile has not"),
    pytest.param("parts.", SERVICES, True, f"at: 'parts.' {NOT_A_REFERENCE}", id="no part"),
    pytest.param(".domain", SERVICES, True, f"at: '.domain' {NOT_A_REFERENCE}", id="no prefix"),
    pytest.param("parts..x", SERVICES, True, f"at: 'parts..x' {NOT_A_REFERENCE}", id="a dot in the part"),
    pytest.param("parts.domain@any", SERVICES, True, f"at: 'parts.domain@any' {NOT_A_REFERENCE}", id="an @ scope"),
    pytest.param("module.services/schema@any", DOMAIN, True, f"at: 'module.services/schema@any' {NOT_A_REFERENCE}",
                 id="an @ in the path"),
    pytest.param("module.services", SERVICES, True,
                 "at: 'module.services' is implied: a part may always import itself, its own instance of the repeating "
                 "folder; remove it (parts.services, another instance's too, stays allowed)", id="the own instance of itself"),
    pytest.param("parts.kernel", KERNEL, True, "at: 'parts.kernel' is implied: a part may always import itself; remove it",
                 id="itself, outside a repeating folder"),
    pytest.param("parts.kernel:*Id", SERVICES, False,
                 "at: 'parts.kernel:*Id' has a name pattern, which this key does not take: drop ':*Id'",
                 id="a pattern where the key takes none"),
    pytest.param("module.services/../x", DOMAIN, True, "at: 'module.services/../x' has an invalid path after the part",
                 id="a path that is not one"),
    pytest.param("parts.kernel:a@b", SERVICES, True,
                 "at: 'parts.kernel:a@b' has a name pattern that is not one: write it with no space, `@`, `/` or `:`, "
                 "`*` standing for any text", id="an @ inside the pattern"),
])
def test_a_reference_written_wrong_is_none_with_its_one_problem(written, owner, patterns, problem):
    assert read(written, owner, patterns=patterns) == (None, [problem])


@pytest.mark.parametrize("written, found, problem", [
    pytest.param("module.domain/values", Target("domain", "own", ("values",)), [], id="a word is the mirrored instance"),
    pytest.param("parts.domain", Target("domain", "any"), [], id="parts is every instance"),
    pytest.param("parts.kernel", Target("kernel", "none"), [], id="parts outside a repeating folder"),
    pytest.param("module.kernel", None, ["at: 'module.kernel': part 'kernel' lies in no <module> folder: write "
                                         "parts.kernel"], id="a word for a part in no repeating folder"),
])
def test_a_test_reads_a_reference_from_the_instance_it_mirrors(written, found, problem):
    assert read(written, None, mirrored=True) == (found, problem)


def test_a_check_s_place_whose_prefix_is_no_word_is_told_a_dotted_name_goes_under_path():
    no_word = ("at: 'os.environ': 'os' is neither parts nor a word of this profile (module, unit): a profile names no "
               "instance; write parts.<part> or <word>.<part>")
    assert read("os.environ", SERVICES, place=True, alone="a check that names no part") == (
        None, [f"{no_word}; a dotted name of code goes under path"])
    assert read("os.environ", SERVICES) == (None, [no_word])
    assert read("module.domain", None, place=True, alone="a check that names no part") == (
        None, ["at: 'module.domain': a check that names no part lies in no <module> folder, so it has no own module: "
               "write parts.domain"])


def test_a_part_named_everything_is_named_parts_everything():
    assert read("parts.everything", None, parts={"everything": ("everything",)}) == (Target("everything", "none"), [])


def test_the_word_comes_from_the_profile_s_repeats_never_from_the_code():
    parts = {"core": ("packages", "*", "core"), "api": ("packages", "*", "api")}
    repeats = (Repeat("pkg", ("packages",)),)
    api = ("api", parts["api"])
    assert read("pkg.core", api, parts=parts, repeats=repeats) == (Target("core", "own"), [])
    assert read("module.core", api, parts=parts, repeats=repeats) == (
        None, ["at: 'module.core': 'module' is neither parts nor a word of this profile (pkg): a profile names no "
               "instance; write pkg.core or parts.core"])


def test_a_profile_with_no_repeating_folder_has_no_word():
    parts = {"kernel": ("kernel",), "cli": ("cli",)}
    assert read("orders.kernel", ("cli", ("cli",)), parts=parts, repeats=()) == (
        None, ["at: 'orders.kernel': 'orders' is neither parts nor a word of this profile, which has none: a profile "
               "names no instance; write parts.kernel"])
    assert read("parts.kernel", ("cli", ("cli",)), parts=parts, repeats=()) == (Target("kernel", "none"), [])


def test_a_part_named_parts_is_named_parts_parts():
    parts = {"parts": ("parts",), "cli": ("cli",)}
    assert read("parts.parts", ("cli", ("cli",)), parts=parts, repeats=()) == (Target("parts", "none"), [])


def test_a_reference_to_a_part_declared_but_not_placed_is_none_with_no_problem():
    assert read("parts.ghost", SERVICES, declared={*PARTS, "ghost"}) == (None, [])


@pytest.mark.parametrize("written, found, problem", [
    pytest.param("kernel/x.py", Target("kernel", "none", ("x.py",)), [], id="a dot in the path"),
    pytest.param("kernel:a.b", Target("kernel", "none", (), "a.b"), [], id="a dot in the pattern"),
    pytest.param(3, None, ["at: 3 is not a target: use <part>, <part>@any, optionally followed by /<path>"],
                 id="no text"),
    pytest.param("", None, ["at: '' is not a target: use <part>, <part>@any, optionally followed by /<path>"],
                 id="empty text"),
])
def test_a_value_whose_head_holds_no_dot_is_read_in_the_old_forms(written, found, problem):
    assert read(written, SERVICES) == (found, problem)
