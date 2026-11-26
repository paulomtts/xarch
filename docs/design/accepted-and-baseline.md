# Accepted findings and the baseline

`parts.<part>.imports.accepted` lists, one by one and each with a reason, imports that `imports.may` does not allow.
`may-import` does not report them, every `check` names them in its enforcement section, and an entry that accepts
nothing any more is itself a violation, so the list can only shrink. This note extends the same idea to the other
findings that need an allowlist which may only shrink (checks of a profile's own, `structure` and `test-tree`, and
`tiers`), and adds a baseline: a recorded set of the findings a project has today, which may only go down, for
adopting xarch on existing code.

## What every acceptance shares

- An entry names one finding, or the findings of one file, and says `why` in one line. An entry with no reason is
  refused when the profile loads.
- A file is written as `imports.accepted` and a check's `examples` write it: its path below the app, or
  `tests/<path>` for a file below the tests root. A profile never names the app folder, so the same entry reads the
  same whatever the app is called.
- A finding an entry accepts is not reported. Every `check` lists it under `accepted:` in its enforcement section, the
  finding's message with the key and the reason, and JSON lists it in `enforcement.accepted_findings` (each `{"rule",
  "file", "line", "key", "message", "why"}`), beside the existing `enforcement.accepted` of `imports.accepted`, whose
  shape is kept.
- An entry that accepts nothing is stale: a violation of the rule it accepts findings of, at the entry's file, telling
  to drop the entry. That is what makes the list a ratchet.
- `profile check` lists each entry the compared profile does not hold as looser.

## (a) Checks of a profile's own: `checks.<id>.accepted`

```yaml
checks:
  no-local-clock:
    read: class
    in: {files: tests}
    may_not: {name: ["*Clock"]}
    message: "{file} defines its own clock {name}"
    fix: "use the shared FixedClock"
    accepted:
      - {file: tests/billing/test_invoice.py, name: InvoiceClock, why: "the invoice tests freeze two clocks"}
      - {file: tests/legacy/test_export.py, why: "the export suite is retired with the export"}
    examples: ...
```

What identifies a finding: the file, plus the values of the check's variables the entry names (any key other than
`file` and `why` is a variable, compared with the value the finding prints for it). An entry naming no variable
accepts every finding of the check in that file, which is the grain of an allowlist of files ("files over 700 lines").

- Chosen: the entry's own keys are its identity. The check's author picks the variable that is stable for what the
  check reads (a class's `name`, an import's `target`), and a reader sees in the entry what it accepts.
- Rejected: a `by: [name]` slot on the check naming the variables every entry must use. It says once what the
  entries already say, and forbids the file-wide entry that a size or backlog allowlist needs.
- Rejected: `line`. A line moves with every edit above it, so the entry would go stale for no reason; `line` is
  refused as an entry's key.
- Rejected: a hash of the message. It is opaque in review and breaks when the message is reworded.
- A finding said once for several facts (`once_per`, `per_line`) is matched on the first fact it says.

## (b) Structure: `structure.accepted`

```yaml
structure:
  accepted:
    - {path: modules/billing/domain/errors.py, why: "billing raises the kernel's errors until it has its own"}
    - {path: tests/modules/legacy/, why: "the legacy tests move with the legacy module"}
```

A `structure` finding (a folder or file of the layout missing) is named by the path that is missing, below the app; a
`test-tree` finding (a folder below the tests that mirrors no folder of the app, or a stray test under
`testing.beside`) by its path, `tests/<path>`. A trailing `/` is optional. The layout module, which owns both rules,
matches the entries, so no other module parses a structure message.

- Chosen: a top-level `structure` key. What is missing belongs to the layout as a whole (often a folder no part
  claims, in one instance of a repeating folder), not to one part.
- Rejected: `parts.<part>.optional` for this. It frees a part in every instance; an entry frees one path in one.

## (c) Tiers: `tiers.<tier>.accepted`

```yaml
tiers:
  unit:
    accepted:
      - {file: tests/modules/billing/test_rates.py, import: adapters/sql/rates.py, why: "rates read the table until the port lands"}
      - {file: tests/frontend/test_old_page.py, why: "the old page is retired with the old UI"}
```

An entry names a test file and, optionally, what it imports, written as `imports.accepted` writes it (a file or
folder below the app, or `tests/<path>` for test code, optionally `:<name>`). With `import`, it accepts the `tiers`
findings of that import in that file; without it, every `tiers` finding of the file, that it lies in no tier
included. The file must be a test of that tier, or a test in no tier (accepted as that tier's backlog): an entry under
another tier accepts nothing, and is stale.

- Chosen: under the tier. It is the tier's rules the test breaks, and a backlog is a tier's ("111 frontend tests not
  yet in render or browser").
- Rejected: a single `testing.accepted`. It would leave the tier of a backlog unsaid.

## (d) The baseline: `.xarch/baseline.json`

For a project adopting xarch with findings it cannot fix at once. `xarch baseline write` records the violations a
whole `check` finds now; from then on `check` reports only what is not recorded, and the record may only go down.

```json
{
  "version": 1,
  "findings": [
    {"rule": "may-import", "file": "app/adapters/mail/send.py", "message": "adapters/ may not import web/ (app.web.i18n)", "count": 1}
  ]
}
```

What identifies a finding: its rule, its file and its message with every run of digits read as one mark, so that a
line number in a message (or a count) does not change it; findings of the same key are counted. A key's count is its
ceiling.

- Chosen: a ceiling by finding key. A new finding never hides behind an old one: fixing one finding and adding
  another of the same rule elsewhere, or in the same file with another name, is a new key, and is reported.
- Rejected: a ceiling by count per rule only. It is simpler and survives renames, but a swap (one fixed, one added)
  keeps the count and passes, which is the regression a ratchet is for.
- Rejected: keying by line. Every edit above a finding would make it new.
- Rejected: a hash in place of the message. The message is what a reviewer reads in the record's diff.

How `check` reads it:

- No file: nothing changes, byte for byte.
- A violation whose key the record holds, up to its count, is baselined: not shown, counted. Every other violation
  is shown and fails the check as before.
- When a whole check finds fewer than the record holds, it passes and says `N below baseline` with the command that
  lowers the record. `--strict` fails on that, so the guard test keeps the record as low as the code.
- `--strict` does not fail on the baselined findings themselves: that is what the record is for.
- `check PATH...` applies the record to the whole run first (every check runs on the whole app), then shows the
  violations of the paths given; the `baseline:` line counts the whole app's.
- `xarch baseline write` runs a whole check. With no record, it writes every violation. With one, it only lowers it:
  a key no longer found is dropped and a count is lowered, never raised, and a new finding stays a violation.
  `--reset` writes the record afresh from what is found now, raising it, which the record's diff shows in review.
- Accepted entries are applied first: a finding an entry accepts is no violation, so it is never baselined, and a
  stale entry is a violation, which may be baselined like any other.
- JSON: `enforcement.baseline` is present only when the file is: `{"file", "recorded", "baselined", "below",
  "rules": [{"rule", "recorded", "found"}]}`.
