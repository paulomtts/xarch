"""The skeleton of docs/project/architecture.md section 1, defined once as data, per profile.

A dict is a package directory holding its entries; None is a file. The scaffold builds from these trees,
the layout rules require them and the import rules place code by them, so the three cannot drift apart.

A profile names the entry-point folder (the part that drives the modules) and what it holds: `cli/` for a
command-line app, `web/` for a web app. Everything else is the same in every profile.
"""
from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass

from xarch.modules.spec.domain.errors import UnknownProfile
from xarch.modules.spec.domain.values import Configured

Tree = dict[str, "Tree | None"]


@dataclass(frozen=True)
class Profile:
    entry_point: str               # the folder that drives the modules
    entry_tree: Tree               # what it holds
    driver_proves: str             # what a test of the entry point proves, for testing.md
    driver_test: str               # the example driver test in testing.md: drives the entry point with a faked controller


PROFILES: dict[str, Profile] = {
    "cli": Profile("cli", {"commands": {}}, "argument parsing, exit codes and terminal output", """\
def test_publish_prints_the_title_and_exits_zero(runner):
    controller = Mock(publish=lambda cmd: Published(DocumentView(cmd.id, "Hello", True)))
    result = runner.invoke(cli_app(controller), ["documents", "publish", str(A_DOCUMENT_ID)])
    assert result.exit_code == 0 and "Published Hello" in result.output
"""),
    "web": Profile("web", {"routes": {}, "i18n": {}, "ui": {}}, "routing, status codes and rendered output", """\
def test_publish_renders_the_title_and_answers_200(client):
    controller = Mock(publish=lambda cmd: Published(DocumentView(cmd.id, "Hello", True)))
    response = client(controller).post(f"/documents/{A_DOCUMENT_ID}/publish")
    assert response.status_code == 200 and "Hello" in response.text
"""),
}

DEFAULT_PROFILE = "cli"

MODULE_TREE: Tree = {
    "contract": {},
    "domain": {},
    "application": {"controller.py": None, "services": {}, "logic": {}, "ports": {}},
    "adapters": {},
}


def profile(name: str, source: Configured | None = None) -> Profile:
    if name not in PROFILES:
        raise UnknownProfile(name, PROFILES, source.source if source else None)
    return PROFILES[name]


def choose(override: str | None, configured: Configured | None) -> str:
    """The profile in force: an explicit override, else the configured one, else the default."""
    if override is not None:
        profile(override)
        return override
    if configured is not None:
        profile(configured.name, configured)
        return configured.name
    return DEFAULT_PROFILE


def top_level_tree(name: str) -> Tree:
    chosen = profile(name)
    return {
        "bootstrap": {"migrations": {}},
        "kernel": {"logic": {}},
        "modules": {},
        "platform": {},
        chosen.entry_point: chosen.entry_tree,
    }


def walk(tree: Tree, prefix: tuple[str, ...] = ()) -> Iterator[tuple[tuple[str, ...], bool, bool]]:
    """Yield (path, is_dir, is_leaf) for every entry, parents before children.

    A leaf is a file, or a directory that holds nothing in the spec.
    """
    for name, sub in tree.items():
        path = prefix + (name,)
        yield path, sub is not None, not sub
        if sub:
            yield from walk(sub, path)
