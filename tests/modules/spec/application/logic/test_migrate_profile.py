"""Converting a profile of format 1 to format 2, on hand-made documents: each fact moves to the place format 2 states it
at, and what has no form in format 2 is reported by name."""
from copy import deepcopy

import pytest

from tests.modules.spec.profiles_v2 import PRESETS, TESTING, parsed
from xarch.modules.spec.application.logic.migrate_examples import referenced_v1
from xarch.modules.spec.application.logic.migrate_profile import Converted, convert
from xarch.modules.spec.application.logic.profile_listing import listing
from xarch.modules.spec.domain.errors import InvalidArchitecture

KIT = {"files": ["test_*.py"], "functions": "test_*"}


def old(**changes) -> dict:
    return {
        "xarch": 1, "name": "layered",
        "layout": {"src": {"singular": "module", "each": {"api": {}, "service": {}}}, "shared": {}},
        "parts": {"api": {"path": "src/*/api", "role": "HTTP handlers"},
                  "service": {"path": "src/*/service", "role": "business logic"},
                  "shared": {"path": "shared", "role": "shared code"}},
        "rules": {"api": ["service@own"], "service": ["shared"], "shared": []},
    } | changes


def tiered(**changes) -> dict:
    return old(tests=deepcopy(KIT), tiers=[
        {"name": "unit", "subject": ["service", "shared"], "proves": "a rule", "may_touch": "nothing",
         "litmus": "Does it decide?\n"},
        {"name": "integration", "subject": ["api"], "proves": "a request", "may_touch": "the database",
         "litmus": "Does it need the database?"}]) | changes


def made(document: dict, files: dict[str, tuple[str, ...]] | None = None, presets=None,
         missing: frozenset[str] | set[str] = frozenset()) -> Converted:
    """The conversion, with every file the document names next to it but those missing, and the folders in files."""
    named = referenced_v1(document)[0]
    return convert(document, "layered.yaml", presets or {},
                   listing((name for name in named if name not in missing), files or {}))


def loads(converted: Converted, folders=None, presets=None):
    return parsed(converted.document, folders=folders, presets=presets or {"kit": KIT}, bundled=())


def test_the_converted_profile_starts_with_the_version_the_name_and_the_language():
    document = made(old()).document
    assert list(document)[:3] == ["xarch", "name", "language"]
    assert (document["xarch"], document["name"], document["language"]) == (2, "layered", "python")


@pytest.mark.parametrize("part, path", [
    pytest.param("api", "src/<module>/api", id="the star of the each folder becomes the word singular names"),
    pytest.param("shared", "shared", id="a path outside the each folder stays as it is"),
])
def test_a_part_path_names_the_repeating_folder_by_its_word(part, path):
    assert made(old()).document["parts"][part]["path"] == path


def test_a_part_keeps_its_role_and_litmus_and_follows_the_order_of_the_placement_when_there_is_one():
    document = made(old(placement=["shared", "service", "api"])).document
    assert list(document["parts"]) == ["shared", "service", "api"]
    assert document["parts"]["shared"]["role"] == "shared code"


def test_without_a_placement_the_parts_keep_the_order_of_the_file():
    assert list(made(old()).document["parts"]) == ["api", "service", "shared"]


def test_the_part_marked_entry_is_the_entry_of_the_docs():
    document = made(old(parts=old()["parts"] | {"api": {"path": "src/*/api", "role": "x", "entry": True}})).document
    assert document["docs"]["entry"] == "api"
    assert "entry" not in document["parts"]["api"]


@pytest.mark.parametrize("rules, may_import", [
    pytest.param({"api": ["service@own"]}, ["service"], id="a target in the own folder drops its scope"),
    pytest.param({"api": ["service@any"]}, ["service@any"], id="a target in any folder keeps its scope"),
    pytest.param({"api": ["service@own/rules", "shared/text"]}, ["service/rules", "shared/text"],
                 id="a path below the part stays"),
    pytest.param({"api": ["*"]}, "everything", id="the star becomes the word everything"),
    pytest.param({"api": ["service@own", "api@any"]}, ["service", "api@any"],
                 id="another instance of the part itself stays since it says more than the part may do"),
])
def test_what_a_part_may_import_is_written_on_the_part(rules, may_import):
    assert made(old(rules=rules)).document["parts"]["api"]["may_import"] == may_import


