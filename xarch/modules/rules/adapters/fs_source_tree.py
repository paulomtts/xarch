"""SourceTree on the local filesystem for Python, the one language xarch reads: lists the files whose name ends in one
of the endings it is given, and parses one as Python with ast and tokenize, never running it.

A name in a call or a class base is read as Python scopes it: through the innermost function, lambda or
comprehension that binds it (a class body only for its own statements), then the module. It is a Ref only when that
scope binds it with an import, however written, that the reader follows, and nothing else; a parameter, an
assignment, a def or a second, different binding of the same name in that scope makes it None, and so does a name no
scope binds.

A relative import is followed from the package of the file it is in, the root's name then the folders below it (a
package file stands for its own folder): up one folder fewer than its dots, then down its module's steps, to a `.py`
file or a folder of that name, looked up on the file system and never opened or run. One that climbs above the root,
or names nothing below it, binds None and is marked unresolved; so is every relative import of a text read with no
file. A name a relative import binds is bound none of its steps, since that import names none of them from the top.

An absolute import is of the standard library when its first step is one of the standard modules the reader is
handed, which spec reads from the language's data file or from the interpreter running xarch; a relative import
never is, nor one that names no module.

A call of a method of a parameter, `<parameter>.<method>(...)`, is listed apart, whatever the parameter's name, when
the nearest scope binding the name binds it as a parameter of its function and nothing else binds it there: a
parameter the body rebinds (an assignment, a loop, an import, a def, `global`) is not read, nor is a call of the
parameter itself, a call deeper in a chain (`p.a.b()`) or a method of any other expression.

A file also lists the names it defines at module level as functions: a name one `def` (or `async def`) binds in the
module's own scope, a branch of an `if` or `try` included, and nothing else binds (no second def, import,
assignment, class or `global`), so that the name is a function and not a class or a value.

A use is every name read in the file's code, called or not, and every chain of attributes on one (`a.b.c` once, as
the whole chain), read the same way; a name no scope binds that is one of Python's builtins is the use
("builtins", <name>), unless the file holds a star import, which might bind it. An annotation is read for uses too, a
parameter's, a return's and an annotated assignment's, in the scope around what it annotates; the text of a string
annotation is not.

A call of a parameter itself by its bare name, `<parameter>(...)`, is listed as a callback under the same condition,
with the name of the function whose parameter it is; the first parameter of a function defined in a class body is
marked as its receiver, unless the function is decorated `staticmethod`, and a parameter whose annotation is
`Callable` (of typing or collections.abc, read through the import that binds it; alone, subscripted, in a `|` union,
inside `Optional[...]`, or as the text of a string annotation) is marked as annotated callable.

A class is an exception when one of its bases is the bare name of a builtin exception that the module does not bind
(and the file holds no star import), or a class defined before it in the file that is one.

A file also lists every name it mentions (`named`), by its last step alone, in code and in annotations, a string
annotation read as the expression it holds, and every imported name; a class lists the same for its bases and body.

A function lists each statement of its body that opens a block, by its keyword, and each conditional expression
(`a if c else b`), by `if`, nested ones included.

A function lists how many statements its body holds, nested ones included, and how many of them are inert: they do
nothing (a docstring, `pass`, a bare `...`). Its shape is the fingerprint the no-duplicates guard compares, a
definition of this reader, per language, since only the reader of a language can say when two bodies are the same
code: its body without the docstring, written as a tree in which every local name (a parameter, or a name the body
binds in any way) is replaced by its number in order of appearance, so that formatting and local names do not show;
what it calls, reads (attributes, globals), its constants, its keyword names, async or not, and how many parameters
of each kind it has, do show. Its annotations, defaults and decorators are no part of it; a body of inert statements
alone has no shape.

A function records whether it is decorated, its parameters by kind, and, when its whole body, a docstring left out, is
one `return` or bare statement of one call, perhaps awaited, that call: its callee as a chain of names, and each of its
arguments as the bare name it passes (a starred one marked), or as nothing for any other expression. A body that is one
`return` of a chain of attributes read on such a call (`return self.repo.get(id).name`) records the call and those
attributes. A method forwards to that call's callee when it has no decorator, is no special method (a name between
`__`), and its whole body is that call on a chain of at least two attributes of its first parameter
(`self.repo.get(...)`), passing each of its other parameters straight through (a `*args` as `*args`, a `**kwargs` as
`**kwargs`) and nothing else.

A call whose callee is an attribute of an expression, `<expr>.<name>(...)`, and is no Ref is listed as a method call by
the attribute's name, marked held when the expression is the first parameter of the method the call lies in (not a
staticmethod's; also inside a function nested in that method) or a chain of attributes on it.

A class is an immutable record when a mark it is given (the language's data file's `immutable`) names one of its bases,
or one of its decorators, by the dotted path its name reaches (read as a call's callee is), called with each keyword
the mark is written with, its value as written (`ast.unparse`); a mark written with keywords names no base.

A class is an interface when a mark it is given (the language's data file's `interface`) is a base mark whose path is
one of its bases, read as for an immutable record (a subscripted base, `Protocol[T]`, by what it subscripts; an alias
by the path it reaches). A keyword mark marks no class: Python declares no class with a keyword.

A class lists its fields: the names a statement of its own body annotates (`x: int`, `y: str = ""`), in order, but one
annotated `ClassVar` (alone or subscripted, by its bare name or as an attribute, or as a string annotation); and the
type of each, its annotation as written (`ast.unparse`, a string annotation by its text).

A file lists the names it binds at the top level by an assignment (`X = ...`, `X: T = ...`, each name of `X, Y = ...`,
`type X = ...`), in a branch of the top level too, but not in a function or class; each with the names its statement
mentions (as a function's names below). A function lists every name its definition mentions, by its last step: names
and attributes in its decorators, its signature and its body, and the names inside a string that is an annotation;
another string's text is no mention.

A file also lists each name a `from` import takes whose bound name (its alias, when it has one) nothing else in the
file mentions as a name, in code or in an annotation (a string annotation read): a name that is only re-exported, such
as one `__all__` lists as text, or not used at all.
"""
from __future__ import annotations

