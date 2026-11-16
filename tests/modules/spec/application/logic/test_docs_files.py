"""The project docs a hand-made architecture declares: each file its template filled, in the order declared, and no
file for a folder."""
from xarch.modules.spec.application.logic.docs_files import doc_files
from xarch.modules.spec.domain.published import DocFile
from xarch.modules.spec.domain.values import Architecture, Doc, Part

ARCHITECTURE = Architecture("small", {"core": {}}, {"core": Part("core", ("core",), "the rules", "Is it a rule?")},
                            {"core": ()}, docs=(Doc(("statement.md",), "statement.md"), Doc(("adrs",), None, "decisions"),
                                                Doc(("adrs", "0000-template.md"), "adr.md")))


def test_each_file_is_its_template_filled_in_the_order_declared_and_a_folder_is_no_file():
    templates = {"statement.md": "# the parts\n\n{{litmus:core}}\n", "adr.md": "# a decision\n"}
    assert list(doc_files(ARCHITECTURE, templates)) == [
        DocFile(("statement.md",), "# the parts\n\n> [!TIP]\n> **Litmus test.** Is it a rule?\n"),
        DocFile(("adrs", "0000-template.md"), "# a decision\n")]
