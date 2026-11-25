"""How a profile writes a target, read against the parts by their paths, the part that writes it and the profile's
repeating folders: the references parts.<part> and <word>.<part>, each read or refused with its one problem, and the
old forms (a bare name, @any, @own), each refused with the reference to write."""
import pytest

from xarch.kernel.logic.targets import outside_imports, target
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


def mirroring(*names):
    """The paths of the parts a tier tests, by name, as the reader of its tests' imports.also is given them."""
    return tuple(PARTS[name] for name in names)


def read(written, owner, parts=PARTS, repeats=REPEATS, patterns=True, mirrored=None, place=False,
         alone="a tier's folder", declared=None):
    problems: list[str] = []
    found = target(written, owner, parts, parts if declared is None else declared, "at", problems, patterns, mirrored,
                   alone=alone, repeats=repeats, place=place)
    return found, problems


REMOVED = "was removed in 0.3.0: write"
BARE = "a bare part name was removed in 0.3.0: write"
OWN_MODULE = "module.domain (this module's) or parts.domain (any module's)"


@pytest.mark.parametrize("written, owner, options, problem", [
    pytest.param("domain@any", SERVICES, {}, f"at: 'domain@any': @any {REMOVED} parts.domain", id="@any"),
    pytest.param("domain@any/published", CLI, {}, f"at: 'domain@any/published': @any {REMOVED} parts.domain/published",
                 id="@any and a path"),
    pytest.param("domain/published@any", CLI, {}, f"at: 'domain/published@any': @any {REMOVED} parts.domain/published",
                 id="@any after the path"),
    pytest.param("domain@any:*Id", SERVICES, {}, f"at: 'domain@any:*Id': @any {REMOVED} parts.domain:*Id",
                 id="@any and a pattern"),
    pytest.param("domain@any", None, {}, f"at: 'domain@any': @any {REMOVED} parts.domain", id="@any from a tier"),
    pytest.param("domain@own", SERVICES, {}, f"at: 'domain@own': @own {REMOVED} module.domain",
                 id="@own where the word is accepted"),
    pytest.param("store@own", LEDGER, {}, f"at: 'store@own': @own {REMOVED} unit.store", id="@own, a second word"),
    pytest.param("domain@own", CLI, {}, f"at: 'domain@own': @own {REMOVED} parts.domain",
                 id="@own from an importer outside the folder"),
    pytest.param("store@own", SERVICES, {}, f"at: 'store@own': @own {REMOVED} parts.store",
                 id="@own from another word's folder"),
    pytest.param("kernel@own", SERVICES, {}, f"at: 'kernel@own': @own {REMOVED} parts.kernel",
                 id="@own for a part in no repeating folder"),
    pytest.param("domain", SERVICES, {}, f"at: 'domain': {BARE} {OWN_MODULE}", id="a bare name, the word accepted"),
    pytest.param("store", LEDGER, {}, f"at: 'store': {BARE} unit.store (this unit's) or parts.store (any unit's)",
                 id="a bare name, the second word in place of module"),
    pytest.param("domain", CLI, {}, f"at: 'domain': {BARE} parts.domain", id="a bare name from outside the folder"),
    pytest.param("domain", None, {}, f"at: 'domain': {BARE} parts.domain", id="a bare name from a tier's folder"),
    pytest.param("domain", None, {"mirrored": mirroring("services")}, f"at: 'domain': {BARE} {OWN_MODULE}",
                 id="a bare name a test mirrors"),
    pytest.param("domain@own", None, {"mirrored": mirroring("services")},
                 f"at: 'domain@own': @own {REMOVED} module.domain", id="@own a test mirrors"),
    pytest.param("domain", None, {"place": True, "alone": "a check that names no part"},
                 f"at: 'domain': {BARE} parts.domain", id="a bare name in the place of a check that names no part"),
    pytest.param("domain", SERVICES, {"place": True}, f"at: 'domain': {BARE} {OWN_MODULE}",
                 id="a bare name in the place of a check in the folder"),
    pytest.param("kernel", SERVICES, {}, f"at: 'kernel': {BARE} parts.kernel", id="a bare name in no repeating folder"),
    pytest.param("domain/values:*Id", SERVICES, {},
                 f"at: 'domain/values:*Id': {BARE} module.domain/values:*Id (this module's) or "
                 "parts.domain/values:*Id (any module's)", id="the tail follows each reference"),
    pytest.param("kernel:*Id", SERVICES, {"patterns": False}, f"at: 'kernel:*Id': {BARE} parts.kernel:*Id",
                 id="a pattern where the key takes none: the old form first"),
    pytest.param("kernel:a b", SERVICES, {}, f"at: 'kernel:a b': {BARE} parts.kernel:a b",
                 id="a bad pattern: the old form first"),
    pytest.param("nope", SERVICES, {}, "at: 'nope' names no part 'nope'", id="a part the profile has not"),
    pytest.param("nope@any", SERVICES, {}, "at: 'nope@any' names no part 'nope'", id="@any of a part it has not"),
    pytest.param("everything", SERVICES, {}, "at: 'everything' names no part 'everything'",
                 id="everything is no part: the key that takes it alone says so"),
    pytest.param("services", SERVICES, {},
                 "at: 'services' is implied: a part may always import itself, its own instance of the repeating "
                 "folder; remove it (parts.services, another instance's too, stays allowed)", id="the part itself"),
    pytest.param("services@own", SERVICES, {},
                 "at: 'services@own' is implied: a part may always import itself, its own instance of the repeating "
                 "folder; remove it (parts.services, another instance's too, stays allowed)", id="its own instance"),
    pytest.param("services@any", SERVICES, {}, f"at: 'services@any': @any {REMOVED} parts.services",
                 id="itself in every instance"),
    pytest.param("kernel", KERNEL, {}, "at: 'kernel' is implied: a part may always import itself; remove it",
                 id="itself, outside a repeating folder"),
    pytest.param("kernel@any", KERNEL, {}, "at: 'kernel@any' is implied: a part may always import itself; remove it",
                 id="@any of itself outside a repeating folder: never a hint refused again"),
    pytest.param("domain@foo", SERVICES, {}, f"at: 'domain@foo' {NOT_A_REFERENCE}", id="an unknown scope"),
    pytest.param("@any", SERVICES, {}, f"at: '@any' {NOT_A_REFERENCE}", id="a scope of no part"),
    pytest.param("domain@", SERVICES, {}, f"at: 'domain@' {NOT_A_REFERENCE}", id="an empty scope"),
    pytest.param("domain@any@own", SERVICES, {}, f"at: 'domain@any@own' {NOT_A_REFERENCE}", id="two scopes"),
    pytest.param("", SERVICES, {}, f"at: '' {NOT_A_REFERENCE}", id="empty text"),
    pytest.param(1, SERVICES, {}, f"at: 1 {NOT_A_REFERENCE}", id="no text"),
    pytest.param(["domain"], SERVICES, {}, f"at: ['domain'] {NOT_A_REFERENCE}", id="a list"),
])
def test_an_old_form_is_refused_with_the_reference_to_write(written, owner, options, problem):
    assert read(written, owner, **options) == (None, [problem])


