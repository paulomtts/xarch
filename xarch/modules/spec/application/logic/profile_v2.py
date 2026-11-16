"""A profile file (format version 2), parsed and validated into an Architecture.

An Architecture, from a file that states each fact once, on the thing it is about. The keys and whether each is
enforced are in key_table, which the messages below read, and what each means in the format's data file (see
key_catalogue); the shape:

    xarch: 2
    name: <name>
    based_on: <bundled name>   optional; the bundled profile this one was copied from, which a report compares with
    language: <language>       optional; the language of the app: the name of a language xarch ships (the first by name
                               when left out), read from its data file
    testing: <preset> | {files, functions, skips, table, mocks}
                               how the test framework names things; a preset is a name, read from data shipped with
                               xarch. Required with `tiers` and with the guards scenario-coverage and stand-ins
    parts: {<part>: {path, role, ...}}
                               in the order their litmus tests run. A part's path is a folder below the app, or a file
                               when its last step holds a dot; one step written `<word>` is the repeating folder, one
                               instance per name, and the word is what the docs call one instance. The layout is the
                               paths of the parts and their `folders` (each with an optional note), nothing else
        may_import: [<part>, <part>@any, <part>/<path>] | everything
                               what the part may import besides itself, which it always may: a bare name of a part in
                               the repeating folder is the importer's own instance, `@any` any instance; everything
        libraries: [<package>, ...] | everything
                               the outside packages by top-level import name; a part that lists none may import none,
                               and everything leaves the part unchecked
        forbidden: <list>      the name of a top-level `forbidden` list the part may not use
        tier: <tier> | untested: <reason>
                               one tier covers the part, or the reason none does; with `tiers`, one of the two
        package_only: true     the part is imported only as a package from outside it
        folders: {<folder>: <note>} | [<folder>, ...]
                               folders below the part that the layout shows
    forbidden: {<list>: [<name>, ...]}         named lists of what a part may not use
    reserved: {<module>: <reason>}             standard-library modules only the parts whose `libraries` list them
                               may import
    layers: {<name>: [<part>, ...]}            chains of parts from the inside out: none imports one after it
    tiers: {<tier>: {proves, litmus, apply_forbidden, types_only, folder, may_import, may_also_import, docs}}
                               the kinds of test, in the order their litmus tests run. A tier with a `folder` below
                               the tests folder says in `may_import` what the tests there may import; `may_also_import`
                               what each of its tests may import beyond that or what the part it mirrors may; `docs`
                               holds what only fills the generated docs
    fakes: {folder, for, prefix}               the folder of the test fakes below the tests folder, the parts they
                               stand in for, and how a fake's name starts
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
    evals: {placement: {lines, examples}, <id>: {ask, answer, reads, ...}}
                               how review reads what it asks: the line of each part below which a file reads as doubtful
                               there, the examples placement is held to besides the docs', and the evals of the
                               profile's own; `check` never reads it (see evals)

Every problem found is collected, so one InvalidArchitecture lists them all, each naming the key by its address in the
file and saying what to write instead; a problem that makes the rest meaningless stops early.
"""
from __future__ import annotations

import re
from collections.abc import Collection, Mapping
from dataclasses import dataclass, replace
from typing import Any

from xarch.kernel.logic.placement import root_of
from xarch.kernel.logic.targets import NAME_PATTERN
from xarch.kernel.placement import EACH, EVERYTHING
from xarch.modules.spec.application.logic import profile_checks as ck
from xarch.modules.spec.application.logic import profile_examples as ex
from xarch.modules.spec.application.logic import profile_needs as needs
from xarch.modules.spec.application.logic import written_checks as own_checks
from xarch.modules.spec.application.logic.evals import evals
from xarch.modules.spec.application.logic.key_lookup import keys_of, names_of, required_of
from xarch.modules.spec.application.logic.language_file import first_language
from xarch.modules.spec.application.logic.layout_walk import is_file
from xarch.modules.spec.application.logic.sending import sending
from xarch.modules.spec.application.logic.targets_written import WORD, may_import
from xarch.modules.spec.domain.errors import InvalidArchitecture
from xarch.modules.spec.domain.guards import GUARD, KEY, ORDER
from xarch.modules.spec.domain.profile_keys import (
    DEAD_CODE,
    DOCS,
    FAKES,
    MOCKS,
    NO_DUPLICATES,
    NO_TWINS,
    PART,
    PASS_THROUGH,
    PROFILE,
    SCENARIO_COVERAGE,
    TESTING,
    TIER,
    TIER_DOCS,
)
from xarch.modules.spec.domain.values import (
    VERSION,
    Architecture,
    DeadCode,
    Guard,
    Language,
    Layout,
    NoDuplicates,
    NoTwins,
    PackageOnly,
    Part,
    PassThrough,
    Subject,
    Tier,
    TierExample,
)
from xarch.profile_values.placement import Repeat, Target
from xarch.profile_values.testing import CaseTable, Fakes, Framework, ScenarioCoverage, StandIns

