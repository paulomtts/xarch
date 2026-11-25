"""The shared check: a part the profile declares shared (`parts.<part>.shared: <least>`) holds only what at least that
many users use. Every public name a file of the part defines at the top level (a class, a function a definition alone
binds, a name an assignment binds), public as the language's reader says it is, is used by at least least users, or
it is reported at its definition.

A user is where a file of the app that uses the name lies: the instance of a repeating folder it is in, for a file of
a part in one (every part of that instance counts as that one user), else its part. A file in no part (the structure,
or ungoverned) is no user, nor is a file of a part declared shared, which passes on the users of its own names that
mention the name instead (below); the tests are never read, and the place the name is defined in is never its own
user (for a part outside every repeating folder, another file of the part itself; for one inside, a file of its own
instance).

A file uses a name when it imports it from the file that defines it (an import that takes the name from that file)
and mentions it anywhere else, in code or an annotation; or reads it through an import of its file or package (the
name read as an attribute of the file, as the reader resolves it). An import of a name the file never mentions again
is a re-export, not a use: the file passes it on, and a file that imports it from there uses the name it passes on,
however many files it passes through. A name is also used by the users of every other name of the part (public or private, of any file of
the part) whose definition mentions it: by its last step, a name its own file defines or one the file imports from a
file of a shared part, as a class's bases and body, a function's decorators, signature and body, or an assignment's
annotation and value mention it, however far that goes, since a name its own part needs to say another name's shape
or to do its work cannot move to one user.

The message names the users it has, when fewer than least: none, one (the fix says to move the name to it, or to its
published types if others read it through them), or several.
"""
from __future__ import annotations

from collections.abc import Iterable

from xarch.kernel.placement import Place
from xarch.kernel.violations import Violation
from xarch.modules.rules.application.logic.imports import dotted, named_targets
from xarch.modules.rules.application.logic.places import instance_folder, place
from xarch.modules.rules.domain.parsed import SourceFile
from xarch.modules.rules.domain.profile import Profile

RULE = "shared"

Name = tuple[tuple[str, ...], str]
"""A name as the file that binds it at its top level, by its steps below the root, and the name."""


def violations(app: Iterable[SourceFile], profile: Profile, root: str) -> list[Violation]:
    if not profile.shared:
        return []
    marks = profile.language.marks
    files = [(file, *dotted(file.path, marks)) for file in sorted(app, key=lambda f: f.name) if file.error is None]
    known = frozenset(steps for _, steps, _ in files)
    where = {steps: place(profile, steps) for _, steps, _ in files}
    defined = _defined(files, where, profile)
    passed = {(steps, name): target for file, steps, package in files
              for _, target, name in named_targets(file.imports, package, known, root) if name is not None}
    users: dict[Name, set[str]] = {key: set() for key in defined}
    for file, steps, package in files:
        own = _user(where[steps], profile)
        if own is None or where[steps].part in profile.shared:
            continue
        for key in _used(file, steps, package, known, passed, defined, root):
            if own != _user(where[key[0]], profile):
                users[key].add(own)
    _spread(users, _mentions(files, defined, passed, known, root))
    found: list[Violation] = []
    for key, (file, line, kind, part, public) in defined.items():
        least = profile.shared[part]
        shown = sorted(users[key])
        if not public or len(shown) >= least:
            continue
        name = key[1]
        message = (f"the {kind} {name} is used by {_users(shown, part)}, but {part}/ holds only what at least {least} "
                   f"users share (parts.{part}.shared)")
        found.append(Violation(file.name, line, message, RULE, _fix(name, shown)))
    return sorted(found, key=lambda v: (v.file, v.line))


