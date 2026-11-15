"""The forbidden check on a throwaway web project, as the bundled profile lists it: the pure parts may not read the
clock or do I/O by name, and neither may the unit tests of those parts."""
import pytest

from tests.bootstrap.project import problems

DOMAIN = "modules/docs/domain/document.py"


@pytest.mark.parametrize("path, body, problem", [
    (DOMAIN, "from datetime import datetime as dt\n\ndef stamp():\n    return dt.now()\n",
     f"app/{DOMAIN}:4: domain/ of modules/docs may not use datetime.datetime.now (parts.domain.forbidden)"),
    (DOMAIN, "import datetime\n\nTODAY = datetime.date.today()\n",
     f"app/{DOMAIN}:3: domain/ of modules/docs may not use datetime.date.today (parts.domain.forbidden)"),
    (DOMAIN, "def load(path):\n    return open(path).read()\n",
     f"app/{DOMAIN}:2: domain/ of modules/docs may not use builtins.open (parts.domain.forbidden)"),
    ("modules/docs/application/logic/rule.py", "import subprocess\n",
     "app/modules/docs/application/logic/rule.py:1: logic/ of modules/docs may not import subprocess "
     "(parts.logic.forbidden)"),
    ("kernel/clock.py", "from time import time\n",
     "app/kernel/clock.py:1: kernel/ may not import time.time (parts.kernel.forbidden)"),
    (DOMAIN, "def show(print):\n    print('x')\n", None),
    ("platform/clock.py", "from datetime import datetime\n\ndef now():\n    return datetime.now()\n", None),
])
def test_a_pure_part_may_not_use_what_the_bundled_profile_forbids_it(tmp_path, path, body, problem):
    assert problems(tmp_path, app={path: body}) == ([problem] if problem else [])


def test_a_unit_test_of_a_pure_part_is_held_to_its_list(tmp_path):
    body = "from app.modules.docs.domain.document import Document\nimport time\n\ndef test_x():\n    time.time()\n"
    assert problems(tmp_path, tests={"modules/docs/domain/test_document.py": body}) == [
        "tests/modules/docs/domain/test_document.py:5: a test of domain/ (unit tier) may not use time.time "
        "(parts.domain.forbidden; tiers.unit.apply_forbidden)"]
