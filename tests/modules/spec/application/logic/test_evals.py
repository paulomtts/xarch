"""The top-level `evals` key: today the line of each part placement reads a file's answer against
(`evals.placement.lines`), by part as written, and every way of writing it wrong refused at its address."""
import pytest

from tests.modules.spec.profiles_v2 import layered, parsed, problems


def test_a_profile_without_evals_sets_no_line_by_hand():
    assert parsed(layered()).lines == {}


def test_the_line_of_each_part_written_loads_by_part_in_the_order_of_the_file():
    architecture = parsed(layered(evals={"placement": {"lines": {"store": 0.2, "api": 0.45, "shared": 1e-1}}}))
    assert list(architecture.lines.items()) == [("store", 0.2), ("api", 0.45), ("shared", 0.1)]


def test_evals_with_placement_and_placement_with_no_lines_set_no_line():
    assert parsed(layered(evals={})).lines == {}
    assert parsed(layered(evals={"placement": {}})).lines == {}


NOT_A_LINE = "is not a line: write a number above 0 and below 1, such as 0.2"


@pytest.mark.parametrize("evals, problem", [
    pytest.param(["placement"], "evals: must be a mapping of the evals review asks, by id, such as "
                                "{placement: {lines: {documents: 0.2}}}", id="a list instead of a mapping"),
    pytest.param({"placement": {}, "purity": {}}, "evals: unknown key 'purity': use placement",
                 id="an eval of the profile's own, which is not built yet"),
    pytest.param({"placement": "on"}, "evals.placement: must be a mapping {lines}: the line of each part, below which "
                                      "a file reads as doubtful there", id="placement not a mapping"),
    pytest.param({"placement": {"line": 0.2}}, "evals.placement: unknown key 'line': use lines", id="an unknown slot"),
    pytest.param({"placement": {"lines": [0.2]}}, "evals.placement.lines: must be a mapping of parts to their line, "
                                                  "such as {documents: 0.2}", id="lines not a mapping"),
    pytest.param({"placement": {"lines": {"domain": 0.2}}}, "evals.placement.lines: 'domain' is not a part of this "
                                                            "profile: name a part under parts", id="a name that is no part"),
    pytest.param({"placement": {"lines": {"store": "low"}}}, f"evals.placement.lines.store: 'low' {NOT_A_LINE}",
                 id="a line that is no number"),
    pytest.param({"placement": {"lines": {"store": True}}}, f"evals.placement.lines.store: True {NOT_A_LINE}",
                 id="a boolean is no number"),
    pytest.param({"placement": {"lines": {"store": 0}}}, f"evals.placement.lines.store: 0 {NOT_A_LINE}",
                 id="a line of 0 would doubt nothing"),
    pytest.param({"placement": {"lines": {"store": 1}}}, f"evals.placement.lines.store: 1 {NOT_A_LINE}",
                 id="a line of 1 would doubt everything"),
    pytest.param({"placement": {"lines": {"store": -0.2}}}, f"evals.placement.lines.store: -0.2 {NOT_A_LINE}",
                 id="a line below 0"),
])
def test_evals_written_wrong_is_refused_at_its_address(evals, problem):
    assert f"layered.yaml: {problem}" in problems(layered(evals=evals))
