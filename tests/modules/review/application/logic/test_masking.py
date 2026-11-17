"""What text a question about a file carries: the comments the reader finds cut, the modules the app's own imports
name, e-mail addresses, and the texts the profile says review hides, masked."""
import pytest

from xarch.kernel.source import CommentSpan, Import
from xarch.modules.review.application.logic.lines import lines
from xarch.modules.review.application.logic.masking import MASK, PERSON, masked, own

OWN = Import(1, ("app", "kernel", "ids"), ("DocumentId",), written="app.kernel.ids")
RELATIVE = Import(2, ("values",), ("Title",), relative=True, written=".values")
OTHER = Import(3, ("dataclasses",), ("dataclass",), standard=True, written="dataclasses")
WHOLE = Import(4, ("app", "platform"), written="app.platform")
TEXT = ("from app.kernel.ids import DocumentId\nfrom .values import Title\nfrom dataclasses import dataclass\n"
        "import app.platform\n")


@pytest.mark.parametrize("imported, root, then", [
    pytest.param(OWN, "app", True, id="an import whose first step is the app's name is its own"),
    pytest.param(RELATIVE, "app", True, id="an import named from the importing file's folder is its own"),
    pytest.param(OTHER, "app", False, id="an import of another package is not"),
    pytest.param(OWN, "shop", False, id="the app's name is what decides, not the word app"),
])
def test_which_imports_name_the_app_s_own_code(imported, root, then):
    assert own(imported, root) is then


def test_the_module_an_import_of_the_app_s_own_code_names_is_masked_on_its_line():
    assert masked(TEXT, (OWN, RELATIVE, OTHER, WHOLE), "app") == (
        f"from {MASK} import DocumentId\nfrom {MASK} import Title\nfrom dataclasses import dataclass\nimport {MASK}\n")


def test_only_the_first_place_on_the_line_is_masked_and_other_lines_are_left_as_they_are():
    text = "from app.kernel.ids import DocumentId  \nX = 'app.kernel.ids'\n"
    assert masked(text, (OWN,), "app") == f"from {MASK} import DocumentId  \nX = 'app.kernel.ids'\n"


def test_an_import_whose_line_is_not_in_the_text_is_left_alone():
    assert masked("x = 1\n", (Import(9, ("app", "x"), written="app.x"),), "app") == "x = 1\n"


@pytest.mark.parametrize("text, then", [
    pytest.param("contact: jane.doe+docs@mail.example.com.\n", f"contact: {PERSON}.\n", id="an address is masked"),
    pytest.param("a@b.c and x_y@d-e.org\n", f"{PERSON} and {PERSON}\n", id="every address is masked"),
    pytest.param("at @home, user@localhost\n", "at @home, user@localhost\n",
                 id="a name with no dot after the @ is no address"),
])
def test_e_mail_addresses_are_masked(text, then):
    assert masked(text, (), "app") == then


@pytest.mark.parametrize("mask, text, then", [
    pytest.param(("Northwind",), "for Northwind, not northwind\n", f"for {MASK}, not northwind\n",
                 id="a text is hidden as written, case counting"),
    pytest.param(("DOC-*",), "see DOC-1042 and DOC-7.x, not DOC-\n", f"see {MASK} and {MASK}, not DOC-\n",
                 id="a star stands for a run of letters, digits, _, - and ."),
    pytest.param(("*.corp.test",), "url = 'https://billing.corp.test/x'\n", f"url = 'https://{MASK}/x'\n",
                 id="a star never runs past a character outside its run"),
    pytest.param(("a+b (c)",), "x = a+b (c)\n", f"x = {MASK}\n", id="every other character is itself"),
    pytest.param(("Northwind", "<masked> Ltd"), "Northwind Ltd\n", f"{MASK}\n",
                 id="the texts are hidden in the profile's order"),
])
def test_the_texts_the_profile_says_review_hides_are_masked_after_the_rest(mask, text, then):
    assert masked(text, (), "app", mask) == then


def test_a_text_the_profile_hides_is_masked_after_the_imports_and_the_addresses():
    assert masked("from app.kernel.ids import DocumentId\n# ask ops@app.example\n", (OWN,), "app", ("app*",)) == (
        f"from {MASK} import DocumentId\n# ask {PERSON}\n")


