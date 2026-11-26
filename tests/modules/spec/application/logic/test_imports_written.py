"""A part's `imports` group, read by the parser: what it may import, each entry alone or marked types_only, what each
of its files must import one of, and its outside packages; every refusal of the group, of `may`'s marks and of
`must`, each at its address in fixed text."""
import pytest

from tests.modules.spec.profiles import layered, parsed, part_of, problems
from xarch.kernel.placement import EVERYTHING
from xarch.modules.spec.application.logic.imports_written import tier_accepted
from xarch.profile_values.placement import AcceptedImport, Target

NOT_A_REFERENCE = ("is not a reference: write parts.<part> or <word>.<part>, optionally followed by /<path> and "
                   ":<pattern>")

USE = "use holds, imports, litmus, name, optional, package_only, role, shared, tests, untested, uses"
"""What every unknown-key problem of a part ends with."""


def with_imports(part: str, imports) -> dict:
    document = layered()
    part_of(document, part)["imports"] = imports
    return document


def test_the_group_gives_what_the_old_keys_gave_for_the_same_lists():
    architecture = parsed(with_imports("store", {"may": ["parts.shared"], "must": ["parts.shared"], "libraries": ["sqlmodel"]}))
    assert architecture.rules["store"] == (Target("shared"),)
    assert architecture.parts["store"].imports_must == (Target("shared"),)
    assert architecture.imports_libraries["store"] == ("sqlmodel",)


@pytest.mark.parametrize("imports, rules", [
    pytest.param({"may": "everything"}, (Target(EVERYTHING),), id="may everything"),
    pytest.param({"may": []}, (), id="may nothing"),
    pytest.param({"libraries": ["sqlmodel"]}, (), id="libraries alone"),
])
def test_what_may_allows(imports, rules):
    assert parsed(with_imports("store", imports)).rules["store"] == rules


def test_a_part_with_no_imports_imports_only_itself_and_no_outside_package():
    document = layered()
    del part_of(document, "store")["imports"]
    architecture = parsed(document)
    assert architecture.rules["store"] == () and architecture.imports_libraries["store"] == ()


@pytest.mark.parametrize("imports, problem", [
    pytest.param({}, "parts.store.imports: says nothing: write may, must, libraries or accepted, or drop it", id="empty"),
    pytest.param(["shared"], "parts.store.imports: must be a map of may, must, libraries and accepted, such as {may: [parts.<part>]}",
                 id="a list"),
    pytest.param(True, "parts.store.imports: must be a map of may, must, libraries and accepted, such as {may: [parts.<part>]}",
                 id="true"),
    pytest.param("shared", "parts.store.imports: must be a map of may, must, libraries and accepted, such as {may: [parts.<part>]}",
                 id="a string"),
    pytest.param(None, "parts.store.imports: must be a map of may, must, libraries and accepted, such as {may: [parts.<part>]}",
                 id="null"),
    pytest.param({"never": "pure"}, "parts.store.imports: unknown key 'never': a key of uses, beside imports: write "
                 "uses: {never: <list>}; use accepted, libraries, may, must", id="never"),
    pytest.param({"types_only": ["shared"]}, "parts.store.imports: unknown key 'types_only': write it as the mode of "
                 "its entry in imports.may, such as [{parts.ports: types_only}]; use accepted, libraries, may, must", id="types_only"),
    pytest.param({"also": ["shared"]}, "parts.store.imports: unknown key 'also': use accepted, libraries, may, must", id="also"),
])
def test_the_group_is_refused_when_written_wrong(imports, problem):
    assert problems(with_imports("store", imports)) == [f"layered.yaml: {problem}"]


def test_a_marked_entry_is_a_target_of_may_and_a_marked_target():
    architecture = parsed(with_imports("service", {"may": ["module.store", {"parts.shared": "types_only"}]}))
    assert architecture.rules["service"] == (Target("store", "own"), Target("shared"))
    assert architecture.parts["service"].imports_types_only == (Target("shared"),)


@pytest.mark.parametrize("entry, marked", [
    pytest.param({"module.store": "types_only"}, Target("store", "own"), id="own instance"),
    pytest.param({"parts.store": "types_only"}, Target("store", "any"), id="any instance"),
    pytest.param({"module.store/rules:*Id": "types_only"}, Target("store", "own", ("rules",), "*Id"), id="path and pattern"),
])
def test_a_mark_keeps_the_scope_path_and_pattern_of_its_target(entry, marked):
    assert parsed(with_imports("service", {"may": [entry]})).parts["service"].imports_types_only == (marked,)


def test_two_marks_keep_the_order_of_may():
    architecture = parsed(with_imports("service", {"may": [{"module.store": "types_only"}, "module.api", {"parts.shared": "types_only"}]}))
    assert architecture.parts["service"].imports_types_only == (Target("store", "own"), Target("shared"))


