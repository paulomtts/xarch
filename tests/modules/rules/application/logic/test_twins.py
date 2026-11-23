"""The no-twins check on hand-made source files: two public classes in different parts that declare the same fields in
the same order are one type written twice."""
import pytest

from tests.modules.rules.builders import APP, imp, profile, source
from xarch.modules.rules.application.logic.twins import checked as twins
from xarch.modules.rules.domain.outcomes import Twins
from xarch.modules.rules.domain.parsed import Call, Class, Function
from xarch.modules.rules.domain.published import Translation

ON = profile(no_twins=3)
DOMAIN = "modules/docs/domain/values.py"
CONTRACT = "modules/docs/contract/__init__.py"
LOGIC = "modules/docs/application/logic/rule.py"
FIELDS = ("key", "part", "what")


def problems(*files, checked=ON) -> list[str]:
    return [str(v) for v in twins(list(files), checked, APP).violations]


def test_a_twin_in_another_part_is_reported_naming_both_places_with_what_to_do():
    found = twins([source(CONTRACT, classes=(Class(9, "LoosenedView", fields=FIELDS),)),
                   source(DOMAIN, classes=(Class(5, "Loosened", fields=FIELDS),))], ON, APP).violations
    assert [(str(v), v.rule, v.fix) for v in found] == [(
        "app/modules/docs/contract/__init__.py:9: LoosenedView declares the fields of Loosened at "
        "app/modules/docs/domain/values.py:5 in the same order (key, part, what): contract/ of modules/docs and "
        "domain/ of modules/docs hold one type written twice (no-twins)", "no-twins",
        "keep one of the two and import it from a part both may import, or give LoosenedView the fields its reader "
        "needs instead of a copy of Loosened's")]


@pytest.mark.parametrize("first, second, reported", [
    pytest.param(Class(5, "A", fields=FIELDS), Class(9, "B", fields=("key", "what", "part")), False,
                 id="the same names in another order"),
    pytest.param(Class(5, "A", fields=FIELDS), Class(9, "B", fields=(*FIELDS, "more")), False,
                 id="one field more"),
    pytest.param(Class(5, "A", fields=FIELDS[:2]), Class(9, "B", fields=FIELDS[:2]), False,
                 id="fewer fields than the minimum"),
    pytest.param(Class(5, "_A", fields=FIELDS), Class(9, "B", fields=FIELDS), False, id="a private class"),
    pytest.param(Class(5, "A", fields=FIELDS, interface=True), Class(9, "B", fields=FIELDS), False,
                 id="an interface, whose fields are a requirement"),
    pytest.param(Class(5, "A", (("typing", "Protocol"),), fields=FIELDS), Class(9, "B", fields=FIELDS), True,
                 id="a class with a Protocol base the reader does not mark is no interface"),
    pytest.param(Class(5, "A", fields=FIELDS), Class(9, "B", fields=FIELDS), True, id="the same names in order"),
])
def test_only_classes_with_the_same_fields_in_order_and_at_least_the_minimum_are_twins(first, second, reported):
    files = [source(DOMAIN, classes=(first,)), source(LOGIC, classes=(second,))]
    assert bool(problems(*files)) == reported


def test_two_classes_of_one_part_are_not_twins_in_one_instance_or_two():
    assert problems(source(DOMAIN, classes=(Class(5, "A", fields=FIELDS),)),
                    source("modules/docs/domain/other.py", classes=(Class(3, "B", fields=FIELDS),)),
                    source("modules/billing/domain/values.py", classes=(Class(3, "C", fields=FIELDS),))) == []


def test_two_instances_of_a_repeating_folder_hold_twins_across_their_parts():
    assert problems(source("modules/billing/domain/values.py", classes=(Class(3, "A", fields=FIELDS),)),
                    source(CONTRACT, classes=(Class(5, "B", fields=FIELDS),))) == [
        "app/modules/docs/contract/__init__.py:5: B declares the fields of A at app/modules/billing/domain/values.py:3 "
        "in the same order (key, part, what): contract/ of modules/docs and domain/ of modules/billing hold one type "
        "written twice (no-twins)"]


