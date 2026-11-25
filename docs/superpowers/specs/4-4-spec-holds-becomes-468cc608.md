# 4.4 spec: `holds` becomes a map of kinds with their settings

Card `468cc608`, subtask of `c34d7f47`, blocked by `f2bf7d53` (4.3, the one needs walker, done on this branch at
`786635b`/`ff55259`). Release step 12 of the merged order
(`/home/mtts/.claude/bedtime/xarch-2026-11-16-audits/0.3.0-cohesion-review-3.md`, below **R3**, section 3).

Parent design: `/home/mtts/.claude/bedtime/xarch-2026-11-16-audits/code-shape-design.md` (below **CS**). Constraints
inherited, by section and line:

- Rulings 4 (CS lines 18-31), 6 (36-38) and 15 (58-59): `holds` is a map keyed by kind, `classes`, `functions`,
  `records`, `exceptions`, each with its own settings among `names`, `immutable`, `built_by`; a kind listed may exist
  in the part, a kind not listed may not; `functions` means top-level functions only; `classes` covers every class,
  `records` and `exceptions` are narrower, and each class follows the settings of the narrowest listed kind it fits.
  `classes:` and `functions:` are not part keys.
- Ruling 10 (46-47) and the default of one wording (65-66): an old key is refused with a hint from the one
  retired-keys table, in fixed text; one problem per retired key.
- Default (66-68): `records` takes `names` as well as `immutable`; the rest of `holds` as CS recommends.
- No compatibility window (72-73); the key keeps the name `holds` (73).
- 2.1 (237-263): the kinds, what each is, its settings, its needs; no `interfaces` kind.
- 2.2 (265-290): the narrowest-kind rule, order `exceptions`, `records`, `classes`; one class, one kind's settings.
- 2.3 (292-302): no `holds`; `holds: {}` refused; `{}` for a kind with no setting; null, `true` or a list refused;
  `records: {}` or `exceptions: {}` beside `classes` refused.
- 2.4 (304-329): the settings table; rule ids `holds`, `names`, `immutable`, `built-by` stay; scope, filters, mode
  and fix of each as today; a finding names the kind it read and the nested key; the four presence messages; `{held}`
  in the order of 2.1; the key of presence stays `parts.<part>.holds`.
- 2.5 (331-339): `functions` is top-level only; methods belong to their class.
- 2.6 (341-366): today's forms and their exact equals; the three named differences; every bundled part keeps its exact
  presence rule, so `review`'s ruled-out parts do not change.
- 2.7 (368-377): review and evals: `RULED_BY` unchanged; `_RULED = ("uses.never", "holds")`; the `alike` text.
- 2.9 (397-425): each kind needs the facts `supplies` gives; a kind listed that the language does not supply is refused
  at load; a kind not listed that the language does not supply is not read, and explain and the enforcement section
  say so in one line; a part of classes is not refused in a language without top-level functions.
- 2.10 (427-447): the refusals, verbatim, with their hints.
- 5.1 items 1-3, 6-8, 12, 14, 15 (664-706), only their `holds` parts; item 9 (`elsewhere.py` docstring); item 16
  (review unchanged).
- 5.2 (708-731), the `holds` rows; 5.3 (733-750), the `holds`, `immutable`, `names`, `built-by` docs lines, README and
  CHANGELOG `holds` lines; 5.4 (752-767), the `holds` tests; 5.5 (769-785), the `holds`, `names` and `built_by` lines.
- 6 (786-793): the retired entries; `profile explain <old key>` answers from the table.
- 7 step 4 (812-814): the extra gate (review's ruled-out parts the same; the golden docs move only the `immutable`
  line).
- Dodges (948-975) that apply, as the card lists them (section 8 below).

R3 rules inherited: **O4**, **O5** (lines 228-229): README and CHANGELOG lines of this step go under
`[Unreleased]`; **O8** (232): the golden docs `docs/{cli,web,xarch}/testing.md` are regenerated and their diff read,
never edited by hand, and move only where the note says; **O11** (235): `evals.py`'s `_RULED` and the `alike` text
of `keys.yaml` change in this step.

## 1. Goal

A part says what its files may define at the top level, and how each kind is held, in one map:

```yaml
services:
  holds: {classes: {names: "*Service", built_by: [bootstrap]}}
logic:
  holds: {functions: {}, records: {immutable: true}, exceptions: {}}
```

The flat keys `names`, `immutable`, `built_by` leave the part, and `holds` as one word (`classes`, `functions`) is
refused, each with a hint that writes the new form. For every bundled profile, what `check` finds is the same as
before, finding for finding, but for the key named in parentheses, the one wording change of 2.4, and the two
differences CS 2.6 names (lines 357-361): in a part of functions, `immutable` reads only records and `names` only
records and exceptions, so a plain class there, already listed by `holds`, is no longer listed a second time. What
`review` rules out is the same for every file.

## 2. The shape

### 2.1 The kinds

| Kind | What it is | Settings |
|---|---|---|
| `classes` | every class defined at the top level of a file, of any name, records and exceptions included | `names`, `immutable`, `built_by` |
| `functions` | every public function defined at the top level of a file, in no class (a method is not one) | `names` |
| `records` | a class the reader reports as a record (`class.record`; for Python, today's filter `record`, unchanged) | `names`, `immutable` |
| `exceptions` | a class that derives from one of the language's exceptions, or from a class of the app that does, however far (today's filter `exception`) | `names` |

