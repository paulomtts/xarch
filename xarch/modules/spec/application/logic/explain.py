"""What `xarch profile explain` reads from the table of keys: the keys of the overview, the key at an address as a person
types it, an example with the names xarch ships filled in, the nearest keys to an address that does not exist, and the
words of a language a text of the format is said in."""
from __future__ import annotations

import re
from difflib import get_close_matches

from xarch.kernel.logic.capabilities import shortfalls
from xarch.kernel.logic.names import outside_text
from xarch.modules.spec.application.logic.key_lookup import keys_of, names_of, of_an_entry, plain, shown
from xarch.modules.spec.application.logic.profile_needs import read_less
from xarch.modules.spec.domain.key_table import KEYS, SLOTS
from xarch.modules.spec.domain.profile_keys import CYCLES, HELD, PART, PROFILE, TIER, Key
from xarch.modules.spec.domain.values import Language
from xarch.profile_values.capabilities import Shortfall, Supply

NEAREST = 3
"""How many keys an unknown one is answered with, at most."""
_TOKENS = {"bundled": "<bundled>", "presets": "<preset>", "languages": "<language>"}
"""What the example of a key writes in place of a name xarch ships, by the list the name comes from."""


_WORD = re.compile(r"%(\w+)%")


def words(language: Language) -> dict[str, str]:
    """What the language says for each `%word%` a text of the format may write: the title, the extension, the package
    file, the name of an interface and its path (the first mark's base as an outside name, or its keyword), the
    namespace of the names bound without an import, the comment marker (its first line form's, else its first block
    form's opening, "" when it has neither) and the comments its tools read, each quoted after that marker, the prefix
    of a private name, and the annotations of no value, each as written, joined by ` or `."""
    checked = language.checked
    first = checked.interface[0] if checked.interface else None
    path = "" if first is None else outside_text(first.base, checked.member) if first.base else first.keyword
    return {"language": checked.title, "extension": checked.extension, "package_file": checked.package_file,
            "private": checked.private, "interface": language.interface_name, "interface_path": path,
            "namespace": language.namespace, "comment": checked.comment,
            "directives": ", ".join(f"`{checked.comment} {word}`" for word in checked.directives),
            "nothing": " or ".join(checked.nothing)}


def words_in(text: str) -> list[str]:
    """The `%word%`s the text writes, each without its marks, in order."""
    return _WORD.findall(text)


def said(text: str, language: Language) -> str:
    """The text with each `%word%` replaced by what the language says for it (see words); a word it has none for
    stays."""
    found = words(language)
    return _WORD.sub(lambda word: found.get(word[1], word[0]), text)


def holder_of(key: Key) -> str:
    """What holds the key when it is set on each of a kind of thing: a part or a tier; "" for anything else."""
    return key.scope if key.scope in (PART, TIER) else ""


def graded_for(key: Key, language: Language) -> str:
    """The language whose reader the facts a key needs are graded for; "" for a key that needs none."""
    return language.checked.title if key.needs else ""


def graded(key: Key, language: Language) -> bool:
    """Whether the language's data file grades the facts the key needs."""
    return bool(key.needs) and language.checked.supplies is not None


def short(key: Key, language: Language) -> tuple[Shortfall, ...]:
    """The facts the key needs that the language supplies partly or not at all, when its data file grades them; one its
    check reads only when supplied said as what the check then reads less."""
    if not graded(key, language):
        return ()
    return tuple(read_less(found, key, language) for found in shortfalls(
        plain(key.address), key.needs, {s.fact: s for s in language.checked.supplies or ()}))


def supplied(fact: str, language: Language) -> Supply | None:
    """How the language's reader supplies a fact a key needs; None when it does not, or its data file does not say."""
    return next((supply for supply in language.checked.supplies or () if supply.fact == fact), None)


def overview_keys() -> list[tuple[Key, int]]:
    """The keys of the file, each followed by the keys it holds, with how far below the file each sits; the keys held
    by one that another command than `check` reads, and those of `cycles`, which its line names, are left to its own
    explanation, which lists them."""
    found: list[tuple[Key, int]] = []
    for key in keys_of(PROFILE):
        found.append((key, 0))
        found += [(held, 1) for held in keys_of(key.opens)] if key.opens and not key.read_by and key.opens != CYCLES else []
    return found


def cleaned(address: str) -> str:
    """The address as the table writes it for a person: placeholders and stray dots and spaces left out."""
    return plain(address.strip().strip("."))


def key_at(address: str) -> Key | None:
    """The key at the address as typed: a key by its plain address, or with the name of a part or a tier in its second
    step (parts.adapters.imports.may), or a slot of an entry of a map of ids written with any id in the id's step
    (evals.title-rule.ask) or with the placeholder itself (evals.<id>.ask)."""
    typed = cleaned(address)
    written = address.strip().strip(".")
    found = next((key for key in KEYS if plain(key.address) == typed), None)
    found = found or next((key for key in KEYS if plain(key.address) == _unnamed(typed)), None)
    return found or next((slot for slot in SLOTS if written == slot.address or of_an_entry(typed, slot.scope, slot.name)), None)


def _unnamed(typed: str) -> str:
    """A typed address of a key of a part or a tier with the name of the one it sits on left out (parts.adapters.imports
    as parts.imports); the address itself when its second step is a key of a part or a tier, or it has no third."""
    steps = typed.split(".")
    scope = {"parts": PART, "tiers": TIER}.get(steps[0])
    if scope is None or len(steps) < 3 or steps[1] in names_of(scope):
        return typed
    return ".".join((steps[0], *steps[2:]))


def held_by(key: Key) -> tuple[Key, ...]:
    """The keys of the scope a key opens, then the slots of each entry of a map of ids it holds (see HELD)."""
    if not key.opens:
        return ()
    return keys_of(key.opens) + tuple(slot for scope, holder in HELD.items() if holder == key.opens
                                      for slot in keys_of(scope))


def example_of(key: Key, example: str, names: tuple[str, ...]) -> str:
    """The example of the key's text, with the first of the names xarch ships where it writes a token for one."""
    return example.replace(_TOKENS[key.choices], names[0]) if names and key.choices else example


def nearest(typed: str) -> tuple[str, ...]:
    """The addresses closest to one that does not exist: those that read like it, else the keys of the deepest
    existing key it starts with, else the keys of the file."""
    known = [shown(key) for key in (*KEYS, *SLOTS)]
    close = get_close_matches(typed, known, n=NEAREST, cutoff=0.6)
    if close:
        return tuple(close)
    steps = typed.split(".")
    for size in range(len(steps) - 1, 0, -1):
        parent = ".".join(steps[:size])
        held = [shown(k) for k in (*KEYS, *SLOTS) if shown(k).rpartition(".")[0] == parent]
        if held:
            return tuple(held[:NEAREST + 2])
    return tuple(key.name for key in keys_of(PROFILE))[:NEAREST + 2]
