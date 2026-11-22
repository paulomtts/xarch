"""The one reading of an outside name a profile or a language's data file writes, by the language's patterns."""
from __future__ import annotations

from xarch.kernel.logic.names import is_name, outside_steps


def outside_name(text: str, name: str, package: str, member: str, namespace: str = "") -> tuple[str, ...] | None:
    """The steps of an outside name the language allows: a package (or the namespace, when one is given) alone, or
    followed by the member and names joined by the step mark, each a name the name pattern allows; None when the text
    is none. Under a language that gives no member, any text but nothing is one step."""
    if not text:
        return None
    if not member:
        return (text,)
    head, *steps = outside_steps(text, member)
    if not ((namespace and head == namespace) or (head and is_name(head, package))):
        return None
    return (head, *steps) if all(is_name(step, name) for step in steps) else None