import ast
import builtins
import copy
import hashlib
import io
import tokenize
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from xarch.kernel.source import Import, Unparsable
from xarch.modules.rules.domain.parsed import (
    Call,
    Callback,
    Class,
    Comment,
    Constant,
    Function,
    Method,
    MethodCall,
    ParameterCall,
    Ref,
    Row,
    Signature,
    SoleCall,
    SourceFile,
    Table,
    Union,
    Use,
)
from xarch.modules.rules.domain.published import CLASS, FUNCTION, METHOD, Piece
from xarch.platform.filesystem import FileSystem
from xarch.profile_values.language import InterfaceMark, RecordMark
from xarch.profile_values.testing import CaseTable


class FsSourceTree:
    def __init__(self, fs: FileSystem):
        self._fs = fs

    def absent(self, roots: Iterable[Path]) -> list[Path]:
        return [root for root in roots if not self._fs.is_dir(root)]

    def paths(self, root: Path, extensions: tuple[str, ...]) -> list[tuple[str, ...]]:
        return sorted({f.relative_to(root).parts for extension in extensions for f in self._fs.files(root, f"*{extension}")})

    def read(self, root: Path, paths: list[tuple[str, ...]], table: CaseTable | None = None,
             immutable: tuple[RecordMark, ...] = (), interface: tuple[InterfaceMark, ...] = (), *,
             standard: frozenset[str]) -> list[SourceFile]:
        """Each file below root, read as UTF-8 and parsed; one that is not UTF-8, or cannot be read, holds why as its
        error, as one that does not parse does."""
        found: list[SourceFile] = []
        for path in paths:
            name = root.joinpath(*path).relative_to(root.parent).as_posix()
            try:
                text = self._fs.read_text(root.joinpath(*path))
            except UnicodeDecodeError as e:
                found.append(SourceFile(name, path, (), error=Unparsable(
                    0, f"not UTF-8 text (byte {e.object[e.start]:#04x} at offset {e.start} cannot be decoded)",
                    unreadable=True)))
                continue
            except OSError as e:
                found.append(SourceFile(name, path, (), error=Unparsable(
                    0, f"cannot be read ({e.strerror or e})", unreadable=True)))
                continue
            found.append(_parsed(name, path, text, table, immutable, interface, standard,
                                 _Where((root.name, *path[:-1]), root, self._fs)))
        return found

    def existing(self, paths: Iterable[Path]) -> frozenset[Path]:
        return frozenset(path for path in paths if self._fs.exists(path))

    def text(self, path: Path) -> str | None:
        return self._fs.read_text(path) if self._fs.is_file(path) else None

    def parsed(self, text: str, standard: frozenset[str]) -> SourceFile:
        return _parsed("", (), text, None, (), (), standard)

    def resolved(self, folder: Path, path: Path) -> Path:
        return self._fs.real(folder / path)


@dataclass(frozen=True)
class _Where:
    """Where a file read below a root lies, so that its relative imports can be followed: the steps of the package it
    is in, the root's name first (a package file stands for its own folder), the root, and the file system the places
    below the root are looked up on."""
    package: tuple[str, ...]
    root: Path
    fs: FileSystem

    def target(self, level: int, module: tuple[str, ...]) -> tuple[str, ...] | None:
        """The place a relative import of that many dots names, the root's name first: up one folder fewer than its
        dots, then down module's steps; None when it climbs above the root or names neither a file nor a folder."""
        kept = len(self.package) - (level - 1)
        if kept < 1:
            return None
        steps = (*self.package[:kept], *module)
        return steps if self._exists(steps[1:]) else None

    def _exists(self, steps: tuple[str, ...]) -> bool:
        """Whether steps below the root name a folder or a `.py` file; a place the file system cannot look up is not
        there."""
        place = self.root.joinpath(*steps)
        try:
            return self.fs.is_dir(place) or (bool(steps) and self.fs.is_file(place.with_name(f"{steps[-1]}.py")))
        except OSError:
            return False


class _Relative(tuple):
    """A path a relative import binds: read as any other, but bound none of its steps, since the import's line names
    none of them from the top (see the module's docstring)."""


def _parsed(name: str, path: tuple[str, ...], text: str, form: CaseTable | None, marks: tuple[RecordMark, ...],
            interface: tuple[InterfaceMark, ...], standard: frozenset[str], where: _Where | None = None) -> SourceFile:
    try:
        tree = ast.parse(text)
        comments = _comments(text)
    except SyntaxError as e:
        return SourceFile(name, path, (), error=Unparsable(e.lineno or 0, e.msg))
    except (tokenize.TokenError, IndentationError) as e:
        return SourceFile(name, path, (), error=Unparsable(0, str(e)))
    calls = _Calls(_BUILTINS if not _star_import(tree) else frozenset(), where)
    calls.visit(tree)
    return SourceFile(name, path, tuple(_imports(tree, standard, where)), comments, _functions(tree, form, where),
                      tuple(_unions(tree)), calls=tuple(calls.found), classes=tuple(_classes(tree, marks, interface, where)),
                      uses=tuple(calls.uses), parameter_calls=tuple(calls.parameter_calls),
                      module_functions=_module_functions(tree), named=_named(tree), callbacks=tuple(calls.callbacks),
                      method_calls=tuple(calls.method_calls), constants=tuple(_constants(tree)),
                      unmentioned=_unmentioned(tree), pieces=_pieces(tree))