def test_a_target_written_plain_and_marked_keeps_its_mark():
    architecture = parsed(with_imports("service", {"may": ["parts.shared", {"parts.shared": "types_only"}]}))
    assert architecture.parts["service"].imports_types_only == (Target("shared"),)


@pytest.mark.parametrize("entry, problem", [
    pytest.param({"module.store": "types"}, "{module.store: types}: no mode 'types': write types_only, or the reference alone",
                 id="another word"),
    pytest.param({"module.store": True}, "{module.store: true}: no mode True: write types_only, or the reference alone",
                 id="true"),
    pytest.param({"module.store": "types_only", "parts.shared": "types_only"},
                 "{module.store: types_only, parts.shared: types_only}: one reference per entry: write each in its own {...}",
                 id="two targets"),
    pytest.param({}, "{}: one reference per entry: write each in its own {...}", id="an empty map"),
    pytest.param({"everything": "types_only"}, "everything takes no mode: list the entries to give one a mode",
                 id="everything"),
    pytest.param({"repo": "types_only"}, "'repo' names no part 'repo'", id="an undeclared part"),
    pytest.param({3: "types_only"}, f"3 {NOT_A_REFERENCE}", id="no target"),
])
def test_a_mark_written_wrong_is_refused_at_may(entry, problem):
    assert problems(with_imports("service", {"may": [entry]})) == [f"layered.yaml: parts.service.imports.may: {problem}"]


@pytest.mark.parametrize("must, problem", [
    pytest.param([], "must be a list of targets such as [parts.<part>, <word>.<part>]", id="empty"),
    pytest.param("shared", "must be a list of targets such as [parts.<part>, <word>.<part>]", id="no list"),
    pytest.param([{"parts.shared": "types_only"}], "{parts.shared: types_only}: must takes references only, with no mode",
                 id="a mode"),
    pytest.param(["module.api"], "'module.api' is not in imports.may, so no file could import it: add it there, or "
                 "name a part the part may import", id="not in may"),
])
def test_must_is_refused_when_written_wrong(must, problem):
    document = with_imports("store", {"may": ["parts.shared"], "must": must})
    assert problems(document) == [f"layered.yaml: parts.store.imports.must: {problem}"]


def test_a_must_entry_equal_to_a_marked_entry_of_may_passes():
    architecture = parsed(with_imports("store", {"may": [{"parts.shared": "types_only"}], "must": ["parts.shared"]}))
    assert architecture.parts["store"].imports_must == (Target("shared"),)


def test_must_without_may_is_refused_entry_by_entry():
    assert problems(with_imports("store", {"must": ["parts.shared"]})) == [
        "layered.yaml: parts.store.imports.must: 'parts.shared' is not in imports.may, so no file could import it: add it "
        "there, or name a part the part may import"]


@pytest.mark.parametrize("key, text", [
    pytest.param("may_import", "moved in 0.3.0: write imports: {may: [...]}", id="may_import"),
    pytest.param("must_import", "moved in 0.3.0: write imports: {must: [...]}", id="must_import"),
    pytest.param("libraries", "moved in 0.3.0: write imports: {libraries: [...]}", id="libraries"),
    pytest.param("types_only", "moved in 0.3.0: write it as the mode of its entry in imports.may, such as "
                 "[{parts.ports: types_only}]", id="types_only"),
])
def test_each_old_key_of_a_part_is_refused_with_the_form_that_replaces_it(key, text):
    document = layered()
    part_of(document, "shared")[key] = ["api"]
    assert problems(document) == [f"layered.yaml: parts.shared: unknown key {key!r}: {text}; {USE}"]


def test_old_keys_written_together_give_one_problem_each_in_sorted_order():
    document = layered()
    part_of(document, "shared").update({"may_import": ["api"], "types_only": ["api"], "libraries": ["yaml"]})
    assert [problem.split(": unknown key ")[1].split("'")[1] for problem in problems(document)] == [
        "libraries", "may_import", "types_only"]


def test_a_retired_key_beside_the_group_is_its_own_problem_and_the_group_is_still_read():
    document = with_imports("store", {"may": ["repo"]})
    part_of(document, "store")["may_import"] = ["shared"]
    assert problems(document) == [
        f"layered.yaml: parts.store: unknown key 'may_import': moved in 0.3.0: write imports: {{may: [...]}}; {USE}",
        "layered.yaml: parts.store.imports.may: 'repo' names no part 'repo'"]


def test_a_standard_library_name_in_libraries_is_refused_at_imports_libraries():
    document = with_imports("store", {"may": ["parts.shared"], "libraries": ["json"]})
    assert problems(document) == [
        "layered.yaml: parts.store.imports.libraries: 'json' is in the standard library, which every part may import "
        "unless `reserved` names it"]


def test_a_never_list_beside_imports_written_as_no_map_names_no_package_and_says_nothing_of_it():
    document = with_imports("store", True)
    document["never"] = {"pure": ["time.time"]}
    part_of(document, "service")["uses"] = {"never": "pure"}
    assert problems(document) == [
        "layered.yaml: parts.store.imports: must be a map of may, must, libraries and accepted, such as {may: [parts.<part>]}"]


