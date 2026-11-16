"""Use case: the project docs of a profile, each filled from its template, which `init` writes."""
import pytest

from tests.fakes.architecture_files import FakeArchitectureFiles
from tests.modules.spec.application.helpers import controller
from xarch.modules.spec.contract import DocFile, Docs, ProfileRefused

LAYERED = {"xarch": 2, "name": "layered", "parts": {"src": {"path": "src", "role": "code"}},
           "docs": {"entry": "src", "pages": {"notes.md": "notes.md"}}}
BAD = LAYERED | {"docs": {"entry": "src", "pages": {"notes.md": "bad.md"}}}
SPEC = controller(FakeArchitectureFiles({"cli": LAYERED, "bad": BAD, "broken": {"xarch": 2, "name": "broken"}},
                                        texts={"notes.md": "# Notes\n", "bad.md": "{{nothing}}\n"}))
UNTYPED = controller(FakeArchitectureFiles({"cli": LAYERED}, texts={"notes.md": "# Notes\n"}, file_types={"sql": {}}))


@pytest.mark.parametrize("given, when, then", [
    pytest.param(SPEC, "cli", Docs(("docs", "project"), (DocFile(("notes.md",), "# Notes\n"),)),
                 id="each doc is its template filled from the profile"),
    pytest.param(SPEC, "broken", ProfileRefused("broken: missing `parts`"),
                 id="a profile that does not load is refused with why"),
    pytest.param(UNTYPED, "cli", ProfileRefused("presets/format/file_types.yaml: sql: must be a dot and a name, such as "
                                                ".sql"),
                 id="the docs are refused with why when the data file of file types does not load"),
])
def test_docs(given, when, then):
    assert given.docs(when) == then


def test_a_template_that_cannot_be_filled_is_refused_naming_it():
    refused = SPEC.docs("bad")
    assert isinstance(refused, ProfileRefused) and refused.reason.startswith("bad.md: unknown placeholder {{nothing}}")
