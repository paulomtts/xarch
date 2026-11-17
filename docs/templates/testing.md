# Testing

How xarch is tested: which kind of test each part admits, where a test is placed, and how one is written. The tiers, their subjects and the guards below come from `architecture.yaml`, and `xarch check` holds xarch's own tests to them as it holds its source. Tests mirror the package: `tests/modules/<module>/<part>/`, `tests/kernel/`, `tests/profile_values/`, `tests/platform/`, `tests/cli/`, `tests/bootstrap/`, `tests/architecture/`. This page is generated from that file and from `docs/templates/testing.md`: edit those, never this page.

## Index

- [[#1. Tiers]]
- [[#2. Running]]
- [[#3. Placement]]
{{tier_index:3}}
- [[#4. Examples]]
- [[#5. Files]]
  - [[#5.1 One file per]]
  - [[#5.2 Tables]]
- [[#6. Fakes]]
- [[#7. Data]]
- [[#8. Guards]]

## 1. Tiers

{{tiers}}

{{untested}}

> [!NOTE]
> `application/ports/` and `contract/` have no behavior of their own to test: the integration tests reach them through the controller that uses them. `application/logic/` sits beside the services but holds pure functions with no port, so it is unit-tested.

## 2. Running

One command runs every tier:

```
uv run pytest tests
```

`tests/conftest.py` takes the decision model's key out of the environment for every test, so no test can send code across the network, whatever the shell running the tests holds.

## 3. Placement

Which part does the subject live in? Its row in section 1 gives the tier. When it is not obvious, run the litmus tests below in order: the first one it passes is the tier. A test imports only what the part its folder mirrors may import (architecture.md, section 5), not all that its tier may touch.

{{tier_litmus:3}}

## 4. Examples

Each example is a short version of a real test, kept in `docs/examples/tests/`. As on the architecture page, it imports from `app.`: read `app.` as `xarch.`. The unit example tests the `cycles` rule of architecture.md, section 8.5, and the guard example runs the wiring of section 6 there on xarch's own source.

{{tier_examples}}

The integration and wired tiers have no example here: `docs/examples/` holds no fake and no profile for one to build on. `tests/modules/layout/application/test_structure.py` is a short integration test to read instead.

## 5. Files

### 5.1 One file per

{{tier_files}}

### 5.2 Tables

Tests that share a shape are one table: one test function, one `pytest.param` per case, its `id` a sentence that states the outcome. A use case's test is a table with the columns `given`, `when` and `then`, and it is the integration tier's alone:

| Column | Holds |
|---|---|
| `given` | the state the fakes start with: the files of a source tree, the profiles spec would give |
| `when` | the use case's command, from the module's `contract/` |
| `then` | the `Result` variant that comes back |

The rows hold one `then` per variant at least, happy and unhappy. The body has no branch or loop: it builds the controller around `given`, calls it with `when` and asserts `== then`. A case that does not fit the shape is a standalone test beside the table, named for its outcome. A unit table names its columns for what they hold, a rule's inputs and its answer, as `test_cycles` does in section 4.

## 6. Fakes

A port is stood in for by a fake: an in-memory implementation in `tests/fakes/`, named `Fake` and the port's name, such as `FakeSourceTree` or `FakeDisk`, which takes its starting state when it is built. That state is what a row's `given` holds. A fake is not an adapter, and no integration test uses an adapter. Where a module's controller needs several fakes, `tests/modules/<module>/application/helpers.py` builds it around them the way `bootstrap/` builds the real one around adapters.

## 7. Data

A test builds the state it needs, so the reader sees all of it. No tier runs a shared seed.

{{tier_data}}

## 8. Guards

`xarch check` runs every guard below on xarch's source and on `tests/`. `tests/architecture/test_self_check.py` runs it in the test suite, plainly and in `--strict` mode, so a broken rule fails the build.

{{guards}}

The other files of `tests/architecture/` hold xarch to what no key of the profile says, among them: that its code names no part of a bundled profile, that the README lists every option of every command, and that `ruff.toml` stays the bundled linter config plus the repository's own exclusions.
