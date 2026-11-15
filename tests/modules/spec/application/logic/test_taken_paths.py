"""How a refusal to write over files names the ones that exist: three at most, then how many more."""
from pathlib import Path

import pytest

from xarch.modules.spec.application.logic.taken_paths import taken_phrase


@pytest.mark.parametrize("taken, phrase", [
    pytest.param([], "", id="nothing taken says nothing"),
    pytest.param([Path("out/a.yaml")], "out/a.yaml already exists", id="one file exists"),
    pytest.param([Path("a"), Path("b")], "a, b already exist", id="two files exist"),
    pytest.param([Path(n) for n in "abcde"], "a, b, c and 2 more already exist", id="past three the rest are counted"),
])
def test_taken_phrase(taken, phrase):
    assert taken_phrase(taken) == phrase
