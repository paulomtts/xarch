"""Which names found on the disk can be an instance of a repeating folder, or the text a counterpart's placeholder
binds: a name of the language, and no private one, so that a cache or private folder never is."""
from __future__ import annotations

from xarch.kernel.logic.names import is_name, is_private_name
from xarch.modules.layout.domain.structure import Naming


def is_instance_name(name: str, naming: Naming) -> bool:
    """Whether a name found on the disk is a name of the language, and no private one."""
    return is_name(name, naming.names) and not is_private_name(name, naming.private)
