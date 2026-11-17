"""The data file of the texts of the profile format (`presets/format/keys.yaml`), read into a Catalogue with every
problem listed:

    fragments   {<name>: <text>}: pieces of profile the examples share, each lines ending in a line break; a line that
                is exactly `<<name>>`, in an example or in another fragment, stands for that fragment's text
    smallest    the smallest valid profile, as text
    symbols     {<symbol>: <meaning>}: what a profile writes in paths and imports
    keys        {<address>: {meaning, accepts, example}}: the text of each key of the table (see key_table), by its
                address, and of no other
    slots       {<address>: {meaning, accepts, example}}: the same, of each slot of an eval of the profile's own (see
                key_table's SLOTS), and of no other

A text may write `%min_statements%` and `%min_fields%`, the defaults of no-duplicates and no-twins, which are filled in
here, and the words a language says (see explain.words), which are filled in when the text is said; no other `%word%`.
"""
from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

from xarch.modules.spec.application.logic.evals import FEWEST_EXAMPLES, MAX_ASK
from xarch.modules.spec.application.logic.explain import words, words_in
from xarch.modules.spec.domain.errors import InvalidArchitecture
from xarch.modules.spec.domain.key_table import KEYS, SLOTS
from xarch.modules.spec.domain.profile_keys import Catalogue, Key, KeyText
from xarch.modules.spec.domain.published import LINE
from xarch.modules.spec.domain.values import FORMAT_KEYS, Language, NoDuplicates, NoTwins

SECTIONS = ("fragments", "smallest", "symbols", "keys", "slots")
FIELDS = ("meaning", "accepts", "example")
_INCLUDE = re.compile(r"<<(.*)>>")
_DEFAULTS = {"min_statements": str(NoDuplicates.min_statements), "min_fields": str(NoTwins.min_fields),
             "line": str(LINE), "max_ask": str(MAX_ASK), "fewest_examples": str(FEWEST_EXAMPLES)}
_WORDS = (*words(Language()), *_DEFAULTS)
"""Every `%word%` a text may write."""


def catalogue_of(document: Any) -> Catalogue:
    """The texts of the format the document of its data file holds; raises InvalidArchitecture listing every problem."""
    if not isinstance(document, Mapping):
        raise InvalidArchitecture(FORMAT_KEYS, [f"must be a mapping of {', '.join(SECTIONS)}"])
    problems: list[str] = []
    unknown = sorted(str(key) for key in document if key not in SECTIONS)
    if unknown:
        problems.append(f"unknown key{'s' if len(unknown) > 1 else ''} {_quoted(unknown)}: use {', '.join(SECTIONS)}")
    problems += [f"missing `{section}`" for section in SECTIONS if section not in document]
    fragments = _texts(document.get("fragments", {}), "fragments", problems)
    for name, text in fragments.items():
        if not text.endswith("\n"):
            problems.append(f"fragments.{name}: must end with a line break")
        _expanded(text, f"fragments.{name}", fragments, problems, (name,))
    smallest = _text(document["smallest"], "smallest", problems) if "smallest" in document else ""
    symbols = _texts(document.get("symbols", {}), "symbols", problems)
    texts = _keys(document["keys"], fragments, problems) if "keys" in document else {}
    slots = _keys(document["slots"], fragments, problems, "slots", SLOTS) if "slots" in document else {}
    written = [("smallest", smallest), *((f"symbols.{s}", f"{s} {m}") for s, m in symbols.items()),
               *((f"keys.{a}.{f}", getattr(t, f)) for a, t in texts.items() for f in FIELDS),
               *((f"slots.{a}.{f}", getattr(t, f)) for a, t in slots.items() for f in FIELDS)]
    problems += [f"{where}: unknown word %{word}%: use {', '.join(f'%{w}%' for w in _WORDS)}"
                 for where, text in written for word in words_in(text) if word not in _WORDS]
    if problems:
        raise InvalidArchitecture(FORMAT_KEYS, list(dict.fromkeys(problems)))
    return Catalogue({address: _filled(text) for address, text in texts.items()},
                     tuple((_defaulted(symbol), _defaulted(meaning)) for symbol, meaning in symbols.items()),
                     _defaulted(smallest), {address: _filled(text) for address, text in slots.items()})


def _keys(found: Any, fragments: Mapping[str, str], problems: list[str], section: str = "keys",
          keys: tuple[Key, ...] = KEYS) -> dict[str, KeyText]:
    if not isinstance(found, Mapping):
        problems.append(f"{section}: must be a mapping of each key's address to {{{', '.join(FIELDS)}}}")
        return {}
    table = [key.address for key in keys]
    unknown = [str(address) for address in found if address not in table]
    if unknown:
        problems.append(f"{section}: the format has no key {_quoted(unknown)}")
    missing = [address for address in table if address not in found]
    if missing:
        problems.append(f"{section}: missing the text of {_quoted(missing)}")
    texts: dict[str, KeyText] = {}
    for address in (address for address in table if address in found):
        entry, where = found[address], f"{section}.{address}"
        if not isinstance(entry, Mapping):
            problems.append(f"{where}: must be a mapping of {', '.join(FIELDS)}")
            continue
        extra = sorted(str(field) for field in entry if field not in FIELDS)
        if extra:
            problems.append(f"{where}: unknown key{'s' if len(extra) > 1 else ''} {_quoted(extra)}: use "
                            f"{', '.join(FIELDS)}")
        meaning, accepts, example = (_text(entry.get(field), f"{where}.{field}", problems) for field in FIELDS)
        texts[address] = KeyText(meaning, accepts, _expanded(example, f"{where}.example", fragments, problems, ()))
    return texts


def _expanded(text: str, where: str, fragments: Mapping[str, str], problems: list[str], within: tuple[str, ...]) -> str:
    """The text with each line `<<name>>` replaced by that fragment's text, expanded in turn; a fragment that is not
    there, or one that includes itself, is a problem and stays as written."""
    lines: list[str] = []
    for line in text.splitlines(keepends=True):
        found = _INCLUDE.fullmatch(line.rstrip("\n"))
        name = found[1] if found else ""
        if found is None:
            lines.append(line)
        elif name in within:
            problems.append(f"{where}: the fragments include each other in a loop: {' -> '.join((*within, name))}")
            lines.append(line)
        elif name not in fragments:
            problems.append(f"{where}: no fragment {name!r}: use {', '.join(fragments) or 'none'}")
            lines.append(line)
        else:
            lines.append(_expanded(fragments[name], f"fragments.{name}", fragments, problems, (*within, name)))
    return "".join(lines)


def _texts(found: Any, where: str, problems: list[str]) -> dict[str, str]:
    if not isinstance(found, Mapping):
        problems.append(f"{where}: must be a mapping of names to text")
        return {}
    return {str(name): _text(value, f"{where}.{name}", problems) for name, value in found.items()}


def _text(value: Any, where: str, problems: list[str]) -> str:
    if not isinstance(value, str) or not value.strip():
        problems.append(f"{where}: must be a non-empty string")
        return ""
    return value


def _filled(text: KeyText) -> KeyText:
    return KeyText(_defaulted(text.meaning), _defaulted(text.accepts), _defaulted(text.example))


def _defaulted(text: str) -> str:
    for word, value in _DEFAULTS.items():
        text = text.replace(f"%{word}%", value)
    return text


def _quoted(names: list[str]) -> str:
    return ", ".join(f"'{name}'" for name in names)