def _defined(files, where: dict[tuple[str, ...], Place | None],
             profile: Profile) -> dict[Name, tuple[SourceFile, int, str, str, bool]]:
    """Every name a file of a shared part binds at its top level, private ones too: the file, the line, what it is,
    the part, and whether the reader says it is public (a function's name is public as that function is)."""
    found: dict[Name, tuple[SourceFile, int, str, str, bool]] = {}
    for file, steps, _ in files:
        at = where[steps]
        if at is None or at.part not in profile.shared:
            continue
        named = [(c.line, c.name, "class", c.public) for c in file.classes]
        named += [(f.line, f.name, "function", f.public) for f in file.functions
                  if not f.owner and f.name in file.module_functions]
        named += [(c.line, c.name, "constant", c.public) for c in file.constants]
        for line, name, kind, public in sorted(named):
            found.setdefault((steps, name), (file, line, kind, at.part, public))
    return found


def _resolved(key: Name, passed: dict[Name, tuple[str, ...]], defined) -> Name | None:
    """The definition a name bound in a file stands for, through the files that pass it on; None for none."""
    seen: set[Name] = set()
    while key not in defined:
        if key in seen or key not in passed:
            return None
        seen.add(key)
        key = (passed[key], key[1])
    return key


def _used(file: SourceFile, steps: tuple[str, ...], package: tuple[str, ...], known, passed, defined,
          root: str) -> set[Name]:
    """The definitions the file uses: by a name it imports and mentions, or by a read through its file."""
    found: set[Name] = set()
    for line, target, name in named_targets(file.imports, package, known, root):
        if name is not None and (line, name) not in file.unmentioned:
            resolved = _resolved((target, name), passed, defined)
            if resolved is not None:
                found.add(resolved)
    for use in file.uses:
        if use.name[:1] != (root,):
            continue
        path = use.name[1:]
        for end in range(len(path) - 1, 0, -1):
            if path[:end] in known:
                resolved = _resolved((path[:end], path[end]), passed, defined)
                if resolved is not None:
                    found.add(resolved)
                    break
    return found


def _mentions(files, defined, passed, known, root: str) -> dict[Name, set[Name]]:
    """The names of the shared parts each of their definitions mentions, resolved in its own file."""
    texts = {steps: file for file, steps, _ in files}
    named: dict[Name, frozenset[str]] = {}
    for steps, name in defined:
        file = texts[steps]
        named[(steps, name)] = next(
            (n for n in [*(c.named for c in file.classes if c.name == name),
                         *(f.named for f in file.functions if not f.owner and f.name == name),
                         *(c.named for c in file.constants if c.name == name)]), frozenset())
    found: dict[Name, set[Name]] = {}
    for (steps, name), mentioned in named.items():
        found[(steps, name)] = {resolved for other in mentioned if other != name
                                if (resolved := _resolved((steps, other), passed, defined)) is not None}
    return found


def _spread(users: dict[Name, set[str]], mentions: dict[Name, set[Name]]) -> None:
    """Give each name the users of every name whose definition mentions it, however far."""
    grown = True
    while grown:
        grown = False
        for name, mentioned in mentions.items():
            for other in mentioned:
                if not users[name] <= users[other]:
                    users[other] |= users[name]
                    grown = True


def _user(at: Place | None, profile: Profile) -> str | None:
    """The user a file at a place is: its instance's folder, or its part; None in no part."""
    if at is None or at.part is None:
        return None
    folder = instance_folder(profile, at)
    return f"{at.part}/" if folder is None else "/".join(folder)


def _users(shown: list[str], part: str) -> str:
    if not shown:
        return f"nothing outside {part}/"
    if len(shown) == 1:
        return f"{shown[0]} alone"
    return f"{', '.join(shown[:-1])} and {shown[-1]} only"


def _fix(name: str, shown: list[str]) -> str:
    if not shown:
        return f"move {name} next to the code that uses it, or delete it if nothing does"
    if len(shown) == 1:
        return (f"move {name} to {shown[0]}, its one user, or to the published types of {shown[0]} if others read it "
                "through them")
    return f"move {name} to the user that owns it and have the others import it from there"
