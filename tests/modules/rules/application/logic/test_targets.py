"""Every kind of target, on the facts of a small project: one row per kind, each the facts of one kind of one file
that match it, by their lines, with the target each matched (its hit); a kind of target that does not apply to a fact
matches none of it; and a fact is a finding under may_not when it matches, under may_only when it does not."""
import pytest

from tests.modules.rules.application.logic.world import DOMAIN, FACTS, PROFILE, SERVICE, TEST, found
from xarch.modules.rules.application.logic import targets
from xarch.modules.rules.application.logic.targets import finding, matched
from xarch.modules.rules.domain.rule import MAY_NOT, MAY_ONLY, Match
from xarch.modules.rules.domain.vocabulary import TARGETS
from xarch.profile_values.placement import Target


@pytest.mark.parametrize("match, file, kind, hits", [
    pytest.param(Match("exist"), DOMAIN, "comment", [(13, ()), (14, ())], id="exist"),
    pytest.param(Match("path", names=(("yaml",),)), DOMAIN, "use", [(18, ("yaml",))], id="path"),
    pytest.param(Match("path", names=(("", "absolute()"),)), DOMAIN, "method-call", [(20, ("", "absolute()"))],
                 id="path: a method called on anything"),
    pytest.param(Match("package", words=("json",)), DOMAIN, "import", [(4, ("json",))], id="package"),
    pytest.param(Match("name", words=("Doc*",)), DOMAIN, "class", [(6, ("Doc*",)), (7, ("Doc*",))], id="name"),
    pytest.param(Match("text", words=("*TODO*",)), DOMAIN, "comment", [(14, ("*TODO*",))], id="text"),
    pytest.param(Match("part", words=("platform",)), SERVICE, "import-into-app", [(3, ("platform", "db"))], id="part"),
    pytest.param(Match("place", places=(Target("kernel"),)), DOMAIN, "import-into-app",
                 [(2, ("kernel", "ids")), (5, ("kernel", "ids")), (5, ("kernel", "ids"))], id="place"),
    pytest.param(Match("permitted"), SERVICE, "import-into-app",
                 [(1, ("modules", "docs", "domain", "doc")), (2, ("modules", "docs", "domain", "doc"))],
                 id="permitted: what a part may import"),
    pytest.param(Match("permitted"), TEST, "import-into-app", [(1, ("modules", "docs", "domain", "doc"))],
                 id="permitted: what the part a test mirrors may import"),
    pytest.param(Match("permitted"), TEST, "import-into-tests", [(2, ("modules", "docs", "builders"))],
                 id="permitted: test code of the test's own folder that is no test"),
    pytest.param(Match("outside"), DOMAIN, "import", [(1, ("yaml",))], id="outside"),
    pytest.param(Match("package", words=("json",)), DOMAIN, "comment", [], id="a kind of target that does not apply"),
])
def test_a_fact_matches_the_targets_it_says(match, file, kind, hits):
    assert [(f.fact.line, hit) for f in found(file, kind) if (hit := matched((match,), f, FACTS, PROFILE)) is not None
            ] == hits


@pytest.mark.parametrize("quantifier, hit, is_finding", [
    pytest.param(MAY_NOT, ("yaml",), True, id="under may_not a fact that matches is a finding"),
    pytest.param(MAY_NOT, None, False, id="under may_not a fact that matches nothing is none"),
    pytest.param(MAY_ONLY, None, True, id="under may_only a fact that matches nothing is a finding"),
    pytest.param(MAY_ONLY, ("yaml",), False, id="under may_only a fact that matches is none"),
])
def test_a_fact_is_a_finding_by_what_it_matched_under_the_quantifier(quantifier, hit, is_finding):
    assert finding(quantifier, hit) is is_finding


def test_every_kind_of_target_the_vocabulary_publishes_has_a_row_and_the_engine_matches_it():
    rows = {param.values[0].kind for param in test_a_fact_matches_the_targets_it_says.pytestmark[0].args[1]}
    assert rows == {kind.name for kind in TARGETS} == set(targets.NAMES)
