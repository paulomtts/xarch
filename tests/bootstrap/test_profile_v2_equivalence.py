"""The proof of `xarch profile migrate`: profiles_v1/ holds the bundled web and cli profiles with every file they name, and
xarch's own profile, as they were written in format 1, frozen; and expected.tar.gz, what migrating each of them gave,
recorded once (a folder per profile, holding the profile and every file the migration wrote beside it). Each frozen
profile is migrated for real into a folder, and what comes out is that recorded result, file for file; what the frozen
profile says of its examples is what the migrated one says of them; and the migrated profile makes its docs. Editing a
shipped profile never touches this proof: the tests of the bundled profiles pin what they hold.

The result was recorded at 6940e9f, the parent of 88c7dbb, where the migrated profiles loaded to the architecture of
the profiles shipped then. Record it again only when a change to the migration is meant to change what it writes: in
that change, migrate each frozen profile with the code of the change (`xarch profile migrate
tests/bootstrap/profiles_v1/xarch.yaml --out <folder>/xarch`, and the same for web and cli unpacked from
architectures.tar.gz, with the files xarch's own names made empty as migrated() makes them), pack the three folders
as expected.tar.gz, and list in the commit every file whose bytes changed and why. Never record it to make a failing
test pass."""
import tarfile
from pathlib import Path

import pytest
import yaml

from xarch.bootstrap.wiring import build_controllers, build_spec, load_architecture
from xarch.modules.spec.contract import Docs, Migrated, MigrateProfile

FROZEN = Path(__file__).parent / "profiles_v1"
OWN_EXAMPLES = ("kernel/logic/test_placement.py", "modules/rules/application/test_check.py", "bootstrap/test_app.py",
                "architecture/test_self_check.py")


def frozen(name: str, tmp_path: Path) -> Path:
    """The folder of the bundled profile name as it was written in format 1, unpacked below tmp_path."""
    with tarfile.open(FROZEN / "architectures.tar.gz") as tar:
        tar.extractall(tmp_path / "frozen", filter="data")
    return tmp_path / "frozen" / "architectures"


def v1_note(note: str) -> str:
    """A note of a tier's example as format 1 wrote it, in parentheses after a space, as format 2 writes it."""
    return note.strip().removeprefix("(").removesuffix(")")


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
    source = frozen(name, tmp_path)
    written = yaml.safe_load((source / f"{name}.yaml").read_text())
    done = migrated(name, tmp_path)
    folder, architecture = done.profile.parent, load_architecture(done.profile)
    old = {example["path"]: (example["part"], example.get("note", ""), (source / example["file"]).read_text())
           for example in written["examples"].values()}
    new = {path: (example.part, example.note, (folder / example.file).read_text())
           for path, example in architecture.examples.items() if path in old}
    assert new == old
    tiers = {tier.name: tier for tier in architecture.tiers}
    for tier in written["tiers"]:
        moved = tiers[tier["name"]]
        assert [(x["path"], v1_note(x.get("note", "")), (source / x["file"]).read_text())
                for x in (tier.get("example"), *tier.get("helpers", ())) if x] == [
            ("/".join(x.path), x.note, (folder / x.file).read_text()) for x in (moved.example, *moved.helpers) if x]


@pytest.mark.parametrize("name", ["web", "cli"])
def test_a_migrated_profile_makes_every_doc_its_frozen_profile_declares_with_every_template_filled(name, tmp_path):
    written = yaml.safe_load((frozen(name, tmp_path) / f"{name}.yaml").read_text())
    docs = build_spec().docs(str(migrated(name, tmp_path).profile))
    assert isinstance(docs, Docs), docs
    assert ([doc.path for doc in docs.files], [doc.path for doc in docs.files if "{{" in doc.template]) == (
        [tuple(path.split("/")) for path, entry in written["docs"].items() if "from" in entry], [])