_REPEATING = re.compile(r"<([A-Za-z_][A-Za-z0-9_-]*)>")
_HOLDS = ("classes", "functions")
_TIER_TEXTS = ("subject", "may_touch", "one_file_per", "cases_from", "data")
"""The keys under a tier's `docs` that hold one line of text each."""
_GUARDS = tuple(name for name in ORDER if name != KEY[PackageOnly])
_NEEDS_TESTING = (KEY[ScenarioCoverage], KEY[StandIns])
_PRESET_MAP = "{files, functions}"
_TIER_INSTEAD = "`tier: <tier>`, or `untested: <reason>`"
_MOVED = {
    "layout": "delete it: the layout comes from each part's `path` and `folders`",
    "notes": "write the note of a folder under `folders` on the part that holds it",
    "rules": "write each part's targets as `may_import` on the part",
    "placement": "delete it: the order of `parts` is the order the litmus tests run",
    "naming": "move it to `docs.naming`",
    "tests": "write `testing`: a preset name, or the map {files, functions, ...}",
    "examples": "move it to `docs.examples`",
    "libraries": "write each part's packages as `libraries` on the part",
}
"""A key of version 1 that has moved, with what to write instead."""


@dataclass(frozen=True)
class _Testing:
    """What `testing` says: how test files and functions are named, and, when written, how a table of cases is held
    and how a mock is built."""
    framework: Framework
    table: CaseTable | None
    mocks: StandIns | None


@dataclass(frozen=True)
class _Layout:
    """The layout and what comes with it, built from the paths of the parts: the parts, the tree, the notes of the
    folders, and the repeating folders in the order they first appear."""
    parts: Mapping[str, Part]
    tree: Layout
    notes: Mapping[tuple[str, ...], str]
    repeats: tuple[Repeat, ...]


def parse_v2(document: Any, source: str, files: Collection[str] = (), presets: Mapping[str, Any] | None = None,
             bundled: Collection[str] = (), languages: Mapping[str, Language] | None = None) -> Architecture:
    """The architecture the document describes; raises InvalidArchitecture listing every problem. files are the files
    next to the profile file that it names, and every file below the folders it names, each as a path from the folder
    holding it (see profile_listing); presets are the documents of the `testing` presets by name; bundled are the
    names of the bundled profiles, which `based_on` may name; languages are the languages xarch ships, by name."""
    if not isinstance(document, Mapping):
        raise InvalidArchitecture(source, [f"must be a mapping of keys, starting with `xarch: {VERSION}`"])
    problems: list[str] = []
    problems += _keys(document)
    name = document.get("name")
    if "name" in document and not ck.text(name):
        problems.append("`name` must be a non-empty string")
    language = _language(document, languages or {}, problems)
    shortfalls = needs.short(document, presets or {}, language)
    problems += needs.refused(shortfalls, language)
    based_on = _based_on(document["based_on"], bundled, problems) if "based_on" in document else ""
    lists = _forbidden_lists(document["forbidden"], problems, language) if "forbidden" in document else {}
    specs = _specs(document.get("parts", {}), problems)
    declared = set(specs)
    built = _layout(specs, problems)
    parts = built.parts
    examples = ex.example_files(document.get("docs", {}), files, problems, language)
    rules = {part: may_import(specs[part].get("may_import"), item, parts, declared, f"parts.{part}.may_import",
                               problems, patterns=True) for part, item in parts.items()}
    reserved = ck.reserved_modules(document["reserved"], problems, language) if "reserved" in document else {}
    libraries = {part: _libraries(specs[part], f"parts.{part}.libraries", problems, language, reserved)
                 for part in parts}
    parts = {part: replace(item, must_import=_must_import(specs[part], item, parts, declared, rules[part], problems))
             for part, item in parts.items()}
    parts = {part: _substance(specs[part], item, declared, rules[part], problems) for part, item in parts.items()}
    forbidden = _forbidden_refs(specs, parts, lists, problems)
    layers = ck.layer_chains(document["layers"], parts, declared, rules, problems) if "layers" in document else {}
    testing = _testing(document["testing"], presets or {}, problems, language) if "testing" in document else None
    tiers = _tiers(document, specs, parts, declared, examples, problems, language)
    problems += [f"tiers.{tier.name}.plain_tables: needs `testing.table`, how a table of cases is written, to know a "
                 "table test" for tier in tiers if tier.plain_tables and (testing is None or testing.table is None)]
    fakes = _fakes(document["fakes"], parts, declared, problems, language) if "fakes" in document else None
    problems += ck.folder_clashes(tiers, fakes)
    guards = _guards(document.get("guards", {}), specs, parts, declared, tiers, fakes, testing, problems, language)
    problems += _needs_testing(document)
    entry, pages, naming = _docs(document.get("docs", {}), declared, files, problems)
    parts = {part: replace(item, entry=True) if part == entry else item for part, item in parts.items()}
    written = ck.init_files(_bare_from(document.get("files", {})), pages, files, problems, "docs.pages", language)
    excluded = ck.excluded_folders(document["excluded"], built.tree, problems) if "excluded" in document else ()
    own = (own_checks.checks(document["checks"], declared, tiers, language, problems) if "checks" in document
           else {})
    hints = ck.rule_hints(document["hints"], problems, own) if "hints" in document else {}
    never, mask = sending(document["review"], problems) if "review" in document else ((), ())
    placement, placed, own_evals = (evals(document["evals"], declared, language, problems) if "evals" in document
                                    else ({}, ((), ()), {}))
    if problems:
        raise InvalidArchitecture(source, problems)
    shown = ex.examples_of(examples, built.tree, parts, language)
    return Architecture(name, built.tree, parts, rules, pages, shown, built.notes, layers, tuple(parts), naming, tiers,
                        libraries, guards, fakes, built.repeats, written, testing.framework if testing else None, forbidden,
                        excluded, hints, based_on, language, reserved, needs.approximate(shortfalls), own, never, mask,
                        placement, own_evals, placed)


