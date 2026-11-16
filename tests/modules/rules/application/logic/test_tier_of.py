"""Where a file below the tests root sits, on hand-made profiles: its tier follows from the part its folder mirrors,
else from the file parts of its folder when they share a tier, else from a tier's folder; a fake has none."""
import pytest

from tests.modules.rules.builders import GUARD, INTEGRATION, PARTS, PROFILE, RENDERING, TWO, UNIT, profile, steps
from xarch.kernel.placement import EACH, Place
from xarch.modules.rules.application.logic import tier_of
from xarch.modules.rules.application.logic.tier_of import as_place, is_test
from xarch.profile_values.placement import Target
from xarch.profile_values.testing import Framework
from xarch.profile_values.tiers import CheckedTier as Tier

KERNEL_LOGIC = Tier("pure", (Target("kernel", sub=("logic",)),))
KERNEL = Tier("kernel", (Target("kernel"),))
MAIN = {**PARTS, "main": ("modules", "*", "application", "main.py")}
SPLIT = profile(parts=MAIN, tiers=(UNIT, INTEGRATION, Tier("entry", (Target("main", "own"),)), GUARD))
SHARED = profile(parts=MAIN, tiers=(UNIT, Tier("integration", (*INTEGRATION.subject, Target("main", "own")),
                                                 INTEGRATION.folder), GUARD))


@pytest.mark.parametrize("checked, path, expected", [
    pytest.param(PROFILE, "modules/docs/domain/test_doc.py",
                 tier_of.Tested(UNIT, "docs", ("modules", "docs"), True, False, ("domain",)),
                 id="a test in a part's folder has the first tier testing that part, in that instance"),
    pytest.param(PROFILE, "modules/docs/application/services/sub/test_svc.py",
                 tier_of.Tested(INTEGRATION, "docs", ("modules", "docs"), True, False, ("services",)),
                 id="a test below a part's folder mirrors that part"),
    pytest.param(PROFILE, "kernel/test_ids.py", tier_of.Tested(UNIT, None, ("kernel",), True, False, ("kernel",)),
                 id="a test of a part outside the instances has no instance and its top folder as its own"),
    pytest.param(PROFILE, "platform/test_sql.py", tier_of.Tested(None, None, ("platform",), True, False, ("platform",)),
                 id="a test of a part no tier tests has no tier, and still mirrors its part"),
    pytest.param(profile(tiers=(KERNEL_LOGIC, KERNEL)), "kernel/logic/test_text.py",
                 tier_of.Tested(KERNEL_LOGIC, None, ("kernel",), True, False, ("kernel",)),
                 id="a tier whose subject names a sub-path tests what lies below it"),
    pytest.param(profile(tiers=(KERNEL_LOGIC, KERNEL)), "kernel/test_ids.py",
                 tier_of.Tested(KERNEL, None, ("kernel",), True, False, ("kernel",)),
                 id="a tier whose subject names a sub-path does not test the rest of the part"),
    pytest.param(PROFILE, "modules/docs/application/test_publish.py",
                 tier_of.Tested(INTEGRATION, "docs", ("modules", "docs"), True, False, ("controller",)),
                 id="a test in the folder of a file part has that part's tier and mirrors it"),
    pytest.param(SHARED, "modules/docs/application/test_publish.py",
                 tier_of.Tested(SHARED.tiers[1], "docs", ("modules", "docs"), True, False, ("controller", "main")),
                 id="a test in a folder of file parts sharing one tier mirrors them all"),
    pytest.param(SPLIT, "modules/docs/application/test_publish.py",
                 tier_of.Tested(INTEGRATION, "docs", ("modules", "docs"), True, False, ()),
                 id="a test in a folder of file parts of different tiers is placed by its tier's folder"),
    pytest.param(PROFILE, "architecture/test_rules.py", tier_of.Tested(GUARD, None, ("architecture",), True, False, ()),
                 id="a test in a tier's folder that mirrors no part has that tier and no subject"),
    pytest.param(PROFILE, "architecture/rules/test_layers.py",
                 tier_of.Tested(GUARD, None, ("architecture",), True, False, ()),
                 id="so does a test in a folder below it"),
    pytest.param(PROFILE, "web/routes/test_docs.py", tier_of.Tested(RENDERING, None, ("web",), True, False, ("web",)),
                 id="a part's own tier wins over a tier's folder"),
    pytest.param(PROFILE, "scripts/test_seed.py", tier_of.Tested(None, None, ("scripts",), True, False, ()),
                 id="a test in no part and no tier folder has no tier"),
    pytest.param(profile(tiers=(Tier("odd", (), ()),)), "scripts/test_seed.py",
                 tier_of.Tested(None, None, ("scripts",), True, False, ()),
                 id="a tier with an empty folder places no test"),
    pytest.param(profile(tiers=(Tier("odd", (), ()),)), "test_seed.py",
                 tier_of.Tested(None, None, (), True, False, ()),
                 id="so a test at the tests root has no tier either"),
    pytest.param(PROFILE, "fakes/repo.py", tier_of.Tested(None, None, ("fakes",), False, True, ()),
                 id="a file under the fakes' folder is a fake, in no tier"),
    pytest.param(PROFILE, "fakes/modules/docs/test_repo.py", tier_of.Tested(None, None, ("fakes",), True, True, ()),
                 id="a fake is a fake whatever its name and folder below the fakes' folder"),
    pytest.param(PROFILE, "conftest.py", tier_of.Tested(None, None, (), False, False, ()),
                 id="a file at the tests root has no own folder"),
    pytest.param(PROFILE, "modules/docs/builders.py", tier_of.Tested(None, "docs", ("modules", "docs"), False, False, ()),
                 id="a helper of an instance has that instance as its own folder"),
    pytest.param(PROFILE, "modules/conftest.py", tier_of.Tested(None, None, ("modules",), False, False, ()),
                 id="a file directly in the each root is in no instance"),
    pytest.param(profile(fakes=None), "fakes/repo.py", tier_of.Tested(None, None, ("fakes",), False, False, ()),
                 id="without fakes in the profile no file is a fake"),
])
def test_tested(checked, path, expected):
    assert tier_of.tested(checked, steps(path)) == expected


