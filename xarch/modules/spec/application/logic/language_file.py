"""The data file of a language (`presets/language/<name>.yaml`): what is true of the language as a whole and is needed
outside the reader that turns source into facts. Read into a Language, with every problem listed; the names of its
standard library, its reserved words and the names it binds without an import are added to it by the service that
holds the runtime, from the lists the file gives or from the runtime.

    title          how a message names the language
    extensions     the endings of a source file's name, each a dot and a name: a non-empty list, the first the one a
                   message prints
    package_files  the names of the files that stand for the folder holding them, each ending in one of the
                   extensions: a non-empty list; optional, left out when no file does. The fact file.package follows
                   it: supplied exactly when it is given, and never written under supplies
    interface      the marks of an interface, each {base: <outside name>}, an outside name (see below) among a
                   declaration's bases, or {keyword: <word>}, a keyword it is declared with or carries, a name
    dynamic        outside names of what imports by a name worked out when the code runs; optional
    dynamic_attributes  outside names of what reads a member of an object by a name worked out when the code runs;
                   a call of one whose first argument an import binds is listed as dynamic; optional
    namespace      the namespace of the names the language binds without an import: a name
    cache          the folder in which its tools keep what they compile, left out of the examples, of a copy of a
                   profile and of the files init writes; optional
    standard       where the standard library, the reserved words and the names bound without an import are known
                   from: interpreter, the interpreter running xarch, or a map of three lists, {modules, reserved,
                   builtins}, each item of modules a package by `package` and each of the others a name by `name`

and, all optional, the tokens of its code the checks and the docs need (empty: the language has none):

    name           a regular expression: what a name may be
    package        a regular expression: what an import names from outside the app as one step
    member         the text that joins a package to a name in it in a profile's lists; name, package and member
                   are given together, and an outside name is written <package> or <package><member><name>, more
                   names after the first joined by `.`. Left out together, any text is a name and an outside name is
                   its whole text
    private        what a name private to its file or folder starts with: a reader may decide by it whether a name
                   is public (the fact public), and scaffold and layout refuse or skip a private name by it
    special        a regular expression: a name the language reserves for itself, matched against the whole name
    call           the special method that calling an instance runs
    nothing        the return annotations, as its reader writes them, that say a function gives no value: a list
    unannotated    `nothing`, its only value: a function with no return annotation gives no value
    comments       the forms a comment is written in, a non-empty list in the order written: {line: <marker>}, from
                   the marker to the end of its line; {block: [<open>, <close>]}, from the one to the other; and
                   {doc: [<open>, <close>]}, a comment the language keeps its documentation in, whose closing may be
                   "" for the end of its line. The docs print the first line form's marker, else the first block
                   form's opening
    directives     the comments its tools read as instructions, each after the marker of a comment of any form; a
                   space stands for any spaces
    shebang        how line 1 names the program that runs the file
    encoding       a regular expression: how line 1 or 2 declares the file's encoding, after the marker of a comment
                   of any form
    branching      the keywords of the statements that branch
    branching_expressions
                   the keywords of the expressions that choose between values, as its reader records them
    immutable      the marks of an immutable record, each {base: <outside name>}, an outside name among a class's
                   bases; {decorator: <outside name>, keywords: {<name>: <value>, ...}}, a decorator called with each
                   keyword given, its value as written, a non-empty string (keywords left out: however it is
                   written); {fields: <word>}, a keyword that marks every field, a name; or {type: <outside name>},
                   a wrapper type
    importing      how a file imports a name from another file of the app: {dotted} stands for that file's dotted
                   path, {name} for the name
    writing        how a row of a table of cases is written, a map of one-line templates, each optional: call, a
                   row that is a call, {callee} standing for what it calls; keyword, a row call whose id a keyword
                   gives, {callee}, {keyword} and {text}; field, a literal row whose id a field gives, {field} and
                   {text}; specs, how a call that builds a mock names its spec, a map of one-line templates, each
                   optional: keyword, by a keyword argument, {callee}, {keyword} and {value}; position, by the
                   positional argument at a place, and type_argument, by the type argument at a place, each
                   {callee}, {before} and {value}. Left out, the language writes no template, and a profile whose
                   table forms or mock specs need one is refused
    worked         how the code of the checks written for the explanation is written, a map of one-line templates,
                   each optional: subclass, a class that derives from a base, {name} and {base}. Left out, the
                   token of that code is left as written

and the facts its reader supplies (see capabilities), each graded:

    supplies       {<fact>: exact | {partial: <what it misses>}}: a fact it does not list it does not supply, so a
                   key whose check needs one is refused; a partial one is listed as approximate where it is read.
                   Left out, the file does not say what a reader supplies (no reader is written for it yet), and
                   no key is held to it; given, file.package is added to it when package_files is given
"""
from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from dataclasses import fields
from typing import Any

