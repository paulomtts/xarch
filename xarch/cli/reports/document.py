"""How every command writes its JSON document: indented by two, its text as it is, not escaped to ASCII."""
from __future__ import annotations

import json
from typing import Any


def document(content: dict[str, Any]) -> str:
    """The content as the JSON document a command prints."""
    return json.dumps(content, indent=2, ensure_ascii=False)
