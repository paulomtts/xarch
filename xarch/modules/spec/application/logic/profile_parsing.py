"""A profile file, parsed and validated into an Architecture.

An Architecture, from a file that states each fact once, on the thing it is about. The keys and whether each is
enforced are in key_table, which the messages below read, and what each means in the format's data file (see
key_catalogue); the shape:

    name: <name>
    based_on: <bundled name>   optional; the bundled profile this one was copied from, which a report compares with
    language: <language>       optional; the language of the app: the name of a language xarch ships (the first by name
                               when left out), read from its data file
    testing: <preset> | {preset, beside, shared} | {files, declared, globals, skips, tables, mocks, beside, shared}
                               how the test framework names things; a preset is a name, alone or under preset, read
                               from data shipped with xarch, and a key of the framework beside it is refused; beside,
                               whether every test of a part sits beside the code it tests (a tier with a `folder`
                               keeps its tests below the tests folder, and no part may name it then); shared, the
                               folders and files below the tests folder (outside every tier's folder and the fakes')
                               whose test code a test of any tier may import besides its own folder's.
                               Required with `tiers` and with the guards scenario-coverage and stand-ins
    parts: {<folder>/: {<key of the part>, <folder>/, <file>, ...}, <file>: {role, ...}}
                               the folder tree of the app: a key ending in / is a folder of one or more steps, one
                               written `<word>` the repeating folder, one instance per name, the word what the docs
                               call one instance; a key holding a dot is a file; any other key is a key of the part
                               the folder or file is. A folder with a part's keys is a part, a file always is; a folder
                               with none is only a folder, its value one line of text (its note) or nothing. A part is
                               named by its folder's last step or its file's name before the first dot, or by `name`;
                               the reading order, a part before the parts inside it, is the order their litmus tests run
        name: <name>           the part's name, when its folder or file does not give it
        imports: {may, must, libraries}
                               what the part may import besides itself, which it always may: each entry a reference
                               (`parts.<part>` the part in every instance, `<word>.<part>` the importer's own
                               instance, `/<path>` below it) or one marked {<reference>: types_only}, or everything;
                               the targets each file must import one of; the outside packages by top-level import
                               name, none unless listed, everything leaving the part unchecked (see imports_written)
        uses: {never: <list>}  the name of a list under the top-level `never`, which the part never uses
        holds: {<kind>: {<setting>: <value>, ...}, ...}
                               the kinds its files may define at the top level, each with its settings (see
                               holds_written)
        tests: <tier> | untested: <reason>
                               one tier covers the part, or the reason none does; with `tiers`, one of the two
        package_only: true     the part is imported only as a package from outside it
    never: {<list>: [<name> | <list>, ...]}    named lists of what a part never uses; an entry naming another
                               list includes it
    reserved: {<module>: <reason>}             standard-library modules only the parts whose `imports.libraries` list them
                               may import
    layers: {<name>: [<part>, ...]}            chains of parts from the inside out: none imports one after it
    tiers: {<tier>: {proves, litmus, uses, plain_tables, folder, imports: {may, also, must, types_only}, docs}}
                               the kinds of test, in the order their litmus tests run. A tier with a `folder` below
                               the tests folder says in `imports.may` what the tests there may import; `imports.also`
                               what each of its tests may import beyond that or what the part it mirrors may;
                               `imports.must` the parts (`parts.<part>`) one of which each of its test files reaches;
                               `imports.types_only` the parts (`parts.<part>`) its tests may import only as types;
                               `uses: {apply_never: true}` holds its tests to the `uses.never` list of the part they
                               mirror; `docs` holds what only fills the generated docs
    fakes: {folder, for, prefix, tiers}        the folder of the test fakes below the tests folder, the parts they
                               stand in for, how a fake's name starts, and the tiers that may import them besides
                               those testing a part they stand in for
    guards: {<guard>: {...}}                   the pre-built checks in use; left out means off
    excluded: {<folder>: <reason>}             folders below the app that are not its source
    hints: {<rule id>: <text>}                 your own advice for a rule, shown after its built-in fix
    checks: {<id>: {read, in, keep, may_not, ..., message, fix, examples}}
                               checks of the profile's own, written in the words of the rules module's vocabulary
                               (see written_checks for the format, `xarch profile explain checks` for the words)
    files: {<path>: <from> | {from, pinned, fill}}  what `init` writes besides the docs
    docs: {entry, pages, naming, examples, example_notes}
                               everything that only fills the docs; `examples` lists folders next to the profile, each
                               an example project, whose every file is an example named by its path in the project
    review: {never, mask}      what `xarch review` may send: path patterns below the app of the files it never sends,
                               and text patterns it hides before it sends; `check` reads neither (see sending)
    evals: {placement: {lines, alike, examples}, <id>: {ask, answer, reads, ...}}
                               how review reads what it asks: the line of each part below which a file reads as doubtful
                               there, the groups of parts one file cannot tell apart, the examples placement is held to
                               besides the docs', and the evals of the profile's own; `check` never acts on it (see
                               evals)

Every problem found is collected, so one InvalidArchitecture lists them all, each naming the key by its address in the
file and saying what to write instead; a problem that makes the rest meaningless stops early.
"""
from __future__ import annotations

import re
from collections.abc import Collection, Mapping
from dataclasses import dataclass, replace
from typing import Any

from xarch.kernel.logic.names import is_name, outside_text
from xarch.kernel.logic.placement import root_of, stem
from xarch.kernel.logic.targets import outside_imports
from xarch.kernel.placement import EACH, EVERYTHING
from xarch.modules.spec.application.logic import imports_written as iw
from xarch.modules.spec.application.logic import never_lists as nl
from xarch.modules.spec.application.logic import parts_tree as pt
from xarch.modules.spec.application.logic import profile_checks as ck
from xarch.modules.spec.application.logic import profile_examples as ex
from xarch.modules.spec.application.logic import profile_needs as needs
from xarch.modules.spec.application.logic import written_checks as own_checks
from xarch.modules.spec.application.logic.evals import evals, unlike, unplaced
from xarch.modules.spec.application.logic.holds_written import holds as held_kinds
from xarch.modules.spec.application.logic.key_lookup import keys_of, names_of, required_of
from xarch.modules.spec.application.logic.language_file import first_language
from xarch.modules.spec.application.logic.sending import sending
from xarch.modules.spec.application.logic.targets_written import WORD, allowed_targets
from xarch.modules.spec.domain.errors import InvalidArchitecture
from xarch.modules.spec.domain.guards import GUARD, KEY, ORDER
from xarch.modules.spec.domain.profile_keys import (
    DEAD_CODE,
    DOCS,
    FAKES,
    MOCKS,
    NO_CALLBACKS,
    NO_DUPLICATES,
    NO_TWINS,
    PART_USES,
    PASS_THROUGH,
    PROFILE,
    SCENARIO_COVERAGE,
    TESTING,
    TIER,
    TIER_DOCS,
    TIER_IMPORTS,
    TIER_USES,
)
from xarch.modules.spec.domain.profile_keys import GUARD as GUARD_SCOPE
from xarch.modules.spec.domain.published import DEFAULT_TESTS
from xarch.modules.spec.domain.values import (
    Architecture,
    ArchitectureSource,
    DeadCode,
    Guard,
    Language,
    Layout,
    NoCallbacks,
    NoDuplicates,
    NoTwins,
    PackageOnly,
    Part,
    PassThrough,
    Subject,
    Tier,
    TierExample,
)
from xarch.profile_values.placement import Repeat
from xarch.profile_values.testing import Fakes, Framework, ScenarioCoverage, StandIns, TableForm