def _keys(document: Mapping[Any, Any]) -> list[str]:
    """The keys of the file that are unknown: one that moved from format 1 says where it went."""
    problems = [f"`{key}`: not a key of format 2: {_MOVED[key]}" for key in sorted(map(str, document)) if key in _MOVED]
    unknown = sorted(str(key) for key in document if key not in names_of(PROFILE) and key not in _MOVED)
    if unknown:
        problems.append(f"unknown key{'s' if len(unknown) > 1 else ''} {ck.quoted(unknown)}: "
                        f"use {', '.join(sorted(names_of(PROFILE)))}")
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
    use = f": use {', '.join(bundled)}" if bundled else ""
    if not isinstance(value, str):
        problems.append(f"based_on: must be the name of a bundled profile{use}")
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


def _specs(value: Any, problems: list[str]) -> dict[str, Any]:
    """Every part with a valid name, by name, whatever it holds: a part already reported is not reported again."""
    if not isinstance(value, Mapping):
        problems.append("parts: must be a mapping of part names to {path, role, ...}")
        return {}
    specs: dict[str, Any] = {}
    for name, spec in value.items():
        if not ck.text(name) or not ck.PART_NAME.fullmatch(name):
            problems.append(f"parts: {name!r} is not a part name: use letters, digits, '_' and '-'")
        else:
            specs[name] = spec
    return specs


def _layout(specs: dict[str, Any], problems: list[str]) -> _Layout:
    """The parts that place validly, in the order of the file, and the layout their paths and `folders` make."""
    parts: dict[str, Part] = {}
    tree: Layout = {}
    notes: dict[tuple[str, ...], str] = {}
    repeats: list[Repeat] = []
    claimed: dict[tuple[str, ...], str] = {}
    owners: dict[tuple[str, ...], str] = {}
    for name, spec in specs.items():
        where = f"parts.{name}"
        if not isinstance(spec, Mapping):
            problems.append(f"{where}: must be a mapping with `path` and `role`")
            continue
        problems += ck.unknown_keys(spec, names_of(PART), where)
        problems += [f"{where}: missing `{key}`" for key in required_of(PART) if key not in spec]
        for key in ("role", "litmus"):
            if key in spec and not isinstance(spec[key], str):
                problems.append(f"{where}.{key}: must be a string")
        if "untested" in spec and not ck.line(spec["untested"]):
            problems.append(f"{where}.untested: must be one line of text: why no tier tests the part")
        if "package_only" in spec and not isinstance(spec["package_only"], bool):
            problems.append(f"{where}.package_only: must be true or false")
        placed = _path(spec["path"], where, problems) if "path" in spec else None
        if placed is None:
            continue
        steps, word = placed
        if not _repeats_alike(name, steps, word, repeats, owners, where, spec["path"], problems):
            continue
        if steps in claimed:
            problems.append(f"{where}.path: '{_shown(steps, word)}' is already claimed by part '{claimed[steps]}'")
            continue
        if not _insert(tree, steps, name, owners, where, _shown(steps, word), problems):
            continue
        claimed[steps] = name
        parts[name] = Part(name, steps, ck.string(spec.get("role")), ck.string(spec.get("litmus")), False,
                                 spec["untested"] if ck.line(spec.get("untested")) else "")
    for name, part in parts.items():
        problems += _folders(specs[name].get("folders"), part, tree, notes, claimed, f"parts.{name}.folders",
                             "folders" in specs[name])
    return _Layout(parts, tree, notes, tuple(repeats))