from xarch.kernel.logic.names import is_name
from xarch.modules.spec.application.logic.outside_name import outside_name
from xarch.modules.spec.domain.errors import InvalidArchitecture
from xarch.modules.spec.domain.values import INTERPRETER, LANGUAGES, Language, StandardLists
from xarch.profile_values.capabilities import EXACT, FACTS, Supply
from xarch.profile_values.language import (
    BLOCK,
    LINE,
    NOTHING,
    CheckedLanguage,
    CommentForm,
    InterfaceMark,
    RecordMark,
    SpecWriting,
    Worked,
    Writing,
)

KEYS = ("title", "extensions", "package_files", "interface", "dynamic", "dynamic_attributes", "namespace", "cache", "standard", "name",
        "package", "member", "private", "special", "call", "nothing", "unannotated", "comments", "directives", "shebang",
        "encoding", "branching", "importing", "supplies", "immutable", "branching_expressions", "writing", "worked")
REQUIRED = ("title", "extensions", "namespace", "standard")
JOINED = ("name", "package", "member")
"""The keys that say how an outside name is written: given together or not at all."""
_EXTENSION = re.compile(r"\.[A-Za-z0-9]+")
PACKAGE_FACT = "file.package"
"""The fact a language supplies, exactly, when its data file gives package_files, and only then; never written under
`supplies`."""
EXTENSIONS = "extensions: must be a non-empty list of endings, each starting with a dot"
"""What the loader says of a value of `extensions` that is not a list of endings, once for the key."""
PACKAGE_FILES = "package_files: must be a list of file names, each ending in one of extensions"
"""What the loader says of a value of `package_files` that is not a list of file names, once for the key."""
DOC = "doc"
"""The kind of a comment form the language keeps its documentation in, from its opening to its closing (empty: the end
of its line); `line` and `block` are LINE and BLOCK of the language value of `profile_values/`, which the language reads itself."""
COMMENTS = "comments: each form is {line: <marker>}, {block: [<open>, <close>]} or {doc: [<open>, <close>]}"
"""What the loader says of a value of `comments` that is not a list of comment forms, once for the key."""
NO_COMMENTS = "comments: needs one form at least"
"""What the loader says of an empty list of comment forms."""
PARTIAL = "partial"
"""How the data file grades a fact its reader supplies only partly, with what it misses."""
_FOLDER = re.compile(r"[A-Za-z0-9_.-]+")
_IMPORTING = re.compile(r"(?=[^\n]*\{dotted\})(?=[^\n]*\{name\})[^\n]+")
_MEMBER = re.compile(r"\S+")
INTERFACE = "interface: each mark is {base: <outside name>} or {keyword: <word>}"
"""What the loader says of a value of `interface` that is not a list of marks, once for the key."""
IMMUTABLE = "immutable: each mark is {base}, {decorator, keywords}, {fields} or {type}"
"""What the loader says of a value of `immutable` that is not a list of marks, once for the key."""
RECORD_FORMS = ("base", "decorator", "fields", "type")
"""The keys of a mark of an immutable record, exactly one of them in each; `keywords` may stand beside `decorator`."""
STANDARD_LISTS = tuple(field.name for field in fields(StandardLists))
"""The keys of the map a data file's `standard` may be: the lists of StandardLists, in its order."""
STANDARD = (f"standard: must be {INTERPRETER}, or a map of {', '.join(STANDARD_LISTS[:-1])} and {STANDARD_LISTS[-1]}, "
            "each a list of names")