_REPEATING = re.compile(r"<([A-Za-z_][A-Za-z0-9_-]*)>")
_TIER_TEXTS = ("subject", "may_touch", "one_file_per", "cases_from", "data")
"""The keys under a tier's `docs` that hold one line of text each."""
_GUARDS = tuple(name for name in ORDER if name != KEY[PackageOnly])
_NEEDS_TESTING = (KEY[ScenarioCoverage], KEY[StandIns])
_LISTED = {PassThrough: (PASS_THROUGH, "the parts whose methods are listed when they only forward"),
           NoCallbacks: (NO_CALLBACKS, "the parts whose functions call none of their parameters annotated as callables")}
"""The guards whose one key is the parts they read, each with the scope of its keys and what its parts are."""
_PRESET_MAP = "{files, declared}"
_TIER_INSTEAD = "`tests: <tier>`, or `untested: <reason>`"
_SETTINGS = ("preset", "beside", "shared")
"""The keys of `testing` that are the project's settings, not the framework's: written beside preset, never refused."""


@dataclass(frozen=True)
class _Testing:
    """What `testing` says: how test files are named and tests declared and the table forms the framework writes, and,
    when written, how a mock is built; preset: the name of the preset it names, "" when the whole framework is written
    out."""
    framework: Framework
    mocks: StandIns | None
    preset: str = ""


@dataclass(frozen=True)
class _Layout:
    """The layout and what comes with it, built from the paths of the parts: the parts, the tree, the notes of the
    folders, and the repeating folders in the order they first appear."""
    parts: Mapping[str, Part]
    tree: Layout
    notes: Mapping[tuple[str, ...], str]
    repeats: tuple[Repeat, ...]


def parse_profile(document: Any, source: str, files: Collection[str] = (), presets: Mapping[str, Any] | None = None,
             bundled: Collection[str] = (), languages: Mapping[str, Language] | None = None) -> Architecture:
    """The architecture the document describes; raises InvalidArchitecture listing every problem. files are the files
    next to the profile file that it names, and every file below the folders it names, each as a path from the folder
    holding it (see profile_listing); presets are the documents of the `testing` presets by name; bundled are the
    names of the bundled profiles, which `based_on` may name; languages are the languages xarch ships, by name."""
    if not isinstance(document, Mapping):
        raise InvalidArchitecture(source, ["must be a mapping of keys"])
    tree = pt.parts_tree(document.get("parts", {}), _language(document, languages or {}, []))
    if tree.old:
        raise InvalidArchitecture(source, list(tree.old))
    problems: list[str] = []
    problems += _keys(document)
    name = document.get("name")
    if "name" in document and not ck.text(name):
        problems.append("`name` must be a non-empty string")
    language = _language(document, languages or {}, problems)
    shortfalls = needs.short(document, presets or {}, language)
    problems += needs.refused(shortfalls, language)
    based_on = _based_on(document["based_on"], bundled, problems) if "based_on" in document else ""
    never_lists = (nl.never_lists(document["never"], problems, language, _named_packages(document, language))
                   if "never" in document else {})
    problems += tree.problems
    specs = {part.name: part.keys for part in tree.parts}
    declared = set(specs)
    built = _layout(tree, problems)
    parts = built.parts
    words = tuple(repeat.word for repeat in built.repeats)
    examples = ex.example_files(document.get("docs", {}), files, problems, language)
    imports = {part: iw.group(specs[part], f"parts.{part}", problems) for part in parts}
    read = {part: iw.may(imports[part].get("may"), item, parts, declared, f"parts.{part}.imports.may", problems,
                         repeats=built.repeats)
            for part, item in parts.items()}
    rules = {part: allowed for part, (allowed, _) in read.items()}
    reserved = ck.reserved_modules(document["reserved"], problems, language) if "reserved" in document else {}
    libraries = {part: _imports_libraries(imports[part], f"parts.{part}.imports.libraries", problems, language, reserved)
                 for part in parts}
    parts = {part: replace(item, imports_must=iw.must(imports[part], item, parts, declared, rules[part], problems,
                                                      repeats=built.repeats),
                           imports_types_only=read[part][1]) for part, item in parts.items()}
    parts = {part: _substance(specs[part], item, declared, problems, words) for part, item in parts.items()}
    uses_never = _never_refs(specs, parts, never_lists, problems)
    layers = (ck.layer_chains(document["layers"], parts, declared, rules, problems, words=words) if "layers" in document
              else {})
    unread = frozenset(item.address for item in shortfalls if item.note is None)
    testing = _testing(document["testing"], presets or {}, problems, language, unread) if "testing" in document else None
    tiers = _tiers(document, specs, parts, declared, examples, problems, language, built.repeats)
    beside = _tests_beside(document, specs, tiers, problems)
    problems += [f"tiers.{tier.name}.plain_tables: needs a table form: the framework {_framework_named(testing)} "
                 "writes none in `testing.tables`" for tier in tiers
                 if tier.plain_tables and testing is not None and not testing.framework.tables]
    written_tiers = _tier_names(document["tiers"]) if isinstance(document.get("tiers"), Mapping) else []
    fakes = (_fakes(document["fakes"], parts, declared, problems, language, words, written_tiers) if "fakes" in document
             else None)
    problems += ck.folder_clashes(tiers, fakes)
    shared = _tests_shared(document, tiers, fakes, problems, language)
    guards = _guards(document.get("guards", {}), specs, parts, declared, tiers, fakes, testing, problems, language,
                     words, written_tiers)
    problems += _needs_testing(document)
    entry, pages, naming = _docs(document.get("docs", {}), declared, files, problems, words)
    parts = {part: replace(item, entry=True) if part == entry else item for part, item in parts.items()}
    written = ck.init_files(_bare_from(document.get("files", {})), pages, files, problems, "docs.pages", language)
    excluded = ck.excluded_folders(document["excluded"], built.tree, problems) if "excluded" in document else ()
    own = (own_checks.checks(document["checks"], declared, tiers, language, problems, words=words)
           if "checks" in document else {})
    hints = ck.rule_hints(document["hints"], problems, own) if "hints" in document else {}
    never, mask = sending(document["review"], problems) if "review" in document else ((), ())
    placement, placed, own_evals, alike = (evals(document["evals"], declared, language, problems, words=words)
                                           if "evals" in document else ({}, ((), ()), {}, ()))
    problems += unplaced(placed, {name: part.path for name, part in parts.items()}, language)
    problems += unlike(alike, {name: (frozenset(uses_never.get(name, ())),
                                      tuple((held.kind, held.immutable) for held in part.holds))
                               for name, part in parts.items()})
    if problems:
        raise InvalidArchitecture(source, problems)
    shown = ex.examples_of(examples, built.tree, parts, language)
    framework = replace(testing.framework, beside=beside, shared=shared) if testing else None
    return Architecture(name, built.tree, parts, rules, pages, shown, built.notes, layers, tuple(parts), naming, tiers,
                        libraries, guards, fakes, built.repeats, written, framework, uses_never, excluded, hints, based_on, language,
                        reserved, needs.approximate(shortfalls), own, never, mask, placement, own_evals, placed, alike)


