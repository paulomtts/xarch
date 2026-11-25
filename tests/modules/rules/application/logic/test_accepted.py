"""The imports a part accepts although its imports.may does not allow them (parts.<part>.imports.accepted), on
hand-made source files: each import an entry accepts is named, and an entry that accepts nothing any more is a
may-import violation."""
import pytest

from tests.modules.rules.builders import imp, profile, source
from xarch.kernel.violations import Violation
from xarch.modules.rules.application.logic.accepted import ratchet
from xarch.modules.rules.application.logic.facts import facts_of
from xarch.modules.rules.domain.published import AcceptedEdge
from xarch.profile_values.placement import AcceptedImport

DOMAIN = "modules/docs/domain/doc.py"
KEY = "parts.domain.imports.accepted"
WHY = "the document reads the store until its port exists"


def entry(target: str = "platform/db.py", name: str = "") -> AcceptedImport:
    return AcceptedImport(tuple(DOMAIN.split("/")), tuple(target.split("/")), name, WHY,
                          f"{target}:{name}" if name else target)


def accepting(*imports, entries=(entry(),)):
    """What the ratchet comes to for the domain file importing imports, beside platform/db.py and kernel/ids.py."""
    files = [source(DOMAIN, *imports), source("platform/db.py"), source("kernel/ids.py")]
    checked = profile(imports_accepted={"domain": tuple(entries)})
    return ratchet(facts_of(files, [], checked, "app"), checked)


@pytest.mark.parametrize("imports, entries, accepted", [
    pytest.param((imp(3, "app.platform", "db"),), (entry(),), [3], id="an import of the file the entry names"),
    pytest.param((imp(3, "app.platform.db", "connect", "close"),), (entry(name="connect"),), [3],
                 id="a name the entry names"),
    pytest.param((imp(3, "app.platform.db", "connect"), imp(5, "app.platform.db", "close")),
                 (entry(name="connect"),), [3], id="only the name the entry names"),
    pytest.param((imp(3, "app.platform", "db"), imp(4, "app.platform.db", "close")), (entry(),), [3, 4],
                 id="every import of what the entry names, by line"),
])
def test_each_import_an_entry_accepts_is_named(imports, entries, accepted):
    found = accepting(*imports, entries=entries)
    assert found.stale == ()
    assert [item.line for item in found.accepted] == accepted
    assert {item.file for item in found.accepted} == {f"app/{DOMAIN}"}


def test_an_accepted_import_says_its_part_its_entry_and_why():
    assert accepting(imp(3, "app.platform", "db")).accepted == (
        AcceptedEdge(f"app/{DOMAIN}", 3, "domain", "platform/db.py", WHY),)


@pytest.mark.parametrize("imports, entries, message", [
    pytest.param((), (entry(),), f"{DOMAIN} no longer imports platform/db.py, which {KEY} accepts ({KEY})",
                 id="the file no longer imports what the entry names"),
    pytest.param((imp(3, "app.platform.db", "close"),), (entry(name="connect"),),
                 f"{DOMAIN} no longer imports platform/db.py:connect, which {KEY} accepts ({KEY})",
                 id="the file no longer takes the name the entry names"),
    pytest.param((imp(3, "app.kernel", "ids"),), (entry("kernel/ids.py"),),
                 f"{DOMAIN} imports kernel/ids.py, which parts.domain.imports.may allows: {KEY} accepts nothing "
                 f"({KEY})", id="imports.may allows the import"),
])
def test_an_entry_that_accepts_nothing_is_a_may_import_violation(imports, entries, message):
    found = accepting(*imports, entries=entries)
    assert found.accepted == ()
    assert found.stale == (Violation(f"app/{DOMAIN}", 0, message, "may-import", f"drop the entry of {DOMAIN} from {KEY}"),)


def test_an_entry_whose_file_is_gone_is_a_may_import_violation():
    gone = AcceptedImport(("modules", "docs", "domain", "gone.py"), ("platform", "db.py"), "", WHY, "platform/db.py")
    assert accepting(entries=(gone,)).stale == (Violation(
        "app/modules/docs/domain/gone.py", 0, f"modules/docs/domain/gone.py is no file of the app, which {KEY} accepts "
        f"an import of ({KEY})", "may-import",
        f"drop the entry of modules/docs/domain/gone.py from {KEY}, or name the file as it is now"),)
