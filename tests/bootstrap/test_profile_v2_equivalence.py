"""The proof of `xarch profile migrate`: profiles_v1/ holds the bundled web and cli profiles with every file they name, and
xarch's own profile, as they were written in format 1, frozen. Each is migrated for real into a folder, and what comes
out loads to the architecture of the profile shipped now in format 2, but for the fields the tests below name, each with
its reason. The docs the migrated profiles generate are the docs of the shipped ones, but for one template's prose."""
import tarfile
from dataclasses import replace
from pathlib import Path

import pytest

import xarch
from xarch.bootstrap.wiring import build_controllers, build_spec, load_architecture
from xarch.modules.spec.contract import Migrated, MigrateProfile
from xarch.modules.spec.domain.values import (
    Architecture,
    DeadCode,
    NoDuplicates,
    NoTwins,
    PassThrough,
    PrivateImports,
)

FROZEN = Path(__file__).parent / "profiles_v1"
CWD = {("pathlib", "Path", "cwd"), ("pathlib", "Path", "absolute"), ("os", "getcwd"), ("os", "path", "abspath"),
       ("os", "path", "realpath"), ("pathlib", "Path", "resolve"), ("pathlib", "Path", "home"),
       ("pathlib", "Path", "expanduser"), ("os", "path", "expanduser"), ("os", "getcwdb"), ("os", "chdir"),
       ("", "absolute()"), ("", "resolve()"), ("", "expanduser()")}
"""The names that read the working directory or resolve a path on disk, added to the `pure` lists and in the
`ambient` list after format 1."""
OWN = Path(xarch.__file__).parent.parent / "architecture.yaml"
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


def both(name: str, tmp_path: Path) -> tuple[Architecture, Architecture]:
    done = migrated(name, tmp_path)
    return load_architecture(done.profile), load_architecture(OWN if name == "xarch" else name)


def comparable(architecture: Architecture) -> Architecture:
    """Without what differs by design: where the example files sit (the shipped profiles keep two folders of examples, a
    migration one), the tiers' examples and subjects' order, the order of the parts, what the profile is based on, and
    what format 1 never had: each part's `must_import`, `holds`, `types_only`, `no_callbacks`, `names` and `built_by`,
    a tier's `must_import`, a name pattern on a target, the names that read the working directory in a `forbidden`
    list (and a list of nothing else), the names `reserved` holds and the parts' libraries that list them, and the
    guards no-duplicates, no-twins, dead-code, pass-through and private-imports; and `kernel/logic/`, a folder of
    `kernel/` in format 1 and a part of its own now, which every part that may import `kernel/` may import too, as
    the part it was a folder of (see kernel_logic); and what changed when services came to assemble what a use case
    hands out, and the part xarch's own profile gained for the values spec builds and rules reads in full (see
    assembled)."""
    architecture = assembled(kernel_logic(architecture))
    tiers = tuple(replace(tier, subject=tuple(sorted(tier.subject, key=lambda s: s.part)), example=None, helpers=(),
                          must_import=()) for tier in architecture.tiers)
    parts = {name: replace(part, must_import=(), holds="", types_only=(), no_callbacks=False, names=(), built_by=(),
                           shared=None)
             for name, part in architecture.parts.items()}
    guards = tuple(g for g in architecture.guards
                   if not isinstance(g, (NoDuplicates, NoTwins, DeadCode, PassThrough, PrivateImports)))
    rules = {name: tuple(replace(t, names="") for t in targets) for name, targets in architecture.rules.items()}
    kept = {name: tuple(n for n in names if n not in CWD) for name, names in architecture.forbidden.items()}
    forbidden = {name: names for name, names in kept.items() if names}
    libraries = None if architecture.libraries is None else {
        name: tuple(p for p in packages if p not in architecture.reserved)
        for name, packages in architecture.libraries.items()}
    return replace(architecture, tiers=tiers, examples={}, files=(), placement=(), based_on="", parts=parts,
                   guards=guards, rules=rules, forbidden=forbidden, reserved={}, libraries=libraries)


LOGIC = "kernel-logic"
REWORDED = ("domain", "services", "controller", "contract", LOGIC)
"""The parts whose role and litmus were reworded when services came to assemble what a use case hands out and a
module came to hand out a value as it is from domain/published.py."""
LITMUS_ADDED = ("reports",)
"""The parts that gained a litmus after format 1, saying what they may decide."""
PUBLISHED = ("published",)
VALUES = "profile-values"