def _path(value: Any, where: str, problems: list[str]) -> tuple[tuple[str, ...], str] | None:
    """A part's path as steps, the repeating step as EACH, and the word between its brackets ("" if none)."""
    if not ck.text(value):
        problems.append(f"{where}.path: must be a path such as 'src/<name>/api'")
        return None
    steps = value.strip("/").split("/")
    if any(step in ("", ".", "..") or "\\" in step for step in steps):
        problems.append(f"{where}.path: '{value}' has an empty, `.` or `..` step")
        return None
    if any(EACH in step for step in steps):
        problems.append(f"{where}.path: '{value}' has a `*` step: write the repeating folder as one word between `<` "
                        "and `>`")
        return None
    words = [_REPEATING.fullmatch(step) for step in steps if "<" in step or ">" in step]
    if any(match is None for match in words):
        problems.append(f"{where}.path: '{value}' has a step with `<` or `>` that is not one word between them: write "
                        "the repeating folder as `<name>`")
        return None
    if len(words) > 1:
        first, second = (match.group(1) for match in words[:2] if match)
        problems.append(f"{where}.path: '{value}' has two repeating steps, <{first}> and <{second}>: a repeating "
                        "folder cannot sit inside another, so give each its own folder")
        return None
    return (tuple(EACH if _REPEATING.fullmatch(step) else step for step in steps),
            words[0].group(1) if words and words[0] else "")


def _shown(steps: tuple[str, ...], word: str) -> str:
    return "/".join(f"<{word}>" if step == EACH else step for step in steps)


def _repeats_alike(name: str, steps: tuple[str, ...], word: str, repeats: list[Repeat],
                   owners: dict[tuple[str, ...], str], where: str, value: str, problems: list[str]) -> bool:
    """A word repeats in one folder, and a folder is repeated by one word."""
    root = root_of(steps)
    if root is None:
        return True
    here = next((repeat for repeat in repeats if repeat.root == root), None)
    named = next((repeat for repeat in repeats if repeat.word == word), None)
    if here is not None and here.word != word:
        problems.append(f"{where}.path: '{value}' calls the repeating folder <{word}>, but part "
                        f"'{owners[(*root, EACH)]}' called it <{here.word}> in the same folder '{'/'.join(root)}': two "
                        "words may not share a parent, use one word")
    elif named is not None and named.root != root:
        problems.append(f"{where}.path: '{value}' repeats <{word}> below '{'/'.join(root)}', but part "
                        f"'{owners[(*named.root, EACH)]}' repeats it below '{'/'.join(named.root)}': one word repeats "
                        "in one folder, so give this one a word of its own")
    else:
        if here is None:
            repeats.append(Repeat(word, root))
            owners[(*root, EACH)] = name
        return True
    return False


def _insert(tree: Layout, steps: tuple[str, ...], name: str, owners: dict[tuple[str, ...], str], where: str,
            shown: str, problems: list[str]) -> bool:
    """The path in the tree: folders for every step, a file for a last step holding a dot; False when it clashes."""
    here = tree
    for i, step in enumerate(steps[:-1], 1):
        if step in here and here[step] is None:
            problems.append(f"{where}.path: '{shown}' lies below '{'/'.join(steps[:i])}', which part "
                            f"'{owners[steps[:i]]}' makes a file")
            return False
        here = here.setdefault(step, {})
    last = steps[-1]
    if "." in last:
        if last in here:
            problems.append(f"{where}.path: '{shown}' is a file, since its last step holds a dot, but part "
                            f"'{owners[steps]}' lies below it: rename one of them")
            return False
        here[last] = None
    else:
        here.setdefault(last, {})
    for i in range(1, len(steps) + 1):
        owners.setdefault(steps[:i], name)
    return True


def _folders(value: Any, part: Part, tree: Layout, notes: dict[tuple[str, ...], str],
             claimed: dict[tuple[str, ...], str], where: str, given: bool) -> list[str]:
    """The `folders` of a part: each goes in the layout below the part, and its note, if any, in the notes."""
    if not given:
        return []
    problems: list[str] = []
    if isinstance(value, Mapping):
        entries = list(value.items())
    elif isinstance(value, list):
        entries = [(item, "") for item in value]
    else:
        return [f"{where}: must be a mapping of folder paths to one line of text, or a list of folder paths"]
    if is_file(tree, part.path):
        return [f"{where}: a file has no folders: drop the key"]
    seen: list[str] = []
    for key, note in entries:
        steps = tuple(key.strip("/").split("/")) if ck.text(key) else ()
        if not steps or any(step in ("", ".", "..") or EACH in step or "<" in step or "\\" in step for step in steps):
            problems.append(f"{where}: {key!r} is not a folder below the part: write a path of plain names such as "
                            "io/disk")
        elif key in seen:
            problems.append(f"{where}: {key!r} is listed twice")
        elif isinstance(value, Mapping) and not ck.line(note):
            problems.append(f"{where}.{key}: must be one line of text")
        else:
            seen.append(key)
            full = (*part.path, *steps)
            if full in claimed:
                problems.append(f"{where}.{key}: '{key}' is part '{claimed[full]}', whose note is its role: drop it "
                                "from `folders`")
                continue
            if not _add_folder(tree, full):
                problems.append(f"{where}.{key}: '{key}' lies below a file")
                continue
            if note:
                notes[full] = note
    return problems


