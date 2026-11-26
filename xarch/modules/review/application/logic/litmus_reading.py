"""What the yes-or-no answers to the entries of a part's litmus list say of a file of it: each entry answers yes when
its probability of yes is at or above the yes line (`evals.placement.yes_line`, a placeholder never measured unless
written); the litmus holds when at least one `any` entry (when there is any) and every `all` entry answers yes. What
the entries say is advisory, a note on the file: it never makes a file doubtful, which placement's question alone
decides, since entries asked one by one have not been shown to tell a part's files from the others'."""
from __future__ import annotations

from dataclasses import replace

from xarch.modules.review.domain.published import LitmusRead, Reading
from xarch.modules.review.domain.values import Answer
from xarch.profile_values.litmus import ALL, ANY, Litmus

YES = "yes"
"""The option of an entry's answer whose probability is read."""


def holds(answers: tuple[tuple[Litmus, bool], ...]) -> bool:
    """Whether code belongs by the answers to the entries of a litmus, each entry with whether it answered yes: at
    least one ANY entry answered yes (when there is any), and every ALL entry did."""
    alternatives = [said for entry, said in answers if entry.mode == ANY]
    return (not alternatives or any(alternatives)) and all(said for entry, said in answers if entry.mode == ALL)


def with_litmus(read: Reading, entries: tuple[Litmus, ...], answers: tuple[Answer, ...], yes_line: float) -> Reading:
    """The reading of a file with what the answers to its part's entries say, each answer the entry's in order: each
    entry read, whether the litmus holds and the yes line, as a note that leaves whether it is doubtful as it was; the
    reading as it was for a part with no entries asked."""
    if not entries:
        return read
    found = tuple(LitmusRead(entry.label, entry.mode, dict(answer.probabilities).get(YES, 0.0),
                             dict(answer.probabilities).get(YES, 0.0) >= yes_line)
                  for entry, answer in zip(entries, answers, strict=True))
    held = holds(tuple((entry, item.said_yes) for entry, item in zip(entries, found, strict=True)))
    return replace(read, litmus=found, litmus_holds=held, yes_line=yes_line)
