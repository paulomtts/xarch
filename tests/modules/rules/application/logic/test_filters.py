"""Every filter, on the facts of a small project: one row per filter, each the facts of one kind of one file it holds
of, by their lines (a filter about the file holds of every fact of a file or of none), so that a filter the vocabulary
publishes and the engine does not answer, or answers wrongly, fails here; a negated filter holds where it does not."""
import pytest

from tests.modules.rules.application.logic.world import (
    BROKEN,
    BUILT,
    DOMAIN,
    ERRORS,
    FACTS,
    FAKE,
    GUARD,
    HELPER,
    LISTED,
    NARROWED,
    PORTS,
    PROFILE,
    RESERVED,
    RULE,
    SERVICE,
    STRUCTURE,
    TEST,
    UNREAD,
    WIRING,
    found,
)
from tests.modules.rules.builders import BRACE, imp, source
from xarch.kernel.logic.conditions import condition
from xarch.modules.rules.application.logic import filters
from xarch.modules.rules.application.logic.facts import facts_of
from xarch.modules.rules.application.logic.filters import question
from xarch.modules.rules.domain.parsed import Class
from xarch.modules.rules.domain.rule import Found
from xarch.modules.rules.domain.vocabulary import FILTERS


@pytest.mark.parametrize("text, file, kind, lines, profile, hit", [
    pytest.param("test", TEST, "file", [0], PROFILE, None, id="test: a test file"),
    pytest.param("test", HELPER, "file", [], PROFILE, None, id="test: a helper is no test"),
    pytest.param("tiered", DOMAIN, "file", [0], PROFILE, None, id="tiered: a file of the app its tier tests"),
    pytest.param("tiered", GUARD, "file", [0], PROFILE, None, id="tiered: a test of a tier"),
    pytest.param("tiered", WIRING, "file", [], PROFILE, None, id="tiered: a file of a part no tier tests"),
    pytest.param("placed", STRUCTURE, "file", [0], PROFILE, None, id="placed: a file of the structure"),
    pytest.param("placed", TEST, "file", [], PROFILE, None, id="placed: a test lies in no place of the app"),
    pytest.param("package-file", STRUCTURE, "file", [0], PROFILE, None, id="package-file: a package file"),
    pytest.param("package-file", DOMAIN, "file", [], PROFILE, None, id="package-file: any other file"),
    pytest.param("mirrors-a-part", TEST, "file", [0], PROFILE, None, id="mirrors-a-part: a test of a part"),
    pytest.param("mirrors-a-part", GUARD, "file", [], PROFILE, None, id="mirrors-a-part: a test of its tier's folder"),
    pytest.param("may-import-everything", WIRING, "file", [0], PROFILE, None,
                 id="may-import-everything: a file of a part that may"),
    pytest.param("may-import-everything", DOMAIN, "file", [], PROFILE, None,
                 id="may-import-everything: a file of a part that may not"),
    pytest.param("below fakes", FAKE, "file", [0], PROFILE, None, id="below: a file below the folder"),
    pytest.param("below fakes", TEST, "file", [], PROFILE, None, id="below: a file elsewhere"),
    pytest.param("relative", DOMAIN, "import", [3], PROFILE, None, id="relative"),
    pytest.param("standard", DOMAIN, "import", [4], PROFILE, None, id="standard"),
    pytest.param("standard", DOMAIN, "import", [4], RESERVED, None, id="standard: a module the profile reserves too"),
    pytest.param("reserved", DOMAIN, "import", [4], RESERVED, None, id="reserved"),
    pytest.param("listed-by-another-part", DOMAIN, "import", [1], LISTED, None, id="listed-by-another-part"),
    pytest.param("app-package", DOMAIN, "import", [2, 5], PROFILE, None, id="app-package"),
    pytest.param("own-code", DOMAIN, "import", [2, 3, 5], PROFILE, None, id="own-code: relative or the app's"),
    pytest.param("own-code", TEST, "import", [1, 2, 3, 4, 5], PROFILE, None, id="own-code: the tests' too"),
    pytest.param("takes-a-name", DOMAIN, "imported-name", [2, 3, 4, 5, 5], PROFILE, None, id="takes-a-name"),
    pytest.param("on-own-object", DOMAIN, "method-call", [19], PROFILE, None, id="on-own-object"),
    pytest.param("public", DOMAIN, "imported-name", [2, 3, 4], PROFILE, None, id="public"),
    pytest.param("special", DOMAIN, "imported-name", [5], PROFILE, None, id="special"),
    pytest.param("named Doc*", DOMAIN, "class", [6, 7], PROFILE, None, id="named"),
    pytest.param("top-level", DOMAIN, "function", [10], PROFILE, None, id="top-level"),
    pytest.param("forwards", DOMAIN, "function", [11, 12], PROFILE, None, id="forwards"),
    pytest.param("returns-an-attribute", DOMAIN, "function", [11], PROFILE, None, id="returns-an-attribute"),
    pytest.param("exception", DOMAIN, "class", [7], PROFILE, None, id="exception"),
    pytest.param("record", DOMAIN, "class", [8], PROFILE, None, id="record"),
    pytest.param("interface", PORTS, "class", [2], PROFILE, None, id="interface"),
    pytest.param("immutable", DOMAIN, "class", [9, 9], PROFILE, None,
                 id="immutable: a class the reader says is an immutable record"),
    pytest.param("receiver", DOMAIN, "callback", [16], PROFILE, None, id="receiver"),
    pytest.param("annotated-callable", DOMAIN, "callback", [15], PROFILE, None, id="annotated-callable"),
    pytest.param("directive", DOMAIN, "comment", [13], PROFILE, None, id="directive"),
    pytest.param("unreadable", UNREAD, "syntax-error", [0], PROFILE, None, id="unreadable"),
    pytest.param("unreadable", BROKEN, "syntax-error", [], PROFILE, None, id="unreadable: a file that does not parse"),
    pytest.param("no-statements", PORTS, "file", [0], PROFILE, None, id="no-statements"),
    pytest.param("no-statements", DOMAIN, "file", [], PROFILE, None, id="no-statements: a file with a real statement is not"),
    pytest.param("exceptions-only", ERRORS, "file", [0], PROFILE, None, id="exceptions-only"),
    pytest.param("exceptions-only", DOMAIN, "file", [], PROFILE, None, id="exceptions-only: classes of other kinds"),
    pytest.param("reported-at-import", DOMAIN, "use", [17], PROFILE, ("datetime", "datetime"), id="reported-at-import"),
    pytest.param("names-restricted", SERVICE, "import-into-app", [1, 2], NARROWED, None, id="names-restricted"),
    pytest.param("of-kind call", SERVICE, "call", [4, 5, 6], PROFILE, None, id="of-kind"),
    pytest.param("of-kind use", SERVICE, "call", [], PROFILE, None, id="of-kind: another kind"),
    pytest.param("target-placed", SERVICE, "call", [4, 5], PROFILE, None, id="target-placed"),
    pytest.param("target-inside-part", DOMAIN, "import-into-app", [2, 5, 5], PROFILE, None, id="target-inside-part"),
    pytest.param("target-in-own-part", DOMAIN, "import-into-app", [3], PROFILE, None, id="target-in-own-part"),
    pytest.param("target-in-own-tier", TEST, "import-into-app", [1], PROFILE, None, id="target-in-own-tier"),
    pytest.param("target-test", TEST, "import-into-tests", [4], PROFILE, None, id="target-test"),
    pytest.param("target-below fakes", TEST, "import-into-tests", [3], PROFILE, None, id="target-below"),
    pytest.param("target-allows-under built_by", WIRING, "construction", [2], BUILT, None, id="target-allows-under"),
    pytest.param("target-allows-under built_by", SERVICE, "construction", [], BUILT, None,
                 id="target-allows-under: a part not listed"),
])
def test_a_filter_holds_of_the_facts_it_says(text, file, kind, lines, profile, hit):
    assert [f.fact.line for f in found(file, kind, hit=hit) if question(condition(text))(f, FACTS, profile)] == lines