"""What the loader says of a value of `standard` that is neither the word nor the three lists, once for the key."""
WRITING = ("writing: must be a mapping {call, keyword, field, specs}: how a row of a table of cases is written, and "
           "how a call that builds a mock names its spec")
"""What the loader says of a value of `writing` that is not a mapping, once for the key."""
_TEMPLATES = {"call": ("{callee}",), "keyword": ("{callee}", "{keyword}", "{text}"), "field": ("{field}", "{text}")}
"""The templates of `writing`, in the order a problem lists them, each with the placeholders it must hold."""
_HOLDING = {"call": "{callee}", "keyword": "{callee}, {keyword} and {text}", "field": "{field} and {text}"}
"""What a problem says each template must hold."""
SPECS = ("writing.specs: must be a mapping {keyword, position, type_argument}: how a call that builds a mock names "
         "its spec")
"""What the loader says of a value of `writing.specs` that is not a mapping, once for the key."""
_SPEC_TEMPLATES = {"keyword": ("{callee}", "{keyword}", "{value}"), "position": ("{callee}", "{before}", "{value}"),
                   "type_argument": ("{callee}", "{before}", "{value}")}
"""The templates of `writing.specs`, in the order a problem lists them, each with the placeholders it must hold."""
_SPEC_HOLDING = {"keyword": "{callee}, {keyword} and {value}", "position": "{callee}, {before} and {value}",
                 "type_argument": "{callee}, {before} and {value}"}
"""What a problem says each template of `writing.specs` must hold."""
WORKED = "worked: must be a mapping {subclass}: how the code of the checks written for the explanation is written"
"""What the loader says of a value of `worked` that is not a mapping, once for the key."""
_WORKED_TEMPLATES = {"subclass": ("{name}", "{base}")}
"""The templates of `worked`, in the order a problem lists them, each with the placeholders it must hold."""
_WORKED_HOLDING = {"subclass": "{name} and {base}"}
"""What a problem says each template of `worked` must hold."""


