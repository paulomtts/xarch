"""The project docs beside the app, defined once as data: every document, and a template for each.

A dict is a folder holding its entries; a str is a file and the template it starts with. A folder holds a
template for the kind of document that lives in it, so no folder is ever empty. The docs are the same in
every profile, and they are not part of the app's structure: `check` does not require them.
"""
from __future__ import annotations

from collections.abc import Iterator

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

## Tiers

- Tier: what a test here proves, where it lives under `tests/`, and what it may touch (nothing, fakes, a real system).

## Running

One command per tier, each in its own invocation. The commands appear here and nowhere else.

## Placement

One litmus test per tier: the question a new test must answer yes to before it goes there.

## Fakes

What `tests/fakes/` implements, and which tiers use it.

## Guards

- Guard: what it refuses, in one line. Each has a file under `artifacts/guards/`.
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


def doc_files(tree: DocTree = DOCS_TREE, prefix: tuple[str, ...] = ()) -> Iterator[tuple[tuple[str, ...], str]]:
    """Yield (path, template) for every file, in the order the tree lists them."""
    for name, sub in tree.items():
        path = prefix + (name,)
        if isinstance(sub, str):
            yield path, sub
        else:
            yield from doc_files(sub, path)
