"""The project docs beside the app, defined once as data: every document, and a template for each.

A dict is a folder holding its entries; a str is a file and the text it starts with. A folder holds a
template for the kind of document that lives in it, so no folder is ever empty. testing.md is written as
content, because the rings fix which tests each part admits; the rest are templates. Only testing.md's
driver row depends on the profile, and the docs are not part of the app's structure: `check` does not
require them.
"""
from __future__ import annotations

from collections.abc import Iterator

from xarch.modules.spec.domain.skeleton import Profile

DocTree = dict[str, "DocTree | str"]

DOCS_ROOT = ("docs", "project")    # below the folder holding the app

STATEMENT = """\
# Problem Statement & Use Cases

> What problems are we trying to solve? What must the system do?

## Problem

What is wrong or missing today, in one or two sentences.

## Who is affected

Who feels the problem, and how.

## Use cases

- Actor / goal / outcome: who wants what, and what they get.

## Out of scope

What this system will not do.
"""

DOMAIN = """\
# Domain Diagram

> What exists in this problem domain, and how does it work?

## Concepts

- Entity: what it is.

## Relationships

How the concepts relate: who owns, references or produces what.

## Rules

What must always hold between them.

## Diagram

```mermaid
classDiagram
  EntityA "1" --> "*" EntityB : relates to
```
"""

DESIGN = """\
# Design Document

> What are we proposing to build, and how will the pieces fit together?

## Proposal

What we will build, in one paragraph.

## Components and how they fit

Each piece, its job, and what it talks to.

## Key flows

The main paths through the system, step by step.

## Alternatives considered

What else we weighed, and why not.

## Open questions

What is still undecided.
"""

ARCHITECTURE = """\
# Architecture Document

> What is the system structurally?

## Structure

The folder tree, with one line on what each part is for.

## Rings

The layers from the inside out, and which parts belong to each.

## Dependency rules

What each part may import; anything not listed is forbidden.

## How modules meet

How one module uses another without importing it.
"""

TESTING = """\
# Testing

> How is the system tested?

Each ring admits one kind of test, so a test's tier follows from the ring its subject lives in
(architecture.md, section 2). Tests mirror the app: `tests/modules/<module>/<part>/`, `tests/{entry}/`,
`tests/architecture/`.

## Tiers

| Tier | Subject | Proves | May touch |
|---|---|---|---|
| unit | `kernel/`, `domain/` | an invariant, a value rule, a state transition | nothing: no I/O, no clock, no fakes |
| use case | `application/`, `contract/` | one `Result` variant per path, driven through the controller | `tests/fakes/` only |
| conformance | `adapters/` | the fake and the real adapter agree on a port | the real system, parametrized `(fake, real)` |
| driver | `{entry}/` | {driver_proves}; never a business outcome | controllers faked |
| smoke | `bootstrap/` | the wiring builds and the app starts | everything, once |
| guard | the source tree | a rule of the architecture holds | `tests/architecture/` |

`platform/` gets no tier of its own: conformance tests reach its clients through the adapters that use them.

## Running

One command per tier that needs a real system (conformance, smoke), one for all the tiers that do not; a
tier that needs a real system never shares a process with one that does not. The commands appear here and
nowhere else.

- unit, use case, driver, guard: `<command>`
- conformance: `<command>`
- smoke: `<command>`

## Placement

Which ring does the subject live in? That is the tier. The usual near-misses: a service test that mocks a
port to assert it was called is a use-case test that should fake the port and assert the `Result`; a driver
test that asserts what the use case did belongs in the use-case tier; an adapter test that runs only against
the fake proves nothing until it is a conformance pair.

## Files

| Tier | One file per | Its cases come from |
|---|---|---|
| unit | domain object or rule | the invariants in the module doc |
| use case | use case, headed by its scenarios | the scenarios: one per `Result` variant, happy and unhappy |
| conformance | port | the port's methods |
| driver | command or route | its arguments and outputs |
| smoke | the app | the flows a demo walks |
| guard | rule | the standard it enforces |

Scenarios belong to the use-case tier only: there a test is one path through one use case, which is what a
scenario names. A unit test proves a rule and a conformance test a port method; neither has a Given.

A use-case file opens with its scenarios, one per `Result` variant of the use case in `contract/`, and
a scenario's name is its test's name, so the header and the tests cannot drift apart. A variant with no
scenario is an untested path; a scenario with no variant is a missing `Result`.

```python
\"\"\"Use case: publish a document.

Scenario: a draft with a title is published
  Given a draft with a title   When its owner publishes it   Then it is Published
Scenario: a draft without a title is refused
  Given a draft with no title  When its owner publishes it   Then it is Refused("title required")
\"\"\"

def test_a_draft_with_a_title_is_published(): ...
def test_a_draft_without_a_title_is_refused(): ...
```

## Fakes

`tests/fakes/` holds one in-memory implementation per port, shared by the use-case tests and used as the
`fake` side of every conformance pair. A fake is not an adapter; conformance is what keeps it honest.

## Data

A test builds the state it needs, so the reader sees all of it; no tier but smoke runs a shared seed.

| Tier | Where its data comes from |
|---|---|
| unit | built in the test |
| use case | the test loads the fake before acting; a builder per aggregate for the common shape, never a shared dataset |
| conformance | the test writes what it then reads, on both sides of the pair |
| driver | none: the faked controller returns the `Result` under test |
| smoke | the seed |
| guard | none |

The seed is product code: it lives in `bootstrap/`, the only part that sees every module, and the demo
environment runs the same seed the smoke tier does.

## Guards

- `tests/architecture/`: `xarch check` on the app, so the dependency rules of architecture.md section 5 hold.

One line per guard. Each has a file under `artifacts/guards/`.
"""