def language_of(name: str, document: Any) -> Language:
    """The language the document of the preset called name describes; raises InvalidArchitecture."""
    source = f"{LANGUAGES}/{name}.yaml"
    if not isinstance(document, Mapping):
        raise InvalidArchitecture(source, ["must be a mapping of keys, such as title, extensions and package_files"])
    problems: list[str] = []
    unknown = sorted(str(key) for key in document if key not in KEYS)
    if unknown:
        problems.append(f"unknown key{'s' if len(unknown) > 1 else ''} {', '.join(f'{key!r}' for key in unknown)}: "
                        f"use {', '.join(sorted(KEYS))}")
    problems += [f"missing `{key}`" for key in REQUIRED if key not in document]
    joins = _joins(document, problems)
    names, package, member = joins or ("", "", "")
    title = _text(document, "title", "must be a non-empty string", problems)
    extensions = _extensions(document, problems)
    package_files = _package_files(document, extensions, problems)
    namespace = _text(document, "namespace", "must be a name", problems)
    if namespace and not is_name(namespace, names):
        problems.append("namespace: must be a name")
        namespace = ""
    interface = _interface(document, problems, joins, namespace)
    dynamic = _outside(document, "dynamic", problems, joins, namespace)
    attributes = _outside(document, "dynamic_attributes", problems, joins, namespace)
    standard = _standard(document, problems, joins)
    cache = _text(document, "cache", "must be a folder name", problems, _FOLDER)
    tokens = {key: _text(document, key, "must be a non-empty string", problems)
              for key in ("private", "call", "shebang")}
    comments = _comments(document, problems)
    special = _pattern(document, "special", problems)
    nothing = _annotations(document, problems)
    unannotated = _text(document, "unannotated", f"must be {NOTHING}", problems, re.compile(re.escape(NOTHING)))
    encoding = _pattern(document, "encoding", problems)
    directives = _words(document, "directives", problems)
    branching = _words(document, "branching", problems)
    expressions = _words(document, "branching_expressions", problems)
    importing = _text(document, "importing", "must be a line holding {dotted} and {name}", problems, _IMPORTING)
    supplies = _supplies(document["supplies"], problems) if "supplies" in document else None
    if supplies is not None and package_files:
        supplies = (*supplies, Supply(PACKAGE_FACT, EXACT))
    immutable = _marks(document, problems, joins, namespace)
    writing = _writing(document, problems)
    worked = _worked(document, problems)
    if problems:
        raise InvalidArchitecture(source, problems)
    checked = CheckedLanguage(title=title, extensions=extensions or (), package_files=package_files,
                              interface=interface, dynamic=dynamic, dynamic_attributes=attributes,
                              private=tokens["private"], special=special, call=tokens["call"],
                              nothing=nothing, comments=comments, directives=directives,
                              shebang=tokens["shebang"], encoding=encoding, branching=branching, supplies=supplies,
                              importing=importing, immutable=immutable, branching_expressions=expressions,
                              names=names, package=package, member=member, unannotated=unannotated,
                              writing=writing, worked=worked)
    return Language(name, checked, namespace, standard, cache, names)


def _extensions(document: Mapping[Any, Any], problems: list[str]) -> tuple[str, ...] | None:
    """The endings of a source file's name, in the order written; None when the key is missing, or refused with one
    problem for it."""
    if "extensions" not in document:
        return None
    value = document["extensions"]
    if not (isinstance(value, list) and value and all(isinstance(item, str) and _EXTENSION.fullmatch(item) for item in value)
            and len(set(value)) == len(value)):
        problems.append(EXTENSIONS)
        return None
    return tuple(value)


def _package_files(document: Mapping[Any, Any], extensions: tuple[str, ...] | None,
                   problems: list[str]) -> tuple[str, ...]:
    """The files that stand for the folder holding them, in the order written; none when the key is left out. Each
    must end in one of extensions and be more than the ending, unless extensions are missing or refused already
    (None)."""
    if "package_files" not in document:
        return ()
    value = document["package_files"]
    if not (isinstance(value, list) and value and all(isinstance(item, str) and item.strip() for item in value)
            and len(set(value)) == len(value)):
        problems.append(PACKAGE_FILES)
        return ()
    if extensions is not None:
        problems += [f"package_files: {item!r} ends in none of extensions" for item in value
                     if not any(item.endswith(extension) and item != extension for extension in extensions)]
    return tuple(value)


def _comments(document: Mapping[Any, Any], problems: list[str]) -> tuple[CommentForm, ...]:
    """The forms a comment is written in, in the order written; none when the key is left out. One problem for the
    key when it is an empty list, or no list, or any item is no form."""
    if "comments" not in document:
        return ()
    value = document["comments"]
    if value == []:
        problems.append(NO_COMMENTS)
        return ()
    items = value if isinstance(value, list) else None
    forms = tuple(form for form in (_comment_form(item) for item in items or ()) if form is not None)
    if items is None or len(forms) != len(items):
        problems.append(COMMENTS)
        return ()
    return forms


def _comment_form(item: Any) -> CommentForm | None:
    """One form: a map of one key, line with a non-empty marker, or block or doc with a list of two strings, the
    opening non-empty and, for a block, the closing too; None when the item is none of them."""
    if not (isinstance(item, Mapping) and len(item) == 1):
        return None
    ((kind, value),) = item.items()
    if kind == LINE:
        return CommentForm(LINE, value) if isinstance(value, str) and value.strip() else None
    if kind in (BLOCK, DOC) and isinstance(value, list) and len(value) == 2 and all(isinstance(part, str) for part in value):
        opening, closing = value
        return CommentForm(kind, opening, closing) if opening.strip() and (closing.strip() or kind == DOC) else None
    return None


