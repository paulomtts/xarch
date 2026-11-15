"""Where code sits in the profile, and whether an import between two places is allowed (section 5).

A file lies in a part, in the structure (a folder of the layout no part claims, such as modules/<module>/, whose
package files hold the tree together and import nothing), or in neither: xarch is a protocol, not a closed world, and
what the profile does not govern is not checked.
"""
from __future__ import annotations

from xarch.kernel.logic.placement import EACH, Place, Target, matches, place_of, reaches, with_itself
from xarch.modules.rules.domain.values import Profile


def place(profile: Profile, path: tuple[str, ...]) -> Place | None:
    """Where a path below the root package sits: in a part, Place(None) in the structure, or None if ungoverned."""
    found = place_of(profile.parts, path, profile.language.marks)
    if found.part is not None:
        return found
    if not path or any(matches(folder, path, profile.language.marks) for folder in profile.folders):
        return found
    return None


def label(profile: Profile, where: Place) -> str:
    """How a place is named in a violation: its part, then the repeating folder it is in by its path, e.g.
    "domain/ of src/billing"; the structure, which no part claims, as "structure/"."""
    if where.part is None:
        return "structure/"
    pattern = profile.parts.get(where.part, ())
    if where.instance is None or EACH not in pattern:
        return f"{where.part}/"
    folder = pattern[:pattern.index(EACH)] + (where.instance,)
    return f"{where.part}/ of {'/'.join(folder)}"


def targets_of(profile: Profile, part: str) -> tuple[Target, ...]:
    """What a part may import: itself (its own instance, for a part in a repeating folder), then its row of rules."""
    return with_itself(part, profile.parts[part], profile.rules.get(part, ())) if part in profile.parts else ()


def allowed(profile: Profile, src: Place, dst: Place, name: str | None = None) -> bool:
    """Whether the part at src may import the name from dst, or (None) dst as a whole."""
    return src.part is not None and any(reaches(target, src, dst, name) for target in targets_of(profile, src.part))