def test_a_part_that_may_import_nothing_has_no_may_import():
    assert "may_import" not in made(old()).document["parts"]["shared"]


def test_a_part_outside_the_each_folder_that_reached_its_own_instance_reaches_any_and_the_change_is_reported():
    document = old(rules={"shared": ["service@own"]})
    converted = made(document)
    assert converted.document["parts"]["shared"]["may_import"] == ["service@any"]
    assert any("parts.shared.may_import" in change and "service@any" in change for change in converted.changes)


def test_a_star_with_other_targets_leaves_them_out_and_says_so():
    converted = made(old(rules={"api": ["service@own", "*"]}))
    assert converted.document["parts"]["api"]["may_import"] == "everything"
    assert any("parts.api.may_import" in change and "everything" in change for change in converted.changes)


def test_libraries_are_written_on_the_parts_that_list_them_and_the_others_have_none():
    document = made(old(libraries={"service": ["sqlmodel"]})).document
    assert document["parts"]["service"]["libraries"] == ["sqlmodel"]
    assert all("libraries" not in document["parts"][name] for name in ("api", "shared"))


def test_a_profile_with_no_libraries_key_checked_none_so_every_part_leaves_them_unchecked_and_the_change_is_reported():
    converted = made(old())
    assert [part["libraries"] for part in converted.document["parts"].values()] == ["everything"] * 3
    assert any("libraries" in change and "unchecked" in change for change in converted.changes)


def test_parts_with_the_same_forbidden_names_share_a_named_list_and_a_part_alone_has_its_own():
    names = ["time.time", "socket"]
    document = made(old(libraries={}, forbidden={"api": names, "service": list(names), "shared": ["os.environ"]})).document
    assert document["forbidden"] == {"shared-names": names, "shared": ["os.environ"]}
    assert [document["parts"][part]["forbidden"] for part in ("api", "service", "shared")] == [
        "shared-names", "shared-names", "shared"]


def test_layers_pass_through_unchanged():
    layers = {"inward": ["shared", "service"]}
    assert made(old(layers=layers, rules={"service": ["shared"]})).document["layers"] == layers


def test_a_part_a_tier_tests_names_the_tier_and_a_part_no_tier_tests_keeps_its_reason():
    document = tiered(parts=old()["parts"] | {"shared": {"path": "shared", "role": "x", "untested": "no logic"}})
    document["tiers"][0]["subject"] = ["service"]
    parts = made(document).document["parts"]
    assert [parts[name].get("tier") for name in ("api", "service", "shared")] == ["integration", "unit", None]
    assert parts["shared"]["untested"] == "no logic"


def test_the_tiers_become_a_map_by_name_with_the_docs_only_texts_under_docs():
    document = tiered()
    document["tiers"][0] |= {"subject_text": "the services", "one_file_per": "rule", "cases_from": "invariants",
                              "data": "built", "forbidden": True, "types_only": ["api"]}
    tiers = made(document).document["tiers"]
    assert list(tiers) == ["unit", "integration"]
    assert tiers["unit"] == {
        "proves": "a rule", "litmus": "Does it decide?", "apply_forbidden": True, "types_only": ["api"],
        "docs": {"subject": "the services", "may_touch": "nothing", "one_file_per": "rule", "cases_from": "invariants",
                 "data": "built"}}
    assert tiers["integration"]["docs"] == {"may_touch": "the database"}