def _joins(document: Mapping[Any, Any], problems: list[str]) -> tuple[str, str, str] | None:
    """The pattern of a name, the pattern of a package and the member that joins a name to it: ("", "", "") when the
    document gives none of them, None when it gives one wrong or not all three."""
    count = len(problems)
    names = _pattern(document, "name", problems)
    package = _pattern(document, "package", problems)
    member = _text(document, "member", "must be a non-empty string with no space", problems, _MEMBER)
    if any(key in document for key in JOINED):
        problems += [f"missing `{key}`: name, package and member are given together" for key in JOINED
                     if key not in document]
    return (names, package, member) if len(problems) == count else None


def _outside(document: Mapping[Any, Any], key: str, problems: list[str], joins: tuple[str, str, str] | None,
             namespace: str) -> tuple[tuple[str, ...], ...]:
    """The outside names listed at key, each as its steps; none read when the keys that say how one is written are
    refused already (joins None)."""
    if key not in document or joins is None:
        return ()
    names, package, member = joins
    such = f"<package>{member}<name>"
    value = document[key]
    if not isinstance(value, list):
        problems.append(f"{key}: must be a list of outside names, such as [{such}]")
        return ()
    found: list[tuple[str, ...]] = []
    for item in value:
        steps = outside_name(item, names, package, member, namespace) if isinstance(item, str) else None
        if steps is None:
            problems.append(f"{key}: {item!r} is not an outside name such as {such}")
        else:
            found.append(steps)
    return tuple(found)


def _interface(document: Mapping[Any, Any], problems: list[str], joins: tuple[str, str, str] | None,
               namespace: str) -> tuple[InterfaceMark, ...]:
    """The marks of an interface, in the order written; one problem for the key when it is no list or any item is
    no mark; none read when the keys that say how an outside name is written are refused already (joins None)."""
    if "interface" not in document or joins is None:
        return ()
    value = document["interface"]
    items = value if isinstance(value, list) else None
    marks = (_interface_mark(item, joins, namespace) for item in items or ())
    found = tuple(mark for mark in marks if mark is not None)
    if items is None or len(found) != len(items):
        problems.append(INTERFACE)
        return ()
    return found


def _interface_mark(item: Any, joins: tuple[str, str, str], namespace: str) -> InterfaceMark | None:
    """One mark: a map of one key, `base` with an outside name or `keyword` with a name of the language holding no
    space; None when the item is neither."""
    if not (isinstance(item, Mapping) and len(item) == 1):
        return None
    ((key, value),) = item.items()
    if not isinstance(value, str):
        return None
    names, package, member = joins
    if key == "base":
        path = outside_name(value, names, package, member, namespace)
        return InterfaceMark(path) if path is not None else None
    if key == "keyword" and _MEMBER.fullmatch(value) and is_name(value, names):
        return InterfaceMark(keyword=value)
    return None


def _standard(document: Mapping[Any, Any], problems: list[str],
              joins: tuple[str, str, str] | None) -> str | StandardLists:
    """INTERPRETER, or the three lists, each item checked by the language's patterns (a module as a package, the
    others as names) unless the keys that say how a name is written are refused already (joins None); "" when the
    document gives neither, with one problem for the key."""
    if "standard" not in document:
        return ""
    value = document["standard"]
    if value == INTERPRETER:
        return INTERPRETER
    if not (isinstance(value, Mapping) and set(value) == set(STANDARD_LISTS)
            and all(isinstance(value[key], list) and all(isinstance(item, str) and item for item in value[key])
                    for key in STANDARD_LISTS)):
        problems.append(STANDARD)
        return ""
    lists = StandardLists(*(tuple(value[key]) for key in STANDARD_LISTS))
    if joins is None:
        return lists
    names, package, _ = joins
    first, *rest = STANDARD_LISTS
    problems += [f"standard.{first}: {item!r} is not a package name the language allows" for item in value[first]
                 if not is_name(item, package)]
    problems += [f"standard.{key}: {item!r} is not a name the language allows" for key in rest for item in value[key]
                 if not is_name(item, names)]
    return lists