Nothing a kind reads is new: `classes` and `functions` are what `holds: classes` and `holds: functions` read today,
`records` and `exceptions` are today's two exemptions of `holds: functions`.

### 2.2 Which kind a class is read as

A class is allowed in a part when one listed kind fits it. It is held to the settings of the narrowest listed kind it
fits, in the order `exceptions`, `records`, `classes`, and to no other kind's settings. So, for a part with
`holds: {classes: {names: "*Service"}, exceptions: {names: "*Error"}}`, an exception is named `*Error` and is not read
by `classes.names`; every other class is named `*Service`. For `holds: {classes: {names: "*Service"}}` alone, every
public class, exceptions and records included, is named `*Service`, as `names: "*Service"` reads today. A class that
fits both `exceptions` and `records` (CS "Not verified": not known to occur) is read as an exception when `exceptions`
is listed, else as a record when `records` is listed.

### 2.3 Absent, empty and bare

- No `holds`: the part may hold every kind; no `holds` rule and no setting runs for it (as today).
- `holds: {}`: refused (2.6).
- A kind written `{}`: the kind may sit there, with no setting. This is the common case.
- A kind written with no value (null), `true`, `false`, a string, a number or a list: refused (2.6).
- `records: {}` or `exceptions: {}` beside `classes`: refused (2.6). Beside `classes`, a narrower kind is written only
  to give it settings.

### 2.4 The settings and the rules they expand to

| Address | Takes | Rule id | Reads | Mode |
|---|---|---|---|---|
| `holds.classes.names` | a pattern or a list, `*` for any text | `names` | every public class held to `classes` (2.2) | fails |
| `holds.classes.immutable` | `true` or `false` (default) | `immutable` | every class held to `classes`, but an exception, as today | listed (weak) |
| `holds.classes.built_by` | `[<part>, ...]`, plain names of declared parts | `built-by` | constructions of a class held to `classes` | fails |
| `holds.functions.names` | a pattern or a list | `names` | every public top-level function | fails |
| `holds.records.names` | a pattern or a list | `names` | every public record held to `records` | fails |
| `holds.records.immutable` | `true` or `false` | `immutable` | every record held to `records` | listed (weak) |
| `holds.exceptions.names` | a pattern or a list | `names` | every public exception | fails |

Each keeps today's scope (`not package-file` where today's rule has it, none where today's `names` and `built-by` have
none), mode and fix. `immutable: false` configures nothing, as today. Rule ids, the rule book's group names
(`holds`, `names`, `built-by`, `immutable`), the README id list and `kernel/violations.py` do not change.

Findings, with the nested key in parentheses. Classes keep today's sentences word for word but for the key:

    {name} does not match {targets}, as every class of {where} must (parts.<part>.holds.classes.names)
    {name} does not match {targets}, as every function of {where} must (parts.<part>.holds.functions.names)
    {name} does not match {targets}, as every record of {where} must (parts.<part>.holds.records.names)
    {name} does not match {targets}, as every exception of {where} must (parts.<part>.holds.exceptions.names)
    {name} is a class that is no immutable record, but every class of {where} is one (parts.<part>.holds.classes.immutable)
    {name} is a record that is not immutable, but every record of {where} is one (parts.<part>.holds.records.immutable)
    {where} builds {name}, a class of {target_part}, which only {built_by} may build (parts.<target part>.holds.classes.built_by)