def _pieces(tree: ast.Module) -> tuple[Piece, ...]:
    """Each function and class at the top level, in a branch of the top level too, and each method of such a class,
    spanning its decorators, in the order of their first line."""
    found: list[Piece] = []
    for node in _top_level(tree.body):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            found.append(_piece(node, FUNCTION))
        elif isinstance(node, ast.ClassDef):
            found.append(_piece(node, CLASS))
            found += [_piece(n, METHOD, node.name) for n in _top_level(node.body)
                      if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    return tuple(sorted(found, key=lambda piece: (piece.first, piece.kind != CLASS)))


def _top_level(body: list[ast.stmt]) -> list[ast.stmt]:
    """The statements of a body and of the branches of its `if` and `try` statements, not those of a nested scope."""
    found: list[ast.stmt] = []
    for node in body:
        if isinstance(node, ast.If):
            found += _top_level(node.body) + _top_level(node.orelse)
        elif isinstance(node, (ast.Try, ast.TryStar)):
            found += _top_level(node.body) + [n for h in node.handlers for n in _top_level(h.body)]
            found += _top_level(node.orelse) + _top_level(node.finalbody)
        else:
            found.append(node)
    return found


def _piece(node: ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef, kind: str, owner: str = "") -> Piece:
    first = min([node.lineno, *(d.lineno for d in node.decorator_list)])
    return Piece(kind, node.name, first, node.end_lineno or node.lineno, owner)


def _module_functions(tree: ast.Module) -> tuple[str, ...]:
    """The names a `def` at module level binds, and nothing else binds, in the order they are defined."""
    names = _bound(tree)[2]
    return tuple(dict.fromkeys(n.name for n in _own(tree.body)
                               if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name in names))


_BUILTINS = frozenset(name for name in vars(builtins) if not name.startswith("__") or name == "__import__")
"""Python's builtins, as a bare name reads them; the dunder names the builtins namespace holds about itself left out."""


def _star_import(tree: ast.AST) -> bool:
    return any(isinstance(n, ast.ImportFrom) and any(a.name == "*" for a in n.names) for n in ast.walk(tree))


def _from(node: ast.ImportFrom, where: _Where | None) -> tuple[str, ...] | None:
    """The place a `from` import takes its names from: its module for an absolute one; for a relative one the place
    it climbs to, the root's name first, or None when it cannot be followed (no file to climb from, above the root,
    or nothing there)."""
    module = tuple(node.module.split(".")) if node.module else ()
    if not node.level:
        return module
    found = where.target(node.level, module) if where is not None else None
    return _Relative(found) if found is not None else None


def _imports(tree: ast.AST, standard: frozenset[str], where: _Where | None = None) -> list[Import]:
    found: list[Import] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found += [Import(node.lineno, tuple(alias.name.split(".")), standard=alias.name.split(".")[0] in standard,
                             written=alias.name, last=_last(node)) for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            module = tuple(node.module.split(".")) if node.module else ()
            found.append(Import(node.lineno, module, tuple(a.name for a in node.names), node.level > 0,
                                max(node.level - 1, 0), not node.level and bool(module) and module[0] in standard,
                                "." * node.level + (node.module or ""), any(a.name == "*" for a in node.names),
                                _last(node), _from(node, where) is None))
    return found


def _last(node: ast.Import | ast.ImportFrom) -> int:
    """The last line an import spans when it is not its first, else 0."""
    end = node.end_lineno or node.lineno
    return end if end != node.lineno else 0


def _comments(text: str) -> tuple[Comment, ...]:
    """Each comment the tokens of the text hold, a `#` inside a string being none, its lines cut where the parser
    cuts them (a carriage return alone ending one too), so that they are the lines an import or a piece is on."""
    tokens = tokenize.generate_tokens(io.StringIO(text, newline=None).readline)
    return tuple(Comment(t.start[0], t.string, t.start[1], t.end[1], t.end[0] if t.end[0] != t.start[0] else 0)
                 for t in tokens if t.type == tokenize.COMMENT)


_BLOCKS = {ast.If: "if", ast.Match: "match", ast.Try: "try", ast.TryStar: "try", ast.For: "for",
           ast.AsyncFor: "for", ast.While: "while", ast.With: "with", ast.AsyncWith: "with"}
"""Each statement that holds a block of statements of its own, by the keyword that opens it."""
_CHOICES = {ast.IfExp: "if"}
"""Each expression that chooses between values, by the keyword that writes the choice (`a if c else b`)."""


def _functions(tree: ast.Module, form: CaseTable | None, where: _Where | None = None) -> tuple[Function, ...]:
    scope = [_scope(tree, where)]
    lists = _lists(tree)
    found: list[Function] = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            found.append(_function(node, scope, lists, form))
        elif isinstance(node, ast.ClassDef):
            found += [_function(n, scope, lists, form, node.name) for n in node.body
                      if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    return tuple(found)


def _function(node: ast.FunctionDef | ast.AsyncFunctionDef, scope: list[Scope], lists: dict[str, ast.expr],
              form: CaseTable | None, owner: str = "") -> Function:
    inside = [n for statement in node.body for n in ast.walk(statement)]
    mentions = frozenset(n.id if isinstance(n, ast.Name) else n.attr for n in inside
                         if isinstance(n, (ast.Name, ast.Attribute)))
    blocks = tuple(sorted((n.lineno, _BLOCKS[type(n)]) for n in inside if type(n) in _BLOCKS))
    choices = tuple(sorted((n.lineno, _CHOICES[type(n)]) for n in inside if type(n) in _CHOICES))
    tables = tuple(table for d in node.decorator_list if form is not None
                   and (table := _table(d, scope, lists, form)) is not None)
    asserts = any(isinstance(n, ast.Assert) for n in inside)
    statements, inert, shape = _shape(node)
    returns = _named(node.returns) if node.returns is not None else frozenset()
    signature, sole_call = _signature(node), _sole_call(node)
    forwards = _forwards(node.name, bool(node.decorator_list), signature, sole_call) if owner else ""
    return Function(node.lineno, node.name, tables, mentions, blocks, asserts, owner, statements, shape,
                    bool(node.decorator_list), signature, sole_call, returns, inert, forwards, _mentioned(node),
                    choices)


def _mentioned(node: ast.AST) -> frozenset[str]:
    """Every name and attribute the node holds, and the names inside a string that is an annotation in it."""
    found = {n.id if isinstance(n, ast.Name) else n.attr for n in ast.walk(node)
             if isinstance(n, (ast.Name, ast.Attribute))}
    for annotation in _annotations(node):
        found.update(name for n in ast.walk(annotation) if isinstance(n, ast.Constant) and isinstance(n.value, str)
                     for name in _in_string(n.value))
    return frozenset(found)


def _annotations(node: ast.AST) -> list[ast.expr]:
    """Every annotation the node holds: of a parameter, of a return, of an annotated assignment."""
    found: list[ast.expr] = []
    for n in ast.walk(node):
        if isinstance(n, ast.arg) and n.annotation is not None:
            found.append(n.annotation)
        elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.returns is not None:
            found.append(n.returns)
        elif isinstance(n, ast.AnnAssign):
            found.append(n.annotation)
    return found


def _constants(tree: ast.Module) -> list[Constant]:
    """The names the assignments of the top level bind, in order, each with what its statement mentions."""
    found: list[Constant] = []
    for node in _own(tree.body):
        if isinstance(node, ast.Assign):
            targets = node.targets
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            targets = [node.target]
        elif isinstance(node, ast.TypeAlias):
            targets = [node.name]
        else:
            continue
        named = _mentioned(node)
        found += [Constant(node.lineno, name, named) for target in targets for name in _bound_names(target)]
    return found


def _bound_names(target: ast.expr) -> list[str]:
    if isinstance(target, ast.Name):
        return [target.id]
    if isinstance(target, (ast.Tuple, ast.List)):
        return [name for item in target.elts for name in _bound_names(item)]
    if isinstance(target, ast.Starred):
        return _bound_names(target.value)
    return []


def _unmentioned(tree: ast.Module) -> frozenset[tuple[int, str]]:
    """(line, name) for each name a `from` import takes whose bound name the rest of the file never mentions."""
    mentioned = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    mentioned.update(name for annotation in _annotations(tree) for n in ast.walk(annotation)
                     if isinstance(n, ast.Constant) and isinstance(n.value, str) for name in _in_string(n.value))
    return frozenset((node.lineno, alias.name) for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)
                     for alias in node.names if alias.name != "*" and (alias.asname or alias.name) not in mentioned)


def _forwards(name: str, decorated: bool, signature: Signature, call: SoleCall | None) -> str:
    """The dotted callee a method only passes its arguments on to, or "" (see the module's docstring)."""
    if decorated or (name.startswith("__") and name.endswith("__")) or call is None or not signature.positional:
        return ""
    own, others = signature.positional[0], [*signature.positional[1:], *signature.keyword_only]
    if call.callee[:1] != (own,) or len(call.callee) < 3:
        return ""
    passed: list[str] = []
    for arg in call.args:
        if (signature.star and arg == f"*{signature.star}") or (arg and not arg.startswith("*") and arg in others):
            passed.append(arg)
        else:
            return ""
    for keyword, value in call.keywords:
        if keyword == "**" and signature.double and value == signature.double:
            passed.append(f"**{value}")
        elif keyword != "**" and value in others:
            passed.append(value)
        else:
            return ""
    wanted = [*others, *([f"*{signature.star}"] if signature.star else []),
              *([f"**{signature.double}"] if signature.double else [])]
    return ".".join(call.callee) if sorted(passed) == sorted(wanted) else ""


def _is_docstring(node: ast.stmt) -> bool:
    return isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str)


def _real(node: ast.AST) -> bool:
    """Whether a node is a statement that does something: not `pass`, a docstring, or a bare `...`."""
    if not isinstance(node, ast.stmt) or isinstance(node, ast.Pass):
        return False
    return not (isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant)
                and (isinstance(node.value.value, str) or node.value.value is Ellipsis))