def test_a_negated_filter_holds_where_the_filter_does_not():
    assert [f.fact.line for f in found(DOMAIN, "import") if question(condition("not relative"))(f, FACTS, PROFILE)] == [
        1, 2, 4, 5]


def test_every_filter_the_vocabulary_publishes_has_a_row_and_the_engine_answers_it():
    rows = {param.values[0].split(" ")[0] for param in test_a_filter_holds_of_the_facts_it_says.pytestmark[0].args[1]}
    assert rows == {word.name for word in FILTERS} == set(filters.NAMES)


def test_the_interface_filter_holds_of_the_classes_the_reader_marks_whatever_their_bases():
    ports = source("modules/docs/application/ports/store.py",
                   classes=(Class(2, "Store", interface=True), Class(4, "Based", (("typing", "Protocol"),))))
    built = facts_of([ports], [], PROFILE, "app", "tests")
    read = built.files[0]
    assert [fact.line for fact in read.facts["class"]
            if question(condition("interface"))(Found(RULE, read, fact, None), built, PROFILE)] == [2]


def test_the_standard_filter_holds_of_the_imports_marked_by_the_standard_modules_of_the_language_read():
    read_as_brace = source("modules/docs/domain/doc.py", imp(1, "fs", "readFile", language=BRACE),
                           imp(2, "lodash", language=BRACE))
    built = facts_of([read_as_brace], [], PROFILE, "app", "tests")
    read = built.files[0]
    assert [fact.line for fact in read.facts["import"]
            if question(condition("standard"))(Found(RULE, read, fact, None), built, PROFILE)] == [1]
