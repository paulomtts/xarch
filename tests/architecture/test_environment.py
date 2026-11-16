"""Only bootstrap reads the environment, where review's key is: xarch's own profile forbids it to every other part, so
that `xarch check` fails a client, an adapter or a command that would read the key itself."""
from pathlib import Path

import xarch
from xarch.bootstrap.wiring import load_architecture

PROFILE = Path(xarch.__file__).parent.parent / "architecture.yaml"


def test_only_bootstrap_may_read_the_environment_where_review_s_key_is():
    architecture = load_architecture(str(PROFILE))
    reading = {("os", "environ"), ("os", "getenv")}
    assert {part for part in architecture.parts if not reading <= set(architecture.forbidden.get(part, ()))} == {
        "bootstrap"}