def _add_folder(tree: Layout, path: tuple[str, ...]) -> bool:
    here = tree
    for step in path:
        if step in here and here[step] is None:
            return False
        here = here.setdefault(step, {})
    return True


def _libraries(spec: Mapping[Any, Any], where: str, problems: list[str], language: Language,
               reserved: Mapping[str, str]) -> tuple[str, ...]:
    """The outside packages of a part, and the reserved modules it may import: none unless it lists them;
    (EVERYTHING,) leaves them unchecked."""
    if "libraries" not in spec:
        return ()
    value = spec["libraries"]
    if value == WORD:
        return (EVERYTHING,)
    if not isinstance(value, list):
        problems.append(f"{where}: must be a list of top-level import names such as [sqlmodel], or {WORD}")
        return ()
    return ck.package_names(value, where, problems, language, reserved) or ()


def _forbidden_lists(value: Any, problems: list[str],
                     language: Language) -> dict[str, tuple[tuple[str, ...], ...] | None] | None:
    """The named lists of names a part may not use; a list already reported is None. None: `forbidden` is no mapping."""
    if not isinstance(value, Mapping):
        problems.append("forbidden: must be a mapping of list names to lists of dotted names, such as "
                        "{pure: [datetime.datetime.now, socket]}")
        return None
    lists: dict[str, tuple[tuple[str, ...], ...] | None] = {}
    for name, names in value.items():
        if not ck.text(name) or not ck.PART_NAME.fullmatch(name):
            problems.append(f"forbidden: {name!r} is not a list name: use letters, digits, '_' and '-'")
        else:
            lists[name] = ck.forbidden_names(names, f"forbidden.{name}", problems, language)
    return lists


def _forbidden_refs(specs: dict[str, Any], parts: dict[str, Part],
                    lists: dict[str, tuple[tuple[str, ...], ...] | None] | None,
                    problems: list[str]) -> dict[str, tuple[tuple[str, ...], ...]]:
    """What each part that names a list may not use."""
    forbidden: dict[str, tuple[tuple[str, ...], ...]] = {}
    for name in parts:
        spec = specs[name]
        if "forbidden" not in spec or lists is None:
            continue
        ref, where = spec["forbidden"], f"parts.{name}.forbidden"
        if not isinstance(ref, str):
            problems.append(f"{where}: must be the name of a list under `forbidden`")
        elif ref not in lists:
            use = f"use {', '.join(sorted(lists))}, or write it" if lists else "write it"
            problems.append(f"{where}: no list named {ref!r}: {use} under `forbidden`")
        elif lists[ref] is not None:
            forbidden[name] = lists[ref]
    return forbidden


def _testing(value: Any, presets: Mapping[str, Any], problems: list[str], language: Language) -> _Testing | None:
    """How the test framework names things: the map in the file, or the one a preset holds, validated the same."""
    if isinstance(value, str):
        if value not in presets:
            names = f"use {', '.join(sorted(presets))}, or write" if presets else "write"
            problems.append(f"testing: no preset {value!r}: {names} the map {_PRESET_MAP}")
            return None
        value = presets[value]
    elif not isinstance(value, Mapping):
        problems.append(f"testing: must be a preset name or a mapping {_PRESET_MAP}: the patterns of a test file's name "
                        "and of a test function's")
        return None
    count = len(problems)
    framework = ck.framework_patterns(value, problems, "testing", names_of(TESTING), language)
    table = ck.case_table(value["table"], "testing.table", problems, language) if "table" in value else None
    mocks = _mocks(value["mocks"], problems, language) if "mocks" in value else None
    if len(problems) != count or framework is None:
        return None
    return _Testing(replace(framework, table=table), table, mocks)


def _mocks(value: Any, problems: list[str], language: Language) -> StandIns | None:
    where = "testing.mocks"
    if not isinstance(value, Mapping):
        problems.append(f"{where}: must be a mapping {{calls, spec_keywords}}, and optionally autospec, spec_position "
                        "and fixtures: the dotted names of the calls that build a mock, the keywords a mock is given "
                        "its spec by, the position of the argument that names it, and the parameters of a test "
                        "function whose methods build one")
        return None
    count = len(problems)
    problems += ck.unknown_keys(value, names_of(MOCKS), where)
    problems += [f"{where}: missing `{key}`" for key in required_of(MOCKS) if key not in value]
    calls = ck.dotted_names(value["calls"], f"{where}.calls", problems, language) if "calls" in value else None
    autospec = ck.dotted_names(value["autospec"], f"{where}.autospec", problems, language) if "autospec" in value else ()
    problems += [f"{where}.autospec: {'.'.join(name)!r} is also listed in calls" for name in autospec or ()
                 if calls and name in calls]
    keywords = (ck.identifiers(value["spec_keywords"], f"{where}.spec_keywords", problems, "keyword", "[spec]",
                               language) if "spec_keywords" in value else None)
    fixtures = (ck.fixtures(value["fixtures"], f"{where}.fixtures", problems, language, "calls")
                if "fixtures" in value else ())
    position = value.get("spec_position")
    if position is not None and not _whole(position, 0):
        problems.append(f"{where}.spec_position: must be a whole number, at least 0, such as 0: the position of the "
                        "argument that names the spec; leave it out when only a keyword names it")
    if len(problems) != count or calls is None or autospec is None or keywords is None or fixtures is None:
        return None
    return StandIns(calls, autospec, keywords, fixtures, position)