def test_a_line_separator_or_a_form_feed_above_an_import_moves_no_line_and_the_import_is_masked():
    text = "# a note\u2028still the note\x0c\nfrom app.kernel.ids import DocumentId\n"
    assert masked(text, (Import(2, ("app", "kernel", "ids"), ("DocumentId",), written="app.kernel.ids"),), "app") == (
        f"# a note\u2028still the note\x0c\nfrom {MASK} import DocumentId\n")


@pytest.mark.parametrize("text, imported, then", [
    pytest.param("from \\\n    app.kernel.ids import DocumentId\nx = 1\n",
                 Import(1, ("app", "kernel", "ids"), ("DocumentId",), written="app.kernel.ids", last=2),
                 f"from \\\n    {MASK} import DocumentId\nx = 1\n", id="an import continued onto the next line"),
    pytest.param("from app . kernel . ids import DocumentId\n",
                 Import(1, ("app", "kernel", "ids"), ("DocumentId",), written="app.kernel.ids"),
                 f"from {MASK} import DocumentId\n", id="blanks around the dots"),
    pytest.param("from app.kernel \\\n  .ids import DocumentId\nx = 1\n",
                 Import(1, ("app", "kernel", "ids"), ("DocumentId",), written="app.kernel.ids", last=2),
                 f"from {MASK}\\\n import DocumentId\nx = 1\n", id="a line continued between two steps keeps its break"),
    pytest.param("import app.kernel.idsx, app.kernel.ids\n", Import(1, ("app", "kernel", "ids"), written="app.kernel.ids"),
                 f"import app.kernel.idsx, {MASK}\n", id="a longer name that starts as the module's is not it"),
])
def test_the_module_of_an_import_is_masked_however_the_source_writes_it_on_the_lines_it_spans(text, imported, then):
    result = masked(text, (imported,), "app")
    assert result == then and len(result.splitlines()) == len(text.splitlines())


@pytest.mark.parametrize("text, comments, then", [
    pytest.param("x = 1  # one\ny = 2\n", (CommentSpan(1, 7, 12),), "x = 1\ny = 2\n",
                 id="a comment after code is cut with the blanks before it"),
    pytest.param("x = 1\n    # one\ny = 2\n", (CommentSpan(2, 4, 9),), "x = 1\n\ny = 2\n",
                 id="a line that held only a comment stays as an empty line"),
    pytest.param("x = '# no'  # yes\n", (CommentSpan(1, 12, 17),), "x = '# no'\n",
                 id="only what the reader says is a comment is cut, the rest of the line as written"),
    pytest.param("x = 1\t\x0c # one\r\ny = 2  # two\rz = 3\n", (CommentSpan(1, 8, 13), CommentSpan(2, 7, 12)),
                 "x = 1\r\ny = 2\rz = 3\n", id="each line keeps its own line break"),
    pytest.param("a /* one\ntwo\nthree */ b\nc\n", (CommentSpan(1, 2, 8, 3),), "a\n\n b\nc\n",
                 id="a comment over lines leaves each of its lines, the text after it kept"),
    pytest.param("a /* x */ b /* y */\n", (CommentSpan(1, 2, 9), CommentSpan(1, 12, 19)), "a b\n",
                 id="two comments on one line are both cut"),
    pytest.param("x = 1\n", (CommentSpan(4, 0, 3),), "x = 1\n", id="a comment past the text is left alone"),
])
def test_each_comment_the_reader_finds_is_cut_from_its_line_and_no_line_moves(text, comments, then):
    result = masked(text, (), "app", comments=comments)
    assert result == then and len(lines(result)) == len(lines(text))


def test_a_comment_on_an_import_is_cut_and_the_import_masked_on_the_same_line():
    text = "from app.kernel.ids import DocumentId  # the ids live in kernel\nx = 1  # mail ops@app.example\n"
    assert masked(text, (OWN,), "app", ("kernel",), comments=(CommentSpan(1, 39, 63), CommentSpan(2, 7, 29))) == (
        f"from {MASK} import DocumentId\nx = 1\n")
