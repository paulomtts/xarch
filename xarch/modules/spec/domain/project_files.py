"""The project files beside the app: the files the architecture declares besides the docs, each filled from its template.

The architecture names every file (`files: {<path>: {from}}`, see architecture_file.py). A file is its template as it
stands, except that `{{app}}` is replaced by the name of the app folder, so a file that must find the app folder can
name it. Any other `{{...}}` is left alone: a template may hold code that has its own braces. The files are not part of
the app's structure: `check` does not require them.
"""
from __future__ import annotations

from collections.abc import Iterator, Mapping

from xarch.modules.spec.domain.errors import InvalidArchitecture
from xarch.modules.spec.domain.values import Architecture

APP_PLACEHOLDER = "{{app}}"
"""The one placeholder of a project file's template: the name of the app folder."""
EXAMPLE_APP = "app"
"""The app folder's name in the docs' example project, which shows an example file with its placeholder filled."""


def with_app(text: str, app: str) -> str:
    """The text with the placeholder replaced by the app folder's name."""
    return text.replace(APP_PLACEHOLDER, app)


def project_files(architecture: Architecture, templates: Mapping[str, str], app: str,
                  source: str) -> Iterator[tuple[tuple[str, ...], str]]:
    """Yield (path below the folder holding the app, text) for every file the architecture declares, in its order.

    templates is the text of each template file, by the name the architecture gives it; source names the architecture
    file in a problem. Raises InvalidArchitecture if a file would lie inside the app folder, whose name is app.
    """
    inside = [f"files.{'/'.join(file.path)}: lies inside the app folder '{app}'"
              for file in architecture.files if file.path[0] == app]
    if inside:
        raise InvalidArchitecture(source, inside)
    for file in architecture.files:
        yield file.path, with_app(templates[file.source], app)
