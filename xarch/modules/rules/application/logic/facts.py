"""The facts of a run, read once from the parsed files: where each file sits (placement, worked out once per file), and
what it says, by kind, each fact as a rule reads it (see Fact, and the kinds of the vocabulary). A file that does not
parse says only its error, and a file of the app no part and no folder of the layout governs, which is not read, only
that it is there.

A dotted name starts at a namespace: the app's own code at the app's root package, the tests' at theirs; a reader
turns its language's imports and names into such paths, and a fact into the app or the tests is read below that root.

    syntax-error        how a file fails to parse: the line, text the parser's message
    file                the file as a whole, at line 0; traits no-statements when no function or method of it holds
                        a real statement, exceptions-only when it defines classes, every one an exception (below), and no
                        top-level function
    names-mentioned     every name the file mentions, annotations included, by its last step alone
    import              each import as written: the module it names (path), relative, standard
    imported-name       each name an import takes, path the module and the name (the module alone for an import of
                        a whole module), the name it takes (None for a whole module); its traits are the import's
    use                 each name read, path the dotted path it reaches, bound how many steps the binding import bound
    method-call         each call of an attribute no import binds, name the attribute; on-own-object when it is
                        on the object a method is called on
    call                each call whose callee an import binds, path the callee; at where the callee sits when it is
                        the app's
    import-into-app     each import into the app's own package, the target the file or package it reaches below the
                        root and at where that sits (None when no part and no folder of the layout governs it), name
                        the name it takes when that is no file; a test's relative imports are its own and none is one
    import-into-tests   each import of a test file into the tests' own package, the target it reaches below the tests
                        root
    comment             each line comment, text as written
    class               each class defined at the top level, name its name, names those its bases and body mention;
                        exception, record and interface when it is one (below)
    function            each function defined at the top level or in a class of the top level, name its name, path
                        its class and its name; top-level when it is in no class; forwards when it is a method the
                        reader says only forwards, text the callee it forwards to and target the attributes it
                        returns of the call's result
    callback            each call of a function's own parameter by its bare name, path the function, name the
                        parameter; receiver when the parameter is the first of a method, annotated-callable when its
                        annotation says it is a callable

and the facts derived from them over the whole app:

    construction        a call of a class the app defines at the top level of a file, read through the import that
                        binds the callee: path the callee, name the class, at where the class's file sits
    function-reference  a use that reaches a function the app defines at the top level of a file (the first prefix,
                        from the one its import bound, whose last name the file binds to a function alone), other than
                        the callee of a call on its line, once for each such call: target that function below the
                        root, at where its file sits
    exception           a class that derives from one of the language's builtin exceptions, as the reader says, or from
                        a class of the app that is an exception, however far that goes (a base read through the
                        absolute import that binds it)
    record              a class with no method but the language's special methods (its data file says how they are
                        named) that a top-level function of its file names in its return annotation
    interface           a class with one of the names the language's data file marks interfaces with among its bases,
                        the last of its name in its file
"""
from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Iterator
from dataclasses import replace

from xarch.kernel.placement import Place
from xarch.modules.rules.application.logic.filters import in_scope
from xarch.modules.rules.application.logic.imports import dotted, named_targets, targets
from xarch.modules.rules.application.logic.places import place
from xarch.modules.rules.application.logic.tier_of import tested
from xarch.modules.rules.domain.rule import MUST_REACH, Defined, Fact, Facts, Read, Rule, Scope
from xarch.modules.rules.domain.values import Class, Function, Profile, SourceFile
from xarch.modules.rules.domain.vocabulary import KINDS as VOCABULARY

Placements = dict[tuple[str, ...], Place | None]
"""Where each path below the root placed so far sits."""

KINDS = tuple(kind.name for kind in VOCABULARY)
"""Every kind of fact, in the order a file's facts are worked out."""

_TRAITS = {(relative, standard, held): frozenset(name for name, on in (("relative", relative), ("standard", standard),
                                                                       ("on-own-object", held)) if on)
           for relative in (False, True) for standard in (False, True) for held in (False, True)}
"""The traits of a fact, by whether it is relative, of the standard library and held."""
_TOP = frozenset({"top-level"})
_RECEIVER, _ANNOTATED = "receiver", "annotated-callable"
_FORWARDS = frozenset({"forwards"})


