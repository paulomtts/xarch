"""The top-level `excluded` key: folders below the app that are not its source, each with the reason."""
import pytest

from tests.modules.spec.profiles_v2 import layered, parsed, problems
from xarch.profile_values.excluded import Excluded


def test_a_profile_without_excluded_folders_excludes_none():
    assert parsed(layered()).excluded == ()


def test_excluded_folders_load_with_their_reason_in_the_order_of_the_file():
    architecture = parsed(layered(excluded={"vendor/": "copied code", "docs/examples": "example sources"}))
    assert architecture.excluded == (Excluded(("vendor",), "copied code"),
                                     Excluded(("docs", "examples"), "example sources"))


@pytest.mark.parametrize("excluded, problem", [
    pytest.param([], "excluded: must be a mapping of folders below the app to the reason each is not its source, "
                     "such as {vendor: copied code}", id="a list instead of a mapping"),
    pytest.param("vendor", "excluded: must be a mapping of folders below the app to the reason each is not its "
                           "source, such as {vendor: copied code}", id="a string instead of a mapping"),
    pytest.param({"": "x"}, "excluded: '' is not a folder below the app, such as vendor/generated",
                 id="an empty path"),
    pytest.param({"/vendor": "x"}, "excluded: '/vendor' is not a folder below the app, such as vendor/generated",
                 id="a path that starts with a slash"),
    pytest.param({"a/../b": "x"}, "excluded: 'a/../b' is not a folder below the app, such as vendor/generated",
                 id="a path with .."),
    pytest.param({"a//b": "x"}, "excluded: 'a//b' is not a folder below the app, such as vendor/generated",
                 id="a path with an empty step"),
    pytest.param({"a/*": "x"}, "excluded: 'a/*' is not a folder below the app, such as vendor/generated",
                 id="a path with a wildcard"),
    pytest.param({3: "x"}, "excluded: 3 is not a folder below the app, such as vendor/generated",
                 id="a key that is no text"),
    pytest.param({"vendor": ""}, "excluded.vendor: must give the reason, one line of text",
                 id="an empty reason"),
    pytest.param({"vendor": "two\nlines"}, "excluded.vendor: must give the reason, one line of text",
                 id="a reason of two lines"),
    pytest.param({"vendor": None}, "excluded.vendor: must give the reason, one line of text",
                 id="a missing reason"),
    pytest.param({"src": "x"}, "excluded.src: 'src' is a folder of the layout: it is source, not excluded",
                 id="a folder of the layout"),
    pytest.param({"vendor": "x", "vendor/a": "y"}, "excluded.vendor/a: overlaps the excluded folder 'vendor': list only one of the two",
                 id="a folder inside an excluded one"),
    pytest.param({"vendor/a": "x", "vendor": "y"}, "excluded.vendor: overlaps the excluded folder 'vendor/a': list only one of the two",
                 id="a folder holding an excluded one"),
    pytest.param({"vendor": "x", "vendor/": "y"}, "excluded.vendor/: overlaps the excluded folder 'vendor': list only one of the two",
                 id="the same folder twice"),
])
def test_a_bad_excluded_entry_is_rejected(excluded, problem):
    assert problems(layered(excluded=excluded)) == [f"layered.yaml: {problem}"]
