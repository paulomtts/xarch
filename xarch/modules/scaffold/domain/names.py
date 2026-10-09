from __future__ import annotations

import keyword


def valid_name(name: str) -> bool:
    return (name.isascii() and name.isidentifier() and name == name.lower()
            and not name.startswith("_") and not keyword.iskeyword(name))