def test_a_part_named_in_two_subjects_goes_to_the_first_tier_and_the_choice_is_reported():
    document = tiered()
    document["tiers"][1]["subject"] = ["api", "shared"]
    converted = made(document)
    assert converted.document["parts"]["shared"]["tier"] == "unit"
    assert any("shared" in change and "unit" in change and "integration" in change for change in converted.changes)


def test_a_sub_path_named_beside_the_whole_part_is_the_part_and_a_sub_path_in_another_tier_is_reported():
    document = tiered()
    document["tiers"][0]["subject"] = ["service", "service/rules", "shared"]
    assert made(document).by_hand == ()
    document["tiers"][0]["subject"] = ["service", "shared/text"]
    document["tiers"][1]["subject"] = ["api", "shared"]
    converted = made(document)
    assert converted.document["parts"]["shared"]["tier"] == "integration"
    assert any("shared/text" in item and "unit" in item for item in converted.by_hand)


def test_a_part_tested_only_below_a_sub_path_is_the_tier_of_the_whole_part_and_the_change_is_reported():
    document = tiered()
    document["tiers"][0]["subject"] = ["service", "shared/text"]
    converted = made(document)
    assert converted.document["parts"]["shared"]["tier"] == "unit"
    assert any("shared/text" in change for change in converted.changes)


def test_a_tier_with_a_folder_states_what_its_tests_may_import_from_its_subject_and_their_rules():
    document = tiered()
    document["tiers"].append({"name": "guard", "subject": ["service"], "proves": "p", "may_touch": "m", "litmus": "l",
                               "folder": "architecture"})
    document["rules"] = {"service": ["shared"], "api": [], "shared": []}
    tier = made(document).document["tiers"]["guard"]
    assert tier["folder"] == "architecture"
    assert tier["may_import"] == ["service@any", "shared"]


def test_a_folder_tier_whose_subject_part_may_import_everything_may_import_everything():
    document = tiered()
    document["tiers"].append({"name": "guard", "subject": ["shared"], "subject_text": "the tree", "proves": "p",
                               "may_touch": "m", "litmus": "l", "folder": "architecture"})
    document["rules"] = {"shared": ["*"]}
    converted = made(document)
    assert converted.document["tiers"]["guard"]["may_import"] == "everything"
    assert converted.document["parts"]["shared"]["tier"] == "unit"


def test_a_folder_tier_with_no_subject_may_import_nothing():
    document = tiered()
    document["tiers"].append({"name": "guard", "subject": [], "subject_text": "the tree", "proves": "p",
                               "may_touch": "m", "litmus": "l", "folder": "architecture"})
    assert made(document).document["tiers"]["guard"]["may_import"] == []


def test_the_converted_tiers_load_in_format_2_with_every_part_in_a_tier_or_untested():
    document = tiered(parts=old()["parts"] | {"shared": {"path": "shared", "role": "x", "untested": "no logic"}})
    document["tiers"][0]["subject"] = ["service"]
    architecture = loads(made(document))
    assert [tier.name for tier in architecture.tiers] == ["unit", "integration"]
    assert architecture.parts["shared"].untested == "no logic"


def test_the_tests_key_is_the_preset_whose_map_it_equals_and_its_own_map_otherwise():
    assert made(tiered(), presets={"kit": KIT}).document["testing"] == "kit"
    assert made(tiered(), presets={"other": {"files": ["x_*.py"], "functions": "x_*"}}).document["testing"] == KIT


