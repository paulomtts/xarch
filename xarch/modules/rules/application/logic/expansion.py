"""What the keys of a profile mean as rules as data: each check's keys expand to the rules the engine runs, in the
order the check reads them, each saying what the check has always said. The keys of the profile stay as they are;
this is what they mean.
"""
from __future__ import annotations

from xarch.kernel.logic.placement import EVERYTHING
from xarch.modules.rules.domain.rule import ALL, APP, MAY_NOT, MAY_ONLY, TESTS, Rule, Saying, Scope, Targets
from xarch.modules.rules.domain.values import Profile

FORBIDDEN_FIX = "do what needs {hit} outside {rule_part}/, and hand {rule_part}/ the result"


def libraries(profile: Profile) -> tuple[Rule, ...]:
    """A part imports only the outside packages its `libraries` list; the standard library and the app's own package
    are always allowed, and a relative import is the app's own, but a module of the standard library the profile
    reserves is an outside package; one finding per package and line. No rule when no part lists libraries, and none
    for a part whose list is everything."""
    if profile.libraries is None:
        return ()
    reserved = "{part} may not import {top}, which the profile reserves: {reason} (reserved.{top}; {key})"
    outside = "{part} may not import the outside package {top} ({key})"
    owners = "move the code that needs {top} to {owners}, which may import it (parts.{first_owner}.libraries)"
    once = ("line", "top")
    sayings = (Saying(reserved, owners, "reserved-and-owned", once),
               Saying(reserved, "list {top} in the libraries of the part it is reserved for, and keep the code that "
                                "needs it there", "reserved", once),
               Saying(outside, owners, "owned", once),
               Saying(outside, "use the standard library or a package listed in {key}, since {top} is listed for no "
                               "part", once=once))
    return tuple(Rule("libraries", Scope(APP, part), ("import",), MAY_ONLY, Targets("packages", words=allowed),
                      sayings, keep=("absolute", "has-a-path"), exempt=("own-package", "standard-unreserved"),
                      key=f"parts.{part}.libraries", part=part)
                 for part in profile.parts if EVERYTHING not in (allowed := profile.libraries.get(part, ())))


def forbidden(profile: Profile) -> tuple[Rule, ...]:
    """A file of a part with a `forbidden` list neither imports what it names, nor uses a name it lists, nor calls a
    method it lists on anything but what its object holds; a test of a tier that applies the lists is held to the
    list of each part it mirrors. One finding per line and name."""
    if not profile.forbidden:
        return ()
    facts = ("imported", "use", "method")
    keep = ("absolute", "unheld")
    found = [Rule("forbidden", Scope(APP, part), facts, MAY_NOT, Targets("names", names=names),
                  (Saying("{part} may not {verb} {hit} ({key})", FORBIDDEN_FIX, once=("line", "hit")),),
                  keep=keep, exempt=("bound-by-the-import-that-hit",), key=f"parts.{part}.forbidden", part=part)
             for part, names in profile.forbidden.items()]
    found += [Rule("forbidden", Scope(TESTS, part, tier.name, ("not-a-fake",)), facts, MAY_NOT,
                   Targets("names", names=names),
                   (Saying("a test of {rule_part}/ ({tier} tier) may not {verb} {hit} ({key})", FORBIDDEN_FIX,
                           once=("line", "hit")),),
                   keep=keep, exempt=("bound-by-the-import-that-hit",),
                   key=f"parts.{part}.forbidden; tiers.{tier.name}.apply_forbidden", part=part)
              for tier in profile.tiers if tier.forbidden for part, names in profile.forbidden.items()]
    return tuple(found)


def package_only(profile: Profile) -> tuple[Rule, ...]:
    """A part the guard names is imported as a package, never by one of its files, from anywhere outside its own
    folder (its own instance, for a part in a repeating folder), the tests included."""
    if not profile.package_only:
        return ()
    return (Rule("package-only", Scope(ALL), ("edge",), MAY_NOT, Targets("parts", words=profile.package_only),
                 (Saying("{target_part} is imported only as a package, never by its files ({target}) (package-only)",
                         "import from {package}"),),
                 keep=("placed", "below-a-package"), exempt=("same-part-instance",)),)


def private_imports(profile: Profile) -> tuple[Rule, ...]:
    """No file of the app or the tests imports a name private in the language from the app's or the tests' own
    package, or relatively; one finding per name."""
    if not profile.private_imports:
        return ()
    return (Rule("private-imports", Scope(ALL), ("imported",), MAY_NOT, Targets("private"),
                 (Saying("imports the private name {name} from {written} (private-imports)",
                         "make {name} public where it is defined (drop the `_`), or move it to a file both may import"),),
                 keep=("names-a-name", "own-code")),)


def built_by(profile: Profile) -> tuple[Rule, ...]:
    """Only the parts a part lists in `built_by` build a class it defines at the top level of a file; the tests are
    not read."""
    if not profile.built_by:
        return ()
    return (Rule("built-by", Scope(APP), ("build",), MAY_NOT, Targets("parts", words=tuple(profile.built_by)),
                 (Saying("{who} builds {class}, a class of {built}, which only {builders} may build "
                         "(parts.{built_part}.built_by)",
                         "take {class} as a parameter of the constructor, and build it in {builders}"),),
                 exempt=("built-by-a-builder",)),)