Fixes: the `names` fix stays for the three class kinds ("rename {name} to match {targets}, or move it to the part
whose kind of class it is"); for `functions.names` it reads "rename {name} to match {targets}, or move it to the part
whose kind of function it is". The `immutable` and `built-by` fixes stay word for word for both kinds that take them.

**Presence** (rule id `holds`, rule book group `holds`, mode listed, scope the part with `not package-file`). For a
part that writes `holds`, each top-level definition of a kind the part does not allow is listed:

    {name} is a function at the top level, but {where} holds {held} ({key})
    {name} is a class, but {where} holds {held} ({key})
    {name} is a record, but {where} holds {held} ({key})
    {name} is an exception, but {where} holds {held} ({key})

- A public top-level function, when `functions` is not listed (private top-level functions pass, as today).
- When `classes` is not listed, every top-level class (a private one too, as today) but those `exceptions` or
  `records` allows when listed. The sentence names the narrowest kind the class fits (an exception, a record, else a
  class), by the order of 2.2.
- `{held}` lists the kinds the part lists, in the order `classes`, `functions`, `records`, `exceptions`, joined as
  the docs join names ("classes"; "functions, records and exceptions"). `{key}` is `parts.<part>.holds`.
- The fixes stay as today: "make {name} a method of the class whose rule it is, or move it to
  {parts_holding_functions}" for a function; "move {name} to {parts_holding_classes}, or make what it does functions"
  for a class, a record or an exception. `parts_holding_functions` and `parts_holding_classes` now mean the parts that
  list `functions`, `classes` under `holds` (`sentences._holding`, `vocabulary.py` variable texts).

**Exact equals** (CS 2.6). For a part listing `{classes}` the group holds exactly today's `classes` rule (kind
`function`, keep `top-level`, `public`); for `{functions, records, exceptions}` exactly today's `functions` rule (kind
`class`, exempt `exception`, `record`) but for its sentence, which says `holds functions, records and exceptions`.
Equal means `Rule` equality, scope and filters and mode included, sayings aside for that one wording. A part's
presence rules read at most the kinds `function` and `class`; `elsewhere.broken` names each part once at most per file
(a part with both a function rule and a class rule is ruled out once, in the profile's order).

### 2.5 Language neutrality (CS 2.9)

Needs (`key_table.NEEDS`), each address the table's nested one:

| Address | Needs |
|---|---|
| `parts.<part>.holds` | `class`, `class.exception`, `class.record`, `function`, `function.top_level`, `public` (unchanged), of which `function.top_level` is read only when supplied (below) |
| `parts.<part>.holds.classes` | `class`, `public` |
| `parts.<part>.holds.classes.names` | `class`, `public` |
| `parts.<part>.holds.classes.immutable` | `class`, `class.exception`, `class.immutable` |
| `parts.<part>.holds.classes.built_by` | `class`, `call`, `import.resolved` |
| `parts.<part>.holds.functions` | `function`, `function.top_level`, `public` |
| `parts.<part>.holds.functions.names` | `function`, `function.top_level`, `public` |
| `parts.<part>.holds.records` | `class`, `class.record`, `function.top_level` (CS 2.9 line 410-411 and 5.4 line 763: a language without top-level functions is refused `records`) |
| `parts.<part>.holds.records.names` | `class`, `class.record`, `public` |
| `parts.<part>.holds.records.immutable` | `class`, `class.record`, `class.immutable` |
| `parts.<part>.holds.exceptions` | `class`, `class.exception` |
| `parts.<part>.holds.exceptions.names` | `class`, `class.exception`, `public` |

The setting rows are the facts their rules read in `test_needs_agree.py`'s `EVERY_KEY` profile (section 5); where a
setting's rule exempts a narrower listed kind (2.2) it reads that kind's fact too, and the row is the agreement test's
answer, not this table's, when they differ. Such an exemption never reads a fact silently unsupplied: the narrower kind
listed already needs it.

- A kind or setting listed whose needs the language does not supply is refused at load by the existing needs text,
  with the nested address (`parts.logic.holds.functions: its check reads function.top_level (...), which the language
  <name> does not supply: drop parts.logic.holds.functions, or check the app with a language whose reader supplies
  function.top_level`). The 4.3 walker reaches the kinds once `Key(PART, "holds", opens=PART_HOLDS)` and the kind
  keys exist. `profile_needs.short` hands every fact of `key.needs` to `shortfalls`, and `refused` turns each missing
  one into a problem, so it must leave out the read-when-supplied fact (below) when it builds that call: `profile_needs.py`
  changes there and in its docstring, and nowhere else.
- `function.top_level` on `parts.<part>.holds` is never a refusal. In a language whose data file lists `supplies` and
  leaves it out, the presence rule reads no functions (no rule of kind `function` is built for any part), and:
  - `xarch profile explain parts.<part>.holds --profile <file>` adds one line: `holds reads no top-level functions:
    the language <title> does not supply function.top_level`;
  - the enforcement section of `check` (text and JSON) lists, among its `approximate` items, one per part that writes
    `holds` without `functions`, key `parts.<part>.holds`, fact `function.top_level`, said as that same sentence.
  A language whose data file says nothing of `supplies` reads functions, as today.
- How the key table marks that one fact as "read when supplied" is the plan's choice (a field of `Key` beside `needs`
  is the expected form); the agreement test still compares the full set of six.

### 2.6 Refusals

Each is a problem of the profile at load, collected with every other problem of the part (never raised alone), with
the exit code of any profile that does not load and the file name prefix every profile problem has. Texts verbatim
(CS 2.10), the kind-specific examples of the fifth line set here:

