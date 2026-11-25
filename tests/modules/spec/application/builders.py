"""Builders for the use cases of the spec module around fakes: its controller with every service."""
from __future__ import annotations

from typing import Any

from tests.fakes.architecture_files import FakeArchitectureFiles
from tests.fakes.example_reader import FakeExampleReader
from tests.fakes.profile_output import FakeProfileOutput
from tests.fakes.runtime import FakeRuntime
from tests.fakes.settings import FakeSettings
from tests.modules.spec.application.helpers import controller
from tests.modules.spec.languages import RUNTIME
from xarch.kernel.source import CommentSpan, Import, Unparsable

TESTING = {"files": ["test_*.py"], "declared": [{"function": "test_*"}]}
BASE = {"name": "base", "testing": TESTING,
        "parts": {"core/": {"role": "the rules"},
                  "api/": {"role": "the handlers", "imports": {"may": ["parts.core"]}}},
        "docs": {"pages": {"a.md": {"from": "docs/a.md"}}}, "files": {"AGENTS.md": "agents.md"}}
BASE_TEXT = "# the base\nname: base\ntesting: x\n"
TEXTS = {"base.yaml": BASE_TEXT, "docs/a.md": "page\n", "agents.md": "agents\n"}


def spec_controller(bundled: dict[str, Any] | None = None, files: dict[str, Any] | None = None,
                    texts: dict[str, str | bytes] | None = None, existing: set | None = None,
                    settings: FakeSettings | None = None, presets: dict[str, Any] | None = None,
                    languages: dict[str, Any] | None = None, runtime: FakeRuntime = RUNTIME,
                    reads: dict[str, tuple[Import, ...] | Unparsable] | None = None,
                    keys: Any = None, comments: dict[str, tuple[CommentSpan, ...] | Unparsable] | None = None):
    port = FakeArchitectureFiles({"base": BASE} if bundled is None else bundled, files, TEXTS | (texts or {}),
                                 presets if presets is not None else {"pytest": TESTING}, languages, keys)
    output = FakeProfileOutput(existing)
    return controller(port, settings, output, runtime=runtime, reader=FakeExampleReader(reads, comments)), output
