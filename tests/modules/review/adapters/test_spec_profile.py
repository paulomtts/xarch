"""Review's Parts read from spec's contract: each part of the profile view, in order, with its folder, litmus and role;
a profile spec refuses raises Refused with spec's reason."""
import pytest

from xarch.modules.review.adapters.spec_profile import SpecParts
from xarch.modules.review.domain.errors import Refused
from xarch.modules.review.domain.values import PartText
from xarch.modules.spec.contract import PartView, ProfileRefused, ProfileResult, ProfileView

VIEW = ProfileView(parts=(PartView("core", ("core",), (), "the rules", "Is it a rule?", "core/"),
                          PartView("api", ("src", "*", "api"), (), "handlers", shown="api/ of src/<module>")))


class Spec:
    """Spec's controller as review's adapter uses it, answering from a fixed result."""

    def __init__(self, result: ProfileResult):
        self._result = result

    def profile(self, location: str) -> ProfileResult:
        return self._result


def test_each_part_is_read_with_its_folder_litmus_and_role_in_order():
    assert SpecParts(Spec(VIEW)).parts("p") == (PartText("core", "core/", "Is it a rule?", "the rules"),
                                               PartText("api", "api/ of src/<module>", "", "handlers"))


def test_a_profile_spec_refuses_is_refused_with_spec_s_reason():
    with pytest.raises(Refused, match="gone: no such file"):
        SpecParts(Spec(ProfileRefused("gone: no such file"))).parts("gone")
