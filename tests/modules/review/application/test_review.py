"""Use case: review chosen files around fakes: with --dry-run, which sends nothing and says what would be sent; or a
reading of each file judged, from the answers kept and from the decision model, the most doubtful first."""
from dataclasses import dataclass, field, replace
from pathlib import Path

import pytest

from tests.fakes.review import FakeAcceptances, FakeAnswers, FakeCode, FakeDecisionModel, FakeProfile
from tests.modules.review.application.helpers import controller
from tests.modules.review.builders import BODY, OWN, PARTS, code_hash, found
from xarch.kernel.source import CommentSpan
from xarch.modules.review.contract import (
    BY_ALL,
    BY_PATHS,
    FAILED,
    HOLDS,
    IMPORTS,
    LARGE,
    MAX_CHARS,
    MISSING,
    NEVER,
    NO_CONTEXT,
    NOT_CACHED,
    REFUSED,
    SETTLED,
    SMALL,
    Acceptance,
    AllAndOthers,
    AllInPieces,
    Choice,
    KeyMissing,
    LeftOut,
    NothingChosen,
    Option,
    PartRead,
    PiecesRead,
    Reading,
    Request,
    Review,
    ReviewPlanned,
    ReviewReading,
    ReviewRefused,
    RuledOut,
    Sender,
    StaleAcceptance,
    TooManyFiles,
    Unasked,
)
from xarch.modules.review.contract import GONE as GONE_FILE
from xarch.modules.review.domain.values import AcceptedFile, Answer, CodeFile, Found, PartText, Span, Words

CWD, APP = Path("/src"), Path("/src/app")
FOLDER = Path("/src/.xarch/cache/review")
DOCUMENT = found()
OTHER = found("app/modules/documents/domain/other.py", text=found().text + "    other: int = 0\n")
SMALL_FILE = found("app/modules/documents/domain/small.py", text="x = 1\n")
GONE = LeftOut("app/modules/documents/domain/gone.py", MISSING)
FOUND = {"app/modules/documents/domain": Found((DOCUMENT, SMALL_FILE), (GONE,)), "app/x.py": Found((DOCUMENT,)),
         "app/two": Found((DOCUMENT, OTHER))}
PLACEMENT = ("Which part of this architecture does this code belong in? Each option is a part and the test that "
             "decides whether code belongs in it.")
QUESTION = Choice(PLACEMENT, (Option("domain", "Is it an invariant of one of this module's values?"),
                              Option("main", "starts the app")))
SENT = "from <masked> import DocumentId\nfrom dataclasses import dataclass\n" + BODY
SENT_OTHER = SENT + "    other: int = 0\n"
ASKED = len(PLACEMENT) + sum(len(o.name) + len(o.description) for o in QUESTION.options)
SENDS = Sender("Model", "https://model.example.test", "m-1", "MODEL_KEY", True)
UNKEYED = Sender("Model", "https://model.example.test", "m-1", "MODEL_KEY", False)
BODY_SENT = f"{PLACEMENT} 2 {SENT}"
REQUEST = Request(DOCUMENT.file, "domain", len(SENT), SENT, False, BODY_SENT)
CHARACTERS = len(SENT) + ASKED
WORDS = {"p": Words(PARTS), "kept": Words(PARTS, ("modules/*/domain/document.py",), ("Doc*", "title"))}
HIDDEN = "from <masked> import <masked>\nfrom dataclasses import dataclass\n" + BODY.replace("Document", "<masked>").replace(
    "title", "<masked>")
LOW = Answer("m-1.0.1", (("domain", 0.1), ("main", 0.9)), 100, 5)
HIGH = Answer("m-1.0.0", (("domain", 0.8), ("main", 0.2)), 90, 4)
DOUBTFUL = Reading(DOCUMENT.file, "domain", len(SENT), 0.1, 0.3, True, LOW.probabilities, "m-1.0.1",
                   small=True)
PLACED = Reading(OTHER.file, "domain", len(SENT_OTHER), 0.8, 0.3, False, HIGH.probabilities, "m-1.0.0", small=True)
PLACED_HERE = Reading(DOCUMENT.file, "domain", len(SENT), 0.8, 0.3, False, HIGH.probabilities, "m-1.0.0",
                      small=True)


def read(count: int, doubtful: int) -> tuple[PartRead, ...]:
    """How the domain files read: count of them, doubtful of those."""
    return (PartRead("domain", count, doubtful, 0.3, False, False, False),)


@dataclass(frozen=True)
class World:
    """What the fakes hold: the files found at each path; the answers kept from an earlier review of app/x.py, whose
    decision model gave these answers to each text; the answers the decision model gives now; and whether its key is
    set now."""
    found: dict[str, Found] = field(default_factory=lambda: FOUND)
    earlier: dict[str, Answer] = field(default_factory=dict)
    answers: dict[str, Answer] = field(default_factory=dict)
    keyed: bool = True


def review(*paths: str, listed: tuple[str, ...] = (), every: bool = False, dry_run: bool = False,
           profile: str = "p", max_files: int | None = 50, offline: bool = False, cache: Path | None = None,
           pieces: bool = False, context: str = NO_CONTEXT) -> Review:
    return Review(tuple(Path(p) for p in paths), tuple(Path(p) for p in listed), every, CWD, APP, profile, None,
                  dry_run, max_files, offline, cache, pieces, context)