def _keys(document: Mapping[Any, Any]) -> list[str]:
    """The keys of the file that are unknown, those xarch retired first, and those it is missing."""
    problems = ck.unknown_of(document, names_of(PROFILE), PROFILE)
    problems += [f"missing `{key}`" for key in required_of(PROFILE) if key not in document]
    return problems


def _language(document: Mapping[Any, Any], languages: Mapping[str, Language], problems: list[str]) -> Language:
    """The language the file names, the first of the languages by name when it names none; Language() when there are
    none to choose from."""
    name = document.get("language", first_language(languages))
    if not isinstance(name, str) or (name not in languages and (languages or "language" in document)):
        problems.append(f"language: {name!r} is not a language xarch reads: use {', '.join(sorted(languages))}")
        return Language()
    return languages.get(name, Language())


def _based_on(value: Any, bundled: Collection[str], problems: list[str]) -> str:
    """The profile the file says it is based on: a bundled name, or the path of a profile file, which is taken as
    written and read by no one here."""
    use = f": use {', '.join(bundled)}" if bundled else ""
    if not isinstance(value, str) or not value:
        problems.append(f"based_on: must be the name of a bundled profile or the path of a profile file{use}")
    elif ArchitectureSource.names_a_file(value):
        return value
    elif value not in bundled:
        problems.append(f"based_on: no bundled profile {value!r}{use}")
    else:
        return value
    return ""


def _bare_from(value: Any) -> Any:
    """A bare string, where a mapping with `from` is expected, is that `from`."""
    if not isinstance(value, Mapping):
        return value
    return {key: {"from": item} if isinstance(item, str) else item for key, item in value.items()}


def _layout(tree: pt.PartsTree, problems: list[str]) -> _Layout:
    """The parts that place validly, in reading order, and the layout they make; then the folders that are no part,
    added after them as the folders of the parts were before 0.3.0, so the layout keeps that order, with their notes."""
    parts: dict[str, Part] = {}
    layout: Layout = {}
    notes: dict[tuple[str, ...], str] = {}
    repeats: list[Repeat] = []
    owners: dict[tuple[str, ...], str] = {}
    for entry in sorted(tree.parts, key=lambda part: part.order):
        where = f"parts.{entry.name}"
        problems += _own_problems(entry)
        if len(entry.words) > 1:
            problems.append(f"{where}: '{entry.shown}' has two repeating steps, <{entry.words[0]}> and "
                            f"<{entry.words[1]}>: a repeating folder cannot sit inside another, so give each its own "
                            "folder")
            continue
        word = entry.words[0] if entry.words else ""
        if not _repeats_alike(entry.name, entry.steps, word, repeats, owners, f"{where}: '{entry.shown}'", problems):
            continue
        _insert(layout, entry.steps, entry.file, entry.name, owners)
        parts[entry.name] = Part(entry.name, entry.steps, ck.string(entry.keys.get("role")),
                                 ck.string(entry.keys.get("litmus")), False,
                                 entry.keys["untested"] if ck.line(entry.keys.get("untested")) else "")
    for folder in tree.folders:
        _add_folder(layout, notes, folder)
    return _Layout(parts, layout, notes, tuple(repeats))


def _own_problems(entry: pt.TreePart) -> list[str]:
    """What is wrong with the values of the part's own keys that the layout reads."""
    where, spec, problems = f"parts.{entry.name}", entry.keys, []
    for key in ("role", "litmus"):
        if key in spec and not isinstance(spec[key], str):
            problems.append(f"{where}.{key}: must be a string")
    if "untested" in spec and not ck.line(spec["untested"]):
        problems.append(f"{where}.untested: must be one line of text: why no tier tests the part")
    if "package_only" in spec and not isinstance(spec["package_only"], bool):
        problems.append(f"{where}.package_only: must be true or false")
    return problems


def _repeats_alike(name: str, steps: tuple[str, ...], word: str, repeats: list[Repeat],
                   owners: dict[tuple[str, ...], str], where: str, problems: list[str]) -> bool:
    """A word repeats in one folder, and a folder is repeated by one word."""
    root = root_of(steps)
    if root is None:
        return True
    here = next((repeat for repeat in repeats if repeat.root == root), None)
    named = next((repeat for repeat in repeats if repeat.word == word), None)
    if here is not None and here.word != word:
        problems.append(f"{where} calls the repeating folder <{word}>, but part '{owners[(*root, EACH)]}' called it "
                        f"<{here.word}> in the same folder '{'/'.join(root)}': two words may not share a parent, use "
                        "one word")
    elif named is not None and named.root != root:
        problems.append(f"{where} repeats <{word}> below '{'/'.join(root)}', but part '{owners[(*named.root, EACH)]}' "
                        f"repeats it below '{'/'.join(named.root)}': one word repeats in one folder, so give this one a "
                        "word of its own")
    else:
        if here is None:
            repeats.append(Repeat(word, root))
            owners[(*root, EACH)] = name
        return True
    return False


def _insert(tree: Layout, steps: tuple[str, ...], file: bool, name: str, owners: dict[tuple[str, ...], str]) -> None:
    """The part's steps in the layout: a folder for every step, the last a file when the part is one."""
    here = tree
    for step in steps[:-1]:
        here = here.setdefault(step, {})
    if file:
        here[steps[-1]] = None
    else:
        here.setdefault(steps[-1], {})
    for i in range(1, len(steps) + 1):
        owners.setdefault(steps[:i], name)


def _add_folder(tree: Layout, notes: dict[tuple[str, ...], str], folder: pt.TreeFolder) -> None:
    """The folder that is no part in the layout, and its note, if it has one, in the notes."""
    here = tree
    for step in folder.steps:
        here = here.setdefault(step, {})
    if folder.note:
        notes[folder.steps] = folder.note


