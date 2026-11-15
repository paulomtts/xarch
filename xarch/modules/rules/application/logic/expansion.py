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
    LIST,
    MAY_NOT,
    MAY_ONLY,
    MUST_BE_REACHED,
    MUST_REACH,
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


def syntax(profile: Profile) -> tuple[Rule, ...]:
    """A file that does not parse is a violation, at the line its error is on, and no other rule reads it."""
    return (Rule("syntax", Scope(ALL), ("error",), MAY_NOT, EXISTING,
                 (Saying("not valid {title}: {text}", "correct the syntax so that the file can be read"),)),)


def names(profile: Profile) -> tuple[Rule, ...]:
    """Every public class of a part that lists `names` matches one of its patterns, `*` standing for any text."""
    return tuple(Rule("names", Scope(APP, part), ("class",), MAY_ONLY, Targets("patterns", words=patterns),
                      (Saying("{name} does not match {wanted}, as every class of {part} must ({key})",
                              "rename {name} to match {wanted}, or move it to the part whose kind of class it is"),),
                      keep=("public",), key=f"parts.{part}.names", part=part)
                 for part, patterns in profile.names.items())


def no_callbacks(profile: Profile) -> tuple[Rule, ...]:
    """Code of a part that lists `no_callbacks` calls none of its own parameters annotated as callables; the first
    parameter of a method, the object it is called on, is no callback."""
    return tuple(Rule("no-callbacks", Scope(APP, part), ("callback",), MAY_NOT, EXISTING,
                      (Saying("{function} calls its parameter {name}: {part} takes no callback ({key})",
                              "have the caller call {name} first and pass {function} the answer as a value"),),
                      keep=("annotated",), exempt=("receiver",), key=f"parts.{part}.no_callbacks", part=part)
                 for part in profile.no_callbacks)


def no_comments(profile: Profile) -> tuple[Rule, ...]:
    """No line comment, in the app or its tests, but those the language's tools read: its directives, a shebang on
    line 1, an encoding declaration on line 1 or 2."""
    if not profile.no_comments:
        return ()
    return (Rule("no-comments", Scope(ALL), ("comment",), MAY_NOT, EXISTING,
                 (Saying("a comment (no-comments)", "say it in a docstring or a name, and delete the comment"),),
                 exempt=("read-by-a-tool",)),)


def closed_tree(profile: Profile) -> tuple[Rule, ...]:
    """Every source file of the app lies in a part, or is a package file of a folder of the layout."""
    if not profile.closed_tree:
        return ()
    return (Rule("closed-tree", Scope(APP, where=("ungoverned",)), ("file",), MAY_NOT, EXISTING,
                 (Saying("lies in no part and no folder of the layout (closed-tree)",
                         "move {file} into the part that fits it (run xarch where {file}), or add its folder to the "
                         "layout"),)),)


def holds(profile: Profile) -> tuple[Rule, ...]:
    """A file of a part that lists `holds` defines at the top level what the part holds, listed without failing:
    no public function in a part of classes; no class in a part of functions but an exception or a record. A package
    file only gathers what its package holds and is not read."""
    found = []
    for part, kind in profile.holds.items():
        key = f"parts.{part}.holds"
        if kind == "classes":
            found.append(Rule("holds", Scope(APP, part, where=("not-a-package",)), ("function",), MAY_NOT, EXISTING,
                              (Saying("{name} is a function at the top level, but {part} holds classes ({key})",
                                      "make {name} a method of the class whose rule it is, or move it to "
                                      "{function_parts}"),),
                              keep=("top-level", "public"), mode=LIST, key=key, part=part))
        else:
            found.append(Rule("holds", Scope(APP, part, where=("not-a-package",)), ("class",), MAY_NOT, EXISTING,
                              (Saying("{name} is a class, but {part} holds functions ({key})",
                                      "move {name} to {class_parts}, or make what it does functions"),),
                              exempt=("exception", "record"), mode=LIST, key=key, part=part))
    return tuple(found)