def test_the_inner_part_comes_first_and_each_copy_names_an_earlier_twin_of_its_own_instance_first():
    found = problems(source(CONTRACT, classes=(Class(5, "A", fields=FIELDS),)),
                     source(DOMAIN, classes=(Class(5, "B", fields=FIELDS),)),
                     source("modules/rules/contract/__init__.py", classes=(Class(5, "C", fields=FIELDS),)),
                     source("modules/rules/domain/values.py", classes=(Class(5, "D", fields=FIELDS),)))
    assert [line.split(" in the same order")[0] for line in found] == [
        "app/modules/docs/contract/__init__.py:5: A declares the fields of B at app/modules/docs/domain/values.py:5",
        "app/modules/rules/contract/__init__.py:5: C declares the fields of D at app/modules/rules/domain/values.py:5"]


def test_a_class_whose_earlier_twins_share_its_part_is_not_reported_but_its_later_twin_in_another_part_is():
    found = problems(source(DOMAIN, classes=(Class(5, "A", fields=FIELDS),)),
                     source("modules/rules/domain/values.py", classes=(Class(5, "B", fields=FIELDS),)),
                     source("modules/billing/contract/__init__.py", classes=(Class(5, "C", fields=FIELDS),)))
    assert [line.split(" in the same order")[0] for line in found] == [
        "app/modules/billing/contract/__init__.py:5: C declares the fields of A at app/modules/docs/domain/values.py:5"]


def test_many_fields_are_shown_by_the_first_four():
    fields = ("a", "b", "c", "d", "e", "f")
    found = problems(source(DOMAIN, classes=(Class(5, "A", fields=fields),)),
                     source(CONTRACT, classes=(Class(9, "B", fields=fields),)))
    assert "in the same order (a, b, c, d and 2 more)" in found[0]


def test_a_class_in_no_part_is_not_read_and_the_check_is_off_without_the_guard():
    files = [source("scripts/seed.py", classes=(Class(5, "A", fields=FIELDS),)),
             source(DOMAIN, classes=(Class(5, "B", fields=FIELDS),))]
    assert problems(*files) == []
    assert problems(source(LOGIC, classes=(Class(5, "A", fields=FIELDS),)), files[1], checked=profile()) == []


def test_the_minimum_is_the_profile_s():
    files = [source(DOMAIN, classes=(Class(5, "A", fields=FIELDS[:2]),)),
             source(CONTRACT, classes=(Class(9, "B", fields=FIELDS[:2]),))]
    assert len(problems(*files, checked=profile(no_twins=2))) == 1


RENAMED = profile(no_twins=3, no_twins_renamed=3)
SUBSET = profile(no_twins=3, no_twins_subset=3)
LOADED = Class(5, "Loaded", fields=("location", "example_problems", "files", "origin"),
               types=("str", "tuple[str, ...]", "int", "Origin"))
CHECKED = Class(9, "Checked", fields=("location", "problems", "files", "origin"),
                types=("str", "tuple[Problem, ...]", "int", "Origin | None"))


def test_a_copy_that_renamed_a_field_is_reported_naming_the_names_and_what_to_do():
    found = twins([source(CONTRACT, classes=(CHECKED,)), source(DOMAIN, classes=(LOADED,))], RENAMED, APP).violations
    assert [(str(v), v.fix) for v in found] == [(
        "app/modules/docs/contract/__init__.py:9: Checked declares the fields of Loaded at "
        "app/modules/docs/domain/values.py:5 in the same order, but for problems in place of example_problems "
        "(location, problems, files, origin): contract/ of modules/docs and domain/ of modules/docs hold one type "
        "written twice (no-twins)",
        "keep one of the two, with one name for each field, and import it from a part both may import, or give Checked "
        "the fields its reader needs instead of a renamed copy of Loaded's")]


