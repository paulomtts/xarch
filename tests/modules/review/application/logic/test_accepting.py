"""The doubtful files a person accepted: the hash of a file's code, blind to blank lines and whitespace at the end of a
line; the part a file reads as; a doubtful file accepted while its code is as it was, accepted before once it changed;
and the files of the record that are stale."""
import hashlib

import pytest

from xarch.modules.review.application.logic.accepting import accepted, digest, reads_as, stale
from xarch.modules.review.domain.published import (
    A_TEST,
    GONE,
    HOLDS,
    MISSING,
    MOVED,
    SETTLED,
    UNJUDGED,
    UNPLACED,
    Acceptance,
    LeftOut,
    Reading,
    RuledOut,
    StaleAcceptance,
)
from xarch.modules.review.domain.values import AcceptedFile, CodeFile

CODE = 'def check(doc):\n    """Refuses a document without a title."""\n    return bool(doc.title)\n'


@pytest.mark.parametrize("edited", [
    pytest.param(CODE.replace("\n    return", "\n\n    return"), id="a blank line added"),
    pytest.param(CODE.replace("(doc):\n", "(doc):   \n"), id="whitespace at the end of a line"),
    pytest.param(CODE.replace("(doc):\n", "(doc):\n    \n"), id="a line of whitespace alone"),
    pytest.param(CODE + "\n\n", id="blank lines at the end"),
])
def test_an_edit_that_leaves_the_code_as_it_was_but_for_blank_lines_and_trailing_whitespace_keeps_the_hash(edited):
    assert digest(edited) == digest(CODE)


@pytest.mark.parametrize("edited", [
    pytest.param(CODE.replace("title)", "name)"), id="the code"),
    pytest.param(CODE.replace("without a title", "with no title"), id="a docstring, which is code here"),
    pytest.param(CODE.replace("    return", "  return"), id="the indentation of a line"),
])
def test_any_other_edit_changes_the_hash(edited):
    assert digest(edited) != digest(CODE)


def test_the_hash_is_the_sha256_of_the_lines_kept_joined_with_line_feeds():
    assert digest("a  \n\nb\n") == hashlib.sha256(b"a\nb").hexdigest()


def at(probability: float, doubtful: bool = True, part: str = "logic", **fields) -> Reading:
    return Reading("app/x.py", part, 1200, probability, 0.3, doubtful,
                   (("logic", probability), ("domain", 0.5), ("kernel-logic", 0.3), ("profile-values", 0.6)), "m",
                   **fields)


@pytest.mark.parametrize("reading, part", [
    pytest.param(at(0.1), "profile-values", id="the part its answer puts most on"),
    pytest.param(at(0.1, ruled_out=(RuledOut("profile-values", HOLDS, 0.6),)), "domain",
                 id="a part ruled out is not one it reads as"),
    pytest.param(at(0.1, alike=("profile-values",)), "domain", id="nor a part of its own part's group"),
    pytest.param(Reading("app/x.py", "logic", 1200, 1.0, 0.3, False, (("logic", 1.0),), "m"), "",
                 id="none when no other part is left"),
])
def test_a_file_reads_as_the_part_outside_its_group_its_answer_puts_most_on_once_parts_are_ruled_out(reading, part):
    assert reads_as(reading) == part


ENTRY = AcceptedFile("logic", "profile-values", digest(CODE), "it decides one rule over the document")


@pytest.mark.parametrize("reading, code, then", [
    pytest.param(at(0.1), digest(CODE),
                 at(0.1, False, accepted=Acceptance("it decides one rule over the document", "profile-values")),
                 id="a doubtful file whose code is as it was is accepted and no longer doubtful"),
    pytest.param(at(0.1), digest(CODE + "x = 1\n"),
                 at(0.1, accepted_before=Acceptance("it decides one rule over the document", "profile-values")),
                 id="a doubtful file whose code changed is doubtful, accepted before"),
    pytest.param(at(0.1, part="domain"), digest(CODE), at(0.1, part="domain"),
                 id="a file accepted in another part is read as if it were not"),
    pytest.param(at(0.6, False), digest(CODE), at(0.6, False), id="a file not doubtful is read as it is"),
])
def test_a_doubtful_file_the_record_names_is_accepted_while_its_code_is_as_it_was(reading, code, then):
    assert accepted((reading,), {"app/x.py": code}, {"app/x.py": ENTRY}) == (then,)


FILE = CodeFile("app/x.py", "logic", CODE)


@pytest.mark.parametrize("judged, left_out, readings, every, then", [
    pytest.param((), (LeftOut("app/x.py", MISSING),), (), False, (StaleAcceptance("app/x.py", "logic", GONE),),
                 id="a file named that is not there is gone"),
    pytest.param((), (), (), True, (StaleAcceptance("app/x.py", "logic", GONE),),
                 id="with every file, a file not found is gone"),
    pytest.param((), (), (), False, (), id="else a file not found is not judged stale"),
    pytest.param((CodeFile("app/x.py", "domain", CODE),), (), (), False,
                 (StaleAcceptance("app/x.py", "logic", MOVED, "domain"),), id="a file in another part has moved"),
    pytest.param((), (LeftOut("app/x.py", UNPLACED),), (), False, (StaleAcceptance("app/x.py", "logic", MOVED),),
                 id="a file in no part has moved to none"),
    pytest.param((), (LeftOut("app/x.py", A_TEST),), (), False,
                 (StaleAcceptance("app/x.py", "logic", UNJUDGED, A_TEST),), id="a file left out is not judged"),
    pytest.param((FILE,), (), (at(0.6, False),), False, (StaleAcceptance("app/x.py", "logic", SETTLED),),
                 id="a file no longer doubtful has nothing to accept"),
    pytest.param((FILE,), (), (at(0.1, False, accepted=Acceptance("w", "domain")),), False, (),
                 id="a file accepted is not stale"),
    pytest.param((FILE,), (), (at(0.1, accepted_before=Acceptance("w", "domain")),), False, (),
                 id="a file changed since it was accepted is doubtful, not stale"),
    pytest.param((FILE,), (), (), True, (), id="a file judged with no answer is not judged stale"),
])
def test_a_file_of_the_record_is_stale_when_it_is_gone_moved_no_longer_doubtful_or_not_judged(judged, left_out, readings,
                                                                                            every, then):
    assert stale({"app/x.py": ENTRY}, judged, left_out, readings, every) == then
