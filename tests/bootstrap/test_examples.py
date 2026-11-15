"""The example check through the wiring: the bundled examples obey their architectures' rules, and a custom
architecture's can be checked."""
from pathlib import Path

import pytest

from xarch.bootstrap.wiring import build_architectures


def test_the_bundled_examples_obey_their_architectures_rules():
    service = build_architectures()
    for profile in service.bundled():
        assert service.check_examples(profile) == (), profile


CUSTOM = """\
xarch: 2
name: layered
parts:
  api:   {path: "src/<module>/api", role: handlers, may_import: [store]}
  store: {path: "src/<module>/store", role: database access}
docs:
  entry: api
  pages:
    architecture.md: {from: layered.md}
  examples: [examples]
"""


def write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path


@pytest.mark.parametrize("code, problems", [
    ("from app.src.billing.store import Repo\n", ()),
    ("from app.src.tax.store import Repo\n",
     ("example (src/billing/api/handler.py): imports app.src.tax.store which api may not import (parts.api.may_import)",)),
])
def test_a_custom_architecture_can_be_checked(tmp_path, code, problems):
    """Not checked unless asked."""
    write(tmp_path / "examples" / "src/billing/api/handler.py", code)
    write(tmp_path / "layered.md", "{{example:src/billing/api/handler.py}}\n")
    path = write(tmp_path / "layered.yaml", CUSTOM)
    service = build_architectures()
    assert service.check_examples(path) == problems
    texts = {"/".join(f.path): f.template for f in service.docs(path).files}
    assert texts["architecture.md"] == f"```python\n# src/billing/api/handler.py\n{code}```\n"