| Written | Problem |
|---|---|
| `holds: functions` | `parts.logic.holds: 'functions': holds as one word was removed in 0.3.0: write holds: {functions: {}, records: {}, exceptions: {}}, which allows what holds: functions allowed` |
| `holds: classes` | `parts.domain.holds: 'classes': holds as one word was removed in 0.3.0: write holds: {classes: {}}` |
| `holds:` any other non-map (null, another string, a list, a number, `true`) | `parts.logic.holds: must be a map of kinds, such as {classes: {}}` |
| `holds: {}` | `parts.logic.holds: lists no kind: list the kinds the part may hold, or drop holds to allow every kind` |
| `holds: {function: {}}` | `parts.logic.holds: no kind 'function': use classes, exceptions, functions, records` (one problem per unknown kind, in the order written) |
| a kind not a map (null, `true`, `false`, a list, a string, a number) | `parts.logic.holds.functions: must be a map of its settings, {} for none, such as {names: "is_*"}`; the example per kind: `classes` `{names: "*Service"}`, `functions` `{names: "is_*"}`, `records` `{immutable: true}`, `exceptions` `{names: "*Error"}` |
| `functions: {immutable: true}` | `parts.logic.holds.functions: unknown key 'immutable': a setting of classes and records; use names` |
| `functions: {built_by: [...]}` | `parts.logic.holds.functions: unknown key 'built_by': a setting of classes; use names` |
| `records: {built_by: [...]}` | `parts.logic.holds.records: unknown key 'built_by': a setting of classes; use immutable, names` |
| `exceptions: {immutable: true}` | `parts.logic.holds.exceptions: unknown key 'immutable': a setting of classes and records; use names` |
| `exceptions: {built_by: [...]}` | `parts.logic.holds.exceptions: unknown key 'built_by': a setting of classes; use names` |
| any other unknown setting, e.g. `functions: {methods: x}` | the plain unknown-key problem: `parts.logic.holds.functions: unknown key 'methods': use names` |
| `exceptions: {}` beside `classes` | `parts.domain.holds.exceptions: says nothing beside classes, which already allows exceptions: give it a setting, or drop it` |
| `records: {}` beside `classes` | `parts.domain.holds.records: says nothing beside classes, which already allows records: give it a setting, or drop it` |
| `names` not a pattern or list of them | `<address>: must be a name pattern with `*` for any text, such as *Service, or a list of them` (today's text with "class " dropped) |
| an entry of `names` that is no pattern | `<address>: 'a b' is not a name pattern: write it with no space, `@`, `/` or `:`, `*` standing for any text` |
| `classes.immutable` not a bool | `parts.<p>.holds.classes.immutable: must be true or false: whether every class of the part, but an exception, is an immutable record` |
| `records.immutable` not a bool | `parts.<p>.holds.records.immutable: must be true or false: whether every record of the part is an immutable record` |
| `classes.built_by` wrong | the problems `ck.part_names` gives today, at `parts.<p>.holds.classes.built_by` |
| part key `immutable` | `parts.logic: unknown key 'immutable': moved in 0.3.0: write it under the kind it applies to, such as holds: {records: {immutable: true}}; use <known part keys>` |
| part key `names` | `parts.services: unknown key 'names': moved in 0.3.0: write it under the kind it names, such as holds: {classes: {names: "*Service"}}; use <known part keys>` |
| part key `built_by` | `parts.services: unknown key 'built_by': moved in 0.3.0: write holds: {classes: {built_by: [<part>, ...]}}; use <known part keys>` |

- The `built_by` hint writes `[<part>, ...]` where CS 2.10 line 440 writes `[...]`, matching the existing
  `no_callbacks` entry (4.2 spec 2.5): the table carries no substitution.
- A part writing several retired keys gets one problem each, in sorted order, as `ck.unknown_of` gives them; the
  `use ...` list of known part keys no longer names `immutable`, `names`, `built_by`.
- `classes:` or `functions:` written as part keys get no entry (they never shipped) and are refused as any unknown key.
- No old form is accepted as an alias, nor with a warning.

**The retired table** (`profile_keys.RETIRED`). It gains, on `PART`: `immutable`, `names`, `built_by` (the texts
above, after `unknown key '<name>': `); on the kind scopes: the five misplaced settings above (`a setting of classes
and records`, `a setting of classes`), as `Retired(PART, "never", ...)` is a misplaced entry today; and two **value
entries** for `holds` (`'classes'`, `'functions'`), each carrying the value it retires and the text after
`'<value>': `. A value entry is a new kind of entry (a `value` field on `Retired`, empty for a key entry, is the
expected form); `key_lookup.retired`, `retired_at` and `ck.unknown_of` read only key entries, so `holds` itself is never
reported as a retired key; the holds parser reads the value entries. `xarch profile explain parts.immutable`,
`parts.<part>.names`, `built_by` and `parts.holds.functions.immutable` answer from the table, as other retired keys do;
`profile explain parts.holds` answers from the catalogue.

### 2.7 Values carried

- `spec/domain/values.py`: `Part.holds` becomes the kinds listed with their settings, in the order of 2.1 whatever
  the order written (empty: no `holds`), each kind a frozen value with `names: tuple[str, ...]`, `immutable: bool`,
  `built_by: tuple[str, ...]` (the fields a kind cannot take stay at their defaults). `Part.names`, `Part.immutable`,
  `Part.built_by` go. The docstring says so.
- `spec/contract` `PartView`: the same change (its own view type of the kinds, or the same frozen value if the
  contract already shares domain values); `publishing.py` builds `PartView` positionally, so its argument list changes
  with it.
- `rules/domain/profile.py` `Profile`: `holds: dict[str, tuple[str, ...]]`, by part the kinds listed, in the order of
  2.1; `names: dict[str, dict[str, tuple[str, ...]]]`, by part then kind, the patterns; `immutable:
  dict[str, tuple[str, ...]]`, by part the kinds (`classes`, `records`) whose `immutable` is true; `built_by:
  dict[str, tuple[str, ...]]` keeps its shape (only `classes` takes it), so the filter `target-allows-under built_by`
  and `vocabulary.PART_KEYS` keep working unchanged. Docstring accordingly. `rules/adapters/spec_profile.py` builds
  them from `PartView`.
- `rules/application/logic/expansion.py`: `_holds`, `_names`, `_immutable`, `_built_by` per 2.4 and 2.2; `KEYS`
  replaces `parts.names` by `parts.holds.classes.names`, `parts.holds.functions.names`, `parts.holds.records.names`,
  `parts.holds.exceptions.names`; `parts.built_by` by `parts.holds.classes.built_by`; `parts.immutable` by
  `parts.holds.classes.immutable`, `parts.holds.records.immutable`, in the order of the book (`explained.general`
  strips the part step, so `profile explain <key> --rule` and `test_rule_ids` find them).
- `rules/application/logic/elsewhere.py`: code unchanged but for naming each part once (2.4); its docstring names
  kinds.

### 2.8 Evals (CS 2.7, R3 O11)

`evals._RULED = ("uses.never", "holds")`; the value `profile_parsing` hands `unlike` for `holds` is the kinds listed
with the `immutable` of each (so two parts differ in `holds` when they list other kinds, or set `immutable` on a kind
differently). The refusal: `evals.placement.alike[<i>]: <a> and <b> differ in <keys>: check tells them apart by rule,
so one file is not all that tells them apart: write the same uses.never, and list the same kinds with the same
immutable under holds, for each, or drop the group`. `evals.py`'s module docstring line 6 and the `accepts` of
`evals.placement.alike` in `keys.yaml` ("parts that differ in `uses.never` or `holds` (the kinds it lists and the
`immutable` of each)") follow. xarch's own `alike` groups stay accepted.

### 2.9 The key catalogue (`xarch/architectures/presets/format/keys.yaml`)

Entries `parts.<part>.immutable`, `parts.<part>.names`, `parts.<part>.built_by` go. `parts.<part>.holds` is rewritten,
and entries are added for each kind (`parts.<part>.holds.classes`, `.functions`, `.records`, `.exceptions`) and each
setting of 2.4, each with meaning, accepts and an example that loads merged into the smallest profile (fragments
`part`/`two` as today; `built_by` keeps `<<two>>`). The texts must say:

- `holds`: a map of kinds, each `{}` or its settings; a kind listed may exist in the part, one not listed may not;
  no `holds` allows every kind; a package file is exempt; presence is listed as `weak` and fails only
  `check --strict`; `classes` covers every class, records and exceptions included, and a class is held to the
  settings of the narrowest listed kind it fits (exceptions, records, classes); `records` or `exceptions` beside
  `classes` only with a setting; a kind the language does not supply cannot be listed, and a part that does not list
  `functions` in a language without `function.top_level` reads no functions.
- `functions`: public functions defined at the top level of a file, in no class (a method is not one, nor is the
  check-language kind `function`, which includes methods).
- `records` and `exceptions`: today's texts of the two exemptions (record: no method but the language's special ones,
  named in the return annotation of a top-level function of its file, as the reader reports it; exception: derives
  from a builtin exception, directly or through classes of the app).
