"""The proof of `xarch profile migrate`: profiles_v1/ holds the bundled web and cli profiles with every file they name, and
xarch's own profile, as they were written in format 1, frozen; and expected.tar.gz, what migrating each of them gave,
recorded once (a folder per profile, holding the profile and every file the migration wrote beside it) at a commit
where the migrated profiles loaded to the architecture of the profiles shipped then. Each frozen profile is migrated
for real into a folder, and what comes out is that recorded result, file for file. Editing a shipped profile never
touches this proof: the tests of the bundled profiles pin what they hold."""
import tarfile
from pathlib import Path

import pytest

from xarch.bootstrap.wiring import build_controllers, load_architecture
from xarch.modules.spec.contract import Migrated, MigrateProfile

FROZEN = Path(__file__).parent / "profiles_v1"
OWN_EXAMPLES = ("kernel/logic/test_placement.py", "modules/rules/application/test_check.py", "bootstrap/test_app.py",
                "architecture/test_self_check.py")


def migrated(name: str, tmp_path: Path) -> Migrated:
    """The frozen profile migrated into tmp_path/out; xarch's own names tests of this repository, so the files it names
    are made empty."""
    source = tmp_path / "v1"
    if name == "xarch":
        source.mkdir()
        (source / "xarch.yaml").write_text((FROZEN / "xarch.yaml").read_text())
        for relative in OWN_EXAMPLES:
            (source / "tests" / relative).parent.mkdir(parents=True, exist_ok=True)
            (source / "tests" / relative).write_text("")
    else:
        with tarfile.open(FROZEN / "architectures.tar.gz") as tar:
            tar.extractall(source, filter="data")
        source = source / "architectures"
    result = build_controllers().spec.migrate(MigrateProfile(source / f"{name}.yaml", tmp_path / "out"))
    assert isinstance(result, Migrated), result
    return result


def expected(name: str, tmp_path: Path) -> Path:
    """The folder the migration of the frozen profile name gave when it was recorded."""
    with tarfile.open(FROZEN / "expected.tar.gz") as tar:
        tar.extractall(tmp_path / "expected", filter="data")
    return tmp_path / "expected" / name


def files_of(folder: Path) -> dict[str, bytes]:
    return {path.relative_to(folder).as_posix(): path.read_bytes() for path in sorted(folder.rglob("*"))
            if path.is_file()}


@pytest.mark.parametrize("name", ["web", "cli", "xarch"])
def test_a_migrated_profile_is_the_recorded_result_file_for_file(name, tmp_path):
    done = migrated(name, tmp_path)
    assert files_of(done.profile.parent) == files_of(expected(name, tmp_path))


@pytest.mark.parametrize("name", ["web", "cli", "xarch"])
def test_the_recorded_result_of_a_migration_loads(name, tmp_path):
    recorded = expected(name, tmp_path)
    assert load_architecture(recorded / f"{name}.yaml").name == name


@pytest.mark.parametrize("name", ["web", "cli"])
def test_the_bundled_profiles_migrate_with_nothing_left_by_hand_and_nothing_changed(name, tmp_path):
    done = migrated(name, tmp_path)
    assert (done.by_hand, done.changes) == ((), ())


@pytest.mark.parametrize("name", ["web", "cli"])
def test_every_example_keeps_its_name_its_part_its_note_and_its_text_though_its_file_moved(name, tmp_path):
    old = load_architecture(migrated(name, tmp_path).profile)
    new = load_architecture(expected(name, tmp_path) / f"{name}.yaml")
    assert set(old.examples) == set(new.examples)
    for path, example in old.examples.items():
        shipped = new.examples[path]
        assert (example.part, example.path, example.note) == (shipped.part, shipped.path, shipped.note)
    for old_tier, new_tier in zip(old.tiers, new.tiers):
        assert [(x.path, x.note) for x in (old_tier.example, *old_tier.helpers) if x] == [
            (x.path, x.note) for x in (new_tier.example, *new_tier.helpers) if x]