def _imports_libraries(written: Mapping[Any, Any], where: str, problems: list[str], language: Language,
                       reserved: Mapping[str, str]) -> tuple[str, ...]:
    """The outside packages the part's `imports` group lists, and the reserved modules it may import: none unless it
    lists them; (EVERYTHING,) leaves them unchecked."""
    if "libraries" not in written:
        return ()
    value = written["libraries"]
    if value == WORD:
        return (EVERYTHING,)
    if not isinstance(value, list):
        problems.append(f"{where}: must be a list of top-level import names such as [sqlmodel], or {WORD}")
        return ()
    return ck.package_names(value, where, problems, language, reserved) or ()


def _named_packages(document: Mapping[Any, Any], language: Language) -> dict[str, str]:
    """Each package the profile names, by the key of the first place naming it: the parts' `imports.libraries` in
    reading order, then `reserved`. Read silently, and only from an `imports` that is a map: each is said
    at its own place."""
    reserved = ck.reserved_modules(document["reserved"], [], language) if "reserved" in document else {}
    named: dict[str, str] = {}
    for part in pt.parts_tree(document.get("parts"), language).parts:
        written = part.keys.get("imports")
        found = (_imports_libraries(written, f"parts.{part.name}.imports.libraries", [], language, reserved)
                 if isinstance(written, Mapping) else ())
        named |= {package: f"parts.{part.name}.imports.libraries" for package in found
                  if package != EVERYTHING and package not in named}
    named |= {module: "reserved" for module in reserved if module not in named}
    return named


def _never_refs(specs: dict[str, Any], parts: dict[str, Part],
                never_lists: dict[str, tuple[tuple[str, ...], ...] | None] | None,
                problems: list[str]) -> dict[str, tuple[tuple[str, ...], ...]]:
    """What each part whose `uses` names a list under `never` never uses; when `never` is no mapping, a part's list
    says nothing more."""
    uses_never: dict[str, tuple[tuple[str, ...], ...]] = {}
    for name in parts:
        spec = specs[name]
        if "uses" not in spec:
            continue
        uses = _group(spec["uses"], PART_USES, "{never: pure}", f"parts.{name}.uses", problems)
        if "never" not in uses or never_lists is None:
            continue
        ref, where = uses["never"], f"parts.{name}.uses.never"
        if isinstance(ref, list):
            problems.append(f"{where}: names one list under never: write the name of a list, such as pure; a list may "
                            "include others")
        elif not isinstance(ref, str):
            problems.append(f"{where}: must be the name of a list under `never`")
        elif ref not in never_lists:
            use = f"use {', '.join(sorted(never_lists))}, or write it" if never_lists else "write it"
            problems.append(f"{where}: no list named {ref!r}: {use} under `never`")
        elif never_lists[ref] is not None:
            uses_never[name] = never_lists[ref]
    return uses_never


def _group(value: Any, scope: str, example: str, where: str, problems: list[str]) -> Mapping[Any, Any]:
    """What a group of keys a part or a tier opens holds, such as `uses`: {} when it is no mapping or says nothing, each
    said at where; its unknown keys are refused under its own scope."""
    names = ", ".join(key.name for key in keys_of(scope))
    if not isinstance(value, Mapping):
        problems.append(f"{where}: must be a mapping {{{names}}}, such as {example}")
        return {}
    if not value:
        problems.append(f"{where}: says nothing: write {names}, or drop it")
        return {}
    problems += ck.unknown_keys(value, names_of(scope), where, scope)
    return value


def _testing(value: Any, presets: Mapping[str, Any], problems: list[str], language: Language,
             unread: Collection[str] = frozenset()) -> _Testing | None:
    """How the test framework names things: the map in the file, or the one a preset holds, named by its name or under
    `preset`, validated the same; a preset's map that names a preset in turn, or says beside, is refused. Once the
    framework and its table forms are sound, each callee of a table `call` form must be listed by a `call` form of
    `testing.declared` (see _undeclared); unread are the addresses the needs of the profile refuse."""
    preset = ""
    if isinstance(value, Mapping) and "preset" in value:
        preset = _preset_of(value, presets, problems)
        if not preset:
            return None
        value = presets[preset]
    elif isinstance(value, str):
        if value not in presets:
            problems.append(f"testing: no preset {value!r}: {_instead(presets)}")
            return None
        preset, value = value, presets[value]
    elif not isinstance(value, Mapping):
        problems.append(f"testing: must be a preset name or a mapping {_PRESET_MAP}: the patterns of a test file's name "
                        "and the forms that declare a test")
        return None
    if preset and isinstance(value, Mapping) and "preset" in value:
        problems.append(f"testing.preset: the preset {preset} names a preset: a preset writes the whole framework")
        return None
    for key in _SETTINGS[1:]:
        if preset and isinstance(value, Mapping) and key in value:
            problems.append(f"testing.{key}: the preset {preset} says {key}: a preset writes the framework; write "
                            f"{key} in the profile, beside preset")
            return None
    count = len(problems)
    framework = ck.framework_patterns(value, problems, "testing", names_of(TESTING), language, TESTING)
    tables = ck.table_forms(value["tables"], "testing.tables", problems, language) if "tables" in value else ()
    if len(problems) == count and framework is not None and tables is not None:
        problems += _undeclared(framework, tables, unread, language)
    mocks = _mocks(value["mocks"], problems, language, unread) if "mocks" in value else None
    if len(problems) != count or framework is None or tables is None:
        return None
    return _Testing(replace(framework, tables=tables), mocks, preset)


def _undeclared(framework: Framework, tables: tuple[TableForm, ...], unread: Collection[str],
                language: Language) -> list[str]:
    """A problem for each callee of a table `call` form that no `call` form of `testing.declared` lists, the forms in
    the order of the list and the callees in the order each writes them; none for a form whose `call` the language's
    reader does not read (unread), which the needs of the profile refuse already."""
    declared = {callee for form in framework.declared for callee in form.call}
    return [f"testing.tables.{index}.call: `{outside_text(callee, language.checked.member)}` declares no test: list it "
            "under a `call` form of `testing.declared`" for index, form in enumerate(tables)
            if f"testing.tables.{index}.call" not in unread for callee in form.call if callee not in declared]


def _instead(presets: Mapping[str, Any]) -> str:
    """What a `testing` that names no preset is told to write: a preset that ships, when one does, or the map."""
    names = f"use {', '.join(sorted(presets))}, or write" if presets else "write"
    return f"{names} the map {_PRESET_MAP}"


def _preset_of(value: Mapping[Any, Any], presets: Mapping[str, Any], problems: list[str]) -> str:
    """The name of the preset a map of `testing` names under `preset`; "" when the map has a problem: a key it does
    not know, a preset that is no name or does not ship, or a key of the framework written beside it, in that order."""
    count = len(problems)
    problems += ck.unknown_keys(value, names_of(TESTING), "testing", TESTING)
    name = value["preset"]
    if not isinstance(name, str):
        problems.append(f"testing.preset: must be a preset name: {_instead(presets)}")
    elif name not in presets:
        problems.append(f"testing.preset: no preset {name!r}: {_instead(presets)}")
    named = name if isinstance(name, str) and name in presets else ""
    problems += [_beside(key.name, named, presets) for key in keys_of(TESTING)
                 if key.name not in _SETTINGS and key.name in value]
    return named if len(problems) == count else ""