- each setting: what today's flat entry says, of the kind it sits under (`immutable` under `classes`: but an
  exception; under `records`: every record).

The catalogue tests (every key of the table has an entry and an example; every `NEEDS` address is a key; examples
load) stay green; the table and this file change in one commit.

### 2.10 Generated docs (CS 5.3, R3 O8)

`docs_template._part_lines`:

- `holds`: one line, the parts grouped by what their `holds` allows (the presence of 2.4: `classes` listed, or else
  which of `functions`, `records`, `exceptions`). A group allowing classes only says, as today, "a file of {parts}
  defines classes, never a public function at the top level"; a group allowing functions, records and exceptions says,
  as today, "a file of {parts} defines functions, never a class (a private one too) but exceptions and the records
  its functions return". Any other group says "a file of {parts} holds {held} and no other kind at the top level". The
  groups come in the order: classes-only, then functions-records-exceptions, then the others in the order their first
  part is written. The line's tail is unchanged. For the bundled profiles the line is byte for byte today's.
- `immutable`: for the parts whose `classes.immutable` is true, today's line ("every class of {parts} is an immutable
  record, as the {title} data file marks one, or an exception; ..."); for the parts whose `records.immutable` is true,
  "`immutable`: every record of {parts} is an immutable record, as the {title} data file marks one; listed in the
  enforcement section, and fails `check --strict` only." Classes line first. In the three golden copies the bundled
  line becomes the records line: this is the one golden line that moves.
- `names`: one line per part and kind with patterns, in the order of 2.1: "every class of {part} is named ...",
  "every function of {part} at the top level is named ...", "every record of {part} is named ...", "every exception of
  {part} is named ...". When a narrower kind is listed beside `classes`, the classes line says "every class of {part}
  but its exceptions" (or "records", or "records and exceptions"). Bundled lines unchanged.
- `built-by`: reads `classes.built_by`; text unchanged.

Regenerate `docs/{cli,web,xarch}/testing.md` with the repo's command and read the diff: each file shows exactly one
line changed, `- `immutable`: every class of ... or an exception; ...` becoming `- `immutable`: every record of ...;
...` with the same parts. Any other moved line is a defect to fix in the template, not in the golden.

### 2.11 Profiles

Edited by hand (CS 2.6, 5.2), each `holds` value replaced and the flat keys folded into it:

| Where | Before | After |
|---|---|---|
| `architecture.yaml`, `cli.yaml`, `web.yaml`: domain, ports; `architecture.yaml` also profile-values, kernel | `holds: classes` | `holds: {classes: {}}` |
| logic, kernel-logic; `architecture.yaml` also reports | `holds: functions`, `immutable: true` | `holds: {functions: {}, records: {immutable: true}, exceptions: {}}` |
| services, controller | `holds: classes`, `names: "*Service"`/`"*Controller"`, `built_by: [bootstrap]` | `holds: {classes: {names: ..., built_by: [bootstrap]}}` |
| adapters | `holds: classes`, `built_by: [bootstrap]` | `holds: {classes: {built_by: [bootstrap]}}` |
| `tests/bootstrap/corpora/7cc6111.yaml`, `df537ca.yaml`, `stress.yaml`: every `holds: classes` with no flat key beside it | `holds: classes` | `holds: {classes: {}}` |
| the same three: every `holds: functions` (no corpus profile writes `immutable`) but stress's platform | `holds: functions` | `holds: {functions: {}, records: {}, exceptions: {}}` |
| the same three: services, controller, adapters | as the bundled rows | as the bundled rows |
| `stress.yaml` domain | `holds: classes`, `built_by: [...]` | `holds: {classes: {built_by: [...]}}` |
| `stress.yaml` adapters | `holds: classes`, `built_by: [...]`, `names: Fs*` | `holds: {classes: {built_by: [...], names: Fs*}}` |
| `stress.yaml` platform | `names: '*Reader'`, `holds: functions` | `holds: {functions: {}, records: {names: '*Reader'}, exceptions: {names: '*Reader'}}` |
| any part with `names`/`immutable`/`built_by` and no `holds` (none in these files; test profiles) | | `holds: {classes: {...}, functions: {}}` |

