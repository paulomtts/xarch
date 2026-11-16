"""Each filter about a fact and each kind of target reads only the fields of a fact the vocabulary says it reads: on
every fact of the small project, changing any other field leaves its answer as it was. What a check needs of the
language is worked out from the fields its words read, so a word that reads a field it does not declare runs on a
language that does not supply that field, neither refused nor listed as approximate."""

from tests.modules.rules.application.logic.world import BUILT, FACTS, LISTED, NARROWED, PROFILE, RESERVED
from xarch.kernel.placement import Place
from xarch.modules.rules.application.logic.filters import question
from xarch.modules.rules.application.logic.targets import matched
from xarch.modules.rules.domain.rule import Fact, Found, Match, Rule
from xarch.modules.rules.domain.vocabulary import FACT, FILTERS, TARGET, TARGETS, Kind
from xarch.modules.rules.domain.vocabulary import KINDS as VOCABULARY
from xarch.profile_values.checks import Condition, Saying, Scope
from xarch.profile_values.placement import Target

KINDS = {kind.name: kind for kind in VOCABULARY}

TRAITS = ("relative", "standard", "on-own-object", "top-level", "forwards", "exception", "record", "interface",
          "immutable", "receiver", "annotated-callable", "no-statements", "exceptions-only")
"""The fields a fact carries as a trait, by its name."""
STORED = {"line": "line", "path": "path", "method": "name", "name": "name", "written": "text", "text": "text",
          "forwarded": "text", "mentions": "names", "reaches": "target", "returned": "target", "place": "at",
          "bound": "bound", "function": "path", **{trait: trait for trait in TRAITS}}
"""Where a fact keeps each field of the vocabulary: an attribute of the fact, or a trait by its name."""
VALUES = {"named": "Doc*", "below": "fakes", "of-kind": "import", "target-below": "fakes",
          "target-allows-under": "built_by"}
MATCHES = {"exist": Match("exist"), "path": Match("path", names=(("yaml",), ("", "absolute()"))),
           "package": Match("package", words=("json",)), "name": Match("name", words=("Doc*",)),
           "text": Match("text", words=("*TODO*",)), "part": Match("part", words=("platform", "kernel")),
           "place": Match("place", places=(Target("kernel"),)), "permitted": Match("permitted"),
           "outside": Match("outside")}
PROFILES = (PROFILE, RESERVED, LISTED, NARROWED, BUILT)
RULE = Rule("mine", Scope(), ("import",), "may_not", (Match("exist"),), (Saying("m", "f"),))


def changed(fact: Fact, stored: str) -> Fact:
    """The fact with the field kept at stored changed."""
    if stored in TRAITS:
        return fact._replace(traits=fact.traits ^ {stored})
    flipped = {"line": fact.line + 1, "path": () if fact.path else ("zz",), "name": None if fact.name else "zz",
               "text": "" if fact.text else "zz", "names": frozenset() if fact.names else frozenset({"zz"}),
               "target": () if fact.target else ("zz",), "at": None if fact.at else Place("kernel"),
               "bound": 0 if fact.bound else 9}
    return fact._replace(**{stored: flipped[stored]})


def unread(kind: Kind, reads: tuple[str, ...]) -> list[str]:
    """The fields the kind carries, outside reads, that need of the language more than the fields of reads do."""
    declared = {STORED[name] for name in reads}
    needed = {need for name in reads for need in kind.field_needs.get(name, ())}
    return [name for name in STORED if kind.carries(name) and name not in reads and STORED[name] not in declared
            and not set(kind.field_needs.get(name, ())) <= needed]


def leaks(reads: tuple[str, ...], answer) -> list[str]:
    """Each fact of the project and field outside reads, needing more of the language, whose change changes the answer,
    as `<kind>:<line> <field>`."""
    found: list[str] = []
    for read in FACTS.files:
        for facts in read.facts.values():
            for fact in facts:
                hit = fact.path[:2] or None
                for name in unread(KINDS[fact.kind], reads):
                    if any(answer(Found(RULE, read, fact, hit), profile)
                           != answer(Found(RULE, read, changed(fact, STORED[name]), hit), profile)
                           for profile in PROFILES):
                        found.append(f"{fact.kind}:{fact.line} {name}")
    return sorted(set(found))


def filter_leaks() -> dict[str, list[str]]:
    found: dict[str, list[str]] = {}
    for word in FILTERS:
        if word.about not in (FACT, TARGET):
            continue
        condition = Condition(word.name, VALUES.get(word.name, ""))
        leaked = leaks(word.reads, lambda f, profile, c=condition: question(c)(f, FACTS, profile))
        if leaked:
            found[word.name] = leaked
    return found


def target_leaks() -> dict[str, list[str]]:
    found: dict[str, list[str]] = {}
    for word in TARGETS:
        match = MATCHES[word.name]
        leaked = leaks(word.reads, lambda f, profile, m=match: matched((m,), f, FACTS, profile) is None)
        if leaked:
            found[word.name] = leaked
    return found


def test_every_filter_about_a_fact_reads_only_the_fields_it_declares():
    assert filter_leaks() == {}


def test_every_kind_of_target_reads_only_the_fields_it_declares():
    assert target_leaks() == {}


def test_a_word_that_reads_a_field_it_does_not_declare_shows_and_one_it_declares_does_not():
    shown = leaks(("path",), lambda f, profile: "standard" in f.fact.traits)
    assert {leak.split(" ")[0].split(":")[0] for leak in shown} == {"import", "imported-name"}
    assert {leak.split(" ")[1] for leak in shown} == {"standard"}
    assert leaks(("standard",), lambda f, profile: "standard" in f.fact.traits) == []