def _beside(key: str, preset: str, presets: Mapping[str, Any]) -> str:
    """The problem of a key of the framework written beside `preset`, which names the preset given, "" for none."""
    instead = "drop it, or drop preset and write the whole map"
    if not preset:
        return f"testing.{key}: written beside preset: {instead}"
    gives = "gives" if isinstance(presets[preset], Mapping) and key in presets[preset] else "writes no"
    return f"testing.{key}: the preset {preset} {gives} {key}: {instead}"


def _tests_beside(document: Mapping[Any, Any], specs: dict[str, Any], tiers: tuple[Tier, ...],
                  problems: list[str]) -> bool:
    """Whether every test of a part sits beside the code it tests, as the map `testing` writes it (`beside`); false
    when it does not say. A value that is no bool, beside with no `tiers`, and each part, in the order of the file,
    that names in `tests` a tier with a `folder` are refused."""
    written = document.get("testing")
    if not isinstance(written, Mapping) or "beside" not in written:
        return False
    beside = written["beside"]
    if not isinstance(beside, bool):
        problems.append("testing.beside: must be true or false: whether every test of a part sits beside the code it "
                        "tests")
        return False
    if not beside:
        return False
    if "tiers" not in document:
        problems.append("testing.beside: the profile has no `tiers`: add them, or drop the key")
        return False
    folders = {tier.name: tier.folder for tier in tiers if tier.folder is not None}
    for name, spec in specs.items():
        tier = spec.get("tests") if isinstance(spec, Mapping) else None
        if isinstance(tier, str) and tier in folders:
            problems.append(f"tiers.{tier}: parts.{name} says tests: {tier}, and {tier} keeps its tests in "
                            f"{'/'.join((DEFAULT_TESTS, *folders[tier]))}: under testing.beside a part's tests sit "
                            "beside its code; give the part a tier with no folder")
    return True


def _tests_shared(document: Mapping[Any, Any], tiers: tuple[Tier, ...], fakes: Fakes | None, problems: list[str],
                  language: Language) -> tuple[tuple[str, ...], ...]:
    """The folders and files below the tests folder whose test code a test of any tier may import, as the map `testing`
    writes them (`shared`), each as its steps; none when it does not say. A value that is no list of paths below the
    tests folder, shared with no `tiers`, and each entry that lies inside, or holds, a tier's folder or the fakes'
    folder are refused."""
    written = document.get("testing")
    if not isinstance(written, Mapping) or "shared" not in written:
        return ()
    value = written["shared"]
    entries = [tuple(item.split("/")) if ck.line(item) and not item.startswith("/") else ()
               for item in value] if isinstance(value, list) else [()]
    if any(not steps or any(step in ("", ".", "..") or EACH in step for step in steps) for steps in entries):
        problems.append("testing.shared: must be a list of folders or files below the tests folder, such as "
                        f"[support, helpers{language.checked.extension}]: each relative, with no `..`, no empty step "
                        "and no `*`")
        return ()
    if entries and "tiers" not in document:
        problems.append("testing.shared: the profile has no `tiers`: add them, or drop the key")
        return ()
    clashes = ck.shared_clashes(tuple(entries), tiers, fakes)
    problems += clashes
    return () if clashes else tuple(entries)


def _framework_named(testing: _Testing) -> str:
    """How a problem names the framework `testing` says: the preset it names, or `testing` itself when written out."""
    return f"`{testing.preset}`" if testing.preset else "of `testing`"


def _mocks(value: Any, problems: list[str], language: Language,
           unread: Collection[str] = frozenset()) -> StandIns | None:
    """How a mock is built, and the ways a call that builds one names its spec; an entry of specs the language does not
    write is refused, unless the needs of the profile refuse it already (unread)."""
    where = "testing.mocks"
    if not isinstance(value, Mapping):
        problems.append(f"{where}: must be a mapping {{calls, specs}}, and optionally autospec and fixtures: the dotted "
                        "names of the calls that build a mock, the ways a mock is given its spec, in order, and the "
                        "parameters of a test function whose methods build one")
        return None
    count = len(problems)
    problems += ck.unknown_keys(value, names_of(MOCKS), where, MOCKS)
    problems += [f"{where}: missing `{key}`" for key in required_of(MOCKS) if key not in value]
    calls = ck.outside_names(value["calls"], f"{where}.calls", problems, language) if "calls" in value else None
    autospec = ck.outside_names(value["autospec"], f"{where}.autospec", problems, language) if "autospec" in value else ()
    problems += [f"{where}.autospec: {outside_text(name, language.checked.member)!r} is also listed in calls"
                 for name in autospec or () if calls and name in calls]
    specs = ck.spec_entries(value["specs"], f"{where}.specs", problems, language) if "specs" in value else None
    problems += ck.unwritten_specs(specs, f"{where}.specs", unread, language) if specs is not None else []
    fixtures = (ck.fixtures(value["fixtures"], f"{where}.fixtures", problems, language, "calls")
                if "fixtures" in value else ())
    if len(problems) != count or calls is None or autospec is None or specs is None or fixtures is None:
        return None
    return StandIns(calls, autospec, specs, fixtures)


def _tiers(document: Mapping[Any, Any], specs: dict[str, Any], parts: dict[str, Part], declared: set[str],
           examples: ex.Examples, problems: list[str], language: Language, repeats: tuple[Repeat, ...]) -> tuple[Tier, ...]:
    """The tiers in the order of the file, each with the parts that say they are tested by it; then the coverage:
    with tiers, every part names one or is untested, and without them none names one."""
    value = document.get("tiers")
    usable = isinstance(value, Mapping) and bool(value)
    if "tiers" in document and not usable:
        problems.append("tiers: must be a mapping of tier names to {proves, litmus, ...}, in the order their litmus "
                        "tests run")
    names = _tier_names(value) if usable else None
    assigned = _coverage(specs, parts, names, "tiers" in document, problems)
    if not usable:
        return ()
    tiers: list[Tier] = []
    for name, spec in value.items():
        if not ck.line(name):
            problems.append(f"tiers: {name!r} is not a tier name: one line of text")
            continue
        subject = tuple(Subject(part) for part in parts if assigned.get(part) == name)
        tier = _tier(name, spec, subject, parts, declared, examples, problems, language, repeats)
        if tier is not None:
            tiers.append(tier)
    return tuple(tiers)


def _tier_names(tiers: Mapping[Any, Any]) -> list[str]:
    return [name for name in tiers if ck.line(name)]


