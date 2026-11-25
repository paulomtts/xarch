"""`layers` through the real app: a chain an import of a type only breaks is refused by `profile check`, unless the
chain says `types_only: true`."""
from pathlib import Path

import pytest
from typer.testing import CliRunner

from xarch.bootstrap.app import app

runner = CliRunner()

PARTS = """\
name: rings
parts:
  services/:
    role: the use cases
    imports: {may: [{parts.controller: types_only}]}
  controller/:
    role: the facade
    imports: {may: [parts.services]}
"""


@pytest.mark.parametrize("layers, code", [
    pytest.param("layers:\n  inward: [services, controller]\n", 1, id="strict layering, the default"),
    pytest.param("layers:\n  inward: {parts: [services, controller], types_only: true}\n", 0,
                 id="an import of a type only allowed"),
])
def test_a_chain_says_whether_an_import_of_a_type_only_breaks_it(tmp_path, monkeypatch, layers, code):
    monkeypatch.chdir(tmp_path)
    Path("rings.yaml").write_text(PARTS + layers)
    result = runner.invoke(app, ["profile", "check", "rings.yaml"])
    assert result.exit_code == code
    assert ("layers.inward: 'services' imports 'controller', which is outward of it" in result.stdout) is (code == 1)
