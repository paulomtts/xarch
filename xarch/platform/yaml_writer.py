"""Writing plain Python values as YAML that reads as written by hand: block style, scalars in the shortest form that reads
back as the same value, a literal block for a text of several lines, a folded one for a long line, short lists in flow
style; and the words of a map or a list written on one line, plain when YAML reads them back as written, else quoted.
Knows no module."""
from __future__ import annotations

import json
import re
import textwrap
from typing import Any

WIDTH = 118
_PLAIN = re.compile(r"[A-Za-z_/<][A-Za-z0-9_ ./<>@*()'-]*")
_RESERVED = {"true", "false", "null", "yes", "no", "on", "off", "y", "n", "~"}
_BLOCKS = (dict, list)
_WORD = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_./@()-]*(?: [A-Za-z0-9_./@()-]+)*")
_WORD_RESERVED = ("true", "false", "null", "yes", "no")


class YamlWriter:
    def dump(self, document: dict[str, Any], width: int = WIDTH) -> str:
        """The document as text; a blank line comes before each top-level key whose value is a block."""
        return _dump(document, width)

    def word(self, text: str) -> str:
        """The text as a word of a map or a list written on one line: as it is when YAML reads it back as that text
        (letters, digits and `_./@()-`, single spaces between, no word YAML reads as a boolean or null), else quoted."""
        return text if _WORD.fullmatch(text) and text not in _WORD_RESERVED else self.quoted(text)

    def quoted(self, text: str) -> str:
        """The text in double quotes, as YAML and JSON both read it back."""
        return json.dumps(text, ensure_ascii=False)


def _dump(document: dict[str, Any], width: int) -> str:
    lines: list[str] = []
    for n, (key, value) in enumerate(document.items()):
        if n and _is_block(value):
            lines.append("")
        lines += _pair(key, value, 0, width)
    return "\n".join(lines) + "\n"


def _is_block(value: Any) -> bool:
    return isinstance(value, _BLOCKS) and bool(value) and not _flat_list(value)


def _flat_list(value: Any) -> bool:
    return isinstance(value, list) and all(not isinstance(item, _BLOCKS) for item in value)


def _scalar(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if (_PLAIN.fullmatch(value) and value == value.strip() and value.lower() not in _RESERVED
            and ": " not in value and " #" not in value and not value.endswith(":")):
        return value
    return json.dumps(value, ensure_ascii=False)


def _flow(value: Any) -> str:
    if isinstance(value, list):
        return "[" + ", ".join(_flow(item) for item in value) + "]"
    if isinstance(value, dict):
        return "{" + ", ".join(f"{_scalar(k)}: {_flow(v)}" for k, v in value.items()) + "}"
    text = _scalar(value)
    if isinstance(value, str) and any(c in value for c in ",[]{}") and not text.startswith('"'):
        return json.dumps(value, ensure_ascii=False)
    return text


def _pair(key: Any, value: Any, indent: int, width: int) -> list[str]:
    pad = " " * indent
    head = f"{pad}{_scalar(key)}:"
    if isinstance(value, dict):
        if not value:
            return [f"{head} {{}}"]
        return [head] + [line for k, v in value.items() for line in _pair(k, v, indent + 2, width)]
    if isinstance(value, list):
        return _list(head, value, indent, width)
    return _text(head, value, indent, width)


def _list(head: str, value: list[Any], indent: int, width: int) -> list[str]:
    if not value:
        return [f"{head} []"]
    if _flat_list(value):
        return _wrapped(head, value, indent, width)
    pad = " " * (indent + 2)
    lines = [head]
    for item in value:
        if isinstance(item, dict) and item:
            rows = [line for k, v in item.items() for line in _pair(k, v, indent + 4, width)]
            lines.append(f"{pad}- {rows[0].lstrip()}")
            lines += rows[1:]
        else:
            lines.append(f"{pad}- {_flow(item)}")
    return lines


def _wrapped(head: str, items: list[Any], indent: int, width: int) -> list[str]:
    cont = " " * (len(head) + 2)
    lines: list[str] = []
    current = f"{head} ["
    for n, item in enumerate(items):
        piece = _flow(item) + ("]" if n == len(items) - 1 else ",")
        if len(current) + len(piece) + 1 > width and not current.endswith("["):
            lines.append(current.rstrip())
            current = cont + piece + " "
        else:
            current += piece + " "
    lines.append(current.rstrip())
    return lines


def _text(head: str, value: Any, indent: int, width: int) -> list[str]:
    if not isinstance(value, str):
        return [f"{head} {_scalar(value)}"]
    pad = " " * (indent + 2)
    if "\n" in value and not value.endswith("\n") and not value.startswith((" ", "\n")):
        return [f"{head} |-"] + [pad + line if line else "" for line in value.split("\n")]
    one = f"{head} {_scalar(value)}"
    foldable = ("\n" not in value and "  " not in value and "\t" not in value and value == value.strip()
                and " " in value)
    if len(one) > width and foldable:
        body = textwrap.wrap(value, width - indent - 2, break_long_words=False, break_on_hyphens=False)
        return [f"{head} >-"] + [pad + line for line in body]
    return [one]
