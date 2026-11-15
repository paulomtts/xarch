"""A profile at a glance: the folder tree and the table of what each part may import, as the generated docs show them."""
from __future__ import annotations

from xarch.modules.spec.application.logic.docs_template import fill
from xarch.modules.spec.domain.values import Architecture

SOURCE = "the view of a profile"


def view(architecture: Architecture) -> tuple[str, str]:
    """(the folder tree with the role of each folder, the table of what each part may import)."""
    return fill("{{tree}}", architecture, SOURCE), fill("{{rules_table}}", architecture, SOURCE)