def _marks(document: Mapping[Any, Any], problems: list[str], joins: tuple[str, str, str] | None,
           namespace: str) -> tuple[RecordMark, ...]:
    """The marks of an immutable record, in the order written; one problem for the key when it is no list or any item
    is no mark; none read when the keys that say how an outside name is written are refused already (joins None)."""
    if "immutable" not in document or joins is None:
        return ()
    value = document["immutable"]
    items = value if isinstance(value, list) else None
    found = tuple(mark for mark in (_record_mark(item, joins, namespace) for item in items or ()) if mark is not None)
    if items is None or len(found) != len(items):
        problems.append(IMMUTABLE)
        return ()
    return found


def _record_mark(item: Any, joins: tuple[str, str, str], namespace: str) -> RecordMark | None:
    """One mark: a map of exactly one of RECORD_FORMS, `keywords` beside `decorator` alone; base, decorator and type
    an outside name, fields a name of the language holding no space, each keyword a name of the language with a
    non-empty string; None when the item is none of them."""
    if not isinstance(item, Mapping):
        return None
    forms = [key for key in item if key in RECORD_FORMS]
    if len(forms) != 1 or set(item) - {*forms, *(("keywords",) if forms == ["decorator"] else ())}:
        return None
    (form,) = forms
    value = item[form]
    if not isinstance(value, str):
        return None
    names, package, member = joins
    if form == "fields":
        return RecordMark(fields=value) if _MEMBER.fullmatch(value) and is_name(value, names) else None
    path = outside_name(value, names, package, member, namespace)
    if path is None:
        return None
    if form == "base":
        return RecordMark(base=path)
    if form == "type":
        return RecordMark(type=path)
    if "keywords" not in item:
        return RecordMark(decorator=path)
    keywords = item["keywords"]
    if not (isinstance(keywords, Mapping) and keywords and all(
            isinstance(key, str) and is_name(key, names) and isinstance(word, str) and word.strip()
            for key, word in keywords.items())):
        return None
    return RecordMark(decorator=path, keywords=tuple(keywords.items()))


def _text(document: Mapping[Any, Any], key: str, said: str, problems: list[str],
          pattern: re.Pattern[str] | None = None) -> str:
    if key not in document:
        return ""
    value = document[key]
    if not isinstance(value, str) or not value.strip() or (pattern is not None and not pattern.fullmatch(value)):
        problems.append(f"{key}: {said}")
        return ""
    return value


def _pattern(document: Mapping[Any, Any], key: str, problems: list[str]) -> str:
    value = _text(document, key, "must be a regular expression", problems)
    try:
        re.compile(value)
    except re.error as e:
        problems.append(f"{key}: must be a regular expression: {e}")
        return ""
    return value


def _annotations(document: Mapping[Any, Any], problems: list[str]) -> tuple[str, ...]:
    """The return annotations that say a function gives no value, as the reader writes them: a non-empty list of
    non-empty texts; none when the document does not say."""
    if "nothing" not in document:
        return ()
    value = document["nothing"]
    if not isinstance(value, list) or not value or not all(isinstance(item, str) and item.strip() for item in value):
        problems.append("nothing: must be a list of return annotations")
        return ()
    return tuple(value)


def _words(document: Mapping[Any, Any], key: str, problems: list[str]) -> tuple[str, ...]:
    if key not in document:
        return ()
    value = document[key]
    if not isinstance(value, list) or not all(isinstance(item, str) and item.strip() for item in value):
        problems.append(f"{key}: must be a list of non-empty strings")
        return ()
    return tuple(value)