def must_import(profile: Profile) -> tuple[Rule, ...]:
    """Each file of a part that lists `must_import` imports one of the targets or an outside package, itself or
    through the files of its own part and instance it imports, however far; a package file and a file with no real
    statement are not said."""
    return tuple(Rule("must-import", Scope(APP, part), ("import", "edge"), MUST_REACH,
                      Targets("places-or-outside", places=wanted),
                      (Saying("{part} imports nothing from {reach_targets} and no outside package, so it touches no "
                              "technology ({key})",
                              "import what it wraps from {reach_targets}, or an outside package, or move its code to "
                              "a part that needs no technology"),),
                      exempt=("a-package-file", "no-code"), key=f"parts.{part}.must_import", part=part, links=("edge",),
                      via="own-part-instance")
                 for part, wanted in profile.must_import.items())


def must_import_tiers(profile: Profile) -> tuple[Rule, ...]:
    """Each test file of a tier that lists `must_import` reaches one of the parts, in any instance, by an import into
    the app or through test code it imports that is no test file, however far; one with no real statement is not
    said."""
    return tuple(Rule("must-import", Scope(TESTS, tier=tier.name, where=("a-test",)), ("edge",), MUST_REACH,
                      Targets("parts", words=tier.must_import),
                      (Saying("{a_tier} test imports nothing from {wanted_parts}, directly or through test code it "
                              "imports ({key})",
                              "drive what it proves through {wanted_parts}, or move it to the tier of the part it "
                              "calls directly"),),
                      keep=("placed",), exempt=("no-code",), key=f"tiers.{tier.name}.must_import",
                      links=("suite_edge",), via="to-a-helper")
                 for tier in profile.tiers if tier.must_import)


def dead_code(profile: Profile) -> tuple[Rule, ...]:
    """A port that no other file of the app names, by any name it reads, but a package file and the wiring; and a
    fake that no test outside the fakes' folder names, nor a fake named so, however far."""
    if not profile.dead_code or profile.fakes is None:
        return ()
    ports = [Rule("dead-code", Scope(APP, part), ("class",), MUST_BE_REACHED, EXISTING,
                  (Saying("{name} is a port that nothing else in the app names (dead-code)",
                          "delete {name} and its fake, or add the code that uses it"),),
                  keep=("port",), links=("names",),
                  roots=Scope(APP, where=("not-a-package-file", "not-wiring", "another-file")))
             for part in profile.fakes.stand_in_for]
    fakes = Rule("dead-code", Scope(TESTS, where=("in-the-fakes",)), ("class",), MUST_BE_REACHED, EXISTING,
                 (Saying("{name} is a fake that no test names (dead-code)",
                         "delete {name}, or write the test that uses it"),),
                 keep=("a-fake-name",), links=("names",), roots=Scope(TESTS, where=("not-in-the-fakes",)),
                 spread=("class",))
    return (*ports, fakes)


def untested(profile: Profile) -> tuple[Rule, ...]:
    """A file of a part a tier tests that no test code of that tier reaches, by an import, or through files of parts
    of that same tier, however far; listed. A package file, a file with no real statement and a file of exceptions
    only are not."""
    if not profile.dead_code or not profile.untested:
        return ()
    return (Rule("dead-code", Scope(APP, where=("tested-by-a-tier",)), ("file",), MUST_BE_REACHED, EXISTING,
                 (Saying("a file of {part} that no {tested_by} test reaches (guards.dead-code.untested)",
                         "write its {tested_by} test in {tests_folder}/, or delete what nothing uses"),),
                 exempt=("a-package", "exceptions-only", "no-code"), mode=LIST, links=("edge",), via="into-its-tier",
                 roots=Scope(TESTS, where=("tiered",)), spread=("edge",)),)


def book(profile: Profile) -> dict[str, tuple[Rule, ...]]:
    """Every check the engine runs, by the name of its group, each the rules its keys expand to."""
    return {"syntax": syntax(profile), "rules": rules(profile), "libraries": libraries(profile),
            "forbidden": forbidden(profile), "tiers": tiers(profile), "types-only tiers": types_only_tiers(profile),
            "package-only": package_only(profile), "types-only parts": types_only_parts(profile),
            "no-callbacks": no_callbacks(profile), "names": names(profile), "built-by": built_by(profile),
            "private-imports": private_imports(profile), "no-comments": no_comments(profile),
            "closed-tree": closed_tree(profile), "holds": holds(profile), "must-import": must_import(profile),
            "must-import tiers": must_import_tiers(profile), "dead-code": dead_code(profile),
            "untested": untested(profile)}