def fields(*named: str) -> tuple[str, ...]:
    return tuple(name.split(":")[0] for name in named)


def types(*named: str) -> tuple[str, ...]:
    return tuple(name.split(":")[1] for name in named)


def cls(line: int, name: str, *named: str) -> Class:
    """A class whose fields are written `<name>:<type>`."""
    return Class(line, name, fields=fields(*named), types=types(*named))


@pytest.mark.parametrize("first, second, reported", [
    pytest.param(cls(5, "Copy", "destination:str", "source:str", "rewritten:bool"),
                 cls(9, "Moved", "path:str", "source:str | None", "rewritten:int"), True,
                 id="three fields, the renamed one of the same type"),
    pytest.param(cls(5, "Doc", "path:str", "source:str", "note:str"),
                 cls(9, "Moved", "path:str", "source:str", "rewritten:int"), False,
                 id="three fields, the renamed one of another type"),
    pytest.param(cls(5, "Supply", "fact:str", "grade:str", "note:str"),
                 cls(9, "Near", "part:str", "folder:str", "path:str"), False,
                 id="the same types, every name different"),
    pytest.param(cls(5, "Slot", "name:str", "meaning:str", "accepts:str", "takes:str"),
                 cls(9, "Field", "name:str", "meaning:str", "when:str"), False,
                 id="the names that agree are not more than half of the larger class's"),
    pytest.param(cls(5, "Conversion", "folder:Path", "profile:str", "copies:tuple[Copied, ...]", "changes:list",
                     "by_hand:list"),
                 cls(9, "Migrated", "folder:Path", "profile:Path", "files:tuple[Moved, ...]", "changes:list",
                     "by_hand:list", "dry_run:bool"), True,
                 id="one field renamed and retyped of five, and one more"),
    pytest.param(cls(5, "A", "a:int", "b:int"), cls(9, "B", "a:int", "c:int"), False,
                 id="fewer fields than the minimum"),
])
def test_a_renamed_copy_keeps_more_than_half_the_names_and_each_renamed_field_its_type_unless_it_is_the_only_one(
        first, second, reported):
    assert bool(problems(source(DOMAIN, classes=(first,)), source(CONTRACT, classes=(second,)),
                         checked=RENAMED)) == reported


def test_a_renamed_copy_with_more_fields_says_how_many_more():
    found = problems(source(DOMAIN, classes=(cls(5, "Conversion", "folder:Path", "profile:str", "copies:tuple",
                                                 "changes:list", "by_hand:list"),)),
                     source(CONTRACT, classes=(cls(9, "Migrated", "folder:Path", "profile:Path", "files:list",
                                                   "changes:list", "by_hand:list", "dry_run:bool"),)),
                     checked=RENAMED)
    assert found == [
        "app/modules/docs/contract/__init__.py:9: Migrated declares the fields of Conversion at "
        "app/modules/docs/domain/values.py:5 in the same order, but for files in place of copies, and 1 more "
        "(dry_run) (folder, profile, files, changes and 2 more): contract/ of modules/docs and domain/ of "
        "modules/docs hold one type written twice (no-twins)"]


def test_a_type_that_is_itself_a_twin_counts_as_the_type_it_copies():
    holder = cls(5, "Batch", "path:str", "items:tuple[Copy, ...]", "count:int")
    copy = cls(9, "Run", "path:str", "entries:tuple[CopyView, ...]", "count:int")
    twins = (Class(3, "Copy", fields=FIELDS), Class(3, "CopyView", fields=FIELDS))
    assert problems(source(DOMAIN, classes=(holder,)), source(CONTRACT, classes=(copy,)), checked=RENAMED) == []
    found = problems(source(DOMAIN, classes=(twins[0], holder)), source(CONTRACT, classes=(twins[1], copy)),
                     checked=RENAMED)
    assert [line.split(" in the same order")[0] for line in found] == [
        "app/modules/docs/contract/__init__.py:3: CopyView declares the fields of Copy at "
        "app/modules/docs/domain/values.py:3",
        "app/modules/docs/contract/__init__.py:9: Run declares the fields of Batch at "
        "app/modules/docs/domain/values.py:5"]


