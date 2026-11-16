"""How a refusal is shown, on hand-made reasons and Results."""
import json

import pytest

from xarch.cli.reports.refusal_report import cannot_run, json_error, no_profile, reason, text_error
from xarch.modules.spec.contract import NoProfileChosen, ProfileRefused


@pytest.mark.parametrize("refused, expected", [
    pytest.param(NoProfileChosen(("cli", "web")), "no profile: pass --profile, or set `profile` under [tool.xarch] in "
                 "pyproject.toml; the profiles found are cli, web", id="no profile chosen says how to choose one"),
    pytest.param(ProfileRefused("unknown profile 'x'"), "unknown profile 'x'", id="a refusal says its own reason"),
])
def test_the_reason_spec_chose_no_profile(refused, expected):
    assert reason(refused) == expected


def test_a_profile_whose_checks_cannot_run_lists_each_problem_indented():
    assert cannot_run(["a", "b"]) == ("the checks the profile writes itself cannot run (`xarch profile check` says "
                                      "the same):\n  a\n  b")


def test_a_refusal_is_one_error_line_as_text_and_a_document_that_is_not_ok_as_json():
    assert (text_error("no app"), json.loads(json_error("no app"))) == ("error: no app", {"ok": False, "error": "no app"})


def test_no_profile_names_the_profiles_found():
    assert no_profile(["cli"]).endswith("the profiles found are cli")