def test_the_names_of_the_framework_held_by_the_guards_move_to_the_testing_map():
    guards = {"scenario-coverage": {"results": "api", "tier": "integration", "suffix": "Result",
                                    "columns": ["given", "when", "then"], "file": "test_{name}.py",
                                    "table": {"decorator": "pytest.mark.parametrize", "row": "pytest.param",
                                              "id": "id", "keywords": ["argnames", "argvalues"]}},
              "stand-ins": {"mocks": ["unittest.mock.Mock"], "autospec": ["unittest.mock.create_autospec"],
                            "spec": ["spec"], "fixtures": {"mocker": {"mocks": ["Mock"], "autospec": ["create_autospec"]}}}}
    document = tiered(guards=guards, fakes={"path": "tests/fakes", "for": ["shared"], "prefix": "Fake"})
    converted = made(document)
    assert converted.document["testing"] == KIT | {
        "table": {"decorator": "pytest.mark.parametrize", "row": "pytest.param", "id": "id",
                  "keywords": ["argnames", "argvalues"]},
        "mocks": {"calls": ["unittest.mock.Mock"], "autospec": ["unittest.mock.create_autospec"],
                  "spec_keywords": ["spec"], "fixtures": {"mocker": {"calls": ["Mock"], "autospec": ["create_autospec"]}}}}
    assert converted.document["guards"] == {
        "scenario-coverage": {"results": "api", "tier": "integration", "suffix": "Result",
                              "columns": ["given", "when", "then"], "file": "test_{name}.py"},
        "stand-ins": {}}
    assert converted.document["fakes"] == {"folder": "fakes", "for": ["shared"], "prefix": "Fake"}


def test_the_framework_names_the_guards_hold_equal_to_a_preset_are_that_preset():
    guards = {"scenario-coverage": {"results": "api", "tier": "integration", "suffix": "Result",
                                    "columns": ["given", "when", "then"], "file": "test_{name}.py",
                                    "table": TESTING["table"]},
              "stand-ins": {"mocks": TESTING["mocks"]["calls"], "autospec": TESTING["mocks"]["autospec"],
                            "spec": TESTING["mocks"]["spec_keywords"],
                            "fixtures": {"mocker": {"mocks": ["Mock", "MagicMock"], "autospec": ["create_autospec"]}}}}
    document = tiered(tests={key: TESTING[key] for key in ("files", "functions", "skips")}, guards=guards,
                      fakes={"path": "tests/fakes", "for": ["shared"], "prefix": "Fake"})
    assert made(document, presets=PRESETS).document["testing"] == "pytest"


def test_the_guard_package_only_becomes_a_fact_of_each_part_and_the_others_stay_guards():
    document = made(old(guards={"package-only": ["api"], "no-comments": {}, "closed-tree": {}})).document
    assert document["parts"]["api"]["package_only"] is True
    assert "package_only" not in document["parts"]["service"]
    assert document["guards"] == {"no-comments": {}, "closed-tree": {}}


def test_the_folder_of_the_fakes_is_below_the_tests_folder_and_the_first_step_of_its_path_is_dropped():
    document = tiered(fakes={"path": "tests/doubles/io", "for": ["shared"]})
    assert made(document).document["fakes"] == {"folder": "doubles/io", "for": ["shared"]}


def test_the_folders_below_a_part_with_their_notes_are_the_folders_of_the_part():
    layout = {"src": {"singular": "module", "each": {"api": {"routes": {}, "ui": {}}, "service": {}}}, "shared": {}}
    document = old(layout=layout, notes={"src/*/api/routes": "one file per group", "src/*/api/ui": "the pages"})
    assert made(document).document["parts"]["api"]["folders"] == {"routes": "one file per group", "ui": "the pages"}


def test_folders_with_no_notes_are_a_list_and_a_folder_that_holds_others_is_implied_by_them():
    layout = {"src": {"singular": "module", "each": {"api": {"a": {"b": {}}, "c": {}}, "service": {}}}, "shared": {}}
    assert made(old(layout=layout)).document["parts"]["api"]["folders"] == ["a/b", "c"]


def test_folders_when_only_some_have_a_note_are_a_list_and_the_notes_are_reported():
    layout = {"src": {"singular": "module", "each": {"api": {"routes": {}, "ui": {}}, "service": {}}}, "shared": {}}
    converted = made(old(layout=layout, notes={"src/*/api/ui": "the pages"}))
    assert converted.document["parts"]["api"]["folders"] == ["routes", "ui"]
    assert any("the pages" in item for item in converted.by_hand)