def test_a_copy_that_kept_part_of_the_fields_in_order_is_reported_at_the_later_part():
    language = Class(5, "Language", fields=("title", "name", "extension", "package_file", "cache"))
    view = Class(9, "CheckedLanguage", fields=("title", "extension", "package_file"))
    found = twins([source(DOMAIN, classes=(language,)), source("kernel/language.py", classes=(view,))], SUBSET,
                  APP).violations
    assert [(str(v), v.fix) for v in found] == [(
        "app/modules/docs/domain/values.py:5: Language declares the fields of CheckedLanguage at app/kernel/language.py:9 "
        "in the same order, and 2 more (name, cache) (title, name, extension, package_file and 1 more): domain/ of "
        "modules/docs and kernel/ hold one type written twice (no-twins)",
        "keep one of the two and import it from a part both may import, or give Language the fields its reader needs "
        "instead of a copy of CheckedLanguage's")]


def test_the_copy_that_kept_part_is_said_so_when_it_is_the_one_reported():
    found = problems(source("kernel/language.py", classes=(Class(5, "Language", fields=("title", "name", "cache")),)),
                     source(DOMAIN, classes=(Class(9, "View", fields=("title", "cache")),)),
                     checked=profile(no_twins=3, no_twins_subset=2))
    assert found == [
        "app/modules/docs/domain/values.py:9: View declares 2 of the 3 fields of Language at app/kernel/language.py:5, "
        "in the same order (title, cache): domain/ of modules/docs and kernel/ hold one type written twice (no-twins)"]


@pytest.mark.parametrize("kept, reported", [
    pytest.param(("title", "extension", "package_file"), True, id="three of five"),
    pytest.param(("title", "extension"), False, id="fewer than the minimum"),
    pytest.param(("title", "package_file", "extension"), False, id="out of order"),
    pytest.param(("title", "extension", "other"), False, id="a field the other does not have"),
])
def test_a_part_is_kept_when_its_fields_are_the_other_s_in_order_at_least_the_minimum(kept, reported):
    language = Class(5, "Language", fields=("title", "name", "extension", "package_file", "cache"))
    assert bool(problems(source(DOMAIN, classes=(language,)), source(CONTRACT, classes=(Class(9, "V", fields=kept),)),
                         checked=SUBSET)) == reported


def test_a_part_of_fewer_than_half_the_fields_is_a_smaller_value_of_its_own_not_a_copy():
    tier = Class(5, "Tier", fields=("name", "proves", "a", "may_touch", "b", "litmus", "c", "d", "e"))
    assert problems(source(DOMAIN, classes=(tier,)),
                    source(CONTRACT, classes=(Class(9, "TierInfo", fields=("name", "proves", "may_touch", "litmus")),)),
                    checked=SUBSET) == []


def test_the_renamed_and_the_partial_copies_are_off_unless_the_profile_gives_their_minimum():
    files = [source(DOMAIN, classes=(LOADED, Class(7, "L", fields=("title", "name", "extension")))),
             source(CONTRACT, classes=(CHECKED, Class(11, "V", fields=("title", "extension"))))]
    assert problems(*files, checked=profile(no_twins=2)) == []
    assert len(problems(*files, checked=profile(no_twins=2, no_twins_renamed=3, no_twins_subset=2))) == 2


def test_two_classes_of_one_part_are_never_compared_as_renamed_or_partial_copies():
    assert problems(source(DOMAIN, classes=(LOADED,)), source("modules/billing/domain/x.py", classes=(CHECKED,)),
                    checked=RENAMED) == []