def test_an_old_form_of_a_part_named_everything_is_told_parts_everything():
    assert read("everything", CLI, parts={"everything": ("everything",), "cli": ("cli",)}) == (
        None, [f"at: 'everything': {BARE} parts.everything"])


def test_an_old_form_of_a_part_declared_but_not_placed_is_none_with_no_problem():
    assert read("ghost@any", SERVICES, declared={*PARTS, "ghost"}) == (None, [])


@pytest.mark.parametrize("pattern", [
    pytest.param("*Id", id="letters and a star"),
    pytest.param("$*", id="a mark another language starts its names with"),
    pytest.param("%Doc*", id="another such mark"),
    pytest.param("Détail*", id="a letter that is not ascii"),
])
def test_a_name_pattern_is_any_text_but_whitespace_and_the_separators_of_a_target(pattern):
    assert read(f"parts.kernel:{pattern}", SERVICES) == (Target("kernel", "none", (), pattern), [])


@pytest.mark.parametrize("written", ["parts.kernel:a b", "parts.kernel:a@b", "parts.kernel:a:b"])
def test_a_name_pattern_with_whitespace_or_a_separator_is_refused(written):
    assert read(written, SERVICES) == (
        None, [f"at: {written!r} has a name pattern that is not one: write it with no space, `@`, `/` or `:`, `*` "
               "standing for any text"])


def test_what_names_no_part_is_named_in_the_callers_words():
    assert read("module.domain", None, alone="a check that names no part") == (
        None, ["at: 'module.domain': a check that names no part lies in no <module> folder, so it has no own module: "
               "write parts.domain"])


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
    pytest.param("<orders>.services", DOMAIN, True,
                 "at: '<orders>.services': write the word without brackets: orders.services",
                 id="brackets around what is no word of the profile"),
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
    assert read(written, None, mirrored=mirroring("services")) == (found, problem)


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


@pytest.mark.parametrize("written, found", [
    pytest.param("parts.kernel/x.py", Target("kernel", "none", ("x.py",)), id="a dot in the path"),
    pytest.param("parts.kernel:a.b", Target("kernel", "none", (), "a.b"), id="a dot in the pattern"),
])
def test_a_dot_after_the_head_is_no_prefix(written, found):
    assert read(written, SERVICES) == (found, [])


def test_a_concrete_instance_name_is_refused_also_when_a_part_bears_that_name():
    parts = {**PARTS, "orders": ("orders",)}
    assert read("orders.services", DOMAIN, parts=parts) == (
        None, ["at: 'orders.services': 'orders' is neither parts nor a word of this profile (module, unit): a profile "
               "names no instance; write module.services or parts.services"])