def _supplies(value: Any, problems: list[str]) -> tuple[Supply, ...]:
    if not isinstance(value, Mapping):
        problems.append(f"supplies: must be a mapping of facts to {EXACT} or {{{PARTIAL}: <what it misses>}}")
        return ()
    found: dict[str, Supply] = {}
    for fact, grade in value.items():
        if fact not in FACTS:
            problems.append(f"supplies: {fact!r} is not a fact a check reads: use {', '.join(sorted(FACTS))}")
        elif fact == PACKAGE_FACT:
            problems.append(f"supplies: {PACKAGE_FACT} follows package_files: drop it from supplies")
        elif grade == EXACT:
            found[fact] = Supply(fact, EXACT)
        elif isinstance(grade, Mapping) and list(grade) == [PARTIAL] and isinstance(grade[PARTIAL], str) \
                and grade[PARTIAL].strip():
            found[fact] = Supply(fact, PARTIAL, grade[PARTIAL])
        else:
            problems.append(f"supplies.{fact}: must be {EXACT}, or {{{PARTIAL}: <what it misses>}} with a line of text")
    return tuple(found.values())


def first_language(languages: Iterable[str]) -> str:
    """The language of an app whose profile names none: the first of the languages xarch reads, by name; "" when it
    reads none."""
    return min(languages, default="")


def _writing(document: Mapping[Any, Any], problems: list[str]) -> Writing:
    """How a row of a table of cases is written, and how a call that builds a mock names its spec (specs); empty
    templates when the key is left out or refused. Each template is a one-line text holding every placeholder of its
    own."""
    if "writing" not in document:
        return Writing()
    value = document["writing"]
    if not isinstance(value, Mapping):
        problems.append(WRITING)
        return Writing()
    found = _templates(value, "writing", _TEMPLATES, _HOLDING, ("specs",), problems)
    specs = _spec_templates(value["specs"], problems) if "specs" in value else SpecWriting()
    return Writing(**found, specs=specs)


def _worked(document: Mapping[Any, Any], problems: list[str]) -> Worked:
    """How the code of the checks written for the explanation is written; empty templates when the key is left out or
    refused. Each template is a one-line text holding every placeholder of its own."""
    if "worked" not in document:
        return Worked()
    value = document["worked"]
    if not isinstance(value, Mapping):
        problems.append(WORKED)
        return Worked()
    return Worked(**_templates(value, "worked", _WORKED_TEMPLATES, _WORKED_HOLDING, (), problems))


def _spec_templates(value: Any, problems: list[str]) -> SpecWriting:
    """How a call that builds a mock names its spec, each way its own template; empty ones when refused."""
    if not isinstance(value, Mapping):
        problems.append(SPECS)
        return SpecWriting()
    return SpecWriting(**_templates(value, "writing.specs", _SPEC_TEMPLATES, _SPEC_HOLDING, (), problems))


def _templates(value: Mapping[Any, Any], where: str, templates: Mapping[str, tuple[str, ...]],
               holding: Mapping[str, str], more: tuple[str, ...], problems: list[str]) -> dict[str, str]:
    """The templates the mapping at where writes, by key, each a one-line text holding every placeholder of its own;
    a key that is neither a template nor one of more is refused, all such keys in one problem."""
    unknown = sorted(str(key) for key in value if key not in templates and key not in more)
    if unknown:
        problems.append(f"{where}: unknown key{'s' if len(unknown) > 1 else ''} "
                        f"{', '.join(f'{key!r}' for key in unknown)}: use {', '.join((*templates, *more))}")
    found: dict[str, str] = {}
    for key, held in templates.items():
        line = value.get(key)
        if key in value and isinstance(line, str) and line.strip() and "\n" not in line and all(h in line for h in held):
            found[key] = line
        elif key in value:
            problems.append(f"{where}.{key}: must be a line holding {holding[key]}")
    return found