TRANSLATED = profile(no_twins=3, no_twins_translated=("adapters",))
KNOWN = source(DOMAIN, classes=(Class(5, "Known", fields=FIELDS),))
VIEW = source("modules/spec/contract/__init__.py", classes=(Class(9, "KnownView", fields=FIELDS), Class(11, "Other")))
BUILDS_KNOWN = (Call(7, ("app", "modules", "docs", "domain", "values", "Known")),)
BUILDS_VIEW = (Call(7, ("app", "modules", "spec", "contract", "KnownView")),)
BOTH = (imp(1, "app.modules.docs.domain.values", "Known"), imp(2, "app.modules.spec.contract", "KnownView"))
NAMES_BOTH = (Function(6, "known", owner="SpecProfiles", named=frozenset({"Known", "KnownView"})),)
TRANSLATOR = "modules/docs/adapters/spec.py"
REPORTED = ["app/modules/spec/contract/__init__.py:9: KnownView declares the fields of Known at "
            "app/modules/docs/domain/values.py:5 in the same order (key, part, what): contract/ of modules/spec and "
            "domain/ of modules/docs hold one type written twice (no-twins)"]
PUBLISHED = source("modules/spec/application/logic/views.py", classes=(Class(9, "KnownView", fields=FIELDS),))
REEXPORTS = source("modules/spec/contract/__init__.py", imp(1, "app.modules.spec.application.logic.views", "KnownView"))


@pytest.mark.parametrize("files, checked, expected", [
    pytest.param([source(TRANSLATOR, *BOTH, calls=BUILDS_KNOWN, functions=NAMES_BOTH)], TRANSLATED, [],
                 id="a file of a listed part builds one, imports the other, and one function of it names both"),
    pytest.param([source(TRANSLATOR, *BOTH, calls=BUILDS_VIEW, functions=NAMES_BOTH)], TRANSLATED, [],
                 id="it builds the other and imports the first one"),
    pytest.param([source(TRANSLATOR, BOTH[0], imp(2, "app.modules.spec", "contract"),
                         calls=BUILDS_VIEW, functions=NAMES_BOTH)], TRANSLATED, [],
                 id="it imports the other's file as a whole"),
    pytest.param([], TRANSLATED, REPORTED, id="no translator"),
    pytest.param([source("modules/docs/application/services/spec.py", *BOTH, calls=BUILDS_KNOWN,
                         functions=NAMES_BOTH)], TRANSLATED, REPORTED, id="the translator in a part not listed"),
    pytest.param([source(TRANSLATOR, *BOTH, calls=BUILDS_KNOWN, functions=NAMES_BOTH)], ON, REPORTED,
                 id="no part listed"),
    pytest.param([source(TRANSLATOR, *BOTH, functions=NAMES_BOTH)], TRANSLATED, REPORTED,
                 id="a file that imports both and builds neither"),
    pytest.param([source(TRANSLATOR, BOTH[0], calls=BUILDS_KNOWN, functions=NAMES_BOTH)], TRANSLATED, REPORTED,
                 id="a file that builds one and imports only its own file"),
    pytest.param([source(TRANSLATOR, BOTH[0], imp(2, "app.modules.spec.contract", "Other"), calls=BUILDS_KNOWN,
                         functions=(Function(6, "known", named=frozenset({"Known", "Other"})),))], TRANSLATED,
                 REPORTED, id="a file that builds one and imports the other's file for another class"),
    pytest.param([source(TRANSLATOR, *BOTH, calls=BUILDS_KNOWN,
                         functions=(Function(6, "known", named=frozenset({"Known"})),
                                    Function(9, "view", named=frozenset({"KnownView"}))))], TRANSLATED, REPORTED,
                 id="a file whose functions name the two apart"),
    pytest.param([source("scripts/spec.py", *BOTH, calls=BUILDS_KNOWN, functions=NAMES_BOTH)], TRANSLATED, REPORTED,
                 id="a translator in no part"),
])
def test_a_pair_a_function_of_a_listed_part_translates_is_no_twin(files, checked, expected):
    assert problems(KNOWN, VIEW, *files, checked=checked) == expected