def facts_of(app: Iterable[SourceFile], tests: Iterable[SourceFile], profile: Profile, root: str,
             tests_root: str = "", rules: Iterable[Rule] | None = None, unread: Iterable[SourceFile] = ()) -> Facts:
    """The facts of the app's files, below the root package root, then of the files of the app that are not read
    (unread), then of the test files, below the package tests_root: every kind of each file, or (rules given) the
    kinds the rules whose scope holds the file read."""
    marks = profile.language.marks
    app, tests = [(f, *dotted(f.path, marks)) for f in app], [(f, *dotted(f.path, marks)) for f in tests]
    known = frozenset(steps for f, steps, _ in app if f.error is None)
    known_tests = frozenset(steps for f, steps, _ in tests if f.error is None)
    cache: Placements = {}
    parsed = [(f, steps) for f, steps, _ in app if f.error is None]
    defined = Defined(root, {(root, *steps, c.name): _placed(profile, cache, steps) for f, steps in parsed
                             for c in f.classes},
                      {steps: frozenset(f.module_functions) for f, steps in parsed},
                      frozenset(exceptions(parsed, root)))
    covered = {s.part: tier.name for tier in reversed(profile.tiers) for s in tier.subject}
    placed = [_covered(Read(file, steps, package, False, _placed(profile, cache, steps)), covered)
              for file, steps, package in app]
    placed += [Read(file, steps, package, False, _placed(profile, cache, steps)) for file, steps, package in
               ((f, *dotted(f.path, marks)) for f in unread)]
    placed += [_tested(file, steps, package, profile) for file, steps, package in tests]
    bare = Facts((), root, tests_root, known, known_tests,
                 frozenset(r.steps for r in placed if r.test and r.is_test and r.file.error is None),
                 {r.steps: r.tier for r in placed if not r.test and r.tier and r.file.error is None})
    rules = tuple(rules) if rules is not None else None
    read = tuple(replace(r, facts={kind: _facts(kind, r, profile, cache, defined, bare)
                                   for kind in (KINDS if rules is None else _read(r, rules, bare, profile))})
                 for r in placed)
    return replace(bare, files=read)


def _covered(read: Read, covered: dict[str, str]) -> Read:
    """The file with the tier whose tests cover its part, the first that does."""
    part = read.place.part if read.place is not None else None
    return replace(read, tier=covered.get(part, "")) if part is not None else read


def _tested(file: SourceFile, steps: tuple[str, ...], package: bool, profile: Profile) -> Read:
    where = tested(profile, file.path)
    return Read(file, steps, package, True, None, where.tier.name if where.tier is not None else "", where.instance,
                where.own, where.parts, where.is_test, where.is_fake)


def _read(read: Read, rules: tuple[Rule, ...], facts: Facts, profile: Profile) -> tuple[str, ...]:
    """The kinds of fact the rules read of the file: those whose scope holds it read their kinds, their links and their
    spread; a rule of reach reads the kinds and the links of every file on its scope's side (see reach_scopes), and
    the links of its roots; and a rule that a file must reach reads the file of each file of its scope, which it
    says."""
    kinds: list[str] = []
    for rule in rules:
        if in_scope(rule.scope, read, facts, profile):
            kinds += [*rule.facts, *rule.spread, *rule.links, *(("file",) if rule.quantifier == MUST_REACH else ())]
        side, roots = reach_scopes(rule)
        if side is not None and in_scope(side, read, facts, profile):
            kinds += [*rule.facts, *rule.links]
        if roots is not None and in_scope(roots, read, facts, profile):
            kinds += rule.links
    return tuple(dict.fromkeys(kinds))


def reach_scopes(rule: Rule) -> tuple[Scope | None, Scope | None]:
    """The files a rule of reach reads besides its scope: for MUST_REACH, every file of its scope's side, whose facts
    may match a target or lead to one; for MUST_BE_REACHED, its roots. None where the rule has none."""
    return (Scope(rule.scope.files) if rule.quantifier == MUST_REACH else None), rule.roots