def _shape(node: ast.FunctionDef | ast.AsyncFunctionDef) -> tuple[int, int, str]:
    """How many statements the body holds, nested ones too, how many of them are inert, and its fingerprint."""
    nodes = [n for statement in node.body for n in ast.walk(statement) if isinstance(n, ast.stmt)]
    inert = sum(1 for n in nodes if not _real(n))
    if inert == len(nodes):
        return len(nodes), inert, ""
    body = [copy.deepcopy(s) for s in node.body if not _is_docstring(s)]
    a = node.args
    parameters = [x.arg for x in [*a.posonlyargs, *a.args, *a.kwonlyargs, *(v for v in (a.vararg, a.kwarg) if v)]]
    numbered: dict[str, str] = {name: f"_{i}" for i, name in enumerate(dict.fromkeys(parameters))}
    local = _Locals(numbered)
    wrapped = ast.Module(body, [])
    local.visit(wrapped)
    local.rename = True
    renamed = local.visit(wrapped)
    arity = (len(a.posonlyargs), len(a.args), len(a.kwonlyargs), a.vararg is not None, a.kwarg is not None)
    text = f"{type(node).__name__}{arity}{ast.dump(renamed)}"
    return len(nodes), inert, hashlib.sha1(text.encode()).hexdigest()