REQUIREMENTS = """\
# Requirements

> What does it require to exist?

## Functional

- FR-1: statement. Rationale: why. Verified by: test, review or demo.

## Non-functional

- NFR-1: statement. Rationale: why. Verified by: measurement or check.
"""

ADR = """\
# ADR 0000: Decision title

> What decisions have we made and why? One decision per record.

## Status

Proposed, accepted, superseded by ADR NNNN, or deprecated.

## Context

The forces at play, and why a decision is needed now.

## Decision

What we decided, in one or two sentences.

## Consequences

What becomes easier or harder because of it.

## Alternatives

What else we considered, and why not.
"""

STANDARD = """\
# Standard: name

> What is the correct way of doing things?

## Rule

The rule, in one sentence.

## Why

What goes wrong without it.

## Do

An example that follows the rule.

## Don't

An example that breaks it.
"""

AUDIT = """\
# Audit: name

> What does inconsistently wrong harness output look like?

## Symptom

What the wrong output looks like.

## Example

A real sample of it.

## Why it is wrong

Which expectation it breaks.

## Detection

How to spot it, by hand or automatically.

## Fix

How to correct it, and how to prevent it.
"""

TAXONOMY = """\
# Taxonomy: pattern name

> What are the names for certain recognizable patterns?

## Definition

What the pattern is, in one sentence.

## Recognize it by

The signs that give it away.

## Example

A short instance of it.
"""

MODULE = """\
# Module: name

> What is this module's responsibility? How does it behave? What are its invariants?

## Responsibility

What it owns, in one sentence.

## Behavior

Its use cases, and what each does.

## Invariants

What must always hold.

## Contract

Inputs it accepts and outputs it returns.

## Dependencies via ports

What it needs from outside, and the port that declares each need.
"""

GUARD = """\
# Guard: name

> What does this guard refuse, and why?

## Refuses

What it fails on, in one sentence.

## Why

What goes wrong if it gets through.

## Caught by

The test file that enforces it.

## Standard

The standard under `artifacts/standards/` it enforces, or "review only" when there is none.

## When it fires

How to get unblocked: fix the cause, or, for a ratchet, where the allowlist is and what a reason must say.
"""

DOCS_TREE: DocTree = {
    "statement.md": STATEMENT,
    "domain.md": DOMAIN,
    "design.md": DESIGN,
    "architecture.md": ARCHITECTURE,
    "testing.md": TESTING,
    "requirements.md": REQUIREMENTS,
    "adrs": {"0000-template.md": ADR},
    "artifacts": {
        "standards": {"_template.md": STANDARD},
        "audits": {"_template.md": AUDIT},
        "taxonomy": {"_template.md": TAXONOMY},
        "modules": {"_template.md": MODULE},
        "guards": {"_template.md": GUARD},
    },
}


def doc_files(chosen: Profile, tree: DocTree = DOCS_TREE,
              prefix: tuple[str, ...] = ()) -> Iterator[tuple[tuple[str, ...], str]]:
    """Yield (path, text) for every file, in the order the tree lists them; testing.md names the profile's driver."""
    for name, sub in tree.items():
        path = prefix + (name,)
        if isinstance(sub, str):
            yield path, sub.format(entry=chosen.entry_point, driver_proves=chosen.driver_proves)
        else:
            yield from doc_files(chosen, sub, path)
