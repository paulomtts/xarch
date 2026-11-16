"""What the keys of a profile mean as rules as data: each check's keys expand to the rules the engine runs, in the
order the check reads them, each saying what the check has always said. The keys of the profile stay as they are;
this is what they mean, in the words a profile writes its own checks in (`xarch profile explain <key> --rule` prints
them so).
"""
from __future__ import annotations

from xarch.kernel.placement import EVERYTHING
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
    Condition,
    Match,
    Rule,
    Saying,
    Scope,
)
from xarch.modules.rules.domain.values import Profile

FORBIDDEN_FIX = "do what needs {hit} outside {scope_part}/, and hand {scope_part}/ the result"
_of = Condition.of


def _all(*texts: str) -> tuple[Condition, ...]:
    return tuple(_of(text) for text in texts)


def libraries(profile: Profile) -> tuple[Rule, ...]:
    """A part imports only the outside packages its `libraries` list; the standard library and the app's own package
    are always allowed, and a relative import is the app's own, but a module of the standard library the profile
    reserves is an outside package; one finding per package and line. No rule when no part lists libraries, and none
    for a part whose list is everything."""
    if profile.libraries is None:
        return ()
    reserved = ("{where} may not import {package}, which the profile reserves: {reserved_reason} (reserved.{package}; "
                "{key})")
    outside = "{where} may not import the outside package {package} ({key})"
    owners = "move the code that needs {package} to {library_owners}, which may import it (parts.{first_library_owner}" \
             ".libraries)"
    once = ("line", "package")
    sayings = (Saying(reserved, owners, _all("reserved", "listed-by-another-part"), once),
               Saying(reserved, "list {package} in the libraries of the part it is reserved for, and keep the code "
                                "that needs it there", _all("reserved"), once),
               Saying(outside, owners, _all("listed-by-another-part"), once),
               Saying(outside, "use the standard library or a package listed in {key}, since {package} is listed for "
                               "no part", once=once))
    return tuple(Rule("libraries", Scope(APP, part), ("import",), MAY_ONLY, (Match("package", words=allowed),),
                      sayings, keep=keep, exempt=exempt, key=f"parts.{part}.libraries")
                 for part in profile.parts if EVERYTHING not in (allowed := profile.libraries.get(part, ()))
                 for keep, exempt in ((_all("not relative", "not reserved"), _all("app-package", "standard")),
                                      (_all("not relative", "reserved"), _all("app-package"))))


def forbidden(profile: Profile) -> tuple[Rule, ...]:
    """A file of a part with a `forbidden` list neither imports what it names, nor uses a name it lists, nor calls a
    method it lists on anything but what its object holds; a test of a tier that applies the lists is held to the
    list of each part it mirrors. One finding per line and name."""
    if not profile.forbidden:
        return ()
    facts = ("imported-name", "use", "method-call")
    keep, exempt = _all("not relative", "not on-own-object"), _all("reported-at-import")
    fakes = (_of(f"not below {'/'.join(profile.fakes.folder)}"),) if profile.fakes is not None else ()
    found = [Rule("forbidden", Scope(APP, part), facts, MAY_NOT, (Match("path", names=names),),
                  (Saying("{where} may not {verb} {hit} ({key})", FORBIDDEN_FIX, once=("line", "hit")),),
                  keep=keep, exempt=exempt, key=f"parts.{part}.forbidden")
             for part, names in profile.forbidden.items()]
    found += [Rule("forbidden", Scope(TESTS, part, tier.name, fakes), facts, MAY_NOT, (Match("path", names=names),),
                   (Saying("a test of {scope_part}/ ({tier} tier) may not {verb} {hit} ({key})", FORBIDDEN_FIX,
                           once=("line", "hit")),),
                   keep=keep, exempt=exempt, key=f"parts.{part}.forbidden; tiers.{tier.name}.apply_forbidden")
              for tier in profile.tiers if tier.forbidden for part, names in profile.forbidden.items()]
    return tuple(found)


