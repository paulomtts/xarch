"""Use case: review chosen files, here with --dry-run, which sends nothing and says what would be sent, around fakes."""
from pathlib import Path

import pytest

from tests.fakes.review import FakeCode, FakeParts
from tests.modules.review.application.helpers import controller
from tests.modules.review.builders import BODY, PARTS, found
from xarch.modules.review.contract import (
    BY_PATHS,
    MISSING,
    SMALL,
    AllAndOthers,
    Choice,
    LeftOut,
    NothingChosen,
    NotSendable,
    Option,
    Request,
    Review,
    ReviewPlanned,
    ReviewRefused,
    TooManyFiles,
)
from xarch.modules.review.domain.values import Found

CWD, APP = Path("/src"), Path("/src/app")
DOCUMENT = found()
SMALL_FILE = found("app/modules/documents/domain/small.py", text="x = 1\n")
GONE = LeftOut("app/modules/documents/domain/gone.py", MISSING)
FOUND = {"app/modules/documents/domain": Found((DOCUMENT, SMALL_FILE), (GONE,)), "app/x.py": Found((DOCUMENT,))}
PLACEMENT = ("Which part of this architecture does this code belong in? Each option is a part and the test that "
             "decides whether code belongs in it.")
QUESTION = Choice(PLACEMENT, (Option("domain", "Is it an invariant of one of this module's values?"),
                              Option("main", "starts the app")))
SENT = "from <masked> import DocumentId\nfrom dataclasses import dataclass\n" + BODY
ASKED = len(PLACEMENT) + sum(len(o.name) + len(o.description) for o in QUESTION.options)
REQUEST = Request(DOCUMENT.file, "domain", len(DOCUMENT.text), SENT)
CHARACTERS = len(SENT) + ASKED


def review(*paths: str, listed: tuple[str, ...] = (), every: bool = False, dry_run: bool = True,
           profile: str = "p", max_files: int = 50) -> Review:
    return Review(tuple(Path(p) for p in paths), tuple(Path(p) for p in listed), every, CWD, APP, profile, None,
                  dry_run, max_files)


@pytest.mark.parametrize("given, when, then", [
    pytest.param(FOUND, review("app/modules/documents/domain"),
                 ReviewPlanned((BY_PATHS,), 3, (REQUEST,), (GONE, LeftOut(SMALL_FILE.file, SMALL, 6)), QUESTION, ("main",),
                               CHARACTERS, -(-CHARACTERS // 4)),
                 id="a dry run says what each file judged would send, masked, and why the others are left out"),
    pytest.param(FOUND, review(), NothingChosen(), id="no file chosen is refused"),
    pytest.param(FOUND, review("app/x.py", every=True), AllAndOthers(), id="every file with paths is refused"),
    pytest.param(FOUND, review("app/modules/documents/domain", "app/x.py", max_files=1), TooManyFiles(2, 1),
                 id="more files than one run judges is refused"),
    pytest.param(FOUND, review("app/x.py", dry_run=False), NotSendable(),
                 id="a review that would send is refused while there is nothing to send with"),
    pytest.param(FOUND, review("/elsewhere"), ReviewRefused("/elsewhere lies outside the project"),
                 id="a path outside the project is refused with why"),
    pytest.param(FOUND, review("app/x.py", profile="gone"), ReviewRefused("gone: no such file"),
                 id="a profile that cannot be used is refused with why"),
])
def test_review(given, when, then):
    code = FakeCode(given, refused={"/elsewhere": "/elsewhere lies outside the project"})
    parts = FakeParts({"p": PARTS}, refused={"gone": "gone: no such file"})
    assert controller(code, parts).review(when) == then


def test_every_file_of_the_app_is_the_app_folder_read():
    code = FakeCode({"/src/app": Found((DOCUMENT,))})
    planned = controller(code, FakeParts({"p": PARTS})).review(review(every=True))
    assert isinstance(planned, ReviewPlanned)
    assert (planned.by, planned.found) == (("all",), 1)


def test_listed_paths_are_read_after_those_named():
    code = FakeCode({"app/x.py": Found((DOCUMENT,)), "app/y.py": Found((SMALL_FILE,))})
    planned = controller(code, FakeParts({"p": PARTS})).review(review("app/x.py", listed=("app/y.py",)))
    assert isinstance(planned, ReviewPlanned)
    assert (planned.by, [r.file for r in planned.requests], [i.file for i in planned.left_out]) == (
        ("paths", "files-from"), [DOCUMENT.file], [SMALL_FILE.file])