def _facts(kind: str, read: Read, profile: Profile, cache: Placements, defined: Defined,
           facts: Facts) -> tuple[Fact, ...]:
    file, root = read.file, defined.root
    package = read.steps if read.package else read.steps[:-1]
    if file.error is not None:
        return (Fact("syntax-error", file.error.line, text=file.error.message),) if kind == "syntax-error" else ()
    match kind:
        case "syntax-error":
            return ()
        case "file":
            return (Fact("file", 0, traits=_file(file, read, defined)),)
        case "names-mentioned":
            return (Fact("names-mentioned", 0, names=file.named),)
        case "comment":
            return tuple(Fact("comment", c.line, text=c.text) for c in file.comments)
        case "class":
            ports = {c.name: c for c in file.classes if any(base in profile.language.interface for base in c.bases)}
            return tuple(Fact("class", c.line, (c.name,), c.name, _class(c, file, read, profile, defined, ports),
                              names=c.named) for c in file.classes)
        case "function":
            return tuple(_function(f) for f in file.functions)
        case "callback":
            return tuple(Fact("callback", c.line, (c.function,), c.parameter,
                              frozenset(n for n, on in ((_RECEIVER, c.receiver), (_ANNOTATED, c.annotated)) if on))
                         for c in file.callbacks)
        case "import":
            return tuple(Fact("import", i.line, i.module, traits=_TRAITS[i.relative, i.standard, False],
                              text=i.written) for i in file.imports)
        case "imported-name":
            return tuple(_imported(file))
        case "use":
            return tuple(Fact("use", u.line, u.name, bound=u.bound) for u in file.uses)
        case "method-call":
            return tuple(Fact("method-call", m.line, name=m.name, traits=_TRAITS[False, False, m.held])
                         for m in file.method_calls)
        case "call":
            return tuple(Fact("call", c.line, c.func,
                              at=_placed(profile, cache, c.func[1:]) if c.func[:1] == (root,) else None)
                         for c in file.calls)
        case "construction":
            return tuple(Fact("construction", c.line, c.func, c.func[-1], at=defined.classes[c.func])
                         for c in file.calls if c.func in defined.classes)
        case "function-reference":
            return tuple(_references(file, profile, cache, defined))
        case "import-into-app" if read.test:
            return tuple(Fact("import-into-app", line, target=target, at=_placed(profile, cache, target))
                         for line, target in targets((i for i in file.imports if not i.relative), (), facts.known,
                                                     root))
        case "import-into-app":
            return tuple(Fact("import-into-app", line, name=name, target=target, at=_placed(profile, cache, target))
                         for line, target, name in named_targets(file.imports, package, facts.known, root))
        case "import-into-tests":
            return tuple(Fact("import-into-tests", line, target=target) for line, target in
                         targets(file.imports, package, facts.known_tests, facts.tests_root)) if read.test else ()
    raise ValueError(f"no kind of fact is named {kind!r}")


def _references(file: SourceFile, profile: Profile, cache: Placements, defined: Defined) -> Iterator[Fact]:
    """The uses that reach a function the app defines, but the callee of a call on its line, once for each call."""
    calls = Counter((call.line, call.func) for call in file.calls)
    for use in file.uses:
        if use.name[:1] != (defined.root,):
            continue
        for end in range(max(use.bound, 2), len(use.name) + 1):
            module, function = use.name[1:end - 1], use.name[end - 1]
            if function in defined.functions.get(module, ()):
                if calls[(use.line, use.name)] > 0:
                    calls[(use.line, use.name)] -= 1
                else:
                    yield Fact("function-reference", use.line, use.name, target=(*module, function),
                               at=_placed(profile, cache, module))
                break


def _placed(profile: Profile, cache: Placements, path: tuple[str, ...]) -> Place | None:
    """Where a path below the root sits, worked out once a run."""
    if path not in cache:
        cache[path] = place(profile, path)
    return cache[path]


def _class(cls: Class, file: SourceFile, read: Read, profile: Profile, defined: Defined,
           ports: dict[str, Class]) -> frozenset[str]:
    exception = (read.steps, cls.name) in defined.exceptions and not read.test
    record = all(profile.language.is_special(m.name) for m in cls.methods) and any(
        cls.name in f.returns_named for f in file.functions if not f.owner)
    return frozenset(n for n, on in (("exception", exception), ("record", record),
                                     ("interface", ports.get(cls.name) is cls)) if on)


def _function(function: Function) -> Fact:
    path = (function.owner, function.name) if function.owner else (function.name,)
    if not function.owner:
        return Fact("function", function.line, path, function.name, _TOP)
    if not function.forwards or function.sole_call is None:
        return Fact("function", function.line, path, function.name)
    return Fact("function", function.line, path, function.name, _FORWARDS, target=function.sole_call.then,
                text=function.forwards)


def _file(file: SourceFile, read: Read, defined: Defined) -> frozenset[str]:
    code = any(f.real_statements for f in file.functions)
    raising = bool(file.classes) and not read.test and all(
        (read.steps, c.name) in defined.exceptions for c in file.classes) and not any(not f.owner for f in file.functions)
    return frozenset(n for n, on in (("no-statements", not code), ("exceptions-only", raising)) if on)


def exceptions(files: Iterable[tuple[SourceFile, tuple[str, ...]]], root: str) -> set[tuple[tuple[str, ...], str]]:
    """Every class of the files, each with its steps below the root, that is an exception, as (its file's steps, its
    name)."""
    classes = {(steps, c.name): c for f, steps in files for c in f.classes}
    found = {key for key, cls in classes.items() if cls.exception}
    grown = True
    while grown:
        grown = False
        for key, cls in classes.items():
            if key not in found and any(base is not None and base[:1] == (root,)
                                        and (base[1:-1], base[-1]) in found for base in cls.bases):
                found.add(key)
                grown = True
    return found


def _imported(file: SourceFile) -> Iterator[Fact]:
    for i in file.imports:
        traits = _TRAITS[i.relative, i.standard, False]
        if i.names is None:
            yield Fact("imported-name", i.line, i.module, traits=traits, text=i.written)
        else:
            yield from (Fact("imported-name", i.line, (*i.module, name), name, traits, text=i.written) for name in i.names)