def _tiers(document: Mapping[Any, Any], specs: dict[str, Any], parts: dict[str, Part], declared: set[str],
           examples: ex.Examples, problems: list[str], language: Language) -> tuple[Tier, ...]:
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
        tier = _tier(name, spec, subject, parts, declared, examples, problems, language)
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
        named, untested = "tier" in spec, "untested" in spec
        if named and untested:
            problems.append(f"{where}: has a `tier` and is `untested`: drop one")
        if named and not has_tiers:
            problems.append(f"{where}.tier: the profile has no `tiers`: add them, or drop the key")
        elif named and names is not None:
            tier = spec["tier"]
            use = f"use {', '.join(names)}"
            if not isinstance(tier, str):
                problems.append(f"{where}.tier: must be the name of a tier: {use}")
            elif tier not in names:
                problems.append(f"{where}.tier: no tier named {tier!r}: {use}")
            else:
                assigned[name] = tier
        elif not named and not untested and names is not None:
            problems.append(f"{where}: no tier tests it: give it {_TIER_INSTEAD}")
    return assigned


def _tier(name: str, spec: Any, subject: tuple[Subject, ...], parts: dict[str, Part], declared: set[str],
          examples: ex.Examples, problems: list[str], language: Language) -> Tier | None:
    where = f"tiers.{name}"
    if not isinstance(spec, Mapping):
        problems.append(f"{where}: must be a mapping, {{}} if it takes nothing")
        return None
    count = len(problems)
    problems += ck.unknown_keys(spec, names_of(TIER), where)
    if "proves" in spec and not ck.line(spec["proves"]):
        problems.append(f"{where}.proves: must be one line of text")
    if "litmus" in spec and not ck.text(spec["litmus"]):
        problems.append(f"{where}.litmus: must be text: the question that tells a test belongs to the tier")
    held = spec.get("apply_forbidden", False)
    if not isinstance(held, bool):
        problems.append(f"{where}.apply_forbidden: must be true or false: whether its tests are held to the "
                        "`forbidden` list of the part they mirror")
    plain = spec.get("plain_tables", False)
    if not isinstance(plain, bool):
        problems.append(f"{where}.plain_tables: must be true or false: whether every table test of the tier holds no "
                        "branch in its body")
    types_only = (ck.part_names(spec["types_only"], declared, f"{where}.types_only", problems)
                  if "types_only" in spec else [])
    folder = ck.tier_folder(spec["folder"], parts, f"{where}.folder", problems, language) if "folder" in spec else None
    if "folder" not in spec and "may_import" in spec:
        problems.append(f"{where}.may_import: only a tier with a `folder` has an allowance of its own: without one, its "
                        "tests import what the part they mirror may")
    allowance = (may_import(spec.get("may_import"), None, parts, declared, f"{where}.may_import", problems)
                 if "folder" in spec else None)
    also = may_import(spec.get("may_also_import"), None, parts, declared, f"{where}.may_also_import", problems,
                      mirrored=True)
    docs = _tier_docs(spec["docs"], folder, examples, f"{where}.docs", problems, language) if "docs" in spec else {}
    reach = (ck.part_names(spec["must_import"], declared, f"{where}.must_import", problems)
             if "must_import" in spec else [])
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
    problems += ck.unknown_keys(value, names_of(TIER_DOCS), where)
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
           language: Language) -> Fakes | None:
    where = "fakes"
    if not isinstance(value, Mapping):
        problems.append(f"{where}: must be a mapping {{folder, for}} and optionally prefix: the folder of the fakes "
                        "below the tests folder, the parts they stand in for, and how a fake's name starts")
        return None
    count = len(problems)
    problems += ck.unknown_keys(value, names_of(FAKES), where)
    problems += [f"{where}: missing `{key}`" for key in required_of(FAKES) if key not in value]
    prefix = value.get("prefix", "")
    if "prefix" in value and (not isinstance(prefix, str) or not ck.is_name(prefix, language)):
        problems.append(f"{where}.prefix: must be the start of a class name, such as Fake")
    folder = value.get("folder")
    steps = tuple(folder.split("/")) if ck.line(folder) and not folder.startswith("/") else ()
    if "folder" in value and (not steps or any(step in ("", ".", "..") or EACH in step for step in steps)):
        problems.append(f"{where}.folder: must be a folder below the tests folder, such as fakes: relative, with no "
                        "`..`, no empty step and no `*`")
    names = ck.part_names(value["for"], declared, f"{where}.for", problems) if "for" in value else []
    if len(problems) != count:
        return None
    return Fakes(steps, tuple(n for n in names if n in parts), prefix)


