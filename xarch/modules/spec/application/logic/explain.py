"""What `xarch profile explain` reads from the table of keys: the keys of the overview, the key at an address as a person
types it, an example with the names xarch ships filled in, and the nearest keys to an address that does not exist."""
from __future__ import annotations

import re
from difflib import get_close_matches

from xarch.kernel.capabilities import Supply
from xarch.modules.spec.application.logic.key_lookup import keys_of, plain
from xarch.modules.spec.domain.profile_keys import KEYS, PROFILE, Key
from xarch.modules.spec.domain.values import Language

NEAREST = 3
"""How many keys an unknown one is answered with, at most."""
_TOKENS = {"bundled": "<bundled>", "presets": "<preset>", "languages": "<language>"}
"""What the example of a key writes in place of a name xarch ships, by the list the name comes from."""


_WORD = re.compile(r"%(\w+)%")


def said(text: str, language: Language) -> str:
    """The text with each `%word%` replaced by what the language says for it: the title, the extension, the package file,
    the name of an interface and its dotted path, the namespace of the names bound without an import, the marker of a
    line comment and the comments its tools read, each quoted after the marker; a word it has none for stays."""
    checked = language.checked
    words = {"language": checked.title, "extension": checked.extension, "package_file": checked.package_file,
             "interface": language.interface_name,
             "interface_path": ".".join(checked.interface[0]) if checked.interface else "",
             "namespace": language.namespace, "comment": checked.comment,
             "directives": ", ".join(f"`{checked.comment} {word}`" for word in checked.directives)}
    return _WORD.sub(lambda found: words.get(found[1], found[0]), text)


def supplied(fact: str, language: Language) -> Supply | None:
    """How the language's reader supplies a fact a key needs; None when it does not, or its data file does not say."""
    return next((supply for supply in language.checked.supplies or () if supply.fact == fact), None)


def overview_keys() -> list[tuple[Key, int]]:
    """The keys of the file, each followed by the keys it holds, with how far below the file each sits."""
    found: list[tuple[Key, int]] = []
    for key in keys_of(PROFILE):
        found.append((key, 0))
        found += [(held, 1) for held in keys_of(key.opens)] if key.opens else []
    return found


def cleaned(address: str) -> str:
    """The address as the table writes it for a person: placeholders and stray dots and spaces left out."""
    return plain(address.strip().strip("."))


def key_at(address: str) -> Key | None:
    typed = cleaned(address)
    return next((key for key in KEYS if plain(key.address) == typed), None)


def held_by(key: Key) -> tuple[Key, ...]:
    return keys_of(key.opens) if key.opens else ()


def example_of(key: Key, names: tuple[str, ...]) -> str:
    """The key's example, with the first of the names xarch ships where it writes a token for one."""
    return key.example.replace(_TOKENS[key.choices], names[0]) if names and key.choices else key.example


def nearest(typed: str) -> tuple[str, ...]:
    """The addresses closest to one that does not exist: those that read like it, else the keys of the deepest
    existing key it starts with, else the keys of the file."""
    known = [plain(key.address) for key in KEYS]
    close = get_close_matches(typed, known, n=NEAREST, cutoff=0.6)
    if close:
        return tuple(close)
    steps = typed.split(".")
    for size in range(len(steps) - 1, 0, -1):
        parent = ".".join(steps[:size])
        held = [plain(k.address) for k in KEYS if plain(k.address).rpartition(".")[0] == parent]
        if held:
            return tuple(held[:NEAREST + 2])
    return tuple(key.name for key in keys_of(PROFILE))[:NEAREST + 2]
