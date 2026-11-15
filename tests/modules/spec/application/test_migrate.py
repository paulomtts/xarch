"""Use case: a profile in format 1 is converted to format 2 in a new folder, with the files it names, and never over a
file that exists."""
from pathlib import Path

import pytest

from tests.fakes.architecture_files import FakeArchitectureFiles
from tests.fakes.profile_output import FakeProfileOutput
from tests.fakes.settings import FakeSettings
from xarch.modules.spec.application.controller import SpecController
from xarch.modules.spec.application.services.architecture import ArchitectureService
from xarch.modules.spec.application.services.migration import MigrationService
from xarch.modules.spec.application.services.skeleton import SkeletonService
from xarch.modules.spec.contract import Migrated, MigratedFile, MigrateProfile, MigrationRefused

OLD = {"xarch": 1, "name": "small", "layout": {"core": {}, "cli": {}},
       "parts": {"core": {"path": "core", "role": "the rules"}, "cli": {"path": "cli", "role": "the commands"}},
       "rules": {"core": [], "cli": ["core"]}, "libraries": {"cli": ["typer"]}}
WITH_EXAMPLES = OLD | {
    "examples": {"rule": {"part": "core", "path": "core/rule.py", "file": "ex/rule.py", "note": "a pure rule"}},
    "docs": {"architecture.md": {"from": "architecture.md"}}}
TEXTS = {"ex/rule.py": "X = 1\n", "architecture.md": "see {{example:rule}} and {{example:nope}}\n", "other.bin": b"\x00\x01"}
OUT = Path("small-v2")


def controller(documents: dict, texts: dict | None = None, existing: set[Path] | None = None):
    output = FakeProfileOutput(existing)
    files = FakeArchitectureFiles({}, documents, texts or {})
    architectures = ArchitectureService(files)
    spec = SpecController(SkeletonService(FakeSettings(None, None, None), architectures), architectures,
                          MigrationService(files, output))
    return spec, output


@pytest.mark.parametrize("given, when, then", [
    pytest.param({"old.yaml": OLD}, MigrateProfile(Path("old.yaml")),
                 Migrated(Path("old-v2"), Path("old-v2/old.yaml"), (MigratedFile("old.yaml", None, 0),), (), (), False),
                 id="a profile with no files is converted into a new folder beside it, named for it"),
    pytest.param({"dir/old.yaml": OLD}, MigrateProfile(Path("dir/old.yaml"), Path("elsewhere")),
                 Migrated(Path("elsewhere"), Path("elsewhere/old.yaml"), (MigratedFile("old.yaml", None, 0),), (), (), False),
                 id="a profile is converted into the folder asked for"),
    pytest.param({"old.yaml": OLD}, MigrateProfile(Path("old.yaml"), dry_run=True),
                 Migrated(Path("old-v2"), Path("old-v2/old.yaml"), (MigratedFile("old.yaml", None, 0),), (), (), True),
                 id="a dry run reports the same and says it wrote nothing"),
    pytest.param({"old.yaml": OLD | {"xarch": 2}}, MigrateProfile(Path("old.yaml")),
                 MigrationRefused("old.yaml: already in format 2: nothing to migrate"),
                 id="a profile already in format 2 is refused"),
    pytest.param({"old.yaml": OLD | {"xarch": 3}}, MigrateProfile(Path("old.yaml")),
                 MigrationRefused("old.yaml: not a profile of format 1: it says `xarch: 3`"),
                 id="a profile of another format is refused"),
    pytest.param({}, MigrateProfile(Path("old.yaml")), MigrationRefused("old.yaml: cannot read the file: no such file"),
                 id="a file that cannot be read is refused with why"),
])
def test_migrate(given, when, then):
    spec, _ = controller(given)
    assert spec.migrate(when) == then


def test_the_converted_profile_and_nothing_else_is_written_for_a_profile_with_no_files():
    spec, output = controller({"old.yaml": OLD})
    spec.migrate(MigrateProfile(Path("old.yaml")))
    assert list(output.written) == [OUT.with_name("old-v2") / "old.yaml"]
    assert output.written[Path("old-v2/old.yaml")].decode().startswith("xarch: 2\nname: small\nlanguage: python\n")


def test_a_dry_run_writes_nothing():
    spec, output = controller({"old.yaml": WITH_EXAMPLES}, TEXTS)
    spec.migrate(MigrateProfile(Path("old.yaml"), dry_run=True))
    assert output.written == {}


def test_the_example_files_go_to_their_paths_and_the_templates_name_them_by_path():
    spec, output = controller({"old.yaml": WITH_EXAMPLES}, TEXTS)
    result = spec.migrate(MigrateProfile(Path("old.yaml")))
    assert output.written[Path("old-v2/examples/core/rule.py")] == b"X = 1\n"
    assert output.written[Path("old-v2/architecture.md")] == b"see {{example:core/rule.py}} and {{example:nope}}\n"
    assert result.files == (MigratedFile("old.yaml", None, 0),
                            MigratedFile("architecture.md", "architecture.md", 1),
                            MigratedFile("examples/core/rule.py", "ex/rule.py", 0))


def test_a_name_a_template_quotes_that_no_example_has_is_reported_and_left_as_written():
    spec, _ = controller({"old.yaml": WITH_EXAMPLES}, TEXTS)
    result = spec.migrate(MigrateProfile(Path("old.yaml")))
    assert any("architecture.md" in item and "nope" in item for item in result.by_hand)


def test_the_converted_profile_is_validated_before_anything_is_written_and_the_loader_s_problems_are_reported():
    broken = OLD | {"parts": OLD["parts"] | {"cli": {"path": "cli/../up", "role": "x"}}}
    spec, output = controller({"old.yaml": broken})
    result = spec.migrate(MigrateProfile(Path("old.yaml")))
    assert isinstance(result, MigrationRefused)
    assert result.reason.startswith("the converted profile does not load:")
    assert "parts.cli.path" in result.reason
    assert output.written == {}


def test_a_file_that_exists_is_never_overwritten_and_then_nothing_is_written_at_all():
    spec, output = controller({"old.yaml": WITH_EXAMPLES}, TEXTS, {Path("old-v2/architecture.md")})
    result = spec.migrate(MigrateProfile(Path("old.yaml")))
    assert result == MigrationRefused("old-v2/architecture.md already exists: migrate writes only new files; "
                                      "pass `--out <folder>` to write somewhere else")
    assert output.written == {}


def test_many_files_that_exist_are_named_three_at_a_time():
    document = WITH_EXAMPLES | {"files": {"AGENTS.md": {"from": "agents.md"}}}
    existing = {Path("old-v2") / name for name in ("old.yaml", "architecture.md", "examples/core/rule.py", "agents.md")}
    spec, _ = controller({"old.yaml": document}, TEXTS | {"agents.md": "x"}, existing)
    assert spec.migrate(MigrateProfile(Path("old.yaml"))) == MigrationRefused(
        "old-v2/old.yaml, old-v2/architecture.md, old-v2/agents.md and 1 more already exist: migrate writes only new "
        "files; pass `--out <folder>` to write somewhere else")