@pytest.mark.parametrize("written, problem", [
    pytest.param("parts.kernel", "'parts.kernel': names a part outside imports: write kernel", id="parts"),
    pytest.param("module.domain", "'module.domain': names a part outside imports: write domain", id="a word"),
    pytest.param("unit.store", "'unit.store': names a part outside imports: write store", id="a second word"),
    pytest.param("module.domain/values", "'module.domain/values': names a part outside imports: write domain",
                 id="a path dropped"),
    pytest.param("parts.kernel:*Id", "'parts.kernel:*Id': names a part outside imports: write kernel",
                 id="a pattern dropped"),
    pytest.param("os.environ", None, id="a prefix that is no word"),
    pytest.param("orders.domain", None, id="an instance named"),
    pytest.param("parts.nope", None, id="a part not declared"),
    pytest.param("kernel", None, id="a plain name"),
    pytest.param(3, None, id="no text"),
])
def test_a_key_outside_imports_is_told_the_plain_name_of_a_prefixed_part(written, problem):
    assert outside_imports(written, PARTS, ("module", "unit")) == problem


NO_MODULE = "no part the tier tests lies in a <module> folder, so its tests mirror no module"


@pytest.mark.parametrize("written, tested, found, problem", [
    pytest.param("module.domain/values", mirroring("services"), Target("domain", "own", ("values",)), [],
                 id="a word a tested part lies in"),
    pytest.param("module.domain", mirroring("services", "kernel"), Target("domain", "own"), [],
                 id="one tested part in the folder is enough"),
    pytest.param("module.domain", (("modules", "*", "services", "logic"),), Target("domain", "own"), [],
                 id="a tested part deeper in the folder"),
    pytest.param("module.domain", (("modules", "*", "main.py"),), Target("domain", "own"), [],
                 id="a tested file part in the folder"),
    pytest.param("module.domain", mirroring("kernel", "cli"), None, [f"at: 'module.domain': {NO_MODULE}: write "
                                                                     "parts.domain"],
                 id="no tested part in the folder"),
    pytest.param("module.domain", mirroring("store"), None, [f"at: 'module.domain': {NO_MODULE}: write parts.domain"],
                 id="the tested parts in another word's folder"),
    pytest.param("module.domain", (), None, [f"at: 'module.domain': {NO_MODULE}: write parts.domain"],
                 id="a tier that tests no part"),
    pytest.param("module.domain/values:*Id", mirroring("kernel"), None,
                 [f"at: 'module.domain/values:*Id': {NO_MODULE}: write parts.domain/values:*Id"],
                 id="the path and pattern kept in the reference to write"),
    pytest.param("unit.store", mirroring("services"), None,
                 ["at: 'unit.store': no part the tier tests lies in a <unit> folder, so its tests mirror no unit: "
                  "write parts.store"], id="each word judged on its own"),
    pytest.param("unit.store", mirroring("services", "store"), Target("store", "own"), [],
                 id="a tier testing parts of both words"),
    pytest.param("module.kernel", (), None,
                 ["at: 'module.kernel': part 'kernel' lies in no <module> folder: write parts.kernel"],
                 id="the target part's folder is checked first"),
    pytest.param("module.store", (), None,
                 ["at: 'module.store': part 'store' lies in the <unit> folder, not <module>: write parts.store"],
                 id="the target part in another word's folder is checked first"),
    pytest.param("parts.domain", (), Target("domain", "any"), [], id="parts is never refused for it"),
])
def test_a_test_reads_a_word_only_where_a_part_its_tier_tests_lies_in_that_word_s_folder(written, tested, found,
                                                                                          problem):
    assert read(written, None, mirrored=tested) == (found, problem)


@pytest.mark.parametrize("written, tested, problem", [
    pytest.param("domain@own", mirroring("services"), f"at: 'domain@own': @own {REMOVED} module.domain",
                 id="@own, a tested part in the folder"),
    pytest.param("domain@own", mirroring("kernel"), f"at: 'domain@own': @own {REMOVED} parts.domain",
                 id="@own, no tested part in the folder"),
    pytest.param("domain@own", (), f"at: 'domain@own': @own {REMOVED} parts.domain",
                 id="@own, a tier that tests no part"),
    pytest.param("domain", mirroring("services"), f"at: 'domain': {BARE} {OWN_MODULE}",
                 id="a bare name, a tested part in the folder"),
    pytest.param("domain", mirroring("kernel"), f"at: 'domain': {BARE} parts.domain",
                 id="a bare name, no tested part in the folder"),
    pytest.param("domain", (), f"at: 'domain': {BARE} parts.domain", id="a bare name, a tier that tests no part"),
    pytest.param("store", mirroring("services"), f"at: 'store': {BARE} parts.store",
                 id="a bare name, the tested parts in another word's folder"),
    pytest.param("domain@any", (), f"at: 'domain@any': @any {REMOVED} parts.domain", id="@any told parts as ever"),
])
def test_an_old_form_a_test_reads_names_the_word_only_where_its_tier_could_write_it(written, tested, problem):
    assert read(written, None, mirrored=tested) == (None, [problem])