A `holds: functions` is always migrated with `exceptions: {}` (or `exceptions` with settings); never
`{functions: {}, records: {}}` alone. No bundled profile gains `functions.names`, `records.names`, `exceptions.names`
or a narrower kind beside `classes`.

### 2.12 Recorded corpora (CS 5.5)

Findings change by find and replace on exact anchored strings, reviewed line by line, the stress file decompressed to
scratch, edited, recompressed with `xz`, its text diff shown (counts fresh on this branch):

| Change | `7cc6111.json` | `df537ca.json` | stress |
|---|---|---|---|
| `is a class, but <where> holds functions (` to `is a class, but <where> holds functions, records and exceptions (` | 2 | 3 | 6 |
| `(parts.services.names)` to `(parts.services.holds.classes.names)` | 7 | 0 | 7 |
| `(parts.adapters.names)` to `(parts.adapters.holds.classes.names)` | 0 | 0 | 4 |
| `(parts.services.built_by)` to `(parts.services.holds.classes.built_by)` | 4 | 0 | 4 |
| `(parts.domain.built_by)` to `(parts.domain.holds.classes.built_by)` | 0 | 0 | 87 |
| `DataFileError does not match *Reader, as every class of platform/ must (parts.platform.names)` to `... as every exception of platform/ must (parts.platform.holds.exceptions.names)` | 0 | 0 | 1 |

Every other line keeps its text: every `(parts.<p>.holds)` stays; the fix texts "a part that holds functions: ..."
stay; lines naming source files (`...logic.names) (package-only)` and the like) are not touched (no blind replace of
`.names)`).

**One finding goes**, the only change of what a check finds in this step: `FileSystem does not match *Reader, as
every class of platform/ must (parts.platform.names)` in the stress recording. `FileSystem` is a plain class of a
part of functions; under the mapping of CS 2.6 `names` reads that part's records and exceptions only, and the class
stays listed by `holds` (`FileSystem is a class, but platform/ holds functions, records and exceptions`). CS 2.6
names this difference ("such a class was listed twice; now once"). It is recorded as `test_recorded_corpora.py`'s
docstring requires for a change of what a check finds: the oracle (`1f6b01b`) is extended in its own scratch worktree
by the same change (its `names` check, for a part whose `holds` is `functions`, reads only exceptions and records),
the stress corpus is recorded from it, and the recording is shown to differ from the current one by that one line;
the wording changes above are then applied by replace. The docstring's stress count becomes 1734 findings. The plan
names the exact oracle edit; nothing of the oracle is committed.

### 2.13 README and CHANGELOG (CS 5.3, R3 O4, O5)

- README: the part-key shape (line 118) writes `holds: {classes: {names, immutable, built_by}, functions: {names},
  records: {names, immutable}, exceptions: {names}}` and drops `immutable`, `names`, `built_by` from the part; lines
  158-161 (the facts `class.record`, `function.top_level`) name `holds` and its kinds; the rule table (308-312) keys
  `holds` by `parts.holds`, `immutable` by `parts.holds.classes.immutable`, `parts.holds.records.immutable`, `names`
  by `parts.holds.<kind>.names`, `built-by` by `parts.holds.classes.built_by`, and their "reads" texts name the kinds;
  the `alike` sentence (758) says "the same `uses.never`, and the same kinds with the same `immutable` under `holds`";
  "ruled out by `holds`" (762-782) gains one sentence: a file rules a part out when it defines at the top level a kind
  that part does not list. Line numbers drift: re-grep.
- CHANGELOG `## [Unreleased]`: under `### Changed`, `holds` is a map of kinds; `names`, `immutable`, `built_by` move
  under the kinds; `holds: classes`/`holds: functions` and the flat keys are refused with the new form; findings name
  the nested keys; a class in a part of functions is said to be where the part "holds functions, records and
  exceptions"; `immutable` in a part of functions reads its records only and `names` its records and exceptions; the
  `immutable` docs line says "every record of"; `alike` compares the kinds and their `immutable`. Under `### Added`:
  the kinds `records` and `exceptions` with their settings; `functions.names`; the narrowest-kind rule; a part that
  does not list `functions` in a language without `function.top_level` reads no functions, and says so.

## 3. Gates

Each passes on this branch alone, the full suite green: `uv run pytest -q` (over two minutes: in the background, read
at the end), `uv run xarch check`, `uv run xarch check --strict`, `uv run ruff check` (never `--fix`),
`uv run xarch profile check architecture.yaml`. No typecheck command exists.

Extra gate (CS 7 step 4): review rules out the same parts for every file before and after.

- `uv run xarch review --offline --all --max-files 500 --format json`, run on the base commit before any change and
  again at the end, diffed. With no kept answers in this worktree (`.xarch/` holds only `accepted.json` and
  `calibration.json`) it reads no file, so its diff is a smoke check only; the report says so.