def _coverage(specs: dict[str, Any], parts: dict[str, Part], names: list[str] | None, has_tiers: bool,
              problems: list[str]) -> dict[str, str]:
    """The tier each part names, by part; a part that fits neither way is reported."""
    assigned: dict[str, str] = {}
    for name in parts:
        spec, where = specs[name], f"parts.{name}"
        named, untested = "tests" in spec, "untested" in spec
        if named and untested:
            problems.append(f"{where}: has `tests` and is `untested`: drop one")
        if named and not has_tiers:
            problems.append(f"{where}.tests: the profile has no `tiers`: add them, or drop the key")
        elif named and names is not None:
            tier = spec["tests"]
            use = f"use {', '.join(names)}"
            if not isinstance(tier, str):
                problems.append(f"{where}.tests: must be the name of a tier: {use}")
            elif tier not in names:
                folder = ": it names a tier of `tiers`, not a folder" if "/" in tier else ""
                problems.append(f"{where}.tests: no tier named {tier!r}{folder}: {use}")
            else:
                assigned[name] = tier
        elif not named and not untested and names is not None:
            problems.append(f"{where}: no tier tests it: give it {_TIER_INSTEAD}")
    return assigned


def _tier(name: str, spec: Any, subject: tuple[Subject, ...], parts: dict[str, Part], declared: set[str],
          examples: ex.Examples, problems: list[str], language: Language, repeats: tuple[Repeat, ...]) -> Tier | None:
    where = f"tiers.{name}"
    if not isinstance(spec, Mapping):
        problems.append(f"{where}: must be a mapping, {{}} if it takes nothing")
        return None
    count = len(problems)
    problems += ck.unknown_keys(spec, names_of(TIER), where, TIER)
    if "proves" in spec and not ck.line(spec["proves"]):
        problems.append(f"{where}.proves: must be one line of text")
    if "litmus" in spec and not ck.text(spec["litmus"]):
        problems.append(f"{where}.litmus: must be text: the question that tells a test belongs to the tier")
    uses = _group(spec["uses"], TIER_USES, "{apply_never: true}", f"{where}.uses", problems) if "uses" in spec else {}
    held = uses.get("apply_never", False)
    if not isinstance(held, bool):
        problems.append(f"{where}.uses.apply_never: must be true or false: whether its tests are held to the "
                        "`uses.never` list of the part they mirror")
    plain = spec.get("plain_tables", False)
    if not isinstance(plain, bool):
        problems.append(f"{where}.plain_tables: must be true or false: whether every table test of the tier holds no "
                        "branch in its body")
    imports = iw.group(spec, where, problems, TIER_IMPORTS, "{must: [parts.<part>]}")
    types_only = (iw.tier_parts(imports["types_only"], declared, f"{where}.imports.types_only", problems)
                  if "types_only" in imports else [])
    folder = ck.tier_folder(spec["folder"], parts, f"{where}.folder", problems, language) if "folder" in spec else None
    if "folder" not in spec and "may" in imports:
        problems.append(f"{where}.imports.may: only a tier with a `folder` has an allowance of its own: without one, "
                        "its tests import what the part they mirror may")
    allowance = (allowed_targets(imports.get("may"), None, parts, declared, f"{where}.imports.may", problems,
                                 repeats=repeats) if "folder" in spec else None)
    also = allowed_targets(imports.get("also"), None, parts, declared, f"{where}.imports.also", problems,
                           mirrored=tuple(parts[tested.part].path for tested in subject), repeats=repeats)
    docs = _tier_docs(spec["docs"], folder, examples, f"{where}.docs", problems, language) if "docs" in spec else {}
    reach = (iw.tier_parts(imports["must"], declared, f"{where}.imports.must", problems)
             if "must" in imports else [])
    if len(problems) != count:
        return None
    return Tier(name, subject, spec.get("proves", ""), docs.get("may_touch", ""), spec.get("litmus", "").strip("\n"),
                docs.get("subject", ""), docs.get("one_file_per", ""), docs.get("cases_from", ""), docs.get("data", ""),
                docs.get("example"), docs.get("helpers", ()), tuple(p for p in types_only if p in parts), held, folder,
                allowance, tuple(p for p in reach if p in parts), plain, also)


def _tier_docs(value: Any, folder: tuple[str, ...] | None, examples: ex.Examples, where: str,
               problems: list[str], language: Language) -> dict[str, Any]:
    """What a tier says only for the docs: its texts, its example and its helpers."""
    if not isinstance(value, Mapping):
        problems.append(f"{where}: must be a mapping of {{{', '.join(key.name for key in keys_of(TIER_DOCS))}}}")
        return {}
    problems += ck.unknown_keys(value, names_of(TIER_DOCS), where, TIER_DOCS)
    problems += [f"{where}.{key}: must be one line of text" for key in _TIER_TEXTS if key in value and not ck.line(value[key])]
    found: dict[str, Any] = {key: value[key] for key in _TIER_TEXTS if key in value and ck.line(value[key])}
    if "example" in value:
        example = ex.example_of(value["example"], examples, f"{where}.example", problems, language)
        if example is not None and folder is not None and example.path[1:-1][:len(folder)] != folder:
            problems.append(f"{where}.example: '{'/'.join(example.path)}' is not inside the tier's folder "
                            f"'{'/'.join(folder)}' below the tests folder: the docs would show a place `check` places "
                            "in no tier")
        found["example"] = example
    if "helpers" in value:
        found["helpers"] = _helpers(value["helpers"], examples, f"{where}.helpers", problems, language)
    return found


def _helpers(value: Any, examples: ex.Examples, where: str, problems: list[str],
             language: Language) -> tuple[TierExample, ...]:
    if not isinstance(value, list):
        problems.append(f"{where}: must be a list of paths in an example project")
        return ()
    helpers = [ex.example_of(item, examples, f"{where}[{i}]", problems, language) for i, item in enumerate(value)]
    return tuple(helper for helper in helpers if helper is not None)


def _fakes(value: Any, parts: dict[str, Part], declared: set[str], problems: list[str],
           language: Language, words: Collection[str], tiers: Collection[str] = ()) -> Fakes | None:
    where = "fakes"
    if not isinstance(value, Mapping):
        problems.append(f"{where}: must be a mapping {{folder, for}} and optionally prefix and tiers: the folder of the "
                        "fakes below the tests folder, the parts they stand in for, how a fake's name starts, and the "
                        "tiers that may import them besides")
        return None
    count = len(problems)
    problems += ck.unknown_keys(value, names_of(FAKES), where, FAKES)
    problems += [f"{where}: missing `{key}`" for key in required_of(FAKES) if key not in value]
    prefix = value.get("prefix", "")
    if "prefix" in value and (not isinstance(prefix, str) or not is_name(prefix, language.names)):
        problems.append(f"{where}.prefix: must be the start of a class name, such as Fake")
    folder = value.get("folder")
    steps = tuple(folder.split("/")) if ck.line(folder) and not folder.startswith("/") else ()
    if "folder" in value and (not steps or any(step in ("", ".", "..") or EACH in step for step in steps)):
        problems.append(f"{where}.folder: must be a folder below the tests folder, such as fakes: relative, with no "
                        "`..`, no empty step and no `*`")
    names = ck.part_names(value["for"], declared, f"{where}.for", problems, words=words) if "for" in value else []
    opened = _fakes_tiers(value["tiers"], tiers, problems) if "tiers" in value else ()
    if len(problems) != count:
        return None
    return Fakes(steps, tuple(n for n in names if n in parts), prefix, opened)