def package_only(profile: Profile) -> tuple[Rule, ...]:
    """A part the guard names is imported as a package, never by one of its files, from anywhere outside its own
    folder (its own instance, for a part in a repeating folder), the tests included."""
    if not profile.package_only:
        return ()
    return (Rule("package-only", Scope(ALL), ("import-into-app",), MAY_NOT,
                 (Match("part", words=profile.package_only),),
                 (Saying("{target_part} is imported only as a package, never by its files ({target}) (package-only)",
                         "import from {target_package}"),),
                 keep=_all("target-placed", "target-inside-part"), exempt=_all("target-in-own-part"),
                 key="parts.<part>.package_only"),)


def private_imports(profile: Profile) -> tuple[Rule, ...]:
    """No file of the app or the tests imports a name private in the language from the app's or the tests' own
    package, or relatively; one finding per name."""
    if not profile.private_imports:
        return ()
    return (Rule("private-imports", Scope(ALL), ("imported-name",), MAY_NOT, EXISTING,
                 (Saying("imports the private name {name} from {written} (private-imports)",
                         "make {name} public where it is defined (drop the `_`), or move it to a file both may import"),),
                 keep=_all("takes-a-name", "own-code", "not public", "not special"), key="guards.private-imports"),)


def built_by(profile: Profile) -> tuple[Rule, ...]:
    """Only the parts a part lists in `built_by` build a class it defines at the top level of a file; the tests are
    not read."""
    if not profile.built_by:
        return ()
    return (Rule("built-by", Scope(APP), ("construction",), MAY_NOT, (Match("part", words=tuple(profile.built_by)),),
                 (Saying("{where} builds {name}, a class of {target_part}, which only {built_by} may build "
                         "(parts.{target_part_name}.built_by)",
                         "take {name} as a parameter of the constructor, and build it in {built_by}"),),
                 exempt=_all("target-allows-under built_by"), key="parts.<part>.built_by"),)


def rules(profile: Profile) -> tuple[Rule, ...]:
    """Every import between places the profile governs is allowed by the rules of the importing file's part: a part
    may import itself and its `may_import` row, where a target with a name pattern allows only the names it matches;
    the structure may import nothing the profile governs."""
    narrowed = Saying("{where} may import only {allowed_names} from {target_part}, {disallowed_name} ({target_name})",
                      "import from {target_part} only names that match {allowed_names} ({key}), or move what "
                      "needs the rest to a part that may import it", _all("names-restricted"))
    plain = "{where} may not import {target_part} ({target})"
    found = [Rule("rules", Scope(APP, part), ("import-into-app",), MAY_ONLY, (Match("permitted"),),
                  (narrowed, Saying(plain, "import only {importable_parts} in {where} ({key}), or {move_fix}")),
                  keep=_all("target-placed"), key=f"parts.{part}.may_import") for part in profile.parts]
    return (*found, Rule("rules", Scope(APP, STRUCTURE), ("import-into-app",), MAY_ONLY, (Match("permitted"),),
                         (Saying(plain, "drop the import of {target_part}, or {move_fix}"),), keep=_all("target-placed")))


def types_only_tiers(profile: Profile) -> tuple[Rule, ...]:
    """A test of a tier that names parts in `types_only` never calls what it imports from them, and never references
    one of their functions; a call is not said again as a reference."""
    return tuple(_types_only(Scope(TESTS, tier=tier.name), f"a {tier.name} test", f"tiers.{tier.name}.types_only",
                             tier.types_only, "{tier_type_only_fix}")
                 for tier in profile.tiers if tier.types_only)


def types_only_parts(profile: Profile) -> tuple[Rule, ...]:
    """A file of a part that names parts in its own `types_only` is held to the same rule."""
    return tuple(_types_only(Scope(APP, part), "{where}", f"parts.{part}.types_only", parts, "{type_only_fix}")
                 for part, parts in profile.types_only.items())


def _types_only(scope: Scope, who: str, key: str, parts: tuple[str, ...], fix: str) -> Rule:
    said = f"{who} uses {{target_part}} only as a type: it may not "
    return Rule("types-only", scope, ("call", "function-reference"), MAY_NOT, (Match("part", words=parts),),
                (Saying(said + "call {path} ({key})", fix, _all("of-kind call")),
                 Saying(said + "reference {target}, a function ({key})", fix)),
                keep=_all("target-placed"), key=key)