- The gate's substance is test 21 below: for every app file of xarch, the parts `elsewhere.broken` names on
  `architecture.yaml`, computed through the rules controller before any change (recorded to scratch, not committed,
  by a script the plan writes) and after, are the same; and test 20 (the `holds` group's rules equal today's for the
  bundled profiles), which implies it for every file of every app.
- The golden docs: one line moved per copy (2.10).

## 4. Project rules

No comments in xarch's code (docstrings only); never `ruff --fix`; tests written first, each seen failing for the
right reason; examples simple, with absolute `app.` imports; recorded corpora (`tests/bootstrap/corpora/`) edited by
hand only, and only as 2.12 says; Python only in the reader adapter and the data files under
`xarch/architectures/presets/`; `.claude/` stays out of commits; nothing is pushed. A fact of `supplies` decides
language questions, never a test of the language's name.

## 5. Tests

Tiers (`docs/xarch/testing.md`): **unit** (`tests/modules/<module>/<part>/...`, `tests/kernel/...`: one module's
logic, no files); **integration** (`tests/modules/<module>/application/test_*.py`: a module's controller around the
fakes of `tests/fakes/`); **wired** (`tests/bootstrap/`, `tests/cli/`: the app as bootstrap wires it, real profile
files, the CLI); **guard** (`tests/architecture/`: xarch checked by its own profile). Written first.

New or changed, each with its tier and why:

1. Unit, `test_profile_parsing_substance.py`: the bundled forms parse to the kinds and settings of 2.7 (order of 2.1
   whatever the order written); every refusal of 2.6 with its exact text, several in one part collected together.
   Unit: parsing is a pure function of the mapping.
2. Unit, `test_retired_keys.py`: the three part keys and the five misplaced settings refused with their texts; the two
   value hints; `holds` never reported as a retired key; `profile explain` (via `key_lookup.retired_at`) answers the
   old part keys and the misplaced settings from the table, and `parts.holds` from the catalogue.
3. Unit, the `use ...` lists of known part keys (`test_profile_parsing.py`, `test_profile_parsing_tests.py`,
   `test_never_use.py`, `test_retired_keys.py`, `tests/bootstrap/test_architecture_files.py`): drop `immutable`,
   `names`, `built_by`, each edited by hand.