def _fakes_tiers(value: Any, tiers: Collection[str], problems: list[str]) -> tuple[str, ...]:
    """The tiers `fakes.tiers` lets import the fakes besides those testing a part they stand in for, in the order
    written; a value that is no list of names, a tier the profile does not have and one listed twice are refused."""
    where = "fakes.tiers"
    if not isinstance(value, list) or not value or not all(isinstance(name, str) and name for name in value):
        problems.append(f"{where}: must be a list of tier names: the tiers that may import the fakes")
        return ()
    found: list[str] = []
    for name in value:
        if name not in tiers:
            problems.append(f"{where}: no tier named {name!r}: use {', '.join(sorted(tiers)) or 'a tier of `tiers`'}")
        elif name in found:
            problems.append(f"{where}: {name!r} is listed twice")
        else:
            found.append(name)
    return tuple(found)


def _guards(value: Any, specs: dict[str, Any], parts: dict[str, Part], declared: set[str], tiers: tuple[Tier, ...],
            fakes: Fakes | None, testing: _Testing | None, problems: list[str],
            language: Language, words: Collection[str], written_tiers: Collection[str]) -> tuple[Guard, ...]:
    guards: list[Guard] = []
    package_only = tuple(name for name in parts if specs[name].get("package_only") is True)
    if package_only:
        guards.append(PackageOnly(package_only))
    if not isinstance(value, Mapping):
        problems.append("guards: must be a mapping of guard names to their parameters, such as {no-comments: {}}")
        return tuple(guards)
    for name, spec in value.items():
        where = f"guards.{name}"
        kind = GUARD.get(name)
        if kind is PackageOnly:
            problems.append(f"{where}: a fact about a part: write `package_only: true` on each part")
        elif name not in _GUARDS:
            problems.append(f"guards: unknown guard {name!r}: {ck.advice(GUARD_SCOPE, str(name), _GUARDS)}")
        elif kind is ScenarioCoverage:
            guard = _scenario_coverage(spec, parts, declared, tiers, testing, where, problems, language, words,
                                       written_tiers)
            if guard is not None:
                guards.append(guard)
        elif kind is StandIns:
            guard = _stand_ins(spec, fakes, testing, where, problems, language)
            if guard is not None:
                guards.append(guard)
        elif kind is NoDuplicates:
            guards.append(_no_duplicates(spec, where, problems))
        elif kind is NoTwins:
            guards.append(_no_twins(spec, declared, parts, where, problems, words))
        elif kind in _LISTED:
            listed = _listed_parts(spec, declared, parts, where, *_LISTED[kind], problems, words)
            if listed is not None:
                guards.append(kind(listed))
        elif kind is DeadCode:
            guard = _dead_code(spec, fakes, where, problems, language)
            if guard is not None:
                guards.append(guard)
        elif spec not in ({}, None):
            problems.append(f"{where}: takes no parameters: write {{}}")
        else:
            guards.append(kind())
    return tuple(guards)


def _scenario_coverage(spec: Any, parts: dict[str, Part], declared: set[str], tiers: tuple[Tier, ...],
                       testing: _Testing | None, where: str, problems: list[str],
                       language: Language, words: Collection[str],
                       written_tiers: Collection[str]) -> ScenarioCoverage | None:
    if not isinstance(spec, Mapping):
        problems.append(f"{where}: must be a mapping {{results, tier, suffix, columns, file}}: the part holding the "
                        "result unions, the tier whose test files hold their tables, how a union's name ends, the "
                        "three names of a table's parameters (its state, its command and its result), and the name "
                        "of a use case's test file")
        return None
    count = len(problems)
    problems += ck.unknown_keys(spec, names_of(SCENARIO_COVERAGE), where, SCENARIO_COVERAGE)
    forms = testing is None or bool(testing.framework.tables)
    required = {*required_of(SCENARIO_COVERAGE), *(("columns",) if forms else ())}
    problems += [f"{where}: missing `{key}`" for key in sorted(required) if key not in spec]
    if not forms and "columns" in spec:
        problems.append(f"{where}.columns: drop `columns`: the framework writes no table, so each result is its own "
                        "test")
    if len(problems) != count:
        return None
    ck.scenario_places(spec["results"], spec["tier"], spec["suffix"], parts, declared, tiers, where, problems,
                       language, words=words, written=written_tiers)
    columns = ck.column_names(spec["columns"], f"{where}.columns", problems, language) if forms else ()
    framework = testing.framework if testing is not None else None
    file = ck.use_case_file(spec["file"], framework, f"{where}.file", problems, language, "testing.files")
    if len(problems) != count or columns is None or file is None or testing is None:
        return None
    return ScenarioCoverage(spec["results"], spec["tier"], spec["suffix"], columns, file)


def _stand_ins(spec: Any, fakes: Fakes | None, testing: _Testing | None, where: str,
               problems: list[str], language: Language) -> StandIns | None:
    if spec not in ({}, None):
        problems.append(f"{where}: takes no parameters: write {{}}")
        return None
    if fakes is None or not fakes.prefix:
        problems.append(f"{where}: needs `fakes` with a `prefix`, such as {{folder: fakes, for: [<part>], prefix: "
                        f"Fake}}: the parts whose {language.interface_name}s the fakes stand in for, where they live "
                        "and how a fake is named")
        return None
    if testing is not None and testing.mocks is None:
        problems.append(f"{where}: needs `testing.mocks`: the calls that build a mock and the keywords a mock is "
                        "given its spec by")
    return testing.mocks if testing is not None else None


def _dead_code(spec: Any, fakes: Fakes | None, where: str, problems: list[str],
               language: Language) -> DeadCode | None:
    if spec is None:
        spec = {}
    if not isinstance(spec, Mapping):
        problems.append(f"{where}: must be a mapping {{untested: true|false, tests_only: true|false, known: "
                        "[<file>:<name>, ...]}, or {}")
        return None
    count = len(problems)
    problems += ck.unknown_keys(spec, names_of(DEAD_CODE), where, DEAD_CODE)
    untested = spec.get("untested", False)
    if not isinstance(untested, bool):
        problems.append(f"{where}.untested: must be true or false")
    tests_only = spec.get("tests_only", False)
    if not isinstance(tests_only, bool):
        problems.append(f"{where}.tests_only: must be true or false")
    known = _known(spec["known"], tests_only is True, f"{where}.known", problems, language) if "known" in spec else ()
    if len(problems) != count:
        return None
    if fakes is None:
        problems.append(f"{where}: needs `fakes`: it reads the {language.interface_name}s of the parts `fakes.for` "
                        "names and the classes in `fakes.folder`")
        return None
    return DeadCode(untested, tests_only, known)


