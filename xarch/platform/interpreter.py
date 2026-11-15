"""What only the interpreter running xarch knows about its language: the names of its standard library, the words it
reserves and the names it binds without an import. Knows no module."""
from __future__ import annotations

import builtins
import keyword
import sys


def standard_library() -> frozenset[str]:
    """The top-level names of the standard library."""
    return frozenset(sys.stdlib_module_names)


def reserved_words() -> frozenset[str]:
    """The words no name may be: the keywords."""
    return frozenset(keyword.kwlist)


def builtin_names() -> frozenset[str]:
    """The names bound without an import."""
    return frozenset(dir(builtins))