class _Locals(ast.NodeTransformer):
    """Numbers the names a function binds, in order of appearance: a first pass finds them, the second renames."""

    def __init__(self, numbered: dict[str, str]) -> None:
        self.numbered = numbered
        self.rename = False

    def _bind(self, name: str) -> None:
        self.numbered.setdefault(name, f"_{len(self.numbered)}")

    def visit_Name(self, node: ast.Name) -> ast.AST:
        if not self.rename and not isinstance(node.ctx, ast.Load):
            self._bind(node.id)
        elif self.rename and node.id in self.numbered:
            node.id = self.numbered[node.id]
        return node

    def visit_arg(self, node: ast.arg) -> ast.AST:
        if not self.rename:
            self._bind(node.arg)
        else:
            node.arg = self.numbered[node.arg]
            node.annotation = None
        return node

    def _definition(self, node: ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef) -> ast.AST:
        if not self.rename:
            self._bind(node.name)
        else:
            node.name = self.numbered[node.name]
            node.decorator_list = []
            if not isinstance(node, ast.ClassDef):
                node.returns = None
        node.body = [s for s in node.body if not _is_docstring(s)] or node.body
        self.generic_visit(node)
        return node

    visit_FunctionDef = visit_AsyncFunctionDef = visit_ClassDef = _definition

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> ast.AST:
        if node.name:
            if not self.rename:
                self._bind(node.name)
            else:
                node.name = self.numbered[node.name]
        self.generic_visit(node)
        return node


def _signature(node: ast.FunctionDef | ast.AsyncFunctionDef) -> Signature:
    a = node.args
    return Signature(tuple(x.arg for x in [*a.posonlyargs, *a.args]), tuple(x.arg for x in a.kwonlyargs),
                     a.vararg.arg if a.vararg else "", a.kwarg.arg if a.kwarg else "")


def _sole_call(node: ast.FunctionDef | ast.AsyncFunctionDef) -> SoleCall | None:
    body = [s for s in node.body if not _is_docstring(s)]
    statement = body[0] if len(body) == 1 else None
    call = statement.value if isinstance(statement, (ast.Return, ast.Expr)) else None
    then: list[str] = []
    while isinstance(statement, ast.Return) and isinstance(call, ast.Attribute):
        then.insert(0, call.attr)
        call = call.value
    if isinstance(call, ast.Await):
        call = call.value
    if not isinstance(call, ast.Call):
        return None
    names: list[str] = []
    chain: ast.expr = call.func
    while isinstance(chain, ast.Attribute):
        names.insert(0, chain.attr)
        chain = chain.value
    callee = (chain.id, *names) if isinstance(chain, ast.Name) else ()
    args = tuple(f"*{arg.value.id}" if isinstance(arg, ast.Starred) and isinstance(arg.value, ast.Name)
                 else arg.id if isinstance(arg, ast.Name) else "" for arg in call.args)
    keywords = tuple((keyword.arg if keyword.arg is not None else "**",
                      keyword.value.id if isinstance(keyword.value, ast.Name) else "") for keyword in call.keywords)
    return SoleCall(callee, args, keywords, tuple(then))


def _named(tree: ast.AST) -> frozenset[str]:
    """Every name the tree mentions: names, attributes, imported names and the names inside string annotations."""
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            found.add(node.id)
        elif isinstance(node, ast.Attribute):
            found.add(node.attr)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            found.update(alias.name.rsplit(".", 1)[-1] for alias in node.names)
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            found.update(_in_string(node.value))
    return frozenset(found)


def _in_string(text: str) -> set[str]:
    """The names an expression written as a string holds; nothing when the string is no expression."""
    try:
        tree = ast.parse(text.strip(), mode="eval")
    except SyntaxError:
        return set()
    return {n.id if isinstance(n, ast.Name) else n.attr for n in ast.walk(tree) if isinstance(n, (ast.Name, ast.Attribute))}


def _lists(tree: ast.Module) -> dict[str, ast.expr]:
    """The module-level names assigned exactly once, to a list or tuple literal."""
    seen: dict[str, list[ast.expr | None]] = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            seen.setdefault(node.targets[0].id, []).append(node.value)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            seen.setdefault(node.target.id, []).append(node.value)
    return {name: values[0] for name, values in seen.items()
            if len(values) == 1 and isinstance(values[0], (ast.List, ast.Tuple))}


def _table(decorator: ast.expr, scope: list[Scope], lists: dict[str, ast.expr], form: CaseTable) -> Table | None:
    if not isinstance(decorator, ast.Call) or _ref(decorator.func, scope) != form.decorator:
        return None
    given = {k.arg: k.value for k in decorator.keywords if k.arg}
    by_keyword = form.keywords or (None, None)
    names = decorator.args[0] if decorator.args else given.get(by_keyword[0])
    values = decorator.args[1] if len(decorator.args) > 1 else given.get(by_keyword[1])
    columns = _columns(names)
    if columns is None:
        return None
    if isinstance(values, ast.Name):
        values = lists.get(values.id)
    rows = None
    if isinstance(values, (ast.List, ast.Tuple)) and not any(isinstance(v, ast.Starred) for v in values.elts):
        rows = tuple(_row(v, scope, form) for v in values.elts)
    return Table(decorator.lineno, columns, rows)


