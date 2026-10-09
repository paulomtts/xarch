"""The console entry point: the typer app with every controller wired in."""
from __future__ import annotations

from xarch.bootstrap.wiring import build_controllers
from xarch.cli.app import build

_controllers = build_controllers()
app = build(_controllers.rules, _controllers.layout, _controllers.scaffold, _controllers.spec)
