"""Where code sits in the profile, and what a part may import (section 5).

A file lies in a part, in the structure (a folder of the layout no part claims, such as modules/<module>/, whose
package files hold the tree together and import nothing), or in neither: xarch is a protocol, not a closed world, and
what the profile does not govern is not checked.
"""
from __future__ import annotations

from collections.abc import Collection, Iterable
from dataclasses import replace

from xarch.kernel.logic.placement import module_steps, named_beside, place_of, reaches, with_itself
from xarch.kernel.placement import EACH, Marks, Place
from xarch.modules.rules.domain.profile import Profile
from xarch.profile_values.excluded import Excluded
from xarch.profile_values.placement import AcceptedImport, Repeat, Target


def place(profile: Profile, path: tuple[str, ...], files: Collection[tuple[str, ...]] = frozenset()) -> Place | None:
    """Where a path below the root package sits: in a part, Place(None) in the structure, or None if ungoverned; files
    are the paths, as the language names them, known to be files, none of which is an instance of a repeating
    folder."""
    found = place_of(profile.parts, path, profile.language.marks, files)
    if found.part is not None:
        return found
    if not path or any(matches(folder, path, profile.language.marks) for folder in profile.folders):
        return found
    return None


def file_place(profile: Profile, path: tuple[str, ...]) -> Place | None:
    """Where a source file sits, by its path below the root package as written: its place as the language names it
    (see place)."""
    return place(profile, path)


def excluded_by(profile: Profile, path: tuple[str, ...]) -> Excluded | None:
    """The folder the profile excludes that a path below the app lies below, if any: nothing there is the app's source."""
    return next((e for e in profile.excluded if path[:len(e.path)] == e.path), None)


def matches(pattern: tuple[str, ...], path: tuple[str, ...], marks: Marks) -> bool:
    """Whether a path is exactly the pattern, `*` standing for any name."""
    pattern, steps = module_steps(pattern, marks), module_steps(path, marks)
    return len(pattern) == len(steps) and all(
        step != EACH and want in (EACH, step) for want, step in zip(pattern, steps))


def label(profile: Profile, where: Place) -> str:
    """How a place is named in a violation: its part, then the repeating folder it is in by its path, e.g.
    "domain/ of src/billing"; the structure, which no part claims, as "structure/"."""
    if where.part is None:
        return "structure/"
    folder = instance_folder(profile, where)
    return f"{where.part}/" if folder is None else f"{where.part}/ of {'/'.join(folder)}"


def instance_folder(profile: Profile, where: Place) -> tuple[str, ...] | None:
    """The folder of the instance of a repeating folder a place lies in (src/billing); None for a place in no
    instance, or of a part outside every repeating folder."""
    pattern = profile.parts.get(where.part or "", ())
    if where.instance is None or EACH not in pattern:
        return None
    return (*pattern[:pattern.index(EACH)], where.instance)


def instance_root(repeats: Iterable[Repeat], path: tuple[str, ...], patterns: Iterable[tuple[str, ...]] = (),
                  files: Collection[tuple[str, ...]] = frozenset()) -> tuple[str, ...] | None:
    """The folder of the instance a path lies below (src/billing for src/billing/x): of the deepest repeating folder
    whose folder the path lies below, an instance of it named; None below none, and None for a step the patterns
    write by name in that folder or for a file of files lying in it, neither of which is an instance."""
    folder = repeat_child(repeats, path, files)
    if folder is None or folder[-1] in named_beside(patterns, folder[:-1]):
        return None
    return folder


def repeat_child(repeats: Iterable[Repeat], path: tuple[str, ...],
                 files: Collection[tuple[str, ...]] = frozenset()) -> tuple[str, ...] | None:
    """The folder a path lies below in the own folder of the deepest repeating folder holding it, an instance or a
    folder the layout names beside the instances (adapters/web for adapters/web/x); None below none, and None for a
    file of files lying in that folder, which is no folder."""
    below = [r for r in repeats if len(path) > len(r.root) and path[:len(r.root)] == r.root]
    deepest = max(below, key=lambda r: len(r.root), default=None)
    if deepest is None:
        return None
    folder = path[:len(deepest.root) + 1]
    return None if folder == path and path in files else folder


def targets_of(profile: Profile, part: str) -> tuple[Target, ...]:
    """What a part may import: itself (its own instance, for a part in a repeating folder), then its row of rules."""
    return with_itself(part, profile.parts[part], profile.rules.get(part, ())) if part in profile.parts else ()


def allowed(profile: Profile, src: Place, dst: Place, name: str | None = None) -> bool:
    """Whether the part at src may import what sits at dst: the name taken from it, or (None) dst as a whole; a target
    of what the part may import (targets_of) reaches it."""
    return src.part is not None and any(reaches(target, src, dst, name) for target in targets_of(profile, src.part))


def narrowed(src: Place | None, at: Place | None, profile: Profile) -> tuple[str, ...]:
    """The name patterns of the targets of the part at src that reach at but for their pattern, each once, in order."""
    if src is None or src.part is None or at is None:
        return ()
    return tuple(dict.fromkeys(t.names for t in targets_of(profile, src.part)
                               if t.names and reaches(replace(t, names=""), src, at)))


def accepting(profile: Profile, part: str | None, path: tuple[str, ...], target: tuple[str, ...],
              name: str | None) -> AcceptedImport | None:
    """The entry of the part's imports.accepted that accepts the import of target (as the language names it, below
    the root) by the file at path (below the app, as written), taking name from it (None: the whole of it), if any: an
    entry of that file naming that target, and that name or none."""
    marks = profile.language.marks
    return next((entry for entry in profile.imports_accepted.get(part or "", ())
                 if entry.file == path and module_steps(entry.target, marks) == target
                 and (not entry.name or entry.name == name)), None)