def test_the_other_class_is_reached_through_a_file_that_takes_it_from_the_file_defining_it():
    translator = source(TRANSLATOR, BOTH[0], imp(2, "app.modules.spec.contract", "KnownView"), calls=BUILDS_KNOWN,
                        functions=NAMES_BOTH)
    reported = ["app/modules/spec/application/logic/views.py:9: KnownView declares the fields of Known at "
                "app/modules/docs/domain/values.py:5 in the same order (key, part, what): logic/ of modules/spec and "
                "domain/ of modules/docs hold one type written twice (no-twins)"]
    assert problems(KNOWN, PUBLISHED, REEXPORTS, checked=TRANSLATED) == reported
    assert problems(KNOWN, PUBLISHED, REEXPORTS, translator, checked=TRANSLATED) == []


def test_a_class_a_file_builds_where_it_defines_it_is_built_through_no_import_and_translates_nothing():
    view = source(TRANSLATOR, BOTH[0], classes=(Class(9, "KnownView", fields=FIELDS),), functions=NAMES_BOTH)
    assert problems(KNOWN, view, checked=TRANSLATED) == [
        "app/modules/docs/adapters/spec.py:9: KnownView declares the fields of Known at "
        "app/modules/docs/domain/values.py:5 in the same order (key, part, what): adapters/ of modules/docs and "
        "domain/ of modules/docs hold one type written twice (no-twins)"]


def test_each_pair_excused_is_handed_out_naming_the_function_that_translates():
    translator = source(TRANSLATOR, *BOTH, calls=BUILDS_KNOWN, functions=NAMES_BOTH)
    assert twins([KNOWN, VIEW, translator], TRANSLATED, APP) == Twins(
        (), (Translation("app/modules/docs/adapters/spec.py", 6, "SpecProfiles.known", "Known", "KnownView"),))
    assert twins([KNOWN, VIEW], TRANSLATED, APP) == Twins(tuple(twins([KNOWN, VIEW], ON, APP).violations), ())


def test_a_translated_pair_is_no_renamed_copy_either_and_other_pairs_are_still_reported():
    renamed = source("modules/spec/contract/__init__.py", classes=(Class(9, "KnownView", fields=("key", "part", "say"),
                                                                         types=("", "", "")),))
    other = source("modules/billing/contract/__init__.py", classes=(Class(3, "Other", fields=FIELDS),))
    translator = source(TRANSLATOR, *BOTH, calls=BUILDS_KNOWN, functions=NAMES_BOTH)
    checked = profile(no_twins=3, no_twins_renamed=2, no_twins_translated=("adapters",))
    known = source(DOMAIN, classes=(Class(5, "Known", fields=FIELDS, types=("", "", "")),))
    assert problems(known, renamed, checked=checked) == [
        "app/modules/spec/contract/__init__.py:9: KnownView declares the fields of Known at "
        "app/modules/docs/domain/values.py:5 in the same order, but for say in place of what (key, part, say): "
        "contract/ of modules/spec and domain/ of modules/docs hold one type written twice (no-twins)"]
    assert twins([known, renamed, translator], checked, APP) == Twins(
        (), (Translation("app/modules/docs/adapters/spec.py", 6, "SpecProfiles.known", "Known", "KnownView"),))
    assert problems(KNOWN, VIEW, other, translator, checked=TRANSLATED) == [
        "app/modules/billing/contract/__init__.py:3: Other declares the fields of Known at "
        "app/modules/docs/domain/values.py:5 in the same order (key, part, what): contract/ of modules/billing and "
        "domain/ of modules/docs hold one type written twice (no-twins)"]