4. Unit, `test_profile_needs.py` with a language data file that leaves `function.top_level` out of `supplies` (in
   `tests/fakes/languages/` or the test's own temp file, as the file already does for other facts): `holds:
   {functions: {}}` and `holds: {records: {}}` refused with the needs text at the nested address; `holds: {classes:
   {}}` not refused; a language without `class.exception` refused `holds.exceptions`. Unit: needs are computed from
   the mapping and the language.
5. Unit, `tests/modules/spec/domain/` key-table tests (`test_profile_keys.py`): the scopes, the rows and the `NEEDS`
   of 2.5, `function.top_level` marked read-when-supplied on `parts.<part>.holds` only.
6. Unit, `tests/modules/rules/application/logic/test_holds.py`: the presence rules of 2.4 for `{classes}`,
   `{functions}`, `{functions, records}`, `{functions, records, exceptions}`, `{records}`, `{classes, exceptions}`,
   with the four sentences and `{held}`; a private top-level function passes a part of classes; a private class is
   listed in a part of functions; a record and an exception in a part of `functions` alone are listed as "a record",
   "an exception"; a package file is not read. Unit: rules over hand-built facts.
7. Unit, same file: in a language whose `supplies` leaves out `function.top_level`, a part of classes gets no
   function rule; one whose data file says nothing of `supplies` gets it.
8. Unit, `test_names.py`: `classes.names` reads every public class (exceptions and records too) when no narrower kind
   is listed; beside `exceptions: {names: "*Error"}` an exception is held to `*Error` only and a plain class to the
   classes pattern only (2.2); `functions.names` lists a public top-level function that does not match and passes a
   method and a private function; `records.names`, `exceptions.names` read their kind only; the sentences and keys of
   2.4.
9. Unit, the `immutable` tests (in `test_expansion.py` or a new `test_immutable.py` beside `test_names.py`):
   `classes.immutable` reads every class but an exception (today's rule, nested key); `records.immutable` reads
   records only, so a plain class of a part of functions is not listed by it; beside `records` listed with its own
   `immutable`, `classes.immutable` does not read records.
10. Unit, `test_built_by.py`: the nested key in the sentence; same constructions found and kept; a class held to
    `exceptions` beside `classes` is not held to `classes.built_by` (2.2).
11. Unit, `test_expansion.py`, `test_expandable.py`, `test_rule_ids`-style tests and `explained` tests: `KEYS` of 2.7;
    `general` maps `parts.services.holds.classes.names` to `parts.holds.classes.names`.
12. Unit, `tests/modules/rules/adapters/test_spec_profile.py`: `PartView` with kinds gives `Profile.holds`, `names`,
    `immutable`, `built_by` of 2.7.
13. Unit, `test_docs_template.py`: the `holds` line for the two bundled groups byte for byte today's, and the general
    form for another; both `immutable` lines; the `names` lines per kind, with the "but its exceptions" form;
    `built-by` unchanged.
14. Unit, `test_evals.py`: `_RULED` of 2.8; two parts that list the same kinds with the same `immutable` stay alike;
    a different kind, or a different `immutable` on `records`, refused with the text of 2.8.
15. Unit, `tests/modules/spec/application/test_explain.py` (or where explain is tested): `profile explain
    parts.holds.functions` and each setting answer from the catalogue; the one line of 2.5 for a profile whose
    language lacks `function.top_level`, and none otherwise.
16. Integration, `tests/modules/rules/application/test_holds.py`: the holding service on given files rules out a part
    of functions for a file defining a public class and not for one defining only functions, records and exceptions;
    a part is named once when a file breaks both a function rule and a class rule.
17. Integration (the enforcement tests under `tests/modules/rules/application/`): the `approximate` item of 2.5 for a
    part without `functions` in a language lacking `function.top_level`.
18. Wired, `tests/bootstrap/test_needs_agree.py`: `EVERY_KEY` writes `holds` on `core` as `{functions: {names: "*"},
    records: {names: "*", immutable: true}, exceptions: {names: "*"}}` and on `api` as `{classes: {names: "*",
    immutable: true, built_by: [core]}}`; both tests stay green (every expanded key has rules; table and rules agree).
19. Wired, `tests/bootstrap/test_key_catalogue.py` / `tests/modules/spec/application/logic/test_key_catalogue.py`:
    green with the new entries; every example loads.
20. Wired, `tests/bootstrap/test_bundled_guards.py` or a new `tests/bootstrap/test_bundled_holds.py`: for `cli.yaml`,
    `web.yaml` and `architecture.yaml`, `book(profile)["holds"]` equals, part by part, the `Rule` today's code builds
    for the part's 0.2.0 form (written out in the test as literal rules, the one sentence wording aside); `names`,
    `immutable` and `built-by` rules read the same kinds with the nested keys.
21. Wired, `tests/bootstrap/test_review_reading.py` (or beside it): for every app file of xarch on `architecture.yaml`,
    the parts the holding service rules out equal a list recorded in the test (the before-run of section 3, literal in
    the test, for the files that rule any part out). Wired: it runs the real wiring on real files.
22. Wired, the CLI refusals (`test_profile_file.py` or `test_profile_check.py` under `tests/bootstrap/`): a profile
    file writing `holds: functions` and one writing `names:` on a part exit as any profile that does not load, with
    the texts of 2.6.
23. Wired, `tests/bootstrap/test_recorded_corpora.py` (data changed, test unchanged but its docstring count): the
    three recordings match with only the lines of 2.12 changed.
24. Wired, `tests/bootstrap/test_docs_templates.py`: the three golden copies match after regeneration with the one
    moved line each.
25. Wired and unit, every other inline profile or keyword field writing `holds`, `names`, `immutable`, `built_by` on a
    part (`test_profile_check`, `test_checks_of_its_own`, `test_check_enforcement`, `test_written_rules`,
    `test_rule_ids`, `test_where`, `test_profile_explain`, `test_profile_file`, `test_profile_new`, `test_skeletons`,
    `test_imports`, `test_review_evals`, `test_review_reading`, `tests/modules/rules/builders.py`, `tests/cli/reports/*`,
    `tests/modules/review/...`; re-grep): rewritten to the map by 2.11's mapping, each by hand. `tests/fakes/*`
    `immutable` (the language's record marks) is no profile key and stays.
26. Guard, `tests/architecture/test_self_check.py`: unchanged, green on the edited `architecture.yaml`.

## 6. Risks the plan must settle

- `classes.built_by` beside a listed narrower kind (2.2, test 10) needs the construction rule to tell whether the
  built class is an exception or a record. If no fact of a construction reaches the built class's traits, the plan
  says so before writing code and escalates; it must not hold such a class to `built_by` silently, nor drop the
  narrowest-kind rule for `built_by`.
- `Saying` conditions choose among the four presence sentences; the class rule's sentence for a record or an exception
  reads `record`/`exception` only when that kind is unlisted, so it reads no fact a listed kind does not already
  need. The plan confirms the rule's derived needs still equal the `parts.<part>.holds` row in `EVERY_KEY` (test 18).
- Positional construction of `PartView` (`publishing.py`) and of `Part` in tests: every caller re-checked.

## 7. Out of scope

- The `imports` group (`may_import`, `must_import`, `libraries`, `types_only` on parts and tiers; card 4.5, release
  steps 13-14) and the docs `rules` line; `types_only` and `shared` stay flat on the part.
- An `interfaces` kind, a `methods` setting, `built_by` on records or exceptions, `immutable` on exceptions or
  functions.
- Adding `functions.names`, `records.names`, `exceptions.names` or a narrower kind to a bundled profile.
- Internal renames (release step 15); part references (release step 24); `looseness.py` (no `holds` key read there).
- `review`'s code (`HOLDS`, `RULED_BY`, `ruling.py`, `eval_report.py`), rule ids, `where`'s JSON fields.
- Historical docs under `docs/superpowers/plans` and `docs/superpowers/specs`.

## 8. Dodges (card; CS 948-975)

Not done, and each test above would catch it: accepting the old flat keys or `holds: classes` as aliases or with a
warning; keeping `classes:` or `functions:` as part keys; reading the kinds as disjoint while the explain text says
`classes` covers all; holding one class to two kinds' settings; changing what a kind reads (counting private top-level
functions, allowing private classes in a part of functions, redefining `record`); a setting a kind cannot mean;
migrating `holds: functions` without `exceptions`; a listed kind the language does not supply loading in silence, or
refusing a part of classes in a language with no top-level functions; changing review's ruled-out parts or the
placement record; regenerating the golden docs without reading the diff; a blind replace of `.names)` in findings, or
dumping findings from the code under test; loosening the "use ..." lists.