def _columns(node: ast.expr | None) -> tuple[str, ...] | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return tuple(part.strip() for part in node.value.split(","))
    if isinstance(node, (ast.List, ast.Tuple)) and all(isinstance(e, ast.Constant) and isinstance(e.value, str)
                                                       for e in node.elts):
        return tuple(e.value for e in node.elts)
    return None


def _row(node: ast.expr, scope: list[Scope], form: CaseTable) -> Row:
    if not isinstance(node, ast.Call) or _ref(node.func, scope) != form.row:
        return Row(node.lineno, False, None, tuple(_head(e) for e in node.elts) if isinstance(node, ast.Tuple) else ())
    ids = [k.value for k in node.keywords if k.arg == form.id]
    given = ids[0].value if ids and isinstance(ids[0], ast.Constant) and isinstance(ids[0].value, str) else None
    return Row(node.lineno, True, given, tuple(_head(a) for a in node.args if not isinstance(a, ast.Starred)))


def _head(node: ast.expr) -> str | None:
    """The name that heads a value: a call's callee, a bare name, an attribute's last name."""
    if isinstance(node, ast.Call):
        node = node.func
    if isinstance(node, ast.Name):
        return node.id
    return node.attr if isinstance(node, ast.Attribute) else None


def _unions(tree: ast.Module) -> list[Union]:
    found: list[Union] = []
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            name, value = node.targets[0].id, node.value
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.value is not None:
            name, value = node.target.id, node.value
        elif isinstance(node, ast.TypeAlias) and isinstance(node.name, ast.Name):
            name, value = node.name.id, node.value
        else:
            continue
        members = _members(value)
        if members is not None:
            found.append(Union(node.lineno, name, members))
    return found


def _members(node: ast.expr) -> tuple[str, ...] | None:
    if isinstance(node, ast.Name):
        return (node.id,)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
        left, right = _members(node.left), _members(node.right)
        return left + right if left is not None and right is not None else None
    return None


Scope = dict[str, Ref]
_FUNCTIONS = (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)
_COMPREHENSIONS = (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)
_NESTED = (*_FUNCTIONS, ast.ClassDef, *_COMPREHENSIONS)


def _scope(node: ast.AST, where: _Where | None = None) -> Scope:
    """The names a module, class, function, lambda or comprehension binds: the path an import binds, however
    written, or None when the name is bound any other way or by a relative import the reader cannot follow."""
    return _bound(node, where)[0]


def _bound(node: ast.AST, where: _Where | None = None) -> tuple[Scope, frozenset[str], frozenset[str]]:
    """What _scope returns, then the names its signature binds as parameters and nothing else binds, and the names
    one `def` binds and nothing else binds."""
    found: Scope = {}
    counts: dict[str, int] = {}
    parameters: set[str] = set()
    functions: set[str] = set()

    def bind(name: str, path: Ref) -> None:
        found[name] = path if found.get(name, path) == path else None
        counts[name] = counts.get(name, 0) + 1

    if isinstance(node, _FUNCTIONS):
        a = node.args
        for arg in [*a.posonlyargs, *a.args, *a.kwonlyargs, *(x for x in (a.vararg, a.kwarg) if x)]:
            bind(arg.arg, None)
            parameters.add(arg.arg)
    if isinstance(node, _COMPREHENSIONS):
        for generator in node.generators:
            for n in ast.walk(generator.target):
                if isinstance(n, ast.Name):
                    bind(n.id, None)
        return found, frozenset(), frozenset()
    body = node.body if isinstance(node.body, list) else [node.body]
    for child in _own(body):
        if isinstance(child, ast.Import):
            for alias in child.names:
                steps = tuple(alias.name.split("."))
                bind(alias.asname or steps[0], steps if alias.asname else steps[:1])
        elif isinstance(child, ast.ImportFrom):
            base = _from(child, where)
            for alias in child.names:
                if alias.name == "*":
                    continue
                path = None if base is None else (*base, alias.name)
                bind(alias.asname or alias.name, _Relative(path) if child.level and path is not None else path)
        elif isinstance(child, ast.Name) and not isinstance(child.ctx, ast.Load):
            bind(child.id, None)
        elif isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            bind(child.name, None)
            if not isinstance(child, ast.ClassDef):
                functions.add(child.name)
        elif isinstance(child, (ast.Global, ast.Nonlocal)):
            for name in child.names:
                bind(name, None)
        elif isinstance(child, (ast.ExceptHandler, ast.MatchAs, ast.MatchStar)) and child.name:
            bind(child.name, None)
        elif isinstance(child, ast.MatchMapping) and child.rest:
            bind(child.rest, None)
    once = {name for name, count in counts.items() if count == 1}
    return found, frozenset(parameters & once), frozenset(functions & once)


def _own(body: list[ast.AST]):
    """Every node of a scope's body, not descending into the scopes nested in it."""
    stack = list(reversed(body))
    while stack:
        node = stack.pop()
        yield node
        if not isinstance(node, _NESTED):
            stack.extend(reversed(list(ast.iter_child_nodes(node))))


def _ref(node: ast.AST, chain: list[Scope]) -> Ref:
    return _reached(node, chain, frozenset())[0]


def _reached(node: ast.AST, chain: list[Scope], names: frozenset[str]) -> tuple[Ref, int]:
    """The path a name or a chain of attributes on one reaches, and how many of its steps the import binding it names
    from the top (none for a relative import); a name no scope binds that is in names is a builtin."""
    attrs: list[str] = []
    while isinstance(node, ast.Attribute):
        attrs.insert(0, node.attr)
        node = node.value
    if not isinstance(node, ast.Name):
        return None, 0
    scope = next((scope for scope in chain if node.id in scope), None)
    if scope is None:
        return (("builtins", node.id, *attrs), 0) if node.id in names else (None, 0)
    base = scope[node.id]
    if base is None:
        return None, 0
    return (*base, *attrs), 0 if isinstance(base, _Relative) else len(base)


