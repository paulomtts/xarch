# Testing

> How is the system tested?

Each ring admits one kind of test, so a test's tier follows from the ring its subject lives in
(architecture.md, section 2). Tests mirror the app: `tests/modules/<module>/<part>/`, `tests/web/`,
`tests/architecture/`.

## Tiers

| Tier | Subject | Proves | May touch |
|---|---|---|---|
| unit | `kernel/`, `domain/` | an invariant, a value rule, a state transition | nothing: no I/O, no clock, no fakes |
| use case | `application/`, `contract/` | one `Result` variant per path, driven through the controller | `tests/fakes/`, and mocks of fire-only ports |
| conformance | `adapters/` | the fake and the real adapter agree on a port | the real system, parametrized `(fake, real)` |
| driver | `web/` | routing, status codes and rendered output; never a business outcome | controllers faked |
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

One module, `documents`, with a use case `publish`; one test per tier, each holding only what its row allows.

```python
# unit: tests/modules/documents/domain/test_document.py
def test_a_document_without_a_title_cannot_be_published():
    with pytest.raises(DocumentIncomplete):
        a_document(title="").publish(NOW)

# use case: tests/modules/documents/application/test_publish.py (its header is shown under Files)
def test_a_document_without_a_title_is_rejected():
    repo = FakeDocumentRepo()
    repo.save(doc := a_document(title=""))
    assert controller(repo).publish(PublishDocument(doc.id)) == Rejected("The document needs a title.")

def test_the_owner_is_notified_once():                  # Notifier: a fire-only port of documents, so a mock
    repo, notifier = FakeDocumentRepo(), Mock(Notifier)
    repo.save(doc := a_document())
    controller(repo, notifier).publish(PublishDocument(doc.id))
    notifier.published.assert_called_once_with(doc.id)

# conformance: tests/modules/documents/adapters/test_document_repo.py
@pytest.fixture(params=["fake", "db"])
def repo(request, sql_session):
    return FakeDocumentRepo() if request.param == "fake" else DbDocumentRepo(sql_session)

def test_get_returns_what_save_stored(repo):
    repo.save(doc := a_document())
    assert repo.get(doc.id) == doc

# driver: tests/web/test_publish.py
def test_publish_renders_the_title_and_answers_200(client):
    controller = Mock(publish=lambda cmd: Published(DocumentView(cmd.id, "Hello", True)))
    response = client(controller).post(f"/documents/{A_DOCUMENT_ID}/publish")
    assert response.status_code == 200 and "Hello" in response.text

# bootstrap: tests/bootstrap/test_app.py, the only test here
def test_the_bootstrap_builds_migrates_seeds_and_answers(database_url):
    app = build_app(Settings(database_url=database_url))
    migrate(app); seed(app)                       # only this bootstrap test seeds
    assert isinstance(app.documents.publish(PublishDocument(SEEDED_DOCUMENT_ID)), Published)

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
"""Use case: publish a document.

Scenario: a document with a title is published
  Given a document with a title   When it is published   Then the Result is Published
Scenario: a document that does not exist is missing
  Given no such document          When it is published   Then the Result is Missing
Scenario: a document without a title is rejected
  Given a document with no title  When it is published   Then the Result is Rejected("The document needs a title.")
"""

def test_a_document_with_a_title_is_published(): ...
def test_a_document_that_does_not_exist_is_missing(): ...
def test_a_document_without_a_title_is_rejected(): ...
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
class DocumentRepo(Protocol):                       # the port, in application/ports/
    def get(self, id: DocumentId) -> Document | None: ...
    def save(self, doc: Document) -> None: ...

class DbDocumentRepo:                              # the adapter, in adapters/: talks to the database
    ...

class FakeDocumentRepo:                             # the fake, in tests/fakes/: a dict standing in for the table
    def __init__(self): self.docs = {}
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