def tiers(profile: Profile) -> tuple[Rule, ...]:
    """A test file lies in a tier; a file of a tier imports, of the app, what the part its folder mirrors may (or its
    tier's subject, for one placed by its tier's folder); and of the test code, the fakes only when its tier tests a
    part they stand in for, never another test file (once per line), and anything else only from its own folder."""
    if not profile.tiers:
        return ()
    folder = "/".join(profile.fakes.folder) if profile.fakes is not None else ""
    not_fake = (_of(f"not below {folder}"),) if folder else ()
    mirrored = Saying("a test of {mirrored_parts} ({tier} tier) may not import {target_part} ({target}): it imports "
                      "only what {mirrored_parts} may ({mirrored_may_import})",
                      "import here only what {mirrored_parts} may; test {target_part} from the folder that mirrors it",
                      _all("mirrors-a-part"))
    by_folder = Saying("a {tier} test may not import {target_part} ({target})",
                       "import here only what the subject of the {tier} tier may; test {target_part} from the folder "
                       "that mirrors it")
    fakes = (Saying("a {tier} test may not import the fakes ({target}): only a tier that tests {faked_parts} may",
                    "drop the import of {target}, or move the test to a tier that tests {faked_parts}",
                    _all(f"target-below {folder}")),) if folder else ()
    test = Saying("a test may not import another test file ({target}): what tests share lives in test code that is no "
                  "test file",
                  "move what {target} holds that this test needs into test code of its folder that is no test file, "
                  "and import it from there", _all("target-test"), ("line", "target"))
    elsewhere = Saying("a test may import test code only from its own folder {own_folder}/ ({target})",
                       "move what {target} holds into {own_folder}/, or drop the import")
    return (Rule("tiers", Scope(TESTS, where=(_of("not tiered"), _of("test"), *not_fake)), ("file",), MAY_NOT,
                 EXISTING, (Saying(NO_TIER, NO_TIER_FIX),), key="tiers"),
            Rule("tiers", Scope(TESTS, where=_all("tiered")), ("import-into-app",), MAY_ONLY, (Match("permitted"),),
                 (mirrored, by_folder), keep=_all("target-placed"), key="tiers"),
            Rule("tiers", Scope(TESTS, where=_all("tiered")), ("import-into-tests",), MAY_ONLY, (Match("permitted"),),
                 (*fakes, test, elsewhere), key="tiers"))


def syntax(profile: Profile) -> tuple[Rule, ...]:
    """A file that does not parse is a violation, at the line its error is on, and no other rule reads it."""
    return (Rule("syntax", Scope(ALL), ("syntax-error",), MAY_NOT, EXISTING,
                 (Saying("not valid {language}: {text}", "correct the syntax so that the file can be read"),)),)


def names(profile: Profile) -> tuple[Rule, ...]:
    """Every public class of a part that lists `names` matches one of its patterns, `*` standing for any text."""
    return tuple(Rule("names", Scope(APP, part), ("class",), MAY_ONLY, (Match("name", words=patterns),),
                      (Saying("{name} does not match {targets}, as every class of {where} must ({key})",
                              "rename {name} to match {targets}, or move it to the part whose kind of class it is"),),
                      keep=_all("public"), key=f"parts.{part}.names")
                 for part, patterns in profile.names.items())


def no_callbacks(profile: Profile) -> tuple[Rule, ...]:
    """Code of a part that lists `no_callbacks` calls none of its own parameters annotated as callables; the first
    parameter of a method, the object it is called on, is no callback."""
    return tuple(Rule("no-callbacks", Scope(APP, part), ("callback",), MAY_NOT, EXISTING,
                      (Saying("{function} calls its parameter {name}: {where} takes no callback ({key})",
                              "have the caller call {name} first and pass {function} the answer as a value"),),
                      keep=_all("annotated-callable"), exempt=_all("receiver"), key=f"parts.{part}.no_callbacks")
                 for part in profile.no_callbacks)


def no_comments(profile: Profile) -> tuple[Rule, ...]:
    """No line comment, in the app or its tests, but those the language's tools read: its directives, a shebang on
    line 1, an encoding declaration on line 1 or 2."""
    if not profile.no_comments:
        return ()
    return (Rule("no-comments", Scope(ALL), ("comment",), MAY_NOT, EXISTING,
                 (Saying("a comment (no-comments)", "say it in a docstring or a name, and delete the comment"),),
                 exempt=_all("directive"), key="guards.no-comments"),)


