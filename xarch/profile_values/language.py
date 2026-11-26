"""The language of the app as a check reads it: spec reads it from the language's data file, the rules module checks
the source with it."""
from __future__ import annotations

import re
from dataclasses import dataclass

from xarch.kernel.placement import Marks
from xarch.profile_values.capabilities import Supply

NOTHING = "nothing"
"""The one value of the data file's `unannotated`: a method with no return annotation gives no value."""


@dataclass(frozen=True)
class RecordMark:
    """What makes a class an immutable record in the language, in one of four forms, exactly one of base, decorator,
    fields and type given: an outside name among its bases (base, as its steps); a decorator (decorator, as its steps)
    called with each keyword of keywords, each (name, value as written) (none: however it is written, bare or called);
    a keyword that marks every field (fields); or a wrapper type (type, as its steps)."""
    base: tuple[str, ...] = ()
    decorator: tuple[str, ...] = ()
    keywords: tuple[tuple[str, str], ...] = ()
    fields: str = ""
    type: tuple[str, ...] = ()


@dataclass(frozen=True)
class InterfaceMark:
    """What makes a class an interface in the language: an outside name among its bases (base, as its steps), or a
    keyword it is declared with or carries (keyword); exactly one of the two is given."""
    base: tuple[str, ...] = ()
    keyword: str = ""


LINE = "line"
"""The kind of a comment form that runs from its marker to the end of its line."""
BLOCK = "block"
"""The kind of a comment form that runs from its opening to its closing."""


@dataclass(frozen=True)
class CommentForm:
    """One form a comment of the language is written in: its kind (LINE, BLOCK or "doc"), the marker that opens it, and
    the one that closes it ("" for a line form, and for a doc form that runs to the end of its line)."""
    kind: str
    opening: str
    closing: str = ""


SPEC_FORMS = ("keyword", "position", "type_argument")
"""The ways a call that builds a mock names its spec, in the order a problem lists them: a keyword argument, the
positional argument at a place, the type argument at a place. They are the keys of an entry of a profile's
`testing.mocks.specs` and of the data file's `writing.specs`."""


@dataclass(frozen=True)
class SpecWriting:
    """How the language writes a call that builds a mock and names its spec, one one-line template per way of naming it
    (empty: the file does not write it): keyword, {callee}, {keyword} and {value} standing for what is called, the
    keyword and the spec; position and type_argument, {callee}, {before} and {value} standing for what is called, the
    places before the spec's own and the spec."""
    keyword: str = ""
    position: str = ""
    type_argument: str = ""


@dataclass(frozen=True)
class Writing:
    """How the language writes a row of a table of cases, and a call that builds a mock, as its data file's `writing`
    says it, each template one line (empty: the file does not write it): call, a row that is a call, {callee} standing
    for what it calls; keyword, a row call whose id a keyword gives, {callee}, {keyword} and {text} standing for what
    it calls, the keyword and the id's text; field, a literal row whose id a field gives, {field} and {text} standing
    for the field and the id's text; specs, how a call that builds a mock names its spec (see SpecWriting). A template
    is filled by `row_call`, `keyword_id`, `field_id` and `spec`: each placeholder replaced in one pass, any other
    text, braces included, kept as it is."""
    call: str = ""
    keyword: str = ""
    field: str = ""
    specs: SpecWriting = SpecWriting()

    def row_call(self, callee: str) -> str:
        """The `call` template for a row that calls callee."""
        return self._fill(self.call, callee=callee)

    def keyword_id(self, callee: str, keyword: str, text: str) -> str:
        """The `keyword` template for a row that calls callee, its id given by keyword with the value text."""
        return self._fill(self.keyword, callee=callee, keyword=keyword, text=text)

    def field_id(self, field: str, text: str) -> str:
        """The `field` template for a literal row, its id given by field with the value text."""
        return self._fill(self.field, field=field, text=text)

    def writes_spec(self, form: str) -> bool:
        """Whether the language writes how a call names its spec in form, one of SPEC_FORMS."""
        return bool(getattr(self.specs, form))

    def spec(self, form: str, callee: str, value: str, keyword: str = "", place: int = 0) -> str:
        """The `specs` template of form, one of SPEC_FORMS, for a call of callee whose spec is value: given by keyword
        for a keyword form, else at place, from 0, each place before it written `..., `."""
        held = {"keyword": keyword} if form == SPEC_FORMS[0] else {"before": "..., " * place}
        return self._fill(getattr(self.specs, form), callee=callee, value=value, **held)

    @staticmethod
    def _fill(template: str, **values: str) -> str:
        """The template with each `{<name>}` of the values replaced in one pass, so that a value holding a
        placeholder is not filled again."""
        return re.sub("{(" + "|".join(values) + ")}", lambda found: values[found.group(1)], template)