def _known(value: Any, tests_only: bool, where: str, problems: list[str], language: Language) -> tuple[str, ...]:
    """The public names tests_only accepts as only the tests', each `<file below the app>:<name>`, each once."""
    example = f"documents/rules{language.checked.extension}:clean"
    if not tests_only:
        problems.append(f"{where}: needs `tests_only: true`: it names the public names that check accepts as only the "
                        "tests'")
        return ()
    if not isinstance(value, list):
        problems.append(f"{where}: must be a list of <file below the app>:<name>, such as [{example}]")
        return ()
    found: list[str] = []
    for item in value:
        file, _, name = item.rpartition(":") if isinstance(item, str) else ("", "", "")
        if not file or file.startswith("/") or stem(file.rsplit("/", 1)[-1], language.checked.marks) is None \
                or not is_name(name, language.names):
            problems.append(f"{where}: {item!r} is not <file below the app>:<name>, such as {example}")
        elif item in found:
            problems.append(f"{where}: {item!r} is listed twice")
        else:
            found.append(item)
    return tuple(found)


def _substance(spec: Any, part: Part, declared: set[str], problems: list[str], words: Collection[str]) -> Part:
    """The keys of a part that say what its code holds and how it is used: holds, with the settings of each kind it
    lists (see holds_written), and shared."""
    where = f"parts.{part.name}"
    if not isinstance(spec, Mapping):
        return part
    holds = held_kinds(spec["holds"], where, declared, problems, words=words) if "holds" in spec else ()
    shared = spec.get("shared")
    if shared is not None and not _whole(shared, 2):
        problems.append(f"{where}.shared: must be a whole number of users, at least 2, such as 2; leave it out for a "
                        "part that is not there to be shared")
        shared = None
    return replace(part, holds=holds, shared=shared)


def _no_duplicates(spec: Any, where: str, problems: list[str]) -> NoDuplicates:
    if spec in ({}, None):
        return NoDuplicates()
    if not isinstance(spec, Mapping):
        problems.append(f"{where}: must be a mapping {{min_statements: <number>}}, or {{}} for the default")
        return NoDuplicates()
    problems += ck.unknown_keys(spec, names_of(NO_DUPLICATES), where, NO_DUPLICATES)
    return NoDuplicates(_minimum(spec, "min_statements", NoDuplicates.min_statements, "statements", where, problems))


def _no_twins(spec: Any, declared: set[str], parts: dict[str, Part], where: str, problems: list[str],
              words: Collection[str]) -> NoTwins:
    if spec in ({}, None):
        return NoTwins()
    if not isinstance(spec, Mapping):
        problems.append(f"{where}: must be a mapping {{min_fields: <number>, min_renamed: <number>, min_subset: "
                        "<number>, translated: [<part>, ...]}, or {} for the default")
        return NoTwins()
    problems += ck.unknown_keys(spec, names_of(NO_TWINS), where, NO_TWINS)
    least = _minimum(spec, "min_fields", NoTwins.min_fields, "fields", where, problems)
    found = []
    for name in ("min_renamed", "min_subset"):
        value = spec.get(name)
        if value is not None and not _whole(value, 2):
            problems.append(f"{where}.{name}: must be a whole number of fields, at least 2, such as 3; leave it out "
                            "to switch this case off")
            value = None
        found.append(value)
    names = (ck.part_names(spec["translated"], declared, f"{where}.translated", problems, words=words)
             if "translated" in spec else [])
    return NoTwins(least, *found, tuple(n for n in names if n in parts))


def _minimum(spec: Mapping[Any, Any], key: str, default: int, noun: str, where: str, problems: list[str]) -> int:
    """The fewest of something a guard counts, at key: a whole number, at least 1; default when left out or wrong."""
    least = spec.get(key, default)
    if not _whole(least, 1):
        problems.append(f"{where}.{key}: must be a whole number of {noun}, at least 1, such as {default}")
        return default
    return least


def _whole(value: Any, least: int) -> bool:
    """Whether a value is a whole number, at least least (true and false are no numbers here)."""
    return isinstance(value, int) and not isinstance(value, bool) and value >= least


def _listed_parts(spec: Any, declared: set[str], parts: dict[str, Part], where: str, scope: str, said: str,
                  problems: list[str], words: Collection[str]) -> tuple[str, ...] | None:
    """The parts a guard whose one key is `parts` reads, in the order written; None, with its problems, when the
    guard is written wrong. scope is the scope of the guard's keys; said, what its parts are, as its refusal says it."""
    if not isinstance(spec, Mapping):
        problems.append(f"{where}: must be a mapping {{parts: [<part>, ...]}}: {said}")
        return None
    count = len(problems)
    problems += ck.unknown_keys(spec, names_of(scope), where, scope)
    problems += [f"{where}: missing `{key}`" for key in required_of(scope) if key not in spec]
    names = ck.part_names(spec["parts"], declared, f"{where}.parts", problems, words=words) if "parts" in spec else []
    if len(problems) != count:
        return None
    return tuple(n for n in names if n in parts)


def _needs_testing(document: Mapping[Any, Any]) -> list[str]:
    """`testing` is required by what reads tests: the tiers and the guards that read them."""
    if "testing" in document:
        return []
    guards = document.get("guards")
    names = [f"`guards.{name}`" for name in _NEEDS_TESTING if isinstance(guards, Mapping) and name in guards]
    needing = (["`tiers`"] if "tiers" in document else []) + names
    if not needing:
        return []
    return [f"missing `testing`: {ck.join_and(needing)} must recognise a test file by its name: write testing: "
            "<preset>, or testing: {files: [<pattern>, ...], declared: [{function: <pattern>}]}"]


def _docs(value: Any, declared: set[str], files: Collection[str], problems: list[str],
          words: Collection[str]) -> tuple[str, tuple, tuple]:
    """What only fills the docs, but for the examples: the entry point's name ("" if none), the pages and the naming
    table."""
    if not isinstance(value, Mapping):
        problems.append(f"docs: must be a mapping of {{{', '.join(key.name for key in keys_of(DOCS))}}}")
        return "", (), ()
    problems += ck.unknown_keys(value, names_of(DOCS), "docs", DOCS)
    entry = value.get("entry", "")
    prefixed = outside_imports(entry, declared, words) if "entry" in value else None
    if prefixed is not None or ("entry" in value and (not isinstance(entry, str) or entry not in declared)):
        problems.append(f"docs.entry: {prefixed or f'no part named {entry!r}'}")
        entry = ""
    pages = ck.doc_pages(_bare_from(value["pages"]), files, problems, "docs.pages") if "pages" in value else ()
    naming = ck.naming_rows(value["naming"], problems, "docs.naming") if "naming" in value else ()
    return entry, pages, naming
