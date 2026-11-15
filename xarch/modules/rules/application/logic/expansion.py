"""What the keys of a profile mean as rules as data: each check's keys expand to the rules the engine runs, in the
order the check reads them, each saying what the check has always said. The keys of the profile stay as they are;
this is what they mean.
"""
from __future__ import annotations

from xarch.kernel.logic.placement import EVERYTHING
from xarch.modules.rules.application.logic.places import targets_of
from xarch.modules.rules.application.logic.tier_of import NO_TIER, NO_TIER_FIX
from xarch.modules.rules.domain.rule import (
    ALL,
    APP,
    EXISTING,
    MAY_NOT,
    MAY_ONLY,
    STRUCTURE,
    TESTS,
    Rule,
    Saying,
    Scope,
    Targets,
)
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


def rules(profile: Profile) -> tuple[Rule, ...]:
    """Every import between places the profile governs is allowed by the rules of the importing file's part: a part
    may import itself and its `may_import` row, where a target with a name pattern allows only the names it matches;
    the structure may import nothing the profile governs."""
    narrowed = Saying("{part} may import only {patterns} from {target_part}, {taken} ({target_name})",
                      "import from {target_part} only names that match {patterns} ({key}), or move what needs the rest "
                      "to a part that may import it", "narrowed")
    plain = "{part} may not import {target_part} ({target})"
    sayings = (narrowed, Saying(plain, "drop the import of {target_part}, or {move}", "permits-nothing"),
               Saying(plain, "import only {permitted} in {part} ({key}), or {move}"))
    found = [Rule("rules", Scope(APP, part), ("edge",), MAY_ONLY, Targets("places", places=targets_of(profile, part)),
                  sayings, keep=("placed",), key=f"parts.{part}.may_import", part=part) for part in profile.parts]
    return (*found, Rule("rules", Scope(APP, STRUCTURE), ("edge",), MAY_ONLY, Targets("places"), sayings,
                         keep=("placed",)))


def types_only_tiers(profile: Profile) -> tuple[Rule, ...]:
    """A test of a tier that names parts in `types_only` never calls what it imports from them, and never references
    one of their functions; a call is not said again as a reference."""
    return tuple(_types_only(Scope(TESTS, tier=tier.name), f"a {tier.name} test", f"tiers.{tier.name}.types_only",
                             tier.types_only, "{tier_fix}")
                 for tier in profile.tiers if tier.types_only)


def types_only_parts(profile: Profile) -> tuple[Rule, ...]:
    """A file of a part that names parts in its own `types_only` is held to the same rule."""
    return tuple(_types_only(Scope(APP, part), "{part}", f"parts.{part}.types_only", parts, "{caller_fix}", part)
                 for part, parts in profile.types_only.items())


def _types_only(scope: Scope, who: str, key: str, parts: tuple[str, ...], fix: str, part: str = "") -> Rule:
    said = f"{who} uses {{target_part}} only as a type: it may not "
    return Rule("types-only", scope, ("call", "reference"), MAY_NOT, Targets("parts", words=parts),
                (Saying(said + "call {callee} ({key})", fix, "a-call"),
                 Saying(said + "reference {target}, a function ({key})", fix)),
                keep=("placed",), exempt=("called",), key=key, part=part)


def tiers(profile: Profile) -> tuple[Rule, ...]:
    """A test file lies in a tier; a file of a tier imports, of the app, what the part its folder mirrors may (or its
    tier's subject, for one placed by its tier's folder); and of the test code, the fakes only when its tier tests a
    part they stand in for, never another test file (once per line), and anything else only from its own folder."""
    if not profile.tiers:
        return ()
    mirrored = Saying("a test of {subject} ({tier} tier) may not import {target_part} ({target}): it imports only what "
                      "{subject} may ({mirrored_keys})",
                      "import here only what {subject} may; test {target_part} from the folder that mirrors it",
                      "mirroring")
    by_folder = Saying("a {tier} test may not import {target_part} ({target})",
                       "import here only what the subject of the {tier} tier may; test {target_part} from the folder "
                       "that mirrors it")
    fakes = Saying("a {tier} test may not import the fakes ({tests_target}): only a tier that tests {faked} may",
                   "drop the import of {tests_target}, or move the test to a tier that tests {faked}", "into-the-fakes")
    test = Saying("a test may not import another test file ({tests_target}): what tests share lives in test code that "
                  "is no test file",
                  "move what {tests_target} holds that this test needs into test code of its folder that is no test "
                  "file, and import it from there", "into-a-test", ("line", "tests_target"))
    elsewhere = Saying("a test may import test code only from its own folder {own}/ ({tests_target})",
                       "move what {tests_target} holds into {own}/, or drop the import")
    return (Rule("tiers", Scope(TESTS, where=("untiered", "a-test", "not-a-fake")), ("file",), MAY_NOT, EXISTING,
                 (Saying(NO_TIER, NO_TIER_FIX),)),
            Rule("tiers", Scope(TESTS, where=("tiered",)), ("edge",), MAY_ONLY, Targets("allowance"),
                 (mirrored, by_folder), keep=("placed",)),
            Rule("tiers", Scope(TESTS, where=("tiered",)), ("suite_edge",), MAY_ONLY, Targets("test-code"),
                 (fakes, test, elsewhere)))


def book(profile: Profile) -> dict[str, tuple[Rule, ...]]:
    """Every check the engine runs, by the name of its group, each the rules its keys expand to."""
    return {"rules": rules(profile), "libraries": libraries(profile), "forbidden": forbidden(profile),
            "tiers": tiers(profile), "types-only tiers": types_only_tiers(profile),
            "package-only": package_only(profile), "types-only parts": types_only_parts(profile),
            "built-by": built_by(profile), "private-imports": private_imports(profile)}