def test_a_folder_of_the_layout_that_is_in_no_part_and_below_none_is_reported_with_its_note():
    layout = {"src": {"singular": "module", "each": {"api": {}, "service": {}}}, "shared": {}, "scripts": {"deep": {}}}
    converted = made(old(layout=layout, notes={"scripts": "helper scripts"}))
    assert [item for item in converted.by_hand if "scripts" in item] != []
    assert any("helper scripts" in item for item in converted.by_hand)
    assert not any("scripts/deep" in item for item in converted.by_hand)


def test_a_note_on_a_folder_that_holds_parts_and_a_file_below_a_part_are_reported():
    layout = {"src": {"singular": "module", "each": {"api": {"app.py": "file"}, "service": {}}}, "shared": {}}
    converted = made(old(layout=layout, notes={"src": "the source"}))
    assert any("src" in item and "the source" in item for item in converted.by_hand)
    assert any("app.py" in item for item in converted.by_hand)


def test_a_file_part_is_a_path_with_a_dot_and_a_file_without_one_is_reported():
    layout = {"src": {"singular": "module", "each": {"api": {}, "service": {}}}, "shared": {}, "Makefile": "file",
              "main.py": "file"}
    parts = old()["parts"] | {"build": {"path": "Makefile", "role": "build"}, "main": {"path": "main.py", "role": "x"}}
    converted = made(old(layout=layout, parts=parts, rules={}))
    assert converted.document["parts"]["main"]["path"] == "main.py"
    assert any("build" in item and "Makefile" in item for item in converted.by_hand)


def test_the_docs_are_pages_and_a_page_with_only_a_template_is_that_file_name():
    docs = {"statement.md": {"from": "docs/statement.md"}, "adrs/": {"note": "decisions"},
            "architecture.md": {"from": "a.md", "note": "this file"}}
    assert made(old(docs=docs)).document["docs"]["pages"] == {
        "statement.md": "docs/statement.md", "adrs/": {"note": "decisions"},
        "architecture.md": {"from": "a.md", "note": "this file"}}


def test_the_naming_table_is_docs_naming_and_the_files_keep_their_options_and_a_bare_template_is_its_name():
    naming = [{"kind": "adapter", "where": "adapters/", "pattern": "x", "example": "y"}]
    files = {"AGENTS.md": {"from": "agents.md"}, "tests/t.py": {"from": "t.py", "pinned": True}}
    document = made(old(naming=naming, files=files)).document
    assert document["docs"]["naming"] == naming
    assert document["files"] == {"AGENTS.md": "agents.md", "tests/t.py": {"from": "t.py", "pinned": True}}


def test_excluded_and_hints_pass_through_unchanged():
    document = made(old(excluded={"vendor": "not ours"}, hints={"layers": "see the wiki"})).document
    assert (document["excluded"], document["hints"]) == ({"vendor": "not ours"}, {"layers": "see the wiki"})


def test_a_key_format_1_does_not_have_is_reported_by_name_and_not_converted():
    converted = made(old(colour="blue"))
    assert any("colour" in item for item in converted.by_hand)
    assert "colour" not in converted.document


@pytest.mark.parametrize("document, problem", [
    pytest.param([1], "must be a mapping", id="a list is not a profile"),
    pytest.param({"xarch": 1}, "missing `layout`", id="a profile with no layout cannot place a part"),
    pytest.param(old(layout=3), "layout: must be a mapping", id="a layout that is no mapping cannot be read"),
    pytest.param(old(parts={"api": {"role": "x"}}), "parts.api: missing `path`", id="a part with no path is unreadable"),
    pytest.param(old(layout={"src": {"each": {}}}), "needs `singular`", id="an each folder needs its word"),
])
def test_a_document_that_is_not_readable_as_format_1_is_refused_with_why(document, problem):
    with pytest.raises(InvalidArchitecture) as caught:
        made(document)
    assert any(problem in item for item in caught.value.problems)
