"""Use case: accept doubtful files around fakes, read from the answers kept and never sent, each recorded with the part
it lies in, the part it reads as, the hash of its code and the reason given; or take files out of the record; every
file that cannot be accepted, or taken out, refused before anything is recorded."""
from dataclasses import dataclass, field
from pathlib import Path

import pytest

from tests.fakes.review import FakeAcceptances, FakeAnswers, FakeCode, FakeDecisionModel, FakeProfile
from tests.modules.review.application.helpers import controller
from tests.modules.review.builders import BODY, PARTS, code_hash, found
from xarch.modules.review.contract import (
    MISSING,
    SMALL,
    Accept,
    Accepted,
    FileAccepted,
    LeftOut,
    NoReason,
    NotAnswered,
    NotDoubtful,
    NothingChosen,
    NotJudged,
    NotRecorded,
    Reading,
    Removed,
    Review,
    ReviewRefused,
    TooManyFiles,
)
from xarch.modules.review.domain.values import AcceptedFile, Answer, Found, Words

CWD, APP = Path("/src"), Path("/src/app")
RECORD = Path("/src/.xarch/accepted.json")
DOCUMENT = found()
OTHER = found("app/modules/documents/domain/other.py", text=found().text + "    other: int = 0\n")
SMALL_FILE = found("app/modules/documents/domain/small.py", text="x = 1\n")
GONE = LeftOut("app/modules/documents/domain/gone.py", MISSING)
FOUND = {"app/x.py": Found((DOCUMENT,)), "app/two": Found((DOCUMENT, OTHER)), "app/other.py": Found((OTHER,)),
         "app/small.py": Found((SMALL_FILE,)), "app/gone.py": Found((), (GONE,)), "app/empty": Found(())}
SENT = "from <masked> import DocumentId\nfrom dataclasses import dataclass\n" + BODY
SENT_OTHER = SENT + "    other: int = 0\n"
LOW = Answer("m-1.0.1", (("domain", 0.1), ("main", 0.9)))
HIGH = Answer("m-1.0.0", (("domain", 0.8), ("main", 0.2)))
WHY = "the document's own values, read against the litmus of domain"
ENTRY = AcceptedFile("domain", "main", code_hash(SENT), WHY)
EARLIER = AcceptedFile("domain", "main", code_hash(SENT_OTHER), "an earlier reason")


@dataclass(frozen=True)
class World:
    """What the fakes hold: the answers kept in the cache, given by an earlier review of these texts; and the files
    accepted already, by the record."""
    kept: dict[str, Answer] = field(default_factory=lambda: {SENT: LOW, SENT_OTHER: HIGH})
    record: dict[str, AcceptedFile] = field(default_factory=dict)


def accept(*paths: str, why: str = WHY, remove: bool = False, profile: str = "p") -> Accept:
    return Accept(tuple(Path(p) for p in paths), CWD, APP, profile, why, remove)


def run(world: World, when: Accept):
    code = FakeCode(FOUND, refused={"/elsewhere": "/elsewhere lies outside the project"})
    profile = FakeProfile({"p": Words(PARTS)}, refused={"gone": "gone: no such file"})
    answers = FakeAnswers()
    for path in ("app/x.py", "app/other.py"):
        controller(code, profile, FakeDecisionModel(dict(world.kept)), answers).review(
            Review((Path(path),), (), False, CWD, APP, "p"))
    acceptances = FakeAcceptances({RECORD: dict(world.record)})
    model = FakeDecisionModel({})
    return controller(code, profile, model, answers, acceptances=acceptances).accept(when), acceptances, model


PLACED = Reading(OTHER.file, "domain", len(SENT_OTHER), 0.8, 0.3, False, HIGH.probabilities, "m-1.0.0", small=True)


@pytest.mark.parametrize("given, when, then", [
    pytest.param(World(), accept("app/x.py"), Accepted((FileAccepted(DOCUMENT.file, "domain", "main"),), WHY, RECORD),
                 id="a doubtful file whose answer is kept is accepted with the part it reads as"),
    pytest.param(World(record={DOCUMENT.file: ENTRY}), accept("app/x.py", remove=True), Removed((DOCUMENT.file,), RECORD),
                 id="a file the record names is taken out of it"),
    pytest.param(World(), accept("app/x.py", why="  "), NoReason(), id="a reason of whitespace alone is refused"),
    pytest.param(World(), accept("app/small.py"), NotJudged((LeftOut(SMALL_FILE.file, SMALL, 6),)),
                 id="a file review does not judge is refused with why"),
    pytest.param(World(kept={}), accept("app/x.py"), NotAnswered((DOCUMENT.file,)),
                 id="a file whose answer is not kept is refused, and nothing is sent"),
    pytest.param(World(), accept("app/two"), NotDoubtful((PLACED,)),
                 id="a file that does not read as doubtful is refused with how it reads"),
    pytest.param(World(), accept("app/x.py", remove=True), NotRecorded((DOCUMENT.file,)),
                 id="a file to take out that the record does not name is refused"),
    pytest.param(World(), accept(), NothingChosen(), id="no file named is refused"),
    pytest.param(World(), accept(*["app/two"] * 26), TooManyFiles(52, 50),
                 id="more files than one run judges is refused"),
    pytest.param(World(), accept("/elsewhere"), ReviewRefused("/elsewhere lies outside the project"),
                 id="a path outside the project is refused with why"),
])
def test_accept(given, when, then):
    assert run(given, when)[0] == then


def test_a_file_accepted_is_recorded_with_its_part_what_it_reads_as_the_hash_of_its_code_and_why_and_nothing_is_sent():
    result, acceptances, model = run(World(record={OTHER.file: EARLIER}), accept("app/x.py"))
    assert isinstance(result, Accepted)
    assert acceptances.kept[RECORD] == {DOCUMENT.file: ENTRY, OTHER.file: EARLIER}
    assert model.asked == []


def test_a_reason_is_recorded_without_the_whitespace_around_it():
    _, acceptances, _ = run(World(), accept("app/x.py", why=f"  {WHY}\n"))
    assert acceptances.kept[RECORD][DOCUMENT.file].why == WHY


def test_a_file_accepted_already_whose_code_is_as_it_was_is_accepted_again_for_the_new_reason():
    result, acceptances, _ = run(World(record={DOCUMENT.file: ENTRY}), accept("app/x.py", why="read again"))
    assert result == Accepted((FileAccepted(DOCUMENT.file, "domain", "main"),), "read again", RECORD)
    assert acceptances.kept[RECORD][DOCUMENT.file].why == "read again"


def test_a_file_that_is_no_longer_there_can_be_taken_out_of_the_record_and_the_others_stay():
    record = {GONE.file: ENTRY, OTHER.file: EARLIER}
    result, acceptances, _ = run(World(record=record), accept("app/gone.py", remove=True))
    assert result == Removed((GONE.file,), RECORD) and acceptances.kept[RECORD] == {OTHER.file: EARLIER}


@pytest.mark.parametrize("when", [
    pytest.param(accept("app/x.py", why=""), id="no reason"),
    pytest.param(accept("app/small.py"), id="a file not judged"),
    pytest.param(accept("app/x.py", remove=True), id="a file not recorded"),
    pytest.param(accept("app/empty"), id="a folder of no file"),
])
def test_nothing_is_recorded_when_anything_is_refused(when):
    result, acceptances, _ = run(World(record={OTHER.file: EARLIER}), when)
    assert not isinstance(result, Accepted | Removed)
    assert acceptances.kept[RECORD] == {OTHER.file: EARLIER}