def _guards(value: Any, specs: dict[str, Any], parts: dict[str, Part], declared: set[str], tiers: tuple[Tier, ...],
            fakes: Fakes | None, testing: _Testing | None, problems: list[str],
            language: Language) -> tuple[Guard, ...]:
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
            problems.append(f"{where}: a fact about a part in format 2: write `package_only: true` on each part")
        elif name not in _GUARDS:
            problems.append(f"guards: unknown guard {name!r}: use {', '.join(sorted(_GUARDS))}")
        elif kind is ScenarioCoverage:
            guard = _scenario_coverage(spec, parts, declared, tiers, testing, where, problems, language)
            if guard is not None:
                guards.append(guard)
        elif kind is StandIns:
            guard = _stand_ins(spec, fakes, testing, where, problems, language)
            if guard is not None:
                guards.append(guard)
        elif kind is NoDuplicates:
            guards.append(_no_duplicates(spec, where, problems))
        elif kind is NoTwins:
            guards.append(_no_twins(spec, declared, parts, where, problems))
        elif kind is PassThrough:
            guard = _pass_through(spec, declared, parts, where, problems)
            if guard is not None:
                guards.append(guard)
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
                       language: Language) -> ScenarioCoverage | None:
    if not isinstance(spec, Mapping):
        problems.append(f"{where}: must be a mapping {{results, tier, suffix, columns, file}}: the part holding the "
                        "result unions, the tier whose test files hold their tables, how a union's name ends, the "
                        "three names of a table's parameters (its state, its command and its result), and the name "
                        "of a use case's test file")
        return None
    count = len(problems)
    problems += ck.unknown_keys(spec, names_of(SCENARIO_COVERAGE), where)
    problems += [f"{where}: missing `{key}`" for key in sorted(required_of(SCENARIO_COVERAGE)) if key not in spec]
    if testing is not None and testing.table is None:
        problems.append(f"{where}: needs `testing.table`: how a table of cases is written, such as "
                        "{decorator, row, id}")
    if len(problems) != count:
        return None
    ck.scenario_places(spec["results"], spec["tier"], spec["suffix"], parts, declared, tiers, where, problems,
                       language)
    columns = ck.column_names(spec["columns"], f"{where}.columns", problems, language)
    framework = testing.framework if testing is not None else None
    file = ck.use_case_file(spec["file"], framework, f"{where}.file", problems, language, "testing.files")
    if len(problems) != count or columns is None or file is None or testing is None or testing.table is None:
        return None
    return ScenarioCoverage(spec["results"], spec["tier"], spec["suffix"], columns, testing.table, file)


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
    problems += ck.unknown_keys(spec, names_of(DEAD_CODE), where)
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
        if not file or file.startswith("/") or not file.endswith(language.checked.extension) \
                or not ck.is_name(name, language):
            problems.append(f"{where}: {item!r} is not <file below the app>:<name>, such as {example}")
        elif item in found:
            problems.append(f"{where}: {item!r} is listed twice")
        else:
            found.append(item)
    return tuple(found)


def _substance(spec: Any, part: Part, declared: set[str], may_import: tuple[Target, ...],
               problems: list[str]) -> Part:
    """The keys of a part that say what its code holds and how it is used: holds, immutable, types_only, no_callbacks,
    names, built_by and shared."""
    where = f"parts.{part.name}"
    if not isinstance(spec, Mapping):
        return part
    holds = spec.get("holds", "")
    if "holds" in spec and holds not in _HOLDS:
        problems.append(f"{where}.holds: must be {' or '.join(_HOLDS)}")
        holds = ""
    no_callbacks = spec.get("no_callbacks", False)
    if not isinstance(no_callbacks, bool):
        problems.append(f"{where}.no_callbacks: must be true or false")
        no_callbacks = False
    immutable = spec.get("immutable", False)
    if not isinstance(immutable, bool):
        problems.append(f"{where}.immutable: must be true or false: whether every class the part defines, but an "
                        "exception, is an immutable record")
        immutable = False
    names = _class_patterns(spec["names"], f"{where}.names", problems) if "names" in spec else ()
    built_by = tuple(ck.part_names(spec["built_by"], declared, f"{where}.built_by", problems)) \
        if "built_by" in spec else ()
    types_only = tuple(ck.part_names(spec["types_only"], declared, f"{where}.types_only", problems)) \
        if "types_only" in spec else ()
    for name in types_only:
        if not any(t.part in (EVERYTHING, name) for t in may_import):
            problems.append(f"{where}.types_only: {name!r} is not in `may_import`, so no file could import it to use as "
                            "a type: add it there, or drop it")
    shared = spec.get("shared")
    if shared is not None and not _whole(shared, 2):
        problems.append(f"{where}.shared: must be a whole number of users, at least 2, such as 2; leave it out for a "
                        "part that is not there to be shared")
        shared = None
    return replace(part, holds=holds, no_callbacks=no_callbacks, names=names, built_by=built_by, types_only=types_only,
                   shared=shared, immutable=immutable)