WHY = "the store reads the api's settings until they move"
ACCEPTED = {"file": "src/docs/store/repo.py", "import": "src/docs/api/settings.py:LIMIT", "why": WHY}


def test_accepted_reads_each_entry_as_the_file_what_it_imports_and_why():
    document = with_imports("store", {"may": ["parts.shared"],
                                      "accepted": [ACCEPTED, {**ACCEPTED, "import": "src/docs/api/"}]})
    assert parsed(document).parts["store"].imports_accepted == (
        AcceptedImport(("src", "docs", "store", "repo.py"), ("src", "docs", "api", "settings.py"), "LIMIT", WHY,
                       "src/docs/api/settings.py:LIMIT"),
        AcceptedImport(("src", "docs", "store", "repo.py"), ("src", "docs", "api"), "", WHY, "src/docs/api/"))


AT = "layered.yaml: parts.store.imports.accepted"


@pytest.mark.parametrize("accepted, found", [
    pytest.param([], [f"{AT}: must be a list of {{file, import, why}}, such as [{{file: <file of the part>, import: "
                      "<file or folder below the app>, why: <the reason>}]"], id="an empty list"),
    pytest.param(["src/docs/store/repo.py"], [f"{AT}.0: must be a map {{file, import, why}}"], id="no map"),
    pytest.param([{**ACCEPTED, "why": ""}], [f"{AT}.0.why: must be one line of text: why the part may import it"],
                 id="no reason"),
    pytest.param([{key: value for key, value in ACCEPTED.items() if key != "why"}], [f"{AT}.0: missing `why`"],
                 id="the reason left out"),
    pytest.param([{**ACCEPTED, "file": "src/docs/api/routes.py"}],
                 [f"{AT}.0.file: 'src/docs/api/routes.py' lies in part api, not in store: list it under the part it "
                  "lies in"], id="a file of another part"),
    pytest.param([{**ACCEPTED, "file": "notes/x.py"}],
                 [f"{AT}.0.file: 'notes/x.py' lies in no part, not in store: list it under the part it lies in"],
                 id="a file of no part"),
    pytest.param([{**ACCEPTED, "file": "app/src/docs/store/repo.py"}],
                 [f"{AT}.0.file: 'app/src/docs/store/repo.py' lies in no part: write it below the app "
                  "(src/docs/store/repo.py, not app/src/docs/store/repo.py)"],
                 id="a file of the part written with the app folder's name first"),
    pytest.param([{**ACCEPTED, "file": "src/src/docs/store/repo.py"}],
                 [f"{AT}.0.file: 'src/src/docs/store/repo.py' lies in no part, not in store: list it under the part "
                  "it lies in"],
                 id="a first step a part starts with is no app folder's name"),
    pytest.param([{**ACCEPTED, "import": "src/./api.py"}],
                 [f"{AT}.0.import: 'src/./api.py': must be a path below the app, such as documents/store"],
                 id="a step that is no name"),
    pytest.param([{**ACCEPTED, "import": "src/docs/api/settings.py:"}],
                 [f"{AT}.0.import: 'src/docs/api/settings.py:': write a name after `:`, or drop the `:`"],
                 id="a colon with no name"),
    pytest.param([{**ACCEPTED, "line": 3}], [f"{AT}.0: unknown key 'line': use file, import, why"], id="an unknown key"),
])
def test_an_entry_of_accepted_is_refused_with_why(accepted, found):
    assert problems(with_imports("store", {"may": ["parts.shared"], "accepted": accepted})) == found


def test_a_tier_reads_its_accepted_entries_with_or_without_an_import():
    found: list[str] = []
    entries = [{"file": "tests/x/test_a.py", "import": "store/db.py:connect", "why": "w"},
               {"file": "tests/x/test_b.py", "why": "v"}]
    assert tier_accepted(entries, "tiers.unit.accepted", found) == (
        AcceptedImport(("tests", "x", "test_a.py"), ("store", "db.py"), "connect", "w", "store/db.py:connect"),
        AcceptedImport(("tests", "x", "test_b.py"), (), "", "v", ""))
    assert found == []


@pytest.mark.parametrize("entries, problem", [
    pytest.param([], "tiers.unit.accepted: must be a list of {file, import, why}, such as [{file: <file of the part>, "
                     "import: <file or folder below the app>, why: <the reason>}]", id="empty"),
    pytest.param([{"why": "w"}], "tiers.unit.accepted.0: missing `file`", id="no file"),
    pytest.param([{"file": "tests/a.py", "why": "a\nb"}],
                 "tiers.unit.accepted.0.why: must be one line of text: why the tier accepts it", id="no line"),
])
def test_a_tier_accepted_entry_written_wrong_is_refused(entries, problem):
    found: list[str] = []
    assert tier_accepted(entries, "tiers.unit.accepted", found) == ()
    assert found == [problem]
