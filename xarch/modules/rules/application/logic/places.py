"""Where code sits in the profile, and what a part may import (section 5).

A file lies in a part, in the structure (a folder of the layout no part claims, such as modules/<module>/, whose
package files hold the tree together and import nothing), or in neither: xarch is a protocol, not a closed world, and
what the profile does not govern is not checked.
"""
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import replace

from xarch.kernel.logic.placement import module_steps, place_of, reaches, with_itself
from xarch.kernel.placement import EACH, Marks, Place
from xarch.modules.rules.domain.profile import Profile
from xarch.profile_values.excluded import Excluded
from xarch.profile_values.placement import Repeat, Target


def place(profile: Profile, path: tuple[str, ...]) -> Place | None:
    """Where a path below the root package sits: in a part, Place(None) in the structure, or None if ungoverned."""
    found = place_of(profile.parts, path, profile.language.marks)
    if found.part is not None:
        return found
    if not path or any(matches(folder, path, profile.language.marks) for folder in profile.folders):
        return found
    return None


def file_place(profile: Profile, path: tuple[str, ...]) -> Place | None:
    """Where a source file sits, by its path below the root package as written: its place as the language names it
    (see place)."""
    return place(profile, module_steps(path, profile.language.marks))


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


def instance_root(repeats: Iterable[Repeat], path: tuple[str, ...]) -> tuple[str, ...] | None:
    """The folder of the instance a path lies below (src/billing for src/billing/x): of the deepest repeating folder
    whose folder the path lies below, an instance of it named; None below none."""
    below = [r for r in repeats if len(path) > len(r.root) and path[:len(r.root)] == r.root]
    deepest = max(below, key=lambda r: len(r.root), default=None)
    return None if deepest is None else path[:len(deepest.root) + 1]


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