@pytest.mark.parametrize("checked, name, expected", [
    pytest.param(PROFILE, "test_doc.py", True, id="a name the first pattern matches is a test"),
    pytest.param(PROFILE, "doc_test.py", True, id="a name the second pattern matches is a test"),
    pytest.param(PROFILE, "conftest.py", False, id="a name no pattern matches is not a test"),
    pytest.param(PROFILE, "test_doc.pyc", False, id="a pattern matches the whole name"),
    pytest.param(profile(framework=Framework(("check_*.py",), "check_*")), "test_doc.py", False,
                 id="the patterns are the profile's"),
    pytest.param(profile(framework=None), "test_doc.py", False, id="without a framework no file is a test"),
])
def test_is_test(checked, name, expected):
    assert is_test(checked, ("modules", name)) == expected


def test_an_empty_path_is_no_test():
    assert is_test(PROFILE, ()) is False


def test_a_test_speaks_from_its_instance():
    assert as_place("docs") == Place(EACH, "docs")


@pytest.mark.parametrize("path, tier, instance, own, parts", [
    pytest.param("plugins/seo/hooks/test_run.py", "plugin", "seo", ("plugins", "seo"), ("hooks",),
                 id="a test below the second repeating folder mirrors its part"),
    pytest.param("plugins/seo/test_manifest.py", "plugin", "seo", ("plugins", "seo"), ("manifest",),
                 id="a test in the folder of a file part of the second repeating folder"),
    pytest.param("modules/docs/domain/test_doc.py", "unit", "docs", ("modules", "docs"), ("domain",),
                 id="a test below the first repeating folder keeps its own"),
    pytest.param("plugins/seo/hooks/builders.py", "plugin", "seo", ("plugins", "seo"), ("hooks",),
                 id="a helper in the folder of a part of the second repeating folder"),
    pytest.param("plugins/seo/other/builders.py", None, "seo", ("plugins", "seo"), (),
                 id="a helper of an instance of the second repeating folder is its own folder's"),
])
def test_a_test_below_any_repeating_folder_takes_its_instance_and_its_own_folder(path, tier, instance, own, parts):
    where = tier_of.tested(TWO, steps(path))
    assert (where.tier.name if where.tier else None, where.instance, where.own, where.parts) == (
        tier, instance, own, parts)