def _class_patterns(value: Any, where: str, problems: list[str]) -> tuple[str, ...]:
    items = [value] if isinstance(value, str) else value
    if not isinstance(items, list) or not items or items == [""]:
        problems.append(f"{where}: must be a class name pattern with `*` for any text, such as *Store, or a list of "
                        "them")
        return ()
    bad = [item for item in items if not isinstance(item, str) or not NAME_PATTERN.fullmatch(item)]
    problems += [f"{where}: {item!r} is not a class name pattern: write it with no space, `@`, `/` or `:`, `*` "
                 "standing for any text" for item in bad]
    return () if bad else tuple(items)


def _no_duplicates(spec: Any, where: str, problems: list[str]) -> NoDuplicates:
    if spec in ({}, None):
        return NoDuplicates()
    if not isinstance(spec, Mapping):
        problems.append(f"{where}: must be a mapping {{min_statements: <number>}}, or {{}} for the default")
        return NoDuplicates()
    problems += ck.unknown_keys(spec, names_of(NO_DUPLICATES), where)
    return NoDuplicates(_minimum(spec, "min_statements", NoDuplicates.min_statements, "statements", where, problems))


def _no_twins(spec: Any, declared: set[str], parts: dict[str, Part], where: str, problems: list[str]) -> NoTwins:
    if spec in ({}, None):
        return NoTwins()
    if not isinstance(spec, Mapping):
        problems.append(f"{where}: must be a mapping {{min_fields: <number>, min_renamed: <number>, min_subset: "
                        "<number>, translated: [<part>, ...]}, or {} for the default")
        return NoTwins()
    problems += ck.unknown_keys(spec, names_of(NO_TWINS), where)
    least = _minimum(spec, "min_fields", NoTwins.min_fields, "fields", where, problems)
    found = []
    for name in ("min_renamed", "min_subset"):
        value = spec.get(name)
        if value is not None and not _whole(value, 2):
            problems.append(f"{where}.{name}: must be a whole number of fields, at least 2, such as 3; leave it out "
                            "to switch this case off")
            value = None
        found.append(value)
    names = ck.part_names(spec["translated"], declared, f"{where}.translated", problems) if "translated" in spec else []
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


def _pass_through(spec: Any, declared: set[str], parts: dict[str, Part], where: str,
                  problems: list[str]) -> PassThrough | None:
    if not isinstance(spec, Mapping):
        problems.append(f"{where}: must be a mapping {{parts: [<part>, ...]}}: the parts whose methods are listed "
                        "when they only forward")
        return None
    count = len(problems)
    problems += ck.unknown_keys(spec, names_of(PASS_THROUGH), where)
    problems += [f"{where}: missing `{key}`" for key in required_of(PASS_THROUGH) if key not in spec]
    names = ck.part_names(spec["parts"], declared, f"{where}.parts", problems) if "parts" in spec else []
    if len(problems) != count:
        return None
    return PassThrough(tuple(n for n in names if n in parts))


def _must_import(spec: Any, owner: Part, parts: dict[str, Part], declared: set[str],
                 allowed: tuple[Target, ...], problems: list[str]) -> tuple[Target, ...]:
    """The targets a part's files must import one of: each one its `may_import` allows."""
    where = f"parts.{owner.name}.must_import"
    if not isinstance(spec, Mapping) or "must_import" not in spec:
        return ()
    value = spec["must_import"]
    if not isinstance(value, list) or not value:
        problems.append(f"{where}: must be a list of targets such as [<part>, <part>@any]")
        return ()
    count = len(problems)
    found = may_import(value, owner, parts, declared, where, problems)
    if len(problems) != count:
        return ()
    for item, target in zip(value, found):
        if not any(t.part == EVERYTHING or t == target for t in allowed):
            problems.append(f"{where}: {item!r} is not in `may_import`, so no file could import it: add it there, or "
                            "name a part the part may import")
    return found if len(problems) == count else ()


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
            "<preset>, or testing: {files: [<pattern>, ...], functions: <pattern>}"]


def _docs(value: Any, declared: set[str], files: Collection[str], problems: list[str]) -> tuple[str, tuple, tuple]:
    """What only fills the docs, but for the examples: the entry point's name ("" if none), the pages and the naming
    table."""
    if not isinstance(value, Mapping):
        problems.append(f"docs: must be a mapping of {{{', '.join(key.name for key in keys_of(DOCS))}}}")
        return "", (), ()
    problems += ck.unknown_keys(value, names_of(DOCS), "docs")
    entry = value.get("entry", "")
    if "entry" in value and (not isinstance(entry, str) or entry not in declared):
        problems.append(f"docs.entry: no part named {entry!r}")
        entry = ""
    pages = ck.doc_pages(_bare_from(value["pages"]), files, problems, "docs.pages") if "pages" in value else ()
    naming = ck.naming_rows(value["naming"], problems, "docs.naming") if "naming" in value else ()
    return entry, pages, naming