class _Calls(ast.NodeVisitor):
    """Collects every call whose callee is a Ref, reading each name in the scope it is read in."""

    def __init__(self, builtins: frozenset[str] = frozenset(), where: _Where | None = None) -> None:
        self._where = where
        self.found: list[Call] = []
        self.uses: list[Use] = []
        self._builtins = builtins
        self._chain: list[Scope] = []
        self._parameters: list[frozenset[str]] = []
        self._classes: list[bool] = []
        self._owners: list[tuple[str, str, frozenset[str]]] = []
        self.parameter_calls: list[ParameterCall] = []
        self.callbacks: list[Callback] = []
        self.method_calls: list[MethodCall] = []

    def visit_Module(self, node: ast.Module) -> None:
        self._within(node, node.body, is_class=False)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        for child in [*node.decorator_list, *node.bases, *node.keywords]:
            self.visit(child)
        self._within(node, node.body, is_class=True)

    def visit_FunctionDef(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        a = node.args
        annotations = [x.annotation for x in [*a.posonlyargs, *a.args, *a.kwonlyargs, *(v for v in (a.vararg, a.kwarg) if v)]
                       if x.annotation is not None]
        for child in [*node.decorator_list, *a.defaults, *(d for d in a.kw_defaults if d), *annotations,
                      *([node.returns] if node.returns is not None else [])]:
            self.visit(child)
        positional = [*a.posonlyargs, *a.args]
        static = any(isinstance(d, ast.Name) and d.id == "staticmethod" for d in node.decorator_list)
        method = bool(self._classes) and self._classes[0] and not static
        receiver = positional[0].arg if method and positional else ""
        callables = frozenset(x.arg for x in [*positional, *a.kwonlyargs]
                              if x.annotation is not None and self._is_callable(x.annotation))
        self._within(node, node.body, is_class=False, owner=(node.name, receiver, callables))

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Lambda(self, node: ast.Lambda) -> None:
        for child in [*node.args.defaults, *(d for d in node.args.kw_defaults if d)]:
            self.visit(child)
        self._within(node, [node.body], is_class=False, owner=("<lambda>", "", frozenset()))

    def _comprehension(self, node: ast.ListComp | ast.SetComp | ast.DictComp | ast.GeneratorExp) -> None:
        first, *rest = node.generators
        self.visit(first.iter)
        parts = [*first.ifs, *(x for g in rest for x in (g.iter, *g.ifs))]
        parts += [node.key, node.value] if isinstance(node, ast.DictComp) else [node.elt]
        self._within(node, parts, is_class=False)

    visit_ListComp = visit_SetComp = visit_DictComp = visit_GeneratorExp = _comprehension

    def _within(self, node: ast.AST, body: list[ast.AST], is_class: bool,
                owner: tuple[str, str, frozenset[str]] = ("", "", frozenset())) -> None:
        keep = [not c for c in self._classes]
        outer = [s for s, k in zip(self._chain, keep) if k]
        outer_parameters = [p for p, k in zip(self._parameters, keep) if k]
        outer_owners = [o for o, k in zip(self._owners, keep) if k]
        saved = self._chain, self._parameters, self._classes, self._owners
        scope, parameters, _ = _bound(node, self._where)
        self._chain, self._parameters = [scope, *outer], [parameters, *outer_parameters]
        self._classes = [is_class, *([False] * len(outer))]
        self._owners = [owner, *outer_owners]
        for child in body:
            self.visit(child)
        self._chain, self._parameters, self._classes, self._owners = saved

    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name):
            index = self._parameter_scope(node.func.id)
            if index is not None:
                function, receiver, callables = self._owners[index]
                self.callbacks.append(Callback(node.lineno, function, node.func.id, node.func.id == receiver,
                                               node.func.id in callables))
        func = _ref(node.func, self._chain)
        if func is None and isinstance(node.func, ast.Attribute):
            self.method_calls.append(MethodCall(node.lineno, node.func.attr, self._held(node.func.value)))
        if func is not None or self._is_parameter_method(node.func):
            args = tuple(_ref(a, self._chain) for a in node.args if not isinstance(a, ast.Starred))
            keywords = tuple((k.arg, _ref(k.value, self._chain)) for k in node.keywords if k.arg is not None)
            unpacked = any(isinstance(a, ast.Starred) for a in node.args) or any(k.arg is None for k in node.keywords)
            if func is not None:
                self.found.append(Call(node.lineno, func, args, keywords, unpacked))
            else:
                assert isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name)
                self.parameter_calls.append(ParameterCall(node.lineno, node.func.value.id, node.func.attr, args,
                                                          keywords, unpacked))
        self.generic_visit(node)

    def _held(self, node: ast.expr) -> bool:
        """Whether node is the first parameter of the method around it, or a chain of attributes on it."""
        while isinstance(node, ast.Attribute):
            node = node.value
        if not isinstance(node, ast.Name):
            return False
        index = self._parameter_scope(node.id)
        return index is not None and self._owners[index][1] == node.id

    def _is_parameter_method(self, func: ast.expr) -> bool:
        """Whether func is `<name>.<attr>` and the nearest scope binding the name binds it as a parameter."""
        if not isinstance(func, ast.Attribute) or not isinstance(func.value, ast.Name):
            return False
        return self._parameter_scope(func.value.id) is not None

    def _is_callable(self, annotation: ast.expr) -> bool:
        """Whether an annotation, read in the scope around the function, is a Callable (see the module's text)."""
        if isinstance(annotation, ast.Constant) and isinstance(annotation.value, str):
            try:
                annotation = ast.parse(annotation.value.strip(), mode="eval").body
            except SyntaxError:
                return False
        if isinstance(annotation, ast.BinOp) and isinstance(annotation.op, ast.BitOr):
            return self._is_callable(annotation.left) or self._is_callable(annotation.right)
        if isinstance(annotation, ast.Subscript):
            if _ref(annotation.value, self._chain) == ("typing", "Optional"):
                return self._is_callable(annotation.slice)
            annotation = annotation.value
        return _ref(annotation, self._chain) in _CALLABLE

    def _parameter_scope(self, name: str) -> int | None:
        """The index of the nearest scope binding the name, when it binds it as a parameter and nothing else."""
        index = next((i for i, scope in enumerate(self._chain) if name in scope), None)
        return index if index is not None and name in self._parameters[index] else None

    def visit_Name(self, node: ast.Name) -> None:
        if isinstance(node.ctx, ast.Load):
            self._use(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        base: ast.expr = node
        while isinstance(base, ast.Attribute):
            base = base.value
        if isinstance(base, ast.Name):
            self._use(node)
        else:
            self.visit(base)

    def _use(self, node: ast.expr) -> None:
        name, bound = _reached(node, self._chain, self._builtins)
        if name is not None:
            self.uses.append(Use(node.lineno, name, bound))


def _classes(tree: ast.Module, marks: tuple[RecordMark, ...] = (), interface: tuple[InterfaceMark, ...] = (),
             where: _Where | None = None) -> list[Class]:
    scope = [_scope(tree, where)]
    builtin = frozenset() if _star_import(tree) else _EXCEPTIONS - set(scope[0])
    exceptions: set[str] = set()
    found: list[Class] = []
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            bases = tuple(_ref(b.value if isinstance(b, ast.Subscript) else b, scope) for b in node.bases)
            methods = tuple(Method(n.lineno, n.name, _annotation(n.returns)) for n in node.body
                            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)))
            exception = any(isinstance(b, ast.Name) and (b.id in builtin or b.id in exceptions) for b in node.bases)
            if exception:
                exceptions.add(node.name)
            declared = _declared(node)
            found.append(Class(node.lineno, node.name, bases, methods, _attributes(node), _named(node) - {node.name},
                               exception, tuple(child.target.id for child in declared),
                               tuple(_annotation(child.annotation) or "" for child in declared),
                               _immutable(node, bases, scope, marks), _interface(bases, interface)))
    return found