def run(world: World, when: Review):
    code = FakeCode(world.found, refused={"/elsewhere": "/elsewhere lies outside the project"})
    profile = FakeProfile(WORDS, refused={"gone": "gone: no such file"})
    answers = FakeAnswers()
    controller(code, profile, FakeDecisionModel(world.earlier), answers).review(
        replace(when, paths=(Path("app/x.py"),), listed=(), every=False, dry_run=False, offline=False,
                profile="p", max_files=50))
    model = FakeDecisionModel(world.answers, world.keyed)
    return controller(code, profile, model, answers).review(when), model, answers


@pytest.mark.parametrize("given, when, then", [
    pytest.param(World(), review("app/modules/documents/domain", dry_run=True),
                 ReviewPlanned((BY_PATHS,), 3, (REQUEST,), (GONE, LeftOut(SMALL_FILE.file, SMALL, 6)), QUESTION, ("main",),
                               CHARACTERS, -(-CHARACTERS // 4), (), SENDS, 1),
                 id="a dry run says what each file judged would send, masked, and why the others are left out"),
    pytest.param(World(earlier={SENT: LOW}, keyed=False), review("app/x.py", dry_run=True),
                 ReviewPlanned((BY_PATHS,), 1, (Request(DOCUMENT.file, "domain", len(SENT), SENT, True,
                                                        BODY_SENT),), (), QUESTION, ("main",), CHARACTERS,
                               -(-CHARACTERS // 4), (), UNKEYED, 1),
                 id="a dry run says which request is in the cache already, and needs no key"),
    pytest.param(World(), review("app/modules/documents/domain", dry_run=True, profile="kept"),
                 ReviewPlanned((BY_PATHS,), 3, (), (GONE, LeftOut(DOCUMENT.file, NEVER, len(DOCUMENT.text),
                                                                  "modules/*/domain/document.py"),
                                                   LeftOut(SMALL_FILE.file, SMALL, 6)), QUESTION, ("main",), 0, 0,
                               ("Doc*", "title"), SENDS, 1, never=("modules/*/domain/document.py",)),
                 id="a file a path review never sends matches is left out with that path and sends nothing"),
    pytest.param(World(found={"app/x.py": Found((DOCUMENT,))}), review("app/x.py", dry_run=True, profile="kept"),
                 ReviewPlanned((BY_PATHS,), 1, (), (LeftOut(DOCUMENT.file, NEVER, len(DOCUMENT.text),
                                                            "modules/*/domain/document.py"),), QUESTION, ("main",), 0, 0,
                               ("Doc*", "title"), SENDS, 1, never=("modules/*/domain/document.py",)),
                 id="a file held back is held back however it is chosen"),
    pytest.param(World(answers={SENT: LOW}), review("app/modules/documents/domain"),
                 ReviewReading((BY_PATHS,), 3, (DOUBTFUL,), (GONE, LeftOut(SMALL_FILE.file, SMALL, 6)), (), SENDS, 1, 0,
                               100, 5, "", ("main",), read(1, 1), answered_by=("m-1.0.1",)),
                 id="a file whose part holds less than the line is doubtful there, asked of the decision model"),
    pytest.param(World(answers={SENT: LOW, SENT_OTHER: HIGH}), review("app/two"),
                 ReviewReading((BY_PATHS,), 2, (DOUBTFUL, PLACED), (), (), SENDS, 2, 0, 190, 9, "", ("main",), read(2, 1),
                               answered_by=("m-1.0.0", "m-1.0.1")),
                 id="the readings are ranked, the most doubtful first"),
    pytest.param(World(earlier={SENT: HIGH}, keyed=False), review("app/x.py"),
                 ReviewReading((BY_PATHS,), 1, (PLACED_HERE,), (), (), UNKEYED, 0, 1, 0, 0, "", ("main",), read(1, 0),
                               answered_by=("m-1.0.0",)),
                 id="an answer kept is read, not asked again, and needs no key"),
    pytest.param(World(earlier={SENT: LOW}), review("app/two", offline=True),
                 ReviewReading((BY_PATHS,), 2, (DOUBTFUL,), (), (Unasked(OTHER.file, NOT_CACHED),), SENDS, 0, 1, 0, 0,
                               "", ("main",), read(1, 1), answered_by=("m-1.0.1",)),
                 id="offline, a file whose answer is not kept is unanswered and nothing is sent"),
    pytest.param(World(answers={SENT_OTHER: HIGH}), review("app/two"),
                 ReviewReading((BY_PATHS,), 2, (), (), (Unasked(DOCUMENT.file, FAILED), Unasked(OTHER.file, FAILED)),
                               SENDS, 0, 0, 0, 0, "the decision model failed", ("main",)),
                 id="when the decision model fails, the files left to ask are unanswered and nothing more is sent"),
    pytest.param(World(keyed=False), review("app/x.py"), KeyMissing("MODEL_KEY"),
                 id="a review that would send with no key set is refused before anything is sent"),
    pytest.param(World(), review(), NothingChosen(), id="no file chosen is refused"),
    pytest.param(World(), review("app/x.py", every=True), AllAndOthers(), id="every file with paths is refused"),
    pytest.param(World(), review("app/modules/documents/domain", "app/x.py", max_files=1), TooManyFiles(2, 1),
                 id="more files than one run judges is refused"),
    pytest.param(World(), review("/elsewhere"), ReviewRefused("/elsewhere lies outside the project"),
                 id="a path outside the project is refused with why"),
    pytest.param(World(), review("app/x.py", profile="gone"), ReviewRefused("gone: no such file"),
                 id="a profile that cannot be used is refused with why"),
])
def test_review(given, when, then):
    assert run(given, when)[0] == then


def test_each_answer_asked_is_kept_under_a_key_of_its_own_in_the_project_s_cache_or_the_one_given():
    _, model, answers = run(World(answers={SENT: LOW, SENT_OTHER: HIGH}), review("app/two"))
    assert (model.asked, sorted(answers.kept.values(), key=lambda kept: kept.model)) == ([SENT, SENT_OTHER], [HIGH, LOW])
    assert {folder for folder, _ in answers.kept} == {FOLDER} and len({key for _, key in answers.kept}) == 2
    elsewhere = Path("/tmp/answers")
    _, _, answers = run(World(answers={SENT: LOW}), review("app/x.py", cache=elsewhere))
    assert list(answers.kept.values()) == [LOW] and {folder for folder, _ in answers.kept} == {elsewhere}


def test_a_text_masked_otherwise_is_another_question_and_is_asked_again():
    world = World(earlier={SENT: LOW}, answers={HIDDEN: HIGH},
                  found={"app/x.py": Found((DOCUMENT,)), "app/y.py": Found((found("app/modules/documents/domain/y.py"),))})
    _, model, _ = run(world, review("app/y.py", profile="kept"))
    assert model.asked == [HIDDEN]


@pytest.mark.parametrize("given, when", [
    pytest.param(World(answers={SENT: LOW}), review("app/x.py", dry_run=True), id="a dry run"),
    pytest.param(World(answers={SENT: LOW}), review("app/x.py", offline=True), id="offline"),
    pytest.param(World(answers={SENT: LOW}, keyed=False), review("app/x.py"), id="with no key"),
])
def test_nothing_is_asked_or_kept_in_a_dry_run_offline_or_with_no_key(given, when):
    _, model, answers = run(given, when)
    assert (model.asked, answers.kept) == ([], {})


def test_after_a_failure_nothing_more_is_asked_and_what_is_kept_is_still_read():
    world = World(found={"app/two": Found((OTHER, DOCUMENT)), "app/x.py": Found((DOCUMENT,))}, earlier={SENT: LOW})
    result, model, _ = run(world, review("app/two"))
    assert model.asked == [SENT_OTHER]
    assert isinstance(result, ReviewReading)
    assert (result.readings, result.unasked, result.complete) == ((DOUBTFUL,), (Unasked(OTHER.file, FAILED),), False)


HUGE = found("app/modules/documents/domain/huge.py", text="x = 1\n" * (MAX_CHARS // 6 + 1))


@pytest.mark.parametrize("dry_run", [True, False])
def test_a_file_over_the_largest_size_sent_is_left_out_with_its_size_and_never_sent(dry_run):
    world = World(found={"app/two": Found((HUGE, DOCUMENT))}, answers={SENT: LOW})
    result, model, _ = run(world, review("app/two", dry_run=dry_run))
    assert result.left_out == (LeftOut(HUGE.file, LARGE, len(HUGE.text)),)
    assert all(HUGE.text not in text for text in model.asked)
    assert [item.file for item in getattr(result, "requests", getattr(result, "readings", ()))] == [DOCUMENT.file]


def test_every_file_of_the_app_is_the_app_folder_read():
    planned, _, _ = run(World(found={"/src/app": Found((DOCUMENT,))}), review(every=True, dry_run=True))
    assert isinstance(planned, ReviewPlanned)
    assert (planned.by, planned.found) == (("all",), 1)


def test_listed_paths_are_read_after_those_named():
    world = World(found={"app/x.py": Found((DOCUMENT,)), "app/y.py": Found((SMALL_FILE,))})
    planned, _, _ = run(world, review("app/x.py", listed=("app/y.py",), dry_run=True))
    assert isinstance(planned, ReviewPlanned)
    assert (planned.by, [r.file for r in planned.requests], [i.file for i in planned.left_out]) == (
        ("paths", "files-from"), [DOCUMENT.file], [SMALL_FILE.file])


def test_the_texts_the_profile_says_review_hides_are_masked_in_what_each_request_would_send():
    world = World(found={"app/x.py": Found((found("app/modules/documents/domain/other.py"),))})
    planned, _, _ = run(world, review("app/x.py", profile="kept", dry_run=True))
    assert isinstance(planned, ReviewPlanned)
    assert [r.text for r in planned.requests] == [HIDDEN]
    assert planned.mask == ("Doc*", "title")


NEAR = Answer("m-1.0.1", (("domain", 0.2), ("main", 0.8)), 100, 5)
NEAR_AGAIN = Answer("m-1.0.1", (("main", 0.7), ("domain", 0.3)), 110, 6)


def _review(model: FakeDecisionModel, answers: FakeAnswers, when: Review):
    return controller(FakeCode(FOUND), FakeProfile(WORDS), model, answers).review(when)


def _kept(again: Answer | None) -> FakeAnswers:
    """The answers an earlier review of app/x.py kept: NEAR in the first order, and again in the other (None: that
    question failed, and only the first is kept)."""
    answers = FakeAnswers()
    _review(FakeDecisionModel({SENT: NEAR}, by_order={(SENT, "main"): again}), answers, review("app/x.py"))
    return answers


def test_a_file_whose_first_answer_is_near_its_line_is_asked_again_in_the_other_order_and_read_on_the_mean():
    model = FakeDecisionModel({SENT: NEAR}, by_order={(SENT, "main"): NEAR_AGAIN})
    answers = FakeAnswers()
    found = _review(model, answers, review("app/x.py"))
    assert isinstance(found, ReviewReading)
    (read,) = found.readings
    assert (read.probability, read.doubtful, read.orders, read.model) == (0.25, True, 2, "m-1.0.1")
    assert dict(read.distribution) == {"domain": 0.25, "main": 0.75}
    assert (found.sent, found.cached, found.input_tokens, found.output_tokens) == (2, 0, 210, 11)
    assert len(model.asked) == 2 and len(answers.kept) == 2


def test_a_file_far_from_its_line_is_asked_once():
    model = FakeDecisionModel({SENT: LOW})
    found = _review(model, FakeAnswers(), review("app/x.py"))
    assert isinstance(found, ReviewReading) and found.readings[0].orders == 1 and len(model.asked) == 1


def test_both_orders_kept_are_read_offline_and_count_as_cached():
    found = _review(FakeDecisionModel({}, keyed=False), _kept(NEAR_AGAIN),
                    review("app/x.py", offline=True))
    assert isinstance(found, ReviewReading)
    assert (found.readings[0].orders, found.cached, found.sent, found.complete) == (2, 2, 0, True)


def test_offline_a_file_near_its_line_whose_other_order_is_not_kept_is_unanswered():
    found = _review(FakeDecisionModel({}), _kept(None), review("app/x.py", offline=True))
    assert isinstance(found, ReviewReading)
    assert (found.readings, found.unasked) == ((), (Unasked(DOCUMENT.file, NOT_CACHED),))


def test_with_no_key_a_file_near_its_line_whose_other_order_is_not_kept_is_refused_before_anything_is_sent():
    model = FakeDecisionModel({}, keyed=False)
    assert _review(model, _kept(None), review("app/x.py")) == KeyMissing("MODEL_KEY")
    assert model.asked == []


def test_when_the_other_order_fails_the_file_is_unanswered_and_nothing_more_is_sent():
    model = FakeDecisionModel({SENT: NEAR, SENT_OTHER: HIGH}, by_order={(SENT, "main"): None})
    found = _review(model, FakeAnswers(), review("app/two"))
    assert isinstance(found, ReviewReading)
    assert found.unasked == (Unasked(DOCUMENT.file, FAILED), Unasked(OTHER.file, FAILED))
    assert found.failure == "the decision model failed" and found.sent == 1


TOO_LARGE = "TypeSafe answered 413: the state is too large"


def test_a_request_refused_alone_leaves_its_file_unanswered_with_the_words_and_the_rest_is_still_asked():
    model = FakeDecisionModel({SENT_OTHER: HIGH}, refused={SENT: TOO_LARGE})
    answers = FakeAnswers()
    found = _review(model, answers, review("app/two"))
    assert isinstance(found, ReviewReading)
    assert model.asked == [SENT, SENT_OTHER] and len(answers.kept) == 1
    assert (found.readings, found.unasked) == ((PLACED,), (Unasked(DOCUMENT.file, REFUSED, said=TOO_LARGE),))
    assert (found.failure, found.sent, found.complete) == ("", 1, False)


def test_a_refused_request_is_said_as_refused_and_a_failure_after_it_still_stops_the_sending():
    model = FakeDecisionModel({}, refused={SENT: TOO_LARGE})
    found = _review(model, FakeAnswers(), review("app/two"))
    assert isinstance(found, ReviewReading)
    assert found.unasked == (Unasked(DOCUMENT.file, REFUSED, said=TOO_LARGE), Unasked(OTHER.file, FAILED))
    assert found.failure == "the decision model failed" and model.asked == [SENT, SENT_OTHER]


def test_a_file_whose_other_order_is_refused_is_unanswered_as_refused_and_the_next_file_is_asked():
    model = FakeDecisionModel({SENT_OTHER: HIGH}, refused={SENT: TOO_LARGE})
    found = _review(model, _kept(None), review("app/two"))
    assert isinstance(found, ReviewReading) and model.asked == [SENT, SENT_OTHER]
    assert found.unasked == (Unasked(DOCUMENT.file, REFUSED, said=TOO_LARGE),)
    assert [item.file for item in found.readings] == [OTHER.file] and found.failure == ""


def test_a_dry_run_says_in_how_many_other_orders_a_file_near_its_line_is_asked_again():
    found = _review(FakeDecisionModel({}), FakeAnswers(), review("app/x.py", dry_run=True))
    assert isinstance(found, ReviewPlanned) and found.reorders == 1


FIRST = "def first():\n" + "    a = 1\n" * 120
SECOND = "def second():\n" + "    b = 2\n" * 120
THIRD = "def third():\n" + "    c = 3\n" * 120
TINY = "class Tiny:\n    x: int\n"
PIECED_TEXT = "from app.kernel.ids import DocumentId\n\n" + FIRST + SECOND + THIRD + TINY
PIECED = CodeFile("app/modules/documents/domain/pieced.py", "domain", PIECED_TEXT, (OWN,), spans=(
    Span("function", "first", "", (3, 123)), Span("function", "second", "", (124, 244)),
    Span("function", "third", "", (245, 365)), Span("class", "Tiny", "", (366, 367))))
WHOLE = PIECED_TEXT.replace("app.kernel.ids", "<masked>")
OPENING = "from <masked> import DocumentId\n\n"


def _on(probability: float) -> Answer:
    return Answer("m-1.0.1", (("domain", probability), ("main", 1 - probability)), 10, 1)


ON_PIECES = {WHOLE: _on(0.9), FIRST: _on(0.5), SECOND: _on(0.05), THIRD + TINY: _on(0.7)}


def _pieces(model: FakeDecisionModel, answers: FakeAnswers, **given):
    code = FakeCode({"app/p.py": Found((PIECED,)), "app/one.py": Found((found(),))})
    return controller(code, FakeProfile(WORDS), model, answers).review(review("app/p.py", **given))


def test_with_pieces_each_piece_judged_is_asked_with_the_piece_question_and_ranked_inside_its_file():
    model = FakeDecisionModel(ON_PIECES)
    found = _pieces(model, FakeAnswers(), pieces=True)
    assert isinstance(found, ReviewReading)
    assert [r.file for r in found.readings] == [PIECED.file]
    (read,) = found.pieces
    assert (read.file, read.part, read.judged, read.too_small, read.context, read.answered) == (
        PIECED.file, "domain", 3, 0, NO_CONTEXT, True)
    assert [(p.rank, p.name, p.kind, p.lines, p.probability) for p in read.lowest] == [
        (1, "second", "function", (124, 244), 0.05), (2, "first", "function", (3, 123), 0.5),
        (3, "third, Tiny", "function", (245, 367), 0.7)]
    assert model.asked == [WHOLE, FIRST, SECOND, THIRD + TINY] and found.sent == 4


def test_with_context_each_piece_is_sent_after_the_file_s_opening_lines():
    model = FakeDecisionModel({WHOLE: _on(0.9)} | {OPENING + text: answer for text, answer in ON_PIECES.items()})
    found = _pieces(model, FakeAnswers(), pieces=True, context=IMPORTS)
    assert isinstance(found, ReviewReading) and found.pieces[0].context == IMPORTS
    assert model.asked[1:] == [OPENING + FIRST, OPENING + SECOND, OPENING + THIRD + TINY]


def test_a_file_with_fewer_than_two_pieces_judged_has_nothing_to_rank_and_its_pieces_are_not_asked():
    model = FakeDecisionModel({SENT: HIGH})
    code = FakeCode({"app/one.py": Found((found(),))})
    result = controller(code, FakeProfile(WORDS), model, FakeAnswers()).review(review("app/one.py", pieces=True))
    assert isinstance(result, ReviewReading)
    assert result.pieces == (PiecesRead(DOCUMENT.file, "domain", 0, 0, NO_CONTEXT, ()),) and model.asked == [SENT]


def test_offline_a_piece_not_kept_is_unanswered_and_its_file_is_not_ranked():
    answers = FakeAnswers()
    _pieces(FakeDecisionModel({WHOLE: _on(0.9), FIRST: _on(0.5)}), answers, pieces=True)
    found = _pieces(FakeDecisionModel({}), answers, pieces=True, offline=True)
    assert isinstance(found, ReviewReading)
    assert found.unasked == (Unasked(PIECED.file, NOT_CACHED, "second"), Unasked(PIECED.file, NOT_CACHED, "third, Tiny"))
    assert (found.pieces[0].lowest, found.pieces[0].answered, found.cached) == ((), False, 2)


def test_a_dry_run_with_pieces_shows_each_piece_request_after_the_files_and_counts_their_characters():
    planned = _pieces(FakeDecisionModel({}), FakeAnswers(), pieces=True, dry_run=True)
    assert isinstance(planned, ReviewPlanned)
    assert planned.piece_ask == f"{PLACEMENT} This text is one piece of a larger file."
    assert [(r.piece, r.text) for r in planned.requests] == [("", WHOLE), ("first", FIRST), ("second", SECOND),
                                                             ("third, Tiny", THIRD + TINY)]
    assert planned.requests[1].body.startswith(f"{PLACEMENT} This text is one piece of a larger file. 2 ")
    asked = ASKED + len(" This text is one piece of a larger file.")
    assert planned.characters == len(WHOLE) + ASKED + len(FIRST + SECOND + THIRD + TINY) + 3 * asked


def test_with_no_key_a_piece_not_kept_is_refused_before_anything_is_sent():
    answers = FakeAnswers()
    _pieces(FakeDecisionModel({WHOLE: _on(0.9)}), answers)
    model = FakeDecisionModel({}, keyed=False)
    assert isinstance(_pieces(model, answers), ReviewReading)
    assert _pieces(model, answers, pieces=True) == KeyMissing("MODEL_KEY") and model.asked == []


def test_every_file_of_the_app_in_pieces_is_refused_before_anything_is_read():
    code = FakeCode({}, refused={"/src/app": "read"})
    model = FakeDecisionModel({})
    assert controller(code, FakeProfile(WORDS), model, FakeAnswers()).review(review(every=True, pieces=True)) == (
        AllInPieces())


def test_an_answer_kept_that_is_not_of_the_question_s_shape_is_no_answer_and_the_question_is_asked_again():
    answers = FakeAnswers()
    _review(FakeDecisionModel({SENT: LOW}), answers, review("app/x.py"))
    for key in answers.kept:
        answers.kept[key] = Answer("m-1.0.1", (("domain", 1.0), ("main", 1.0)), 100, 5)
    model = FakeDecisionModel({SENT: HIGH})
    result = _review(model, answers, review("app/x.py"))
    assert model.asked == [SENT] and isinstance(result, ReviewReading) and result.readings[0].model == HIGH.model


def test_a_cache_folder_that_cannot_keep_answers_is_refused_before_anything_is_sent():
    model = FakeDecisionModel({SENT: LOW})
    answers = FakeAnswers(unready={FOLDER: f"cannot keep answers in {FOLDER}: it is a file, not a folder"})
    assert _review(model, answers, review("app/x.py")) == ReviewRefused(
        f"cannot keep answers in {FOLDER}: it is a file, not a folder")
    assert model.asked == []


@pytest.mark.parametrize("when", [
    pytest.param(review("app/x.py"), id="a review that would send"),
    pytest.param(review("app/x.py", dry_run=True), id="a dry run"),
])
def test_examples_that_cannot_be_read_are_refused_before_anything_is_sent(when):
    model = FakeDecisionModel({SENT: LOW})
    profile = FakeProfile(WORDS, unreadable={"p": "examples/text.py: not valid UTF-8"})
    result = controller(FakeCode(FOUND), profile, model, FakeAnswers()).review(when)
    assert (result, model.asked) == (ReviewRefused("examples/text.py: not valid UTF-8"), [])


def test_a_dry_run_says_the_paths_of_review_never_in_force_and_those_that_matched_no_file_found():
    profile = FakeProfile({"p": Words(PARTS, ("app/modules/documents/domain/document.py", "modules/*/domain/*.py"))})
    planned = controller(FakeCode(FOUND), profile, FakeDecisionModel({}), FakeAnswers()).review(
        review("app/x.py", dry_run=True))
    assert isinstance(planned, ReviewPlanned)
    assert (planned.never, planned.unmatched) == (("app/modules/documents/domain/document.py", "modules/*/domain/*.py"),
                                                  ("app/modules/documents/domain/document.py",))


UNUSABLE = "it holds a character a request header cannot carry; set it to the key alone"


def test_a_key_that_cannot_be_used_refuses_a_review_that_would_send_before_anything_is_sent():
    model = FakeDecisionModel({SENT: LOW}, unusable=UNUSABLE)
    found = controller(FakeCode(FOUND), FakeProfile(WORDS), model, FakeAnswers()).review(review("app/x.py"))
    assert found == ReviewRefused(f"MODEL_KEY cannot be used: {UNUSABLE}") and model.tried == []


def test_a_key_that_cannot_be_used_blocks_no_dry_run_which_says_why_and_no_review_offline():
    model = FakeDecisionModel({}, unusable=UNUSABLE)
    answers = FakeAnswers()
    planned = controller(FakeCode(FOUND), FakeProfile(WORDS), model, answers).review(review("app/x.py", dry_run=True))
    assert isinstance(planned, ReviewPlanned) and planned.sends == replace(SENDS, unusable=UNUSABLE)
    offline = controller(FakeCode(FOUND), FakeProfile(WORDS), model, answers).review(review("app/x.py", offline=True))
    assert isinstance(offline, ReviewReading) and [item.why for item in offline.unasked] == [NOT_CACHED]
    assert model.asked == []


def test_a_key_that_cannot_be_used_blocks_no_review_whose_every_answer_is_kept():
    code, profile, answers = FakeCode(FOUND), FakeProfile(WORDS), FakeAnswers()
    controller(code, profile, FakeDecisionModel({SENT: HIGH}), answers).review(review("app/x.py"))
    model = FakeDecisionModel({}, unusable=UNUSABLE)
    found = controller(code, profile, model, answers).review(review("app/x.py"))
    assert isinstance(found, ReviewReading) and found.cached == 1 and model.asked == []


NOTED_TEXT = ("from app.kernel.ids import DocumentId  # ids are kernel's\n# a value of domain/\nMARK = '# kept: no comment'\n"
              + BODY)
NOTED = CodeFile("app/modules/documents/domain/noted.py", "domain", NOTED_TEXT, (OWN,),
                 comments=(CommentSpan(1, 39, 57), CommentSpan(2, 0, 20)))
NOTED_SENT = "from <masked> import DocumentId\n\nMARK = '# kept: no comment'\n" + BODY


def test_each_comment_of_a_file_is_cut_from_what_its_request_sends_and_its_characters_are_those_sent():
    code = FakeCode({"app/n.py": Found((NOTED,))})
    planned = controller(code, FakeProfile(WORDS), FakeDecisionModel({}), FakeAnswers()).review(
        review("app/n.py", dry_run=True))
    assert isinstance(planned, ReviewPlanned)
    assert [(item.text, item.chars) for item in planned.requests] == [(NOTED_SENT, len(NOTED_SENT))]
    assert planned.characters == len(NOTED_SENT) + ASKED
    model = FakeDecisionModel({NOTED_SENT: HIGH})
    assert isinstance(controller(code, FakeProfile(WORDS), model, FakeAnswers()).review(review("app/n.py")),
                      ReviewReading) and model.asked == [NOTED_SENT]


def test_a_comment_inside_a_piece_or_in_the_opening_lines_sent_before_it_is_cut_and_no_line_of_a_piece_moves():
    text = ("from app.kernel.ids import DocumentId  # the ids\n\n" + "def first():\n    # first is domain\n"
            + "    a = 1\n" * 119 + SECOND + THIRD + TINY)
    pieced = replace(PIECED, text=text, comments=(CommentSpan(1, 39, 48), CommentSpan(4, 4, 21)))
    code = FakeCode({"app/p.py": Found((pieced,))})
    first = "def first():\n\n" + "    a = 1\n" * 119
    model = FakeDecisionModel({OPENING + first: _on(0.5), OPENING + SECOND: _on(0.05), OPENING + THIRD + TINY: _on(0.7),
                               text.replace("app.kernel.ids", "<masked>").replace("  # the ids", "").replace(
                                   "    # first is domain", ""): _on(0.9)})
    found = controller(code, FakeProfile(WORDS), model, FakeAnswers()).review(
        review("app/p.py", pieces=True, context=IMPORTS))
    assert isinstance(found, ReviewReading)
    assert [(p.name, p.lines) for p in found.pieces[0].lowest] == [
        ("second", (124, 244)), ("first", (3, 123)), ("third, Tiny", (245, 367))]
    assert model.asked[1:] == [OPENING + first, OPENING + SECOND, OPENING + THIRD + TINY]
    assert not any("the ids" in sent or "first is domain" in sent for sent in model.asked)


KERNEL = PartText("kernel", "kernel/", "Is it shared by every module?", "shared code", 0.3, alike=("domain",))
ALIKE = Words((replace(PARTS[0], alike=("kernel",)), PARTS[1], KERNEL))
"""A profile whose domain and kernel one file cannot tell apart."""
SPLIT = Answer("m-1.0.1", (("domain", 0.25), ("main", 0.25), ("kernel", 0.5)), 100, 5)
"""An answer that puts a quarter on domain alone, within the band of its line, and three quarters on its group."""
SUMMED = Reading(DOCUMENT.file, "domain", len(SENT), 0.75, 0.3, False, SPLIT.probabilities, "m-1.0.1", small=True,
                 alike=("kernel",))


@dataclass(frozen=True)
class Alike:
    """What the fakes hold for a profile reading domain and kernel alike: the files found at each path; the answers a
    run before this one kept, asked of its decision model with the same profile; and the answers the decision model
    gives now."""
    found: dict[str, Found] = field(default_factory=lambda: {"app/x.py": Found((DOCUMENT,)), "/src/app": Found((DOCUMENT,))})
    earlier: dict[str, Answer] = field(default_factory=dict)
    answers: dict[str, Answer] = field(default_factory=dict)


def alike(given: Alike, when: Review):
    code, profile, answers = FakeCode(given.found), FakeProfile({"alike": ALIKE}), FakeAnswers()
    if given.earlier:
        controller(code, profile, FakeDecisionModel(given.earlier), answers).review(review("app/x.py", profile="alike"))
    model = FakeDecisionModel(given.answers)
    return controller(code, profile, model, answers).review(replace(when, profile="alike")), model


@pytest.mark.parametrize("given, when, then", [
    pytest.param(Alike(answers={SENT: SPLIT}), review("app/x.py"),
                 ReviewReading((BY_PATHS,), 1, (SUMMED,), (), (), SENDS, 1, 0, 100, 5, "", ("main",), read(1, 0),
                               answered_by=("m-1.0.1",)),
                 id="a file of a part read alike is read on its group's sum, far from its line, and asked once"),
    pytest.param(Alike(earlier={SENT: SPLIT}), review("app/x.py", offline=True),
                 ReviewReading((BY_PATHS,), 1, (SUMMED,), (), (), SENDS, 0, 1, 0, 0, "", ("main",), read(1, 0),
                               answered_by=("m-1.0.1",)),
                 id="offline, the answer kept is read on the group's sum alike"),
    pytest.param(Alike(answers={SENT: SPLIT}), review(every=True),
                 ReviewReading((BY_ALL,), 1, (SUMMED,), (), (), SENDS, 1, 0, 100, 5, "", ("main",), read(1, 0),
                               answered_by=("m-1.0.1",)),
                 id="every file of the app is read on its group's sum alike"),
    pytest.param(Alike(), review("app/x.py", dry_run=True),
                 ReviewPlanned((BY_PATHS,), 1, (replace(REQUEST, body=f"{PLACEMENT} 3 {SENT}"),), (),
                               replace(QUESTION, options=(*QUESTION.options, Option("kernel", KERNEL.litmus))),
                               ("main",), CHARACTERS + len("kernel") + len(KERNEL.litmus),
                               -(-(CHARACTERS + len("kernel") + len(KERNEL.litmus)) // 4), (), SENDS, 2,
                               alike=(("domain", "kernel"),)),
                 id="a dry run says the groups of parts read alike"),
])
def test_review_with_parts_read_alike(given, when, then):
    assert alike(given, when)[0] == then


def test_a_file_of_a_part_read_alike_is_not_asked_again_though_its_own_part_alone_is_near_its_line():
    _, model = alike(Alike(answers={SENT: SPLIT}), review("app/x.py"))
    assert model.asked == [SENT]


def test_the_pieces_of_a_file_of_a_part_read_alike_are_ranked_on_its_group_s_sum_and_say_so():
    def split(own: float, other: float) -> Answer:
        return Answer("m-1.0.1", (("domain", own), ("main", 1 - own - other), ("kernel", other)), 10, 1)

    model = FakeDecisionModel({WHOLE: split(0.5, 0.5), FIRST: split(0.5, 0.25), SECOND: split(0.25, 0.0),
                               THIRD + TINY: split(0.0, 0.5)})
    found = controller(FakeCode({"app/p.py": Found((PIECED,))}), FakeProfile({"alike": ALIKE}), model,
                       FakeAnswers()).review(review("app/p.py", profile="alike", pieces=True))
    assert isinstance(found, ReviewReading)
    (read,) = found.pieces
    assert [(p.name, p.probability) for p in read.lowest] == [("second", 0.25), ("third, Tiny", 0.5), ("first", 0.75)]
    assert read.alike == ("kernel",)


def test_a_file_is_read_once_the_parts_whose_holds_it_would_break_are_ruled_out_of_its_answer():
    code = FakeCode(FOUND, breaks={DOCUMENT.text: ("main", "domain")})
    model = FakeDecisionModel({SENT: Answer("m-1.0.1", (("domain", 0.25), ("main", 0.75)), 100, 5)})
    found = controller(code, FakeProfile(WORDS), model, FakeAnswers()).review(review("app/x.py"))
    assert isinstance(found, ReviewReading)
    (file,) = found.readings
    assert (file.probability, file.doubtful, file.orders) == (1.0, False, 1)
    assert file.ruled_out == (RuledOut("main", HOLDS, 0.75),)
    assert file.distribution == (("domain", 0.25), ("main", 0.75))
    assert found.parts == read(1, 0)
    assert code.held == [("app", ("modules/documents/domain/document.py",), APP)]


def test_nothing_is_asked_of_where_else_a_file_could_lie_in_a_dry_run():
    code = FakeCode(FOUND, breaks={DOCUMENT.text: ("main",)})
    controller(code, FakeProfile(WORDS), FakeDecisionModel({}), FakeAnswers()).review(review("app/x.py", dry_run=True))
    assert code.held == []


ACCEPTED_RECORD = Path("/src/.xarch/accepted.json")


def _accepted(record: dict, when: Review, answers: dict | None = None):
    acceptances = FakeAcceptances({ACCEPTED_RECORD: record})
    model = FakeDecisionModel(answers if answers is not None else {SENT: LOW, SENT_OTHER: HIGH})
    return controller(FakeCode(FOUND), FakeProfile(WORDS), model, FakeAnswers(), acceptances=acceptances).review(when)


def test_a_doubtful_file_accepted_whose_code_is_as_it_was_reads_as_accepted_and_not_doubtful():
    record = {DOCUMENT.file: AcceptedFile("domain", "main", code_hash(SENT), "read: the values")}
    found = _accepted(record, review("app/x.py"))
    assert isinstance(found, ReviewReading)
    assert found.readings == (replace(DOUBTFUL, doubtful=False, accepted=Acceptance("read: the values", "main")),)
    assert (found.parts, found.accepted, found.stale) == (read(1, 0), 1, ())


def test_a_doubtful_file_accepted_whose_code_changed_since_is_doubtful_again_with_what_was_said_before():
    record = {DOCUMENT.file: AcceptedFile("domain", "main", code_hash(SENT + "x = 1\n"), "read: the values")}
    found = _accepted(record, review("app/x.py"))
    assert isinstance(found, ReviewReading)
    assert found.readings == (replace(DOUBTFUL, accepted_before=Acceptance("read: the values", "main")),)
    assert found.parts == read(1, 1)


def test_the_files_of_the_record_that_are_stale_are_said_for_the_files_found_and_every_file_with_all():
    record = {OTHER.file: AcceptedFile("domain", "main", code_hash(SENT_OTHER), "w"),
              GONE.file: AcceptedFile("domain", "main", "x", "w"), "app/elsewhere.py": AcceptedFile("domain", "", "x", "w")}
    found = _accepted(record, review("app/modules/documents/domain", "app/two"))
    assert isinstance(found, ReviewReading)
    assert found.stale == (StaleAcceptance(GONE.file, "domain", GONE_FILE),
                           StaleAcceptance(OTHER.file, "domain", SETTLED))
    every = _accepted(record, review(every=True), {SENT: LOW})
    assert isinstance(every, ReviewReading) and every.readings == ()
    assert every.stale == tuple(StaleAcceptance(file, "domain", GONE_FILE) for file in sorted(record))


def test_a_file_accepted_is_still_asked_when_its_answer_is_not_kept_and_a_dry_run_says_how_many_are_accepted():
    record = {DOCUMENT.file: AcceptedFile("domain", "main", code_hash(SENT), "w")}
    acceptances = FakeAcceptances({ACCEPTED_RECORD: record})
    model = FakeDecisionModel({SENT: LOW})
    controller(FakeCode(FOUND), FakeProfile(WORDS), model, FakeAnswers(), acceptances=acceptances).review(
        review("app/x.py"))
    assert model.asked == [SENT]
    planned = _accepted(record, review("app/x.py", dry_run=True))
    assert isinstance(planned, ReviewPlanned) and planned.accepted == 1


def test_a_record_of_accepted_files_that_cannot_be_read_refuses_the_review_before_anything_is_sent():
    acceptances = FakeAcceptances(unreadable={ACCEPTED_RECORD: "the record of accepted files cannot be read"})
    model = FakeDecisionModel({SENT: LOW})
    found = controller(FakeCode(FOUND), FakeProfile(WORDS), model, FakeAnswers(), acceptances=acceptances).review(
        review("app/x.py"))
    assert found == ReviewRefused("the record of accepted files cannot be read") and model.asked == []
