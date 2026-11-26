"""Which names found on the disk can be an instance of a repeating folder, or the text a counterpart's placeholder
binds: a name of the language, and no private one, so that a cache or private folder never is; and which folders found
in a repeating folder's own folder are its instances: such a name that the layout does not write there by name."""
from __future__ import annotations

from collections.abc import Collection

from xarch.kernel.logic.names import is_name, is_private_name
from xarch.modules.layout.domain.structure import Naming


def is_instance_name(name: str, naming: Naming) -> bool:
    """Whether a name found on the disk is a name of the language, and no private one."""
    return is_name(name, naming.names) and not is_private_name(name, naming.private)


def is_instance(name: str, naming: Naming, named: Collection[str]) -> bool:
    """Whether a folder found in a repeating folder's own folder is an instance of it: its name is a name of the
    language, no private one, and none of named, the names the layout writes beside the instances there."""
    return is_instance_name(name, naming) and name not in named
