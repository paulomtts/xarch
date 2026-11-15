"""Where code sits in the profile, and whether an import between two places is allowed (section 5).

A file lies in a part, in the structure (a folder of the layout no part claims, such as modules/<module>/, whose
package files hold the tree together and import nothing), or in neither: xarch is a protocol, not a closed world, and
what the profile does not govern is not checked.
"""
from __future__ import annotations

from xarch.kernel.logic.placement import EACH, Place, matches, place_of, reaches
from xarch.modules.rules.domain.values import Profile


def place(profile: Profile, path: tuple[str, ...]) -> Place | None:
    """Where a path below the root package sits: in a part, Place(None) in the structure, or None if ungoverned."""
    found = place_of(profile.parts, path)
    if found.part is not None:
        return found
    if not path or any(matches(folder, path) for folder in profile.folders):
        return found
    return None


def label(profile: Profile, where: Place) -> str:
    """How a place is named in a violation: its part, then the `each` folder it is in by its path, e.g.
    "domain/ of src/billing"; the structure, which no part claims, as "structure/"."""
    if where.part is None:
        return "structure/"
    pattern = profile.parts.get(where.part, ())
    if where.instance is None or EACH not in pattern:
        return f"{where.part}/"
    folder = pattern[:pattern.index(EACH)] + (where.instance,)
    return f"{where.part}/ of {'/'.join(folder)}"


def allowed(profile: Profile, src: Place, dst: Place) -> bool:
    return src.part is not None and any(reaches(target, src, dst) for target in profile.rules.get(src.part, ()))