def assembled(architecture: Architecture) -> Architecture:
    """The architecture without the role and litmus of the parts REWORDED, the litmus of LITMUS_ADDED, without the
    target the contract gained for the values a module hands out as they are (domain/published), and without the
    part VALUES and every target naming it, which format 1 never had."""
    parts = {name: replace(part, role="", litmus="") if name in REWORDED else
             replace(part, litmus="") if name in LITMUS_ADDED else part
             for name, part in architecture.parts.items() if name != VALUES}
    rules = {name: tuple(t for t in targets if not (t.part == "domain" and t.sub == PUBLISHED) and t.part != VALUES)
             for name, targets in architecture.rules.items() if name != VALUES}
    forbidden = {name: names for name, names in architecture.forbidden.items() if name != VALUES}
    tiers = tuple(replace(tier, subject=tuple(s for s in tier.subject if s.part != VALUES)) for tier in architecture.tiers)
    notes = {path: note for path, note in architecture.notes.items()
             if VALUES not in architecture.parts or path != architecture.parts[VALUES].path}
    layout = {name: sub for name, sub in architecture.layout.items()
              if VALUES not in architecture.parts or (name,) != architecture.parts[VALUES].path}
    libraries = None if architecture.libraries is None else {
        name: packages for name, packages in architecture.libraries.items() if name != VALUES}
    return replace(architecture, parts=parts, rules=rules, forbidden=forbidden, tiers=tiers, notes=notes, layout=layout,
                   libraries=libraries)



def kernel_logic(architecture: Architecture) -> Architecture:
    """The architecture with the part kernel-logic taken back into kernel: no such part, no target naming it, its
    forbidden list, its libraries and its tier's subject gone, its folder a folder of kernel's again, and neither its
    note as a folder nor kernel's role compared, which says kernel no longer holds the shared rules."""
    if LOGIC not in architecture.parts:
        notes = {path: note for path, note in architecture.notes.items() if path != ("kernel", "logic")}
        parts = {name: replace(part, role="") if name == "kernel" else part for name, part in architecture.parts.items()}
        return replace(architecture, notes=notes, parts=parts)
    parts = {name: part for name, part in architecture.parts.items() if name != LOGIC}
    rules = {name: tuple(t for t in targets if t.part != LOGIC) for name, targets in architecture.rules.items()
             if name != LOGIC}
    forbidden = {name: names for name, names in architecture.forbidden.items() if name != LOGIC}
    tiers = tuple(replace(tier, subject=tuple(s for s in tier.subject if s.part != LOGIC)) for tier in architecture.tiers)
    libraries = None if architecture.libraries is None else {
        name: packages for name, packages in architecture.libraries.items() if name != LOGIC}
    parts["kernel"] = replace(parts["kernel"], role="")
    notes = {path: note for path, note in architecture.notes.items() if path != architecture.parts[LOGIC].path}
    return replace(architecture, parts=parts, rules=rules, forbidden=forbidden, tiers=tiers, libraries=libraries,
                   notes=notes)


@pytest.mark.parametrize("name", ["web", "cli", "xarch"])
def test_a_migrated_profile_loads_to_the_architecture_of_the_shipped_one(name, tmp_path):
    old, new = both(name, tmp_path)
    assert comparable(old) == comparable(new)


@pytest.mark.parametrize("name", ["web", "cli"])
def test_the_bundled_profiles_migrate_with_nothing_left_by_hand_and_nothing_changed(name, tmp_path):
    done = migrated(name, tmp_path)
    assert (done.by_hand, done.changes) == ((), ())


@pytest.mark.parametrize("name", ["web", "cli"])
def test_every_example_keeps_its_name_its_part_its_note_and_its_text_though_its_file_moved(name, tmp_path):
    old, new = both(name, tmp_path)
    assert set(old.examples) == set(new.examples)
    for path, example in old.examples.items():
        shipped = new.examples[path]
        part = "kernel" if shipped.part == LOGIC else shipped.part
        assert (example.part, example.path, example.note) == (part, shipped.path, shipped.note)
    for old_tier, new_tier in zip(old.tiers, new.tiers):
        assert [(x.path, x.note) for x in (old_tier.example, *old_tier.helpers) if x] == [
            (x.path, x.note) for x in (new_tier.example, *new_tier.helpers) if x]


@pytest.mark.parametrize("name", ["web", "cli"])
def test_the_docs_of_a_migrated_profile_are_the_docs_of_the_shipped_one_but_for_the_prose_of_one_template(name, tmp_path):
    """The shipped testing.md was also reworded where it names keys of format 1, and lists the checks format 1 never
    had; architecture.md shows the name pattern format 1 could not write on what contract/ imports. A migration moves
    keys, not prose."""
    done = migrated(name, tmp_path)
    old, new = build_spec().docs(str(done.profile)), build_spec().docs(str(name))
    assert [doc.path for doc in old.files] == [doc.path for doc in new.files]
    assert [doc.path for doc, other in zip(old.files, new.files) if doc != other] == [("architecture.md",),
                                                                                       ("testing.md",)]


def test_xarch_s_own_profile_differs_in_what_the_shipped_one_chose_to_change(tmp_path):
    """The shipped one is ordered as the cli profile is and says it is based on it; it drops the example tests of this
    repository, which the migration keeps as examples; and it states the allowance of its guard tier as the migration
    does."""
    old, new = both("xarch", tmp_path)
    assert (old.based_on, new.based_on) == ("", "cli")
    assert sorted(old.parts) == sorted(assembled(kernel_logic(new)).parts) and old.placement != new.placement
    assert sorted(old.examples) == sorted(f"tests/{relative}" for relative in OWN_EXAMPLES) and new.examples == {}
    assert old.tiers[3].may_import == new.tiers[3].may_import
    assert [tier.example is None for tier in old.tiers] == [False] * 4
