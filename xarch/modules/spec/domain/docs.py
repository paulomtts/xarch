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
| use case | `application/`, `contract/` | one `Result` variant per path, driven through the controller | `tests/fakes/`, and mocks of fire-only ports |
| conformance | `adapters/` | the fake and the real adapter agree on a port | the real system, parametrized `(fake, real)` |
| driver | `{entry}/` | {driver_proves}; never a business outcome | controllers faked |
| bootstrap | `bootstrap/` | one test: the app builds as `main` builds it, migrates, seeds and answers one command | everything, once |
| guard | the source tree | a rule of the architecture holds | `tests/architecture/` |

`platform/` gets no tier of its own: conformance tests reach its clients through the adapters that use them.

## Running

One command per tier that needs a real system (conformance, bootstrap), one for all the tiers that do not; a
tier that needs a real system never shares a process with one that does not. The commands appear here and
nowhere else.

- unit, use case, driver, guard: `<command>`
- conformance: `<command>`
- bootstrap: `<command>`

## Placement

Which ring does the subject live in? That is the tier. When it is not obvious, run the litmus tests; the
first one it passes is where it goes.

> **unit.** Does it prove a rule, value or transition by building the object and asking it, with no port in
> sight? If yes, it is a unit test. If it needs a port to get an answer, it is a use-case test. If it asserts
> how a port was called, it is testing nothing.

> **use case.** Does it drive one use case through the controller and assert one `Result` variant? If yes,
> it is a use-case test. If it asserts what a fake holds instead of the `Result`,
> check first that the `Result` would not already say it. If it asserts SQL, the order of rows or a
> technology, it is a conformance test. If it mocks a repo to assert it was called, fake the repo and assert
> the `Result`.

> **conformance.** Does it assert something the port promises, and would it pass unchanged on both the fake
> and the real adapter? If yes, it is a conformance test. If it would pass only on the real one, the fake is
> wrong or the promise is not the port's. If it runs only against the fake, it proves nothing until it is a
> pair. If it needs a use case to set the state up, it is a use-case test.

> **driver.** Does it prove the entry point turned input into a command and a `Result` into output, with
> the controller faked? If yes, it is a driver test. If it asserts what the use case did, or needs the real
> controller to mean anything, it is a use-case test wearing a terminal.

> **bootstrap.** Is it the one test that builds the app as `main` does? If yes, it is the bootstrap test. If
> there is already one, this one belongs in a lower tier.

> **guard.** Does it read the source tree and fail on a rule of architecture.md, whatever the app does? If
> yes, it is a guard, and it has a file under `artifacts/guards/`. If it runs the app, it is not a guard.

## Examples

One module, `docs`, with a use case `publish`; one test per tier, each holding only what its row allows.

```python
# unit: tests/modules/docs/domain/test_draft.py
def test_a_draft_without_a_title_cannot_publish():
    assert Draft(title="").can_publish() is False

# use case: tests/modules/docs/application/test_publish.py (its header is shown under Files)
def test_a_draft_without_a_title_is_refused():
    repo = FakeDocsRepo()
    repo.add(draft := a_draft(title=""))
    assert controller(repo).publish(Publish(draft.id)) == Refused("title required")

def test_the_owner_is_notified_once():
    repo, mailer = FakeDocsRepo(), Mock(Mailer)
    repo.add(draft := a_draft())
    controller(repo, mailer).publish(Publish(draft.id))
    mailer.send.assert_called_once_with(to=draft.owner, subject="Published")

# conformance: tests/modules/docs/adapters/test_docs_repo.py
@pytest.fixture(params=["fake", "sql"])
def repo(request, sql_session):
    return FakeDocsRepo() if request.param == "fake" else SqlDocsRepo(sql_session)

def test_get_returns_what_save_stored(repo):
    repo.save(doc := a_doc())
    assert repo.get(doc.id) == doc

# driver: tests/{entry}/test_publish.py
def test_publish_prints_the_id_and_exits_zero(runner):
    controller = Mock(publish=lambda cmd: Published(cmd.id))
    result = runner.invoke(app(controller), ["docs", "publish", "42"])
    assert result.exit_code == 0 and "42" in result.output

# bootstrap: tests/bootstrap/test_app.py, the only test here
def test_the_bootstrap_builds_migrates_seeds_and_answers(database_url):
    app = build_app(Settings(database_url=database_url))
    migrate(app); seed(app)                       # only this bootstrap test seeds
    assert app.docs.list(ListDocs()).items

# guard: tests/architecture/test_rules.py
def test_the_dependency_rules_hold():
    assert check(Path("app")).violations == []
```

## Files

| Tier | One file per | Its cases come from |
|---|---|---|
| unit | domain object or rule | the invariants in the module doc |
| use case | use case, headed by its scenarios | the scenarios: one per `Result` variant, happy and unhappy |
| conformance | port | the port's methods |
| driver | command or route | its arguments and outputs |
| bootstrap | the app | the one command it answers; a second test here belongs in a lower tier |
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

## Fakes and mocks

A port is faked or mocked by what the use case does with it:

| The use case | Port kind | Stand-in | Example |
|---|---|---|---|
| reads back what it wrote | stateful | a fake: an in-memory implementation in `tests/fakes/`, one per port | a repo, a clock, a blob store |
| only fires and never reads | fire-only | a mock asserting the call and its payload, since the call is the contract | send an email, publish an event |

> **Litmus test.** Does the use case ever read back through this port what it or anything else wrote, or
> branch on its answer? If yes, fake it: a mock would script the answer, and the test would prove only what
> it was told. If the use case only calls it and never looks at it again, mock it: the call is the outcome,
> and a fake would be ceremony. If a port does both, split the port: one that is written and read is not
> the same need as one that only fires.

A fake is a working implementation of the port that keeps its state in memory, not a recording of calls:

```python
class DocsRepo(Protocol):                       # the port, in application/ports/
    def get(self, id: DocumentId) -> Document | None: ...
    def save(self, doc: Document) -> None: ...

class SqlDocsRepo:                              # the adapter, in adapters/: talks to the database
    ...

class FakeDocsRepo:                             # the fake, in tests/fakes/: a dict standing in for the table
    def __init__(self): self.docs = {{}}
    def get(self, id): return self.docs.get(id)
    def save(self, doc): self.docs[doc.id] = doc
```

The fakes are shared by every use-case test and are the `fake` side of every conformance pair. A fake is
not an adapter; conformance is what keeps it honest. A mock has nothing to conform.

## Data

A test builds the state it needs, so the reader sees all of it; no tier but bootstrap runs a shared seed.

| Tier | Where its data comes from |
|---|---|
| unit | built in the test |
| use case | the test loads the fake before acting; a builder per aggregate for the common shape, never a shared dataset |
| conformance | the test writes what it then reads, on both sides of the pair |
| driver | none: the faked controller returns the `Result` under test |
| bootstrap | the seed |
| guard | none |

The seed is product code: it lives in `bootstrap/`, the only part that sees every module, and the demo
environment runs the same seed the bootstrap test does.

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