@dataclass(frozen=True)
class Worked:
    """How the language writes the code of the checks written for the explanation, as its data file's `worked` says
    it, each template one line (empty: the file does not write it, and the token is left as written): subclass, a
    class that derives from a base, {name} and {base} standing for the class's name and its base's; function, a function
    of one parameter, {name} and {parameter}; defaulted, the same whose parameter has a default, {value}; annotated,
    the same whose parameter has an annotation, {annotation}; returning, a function of no parameter with a return
    annotation, {name} and {returns}; keyword_call, a call passing one keyword argument, {callee}, {keyword} and
    {value}; and positional_call, a call passing one positional argument, {callee} and {value}."""
    subclass: str = ""
    function: str = ""
    defaulted: str = ""
    annotated: str = ""
    returning: str = ""
    keyword_call: str = ""
    positional_call: str = ""


@dataclass(frozen=True)
class CheckedLanguage:
    """The language of the app as a check reads it: how a message names it, the endings of a source file's name
    (extensions, in the order written; a message prints the first), the files that stand for the folder holding them
    (package_files; none: no file does), the marks that make a class an interface (interface: an outside name
    among its bases, or a keyword it is declared with or carries), the dotted names of what imports by a name worked
    out when the code runs, and of what reads a member of an object by a name worked out when the code runs
    (dynamic_attributes); and the tokens of its code: what a private name starts with, the pattern of a special
    name (special: a regular expression the whole name matches), the special method calling an instance runs, the
    return annotations of no value as its reader writes them (nothing), whether a method with no return annotation
    gives none (unannotated: nothing when it does; empty when the data file does not say), the forms a comment is
    written in (comments, in the order written: a line form runs from its marker to the end of its line, a block form
    from its opening to its closing, and a doc form, a comment the language keeps its documentation in, the same, an
    empty closing being the end of its line; none: the language has no comments), the comments its tools read (after
    the marker of a comment of any form, a space standing for any spaces), how line 1 names the program that runs the
    file, how line 1 or 2 declares the encoding (a regular expression, after the marker of a comment), and
    the keywords of the statements that branch and of the expressions that choose between values
    (branching_expressions); and what makes a class an immutable record (immutable). An empty token: the language
    has none. supplies are the facts its reader supplies, each graded (None: its data file does not say); importing
    is how a file imports a name from another file of the app, {dotted} standing for that file's dotted path and
    {name} for the name (empty: its data file does not say); writing is how it writes a row of a table of cases (see
    Writing), and worked how it writes the code of the checks written for the explanation (see Worked); names is the
    pattern of a name the language allows, a regular expression (empty: its data file gives none); package is the
    pattern of what an import names from outside the app as one step, and member the text that joins a package to a name
    in it in a profile's lists (both empty: its data file does not say, and an outside name is then its whole text);
    standard_modules are the top-level modules of its standard library, which the reader is handed to mark an import
    of one: spec fills them from the data file's lists or from the runtime (empty: no module is standard)."""
    title: str = ""
    extensions: tuple[str, ...] = ()
    package_files: tuple[str, ...] = ()
    interface: tuple[InterfaceMark, ...] = ()
    dynamic: tuple[tuple[str, ...], ...] = ()
    dynamic_attributes: tuple[tuple[str, ...], ...] = ()
    private: str = ""
    special: str = ""
    call: str = ""
    nothing: tuple[str, ...] = ()
    comments: tuple[CommentForm, ...] = ()
    directives: tuple[str, ...] = ()
    shebang: str = ""
    encoding: str = ""
    branching: tuple[str, ...] = ()
    supplies: tuple[Supply, ...] | None = None
    importing: str = ""
    immutable: tuple[RecordMark, ...] = ()
    branching_expressions: tuple[str, ...] = ()
    names: str = ""
    package: str = ""
    member: str = ""
    unannotated: str = ""
    standard_modules: frozenset[str] = frozenset()
    writing: Writing = Writing()
    worked: Worked = Worked()

    @property
    def marks(self) -> Marks:
        return Marks(self.extensions, self.package_files)

    @property
    def extension(self) -> str:
        """The first ending of a source file's name, the one a message prints; "" when the language gives none. Never
        what decides whether a file is a source file: every ending does (see marks)."""
        return self.extensions[0] if self.extensions else ""

    @property
    def package_file(self) -> str:
        """The first file that stands for its folder, the one a message prints and init writes; "" when the language
        has none."""
        return self.package_files[0] if self.package_files else ""

    @property
    def comment(self) -> str:
        """The marker the docs and `%comment%` print: the first line form's, else the first block form's opening; ""
        when the language has neither. A doc form's opening never is."""
        line = next((form.opening for form in self.comments if form.kind == LINE), "")
        return line or next((form.opening for form in self.comments if form.kind == BLOCK), "")

    def is_special(self, name: str) -> bool:
        """Whether a name is one the language reserves for itself: special, a regular expression, matches the whole
        name; no name is when the language gives none."""
        return bool(self.special) and re.fullmatch(self.special, name) is not None

    def gives_nothing(self, returns: str | None) -> bool:
        """Whether a method whose return annotation is returns, as the reader writes it (None: it has none), gives no
        value: its annotation is one nothing lists, or it has none and unannotated says so."""
        return returns in self.nothing if returns is not None else self.unannotated == NOTHING