def closed_tree(profile: Profile) -> tuple[Rule, ...]:
    """Every source file of the app lies in a part, or is a package file of a folder of the layout."""
    if not profile.closed_tree:
        return ()
    return (Rule("closed-tree", Scope(APP, where=_all("not placed")), ("file",), MAY_NOT, EXISTING,
                 (Saying("lies in no part and no folder of the layout (closed-tree)",
                         "move {file} into the part that fits it (run xarch where {file}), or add its folder to the "
                         "layout"),), key="guards.closed-tree"),)


def holds(profile: Profile) -> tuple[Rule, ...]:
    """A file of a part that lists `holds` defines at the top level what the part holds, listed without failing:
    no public function in a part of classes; no class in a part of functions but an exception or a record. A package
    file only gathers what its package holds and is not read."""
    found = []
    for part, kind in profile.holds.items():
        key = f"parts.{part}.holds"
        if kind == "classes":
            found.append(Rule("holds", Scope(APP, part, where=_all("not package-file")), ("function",), MAY_NOT,
                              EXISTING,
                              (Saying("{name} is a function at the top level, but {where} holds classes ({key})",
                                      "make {name} a method of the class whose rule it is, or move it to "
                                      "{parts_holding_functions}"),),
                              keep=_all("top-level", "public"), mode=LIST, key=key))
        else:
            found.append(Rule("holds", Scope(APP, part, where=_all("not package-file")), ("class",), MAY_NOT, EXISTING,
                              (Saying("{name} is a class, but {where} holds functions ({key})",
                                      "move {name} to {parts_holding_classes}, or make what it does functions"),),
                              exempt=_all("exception", "record"), mode=LIST, key=key))
    return tuple(found)


def immutable(profile: Profile) -> tuple[Rule, ...]:
    """Every class a file of a part that lists `immutable` defines at the top level is an immutable record, as the
    language's data file says one is made, but an exception; listed without failing. A package file only gathers what
    its package holds and is not read."""
    return tuple(Rule("holds", Scope(APP, part, where=_all("not package-file")), ("class",), MAY_NOT, EXISTING,
                      (Saying("{name} is a class that is no immutable record, but every class of {where} is one ({key})",
                              "make {name} an immutable record (the {language} data file's `immutable` says how), or "
                              "move it to {parts_holding_classes}"),),
                      exempt=_all("exception", "immutable"), mode=LIST, key=f"parts.{part}.immutable")
                 for part in profile.immutable)


def must_import(profile: Profile) -> tuple[Rule, ...]:
    """Each file of a part that lists `must_import` imports one of the targets or an outside package, itself or
    through the files of its own part and instance it imports, however far; a package file and a file with no real
    statement are not said."""
    return tuple(Rule("must-import", Scope(APP, part), ("import", "import-into-app"), MUST_REACH,
                      (Match("place", places=wanted), Match("outside")),
                      (Saying("{where} imports nothing from {targets} and no outside package, so it touches no "
                              "technology ({key})",
                              "import what it wraps from {targets}, or an outside package, or move its code to a part "
                              "that needs no technology"),),
                      exempt=_all("package-file", "no-statements"), key=f"parts.{part}.must_import",
                      links=("import-into-app",), via=_all("target-in-own-part"))
                 for part, wanted in profile.must_import.items())


def must_import_tiers(profile: Profile) -> tuple[Rule, ...]:
    """Each test file of a tier that lists `must_import` reaches one of the parts, in any instance, by an import into
    the app or through test code it imports that is no test file, however far; one with no real statement is not
    said."""
    return tuple(Rule("must-import", Scope(TESTS, tier=tier.name, where=_all("test")), ("import-into-app",),
                      MUST_REACH, (Match("part", words=tier.must_import),),
                      (Saying("a test of the {tier} tier imports nothing from {targets}, directly or through test code it imports "
                              "({key})",
                              "drive what it proves through {targets}, or move it to the tier of the part it calls "
                              "directly"),),
                      keep=_all("target-placed"), exempt=_all("no-statements"), key=f"tiers.{tier.name}.must_import",
                      links=("import-into-tests",), via=_all("not target-test"))
                 for tier in profile.tiers if tier.must_import)


