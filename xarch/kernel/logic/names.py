"""Whether a text is a name a language allows, by the pattern its data file gives (a regular expression; any text but
nothing when it gives none), and whether a name is private, by how the language starts one ("" for none); and the
names a profile writes from outside the app, by the language's package pattern and its member: read into their steps,
and printed back from them. Nothing else splits or joins an outside name."""
from __future__ import annotations

import re

STEP = "."
"""What stands between the names after a package in an outside name, and before a method called on anything: a
notation of the profile format, not of a language."""


def is_name(text: str, pattern: str) -> bool:
    """Whether text is a name the pattern allows; any text but nothing when the pattern is empty."""
    return re.fullmatch(pattern or ".+", text) is not None


def is_private_name(text: str, private: str) -> bool:
    """Whether text starts as a private name does; no text does when the language marks none ("")."""
    return bool(private) and text.startswith(private)


def outside_steps(text: str, member: str) -> tuple[str, ...]:
    """The steps of an outside name as written, checked against nothing: the text up to the first member, then the rest
    split at each step mark; the whole text as one step when the language gives no member or the text holds none."""
    if not member:
        return (text,)
    head, found, rest = text.partition(member)
    return (head, *rest.split(STEP)) if found else (head,)


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


def outside_text(steps: tuple[str, ...], member: str) -> str:
    """An outside name as a profile writes it: a method called on anything, ("", "<name>()"), after the step mark; else
    the package, then the member and the names after it joined by the step mark."""
    if len(steps) == 2 and not steps[0]:
        return f"{STEP}{steps[1]}"
    return steps[0] + member + STEP.join(steps[1:]) if len(steps) > 1 else "".join(steps)