def _immutable(node: ast.ClassDef, bases: tuple[Ref, ...], scope: list[Scope], marks: tuple[RecordMark, ...]) -> bool:
    """Whether a mark names one of the class's bases, or one of its decorators called with each keyword of the mark."""
    for decorator in node.decorator_list:
        called = isinstance(decorator, ast.Call)
        path = _ref(decorator.func if called else decorator, scope)
        given = {(k.arg, ast.unparse(k.value)) for k in decorator.keywords if k.arg} if called else set()
        if any(mark.path == path and set(mark.keywords) <= given for mark in marks):
            return True
    return any(mark.path in bases and not mark.keywords for mark in marks)


def _interface(bases: tuple[Ref, ...], marks: tuple[InterfaceMark, ...]) -> bool:
    """Whether a base mark names one of the class's bases; a keyword mark names none, since Python declares no class
    with a keyword."""
    return any(mark.base and mark.base in bases for mark in marks)


def _declared(node: ast.ClassDef) -> list[ast.AnnAssign]:
    """The statements of the class body itself that annotate a name, in order, but those of a class variable."""
    return [child for child in node.body if isinstance(child, ast.AnnAssign) and isinstance(child.target, ast.Name)
            and not _class_variable(child.annotation)]


def _class_variable(annotation: ast.expr) -> bool:
    if isinstance(annotation, ast.Constant) and isinstance(annotation.value, str):
        try:
            annotation = ast.parse(annotation.value.strip(), mode="eval").body
        except SyntaxError:
            return False
    if isinstance(annotation, ast.Subscript):
        annotation = annotation.value
    name = annotation.id if isinstance(annotation, ast.Name) else annotation.attr \
        if isinstance(annotation, ast.Attribute) else ""
    return name == "ClassVar"


_CALLABLE = (("typing", "Callable"), ("collections", "abc", "Callable"))
"""Where Python's Callable is imported from, as the path its import binds."""

_EXCEPTIONS = frozenset(name for name, value in vars(builtins).items()
                        if isinstance(value, type) and issubclass(value, BaseException))
"""The builtin exceptions, by the bare name that reads them."""


def _attributes(node: ast.ClassDef) -> tuple[str, ...]:
    """The names the class body assigns, then those its methods assign on their first parameter, each once."""
    names: list[str] = []
    for child in node.body:
        targets = child.targets if isinstance(child, ast.Assign) else [child.target] \
            if isinstance(child, ast.AnnAssign) else []
        names += [t.id for t in targets if isinstance(t, ast.Name)]
    for method in node.body:
        if not isinstance(method, (ast.FunctionDef, ast.AsyncFunctionDef)) or not method.args.args:
            continue
        own = method.args.args[0].arg
        names += [n.attr for n in ast.walk(method) if isinstance(n, ast.Attribute) and isinstance(n.ctx, ast.Store)
                  and isinstance(n.value, ast.Name) and n.value.id == own]
    return tuple(dict.fromkeys(names))


def _annotation(node: ast.expr | None) -> str | None:
    if node is None:
        return None
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return ast.unparse(node)