def dead_code(profile: Profile) -> tuple[Rule, ...]:
    """A port that no other file of the app names, by any name it reads, but a package file and a part that may
    import everything; and a fake that no test outside the fakes' folder names, nor a fake named so, however far."""
    if not profile.dead_code or profile.fakes is None:
        return ()
    folder, prefix = "/".join(profile.fakes.folder), profile.fakes.prefix
    ports = [Rule("dead-code", Scope(APP, part), ("class",), MUST_BE_REACHED, EXISTING,
                  (Saying("{name} is a port that nothing else in the app names (dead-code)",
                          "delete {name} and its fake, or add the code that uses it"),),
                  keep=_all("interface"), links=("names-mentioned",),
                  roots=Scope(APP, where=_all("not package-file", "not may-import-everything")), elsewhere=True,
                  key="guards.dead-code")
             for part in profile.fakes.stand_in_for]
    fakes = Rule("dead-code", Scope(TESTS, where=_all(f"below {folder}")), ("class",), MUST_BE_REACHED, EXISTING,
                 (Saying("{name} is a fake that no test names (dead-code)",
                         "delete {name}, or write the test that uses it"),),
                 keep=_all(f"named {prefix}*"), exempt=_all(f"named {prefix}") if prefix else (), links=("names-mentioned",),
                 roots=Scope(TESTS, where=_all(f"not below {folder}")), spread=("class",), key="guards.dead-code")
    return (*ports, fakes)


def untested(profile: Profile) -> tuple[Rule, ...]:
    """A file of a part a tier tests that no test code of that tier reaches, by an import, or through files of parts
    of that same tier, however far; listed. A package file, a file with no real statement and a file of exceptions
    only are not."""
    if not profile.dead_code or not profile.untested:
        return ()
    return (Rule("dead-code", Scope(APP, where=_all("tiered")), ("file",), MUST_BE_REACHED, EXISTING,
                 (Saying("a file of {where} that no {tier} test reaches (guards.dead-code.untested)",
                         "write its {tier} test in {tests_folder}/, or delete what nothing uses"),),
                 exempt=_all("package-file", "exceptions-only", "no-statements"), mode=LIST, links=("import-into-app",),
                 via=_all("target-in-own-tier"), roots=Scope(TESTS, where=_all("tiered")),
                 spread=("import-into-app",), key="guards.dead-code.untested"),)


def pass_through(profile: Profile) -> tuple[Rule, ...]:
    """A method of a listed part that only forwards to one call, listed without failing."""
    keep = "it stays listed and fails only `check --strict`"
    return tuple(Rule("pass-through", Scope(APP, part), ("function",), MAY_NOT, EXISTING,
                      (Saying("{qualified_name} only passes its arguments on to {forwarded} and returns its .{returned}",
                              f"have the caller use {{forwarded}}(...).{{returned}}, or keep it as a deliberate plain "
                              f"forward: {keep}", _all("returns-an-attribute")),
                       Saying("{qualified_name} only passes its arguments on to {forwarded}",
                              f"have the caller use {{forwarded}}, or keep it as a deliberate plain forward: {keep}")),
                      keep=_all("forwards"), mode=LIST, key="guards.pass-through.parts")
                 for part in profile.pass_through)


def book(profile: Profile) -> dict[str, tuple[Rule, ...]]:
    """Every check the engine runs, by the name of its group, each the rules its keys expand to."""
    return {"syntax": syntax(profile), "rules": rules(profile), "libraries": libraries(profile),
            "forbidden": forbidden(profile), "tiers": tiers(profile), "types-only tiers": types_only_tiers(profile),
            "package-only": package_only(profile), "types-only parts": types_only_parts(profile),
            "no-callbacks": no_callbacks(profile), "names": names(profile), "built-by": built_by(profile),
            "private-imports": private_imports(profile), "no-comments": no_comments(profile),
            "closed-tree": closed_tree(profile), "holds": (*holds(profile), *immutable(profile)),
            "must-import": must_import(profile),
            "must-import tiers": must_import_tiers(profile), "dead-code": dead_code(profile),
            "untested": untested(profile), "pass-through": pass_through(profile)}
