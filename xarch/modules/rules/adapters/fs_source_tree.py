"""SourceTree on the local filesystem: lists the .py files, and parses one with ast and tokenize, never running it.

A name in a call or a class base is read as Python scopes it: through the innermost function, lambda or
comprehension that binds it (a class body only for its own statements), then the module. It is a Ref only when that
scope binds it with an absolute import and nothing else; a parameter, an assignment, a def, a relative import or a
second, different binding of the same name in that scope makes it None, and so does a name no scope binds.
"""
from __future__ import annotations

import ast
import io
import tokenize
from pathlib import Path

from xarch.modules.rules.domain.values import (Call, Class, Comment, Function, Import, Method, Ref, Row, SourceFile, Table,
                                               Union)
from xarch.platform.filesystem import FileSystem


class FsSourceTree:
    def __init__(self, fs: FileSystem):
        self._fs = fs

    def is_dir(self, root: Path) -> bool:
        return self._fs.is_dir(root)

    def paths(self, root: Path) -> list[tuple[str, ...]]:
        return [f.relative_to(root).parts for f in self._fs.files(root, "*.py")]

    def read(self, root: Path, paths: list[tuple[str, ...]]) -> list[SourceFile]:
        return [_parsed(root.joinpath(*path).relative_to(root.parent).as_posix(), path,
                        self._fs.read_text(root.joinpath(*path))) for path in paths]


def _parsed(name: str, path: tuple[str, ...], text: str) -> SourceFile:
    try:
        tree = ast.parse(text)
        comments = _comments(text)
    except SyntaxError as e:
        return SourceFile(name, path, (), error=(e.lineno or 0, f"not valid Python: {e.msg}"))
    except (tokenize.TokenError, IndentationError) as e:
        return SourceFile(name, path, (), error=(0, f"not valid Python: {e}"))
    calls = _Calls()
    calls.visit(tree)
    return SourceFile(name, path, tuple(_imports(tree)), comments, _functions(tree),
                      tuple(_unions(tree)), calls=tuple(calls.found), classes=tuple(_classes(tree)))


def _imports(tree: ast.AST) -> list[Import]:
    found: list[Import] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found += [Import(node.lineno, tuple(alias.name.split("."))) for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            module = tuple(node.module.split(".")) if node.module else ()
            found.append(Import(node.lineno, module, node.level, tuple(a.name for a in node.names)))
    return found


def _comments(text: str) -> tuple[Comment, ...]:
    tokens = tokenize.generate_tokens(io.StringIO(text).readline)
    return tuple(Comment(t.start[0], t.string) for t in tokens if t.type == tokenize.COMMENT)


_BRANCHES = {ast.If: "if", ast.Match: "match", ast.Try: "try", ast.TryStar: "try", ast.For: "for",
             ast.AsyncFor: "for", ast.While: "while"}
_PARAMETRIZE = ("pytest", "mark", "parametrize")
_PARAM = ("pytest", "param")


def _functions(tree: ast.Module) -> tuple[Function, ...]:
    scope = [_scope(tree)]
    lists = _lists(tree)
    found: list[Function] = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            found.append(_function(node, scope, lists))
        elif isinstance(node, ast.ClassDef):
            found += [_function(n, scope, lists) for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    return tuple(found)


def _function(node: ast.FunctionDef | ast.AsyncFunctionDef, scope: list[Scope], lists: dict[str, ast.expr]) -> Function:
    inside = [n for statement in node.body for n in ast.walk(statement)]
    mentions = frozenset(n.id if isinstance(n, ast.Name) else n.attr for n in inside
                         if isinstance(n, (ast.Name, ast.Attribute)))
    branches = tuple(sorted((n.lineno, _BRANCHES[type(n)]) for n in inside if type(n) in _BRANCHES))
    tables = tuple(table for d in node.decorator_list if (table := _table(d, scope, lists)) is not None)
    return Function(node.lineno, node.name, tables, mentions, branches)


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


def _table(decorator: ast.expr, scope: list[Scope], lists: dict[str, ast.expr]) -> Table | None:
    if not isinstance(decorator, ast.Call) or _ref(decorator.func, scope) != _PARAMETRIZE:
        return None
    given = {k.arg: k.value for k in decorator.keywords if k.arg}
    names = decorator.args[0] if decorator.args else given.get("argnames")
    values = decorator.args[1] if len(decorator.args) > 1 else given.get("argvalues")
    columns = _columns(names)
    if columns is None:
        return None
    if isinstance(values, ast.Name):
        values = lists.get(values.id)
    rows = None
    if isinstance(values, (ast.List, ast.Tuple)) and not any(isinstance(v, ast.Starred) for v in values.elts):
        rows = tuple(_row(v, scope) for v in values.elts)
    return Table(decorator.lineno, columns, rows)


def _columns(node: ast.expr | None) -> tuple[str, ...] | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return tuple(part.strip() for part in node.value.split(","))
    if isinstance(node, (ast.List, ast.Tuple)) and all(isinstance(e, ast.Constant) and isinstance(e.value, str)
                                                       for e in node.elts):
        return tuple(e.value for e in node.elts)
    return None


def _row(node: ast.expr, scope: list[Scope]) -> Row:
    if not isinstance(node, ast.Call) or _ref(node.func, scope) != _PARAM:
        return Row(node.lineno, False, None, tuple(_head(e) for e in node.elts) if isinstance(node, ast.Tuple) else ())
    ids = [k.value for k in node.keywords if k.arg == "id"]
    given = ids[0].value if ids and isinstance(ids[0], ast.Constant) and isinstance(ids[0].value, str) else None
    return Row(node.lineno, True, given if given and given.strip() else None,
               tuple(_head(a) for a in node.args if not isinstance(a, ast.Starred)))


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
        if members is not None and len(members) > 1:
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


def _scope(node: ast.AST) -> Scope:
    """The names a module, class, function, lambda or comprehension binds: the path an absolute import binds, or
    None when the name is bound any other way."""
    found: Scope = {}

    def bind(name: str, path: Ref) -> None:
        found[name] = path if found.get(name, path) == path else None

    if isinstance(node, _FUNCTIONS):
        a = node.args
        for arg in [*a.posonlyargs, *a.args, *a.kwonlyargs, *(x for x in (a.vararg, a.kwarg) if x)]:
            bind(arg.arg, None)
    if isinstance(node, _COMPREHENSIONS):
        for generator in node.generators:
            for n in ast.walk(generator.target):
                if isinstance(n, ast.Name):
                    bind(n.id, None)
        return found
    body = node.body if isinstance(node.body, list) else [node.body]
    for child in _own(body):
        if isinstance(child, ast.Import):
            for alias in child.names:
                steps = tuple(alias.name.split("."))
                bind(alias.asname or steps[0], steps if alias.asname else steps[:1])
        elif isinstance(child, ast.ImportFrom):
            for alias in child.names:
                if alias.name != "*":
                    path = (*child.module.split("."), alias.name) if child.module and not child.level else None
                    bind(alias.asname or alias.name, path)
        elif isinstance(child, ast.Name) and not isinstance(child.ctx, ast.Load):
            bind(child.id, None)
        elif isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            bind(child.name, None)
        elif isinstance(child, (ast.Global, ast.Nonlocal)):
            for name in child.names:
                bind(name, None)
        elif isinstance(child, (ast.ExceptHandler, ast.MatchAs, ast.MatchStar)) and child.name:
            bind(child.name, None)
        elif isinstance(child, ast.MatchMapping) and child.rest:
            bind(child.rest, None)
    return found


def _own(body: list[ast.AST]):
    """Every node of a scope's body, not descending into the scopes nested in it."""
    stack = list(reversed(body))
    while stack:
        node = stack.pop()
        yield node
        if not isinstance(node, _NESTED):
            stack.extend(reversed(list(ast.iter_child_nodes(node))))


def _ref(node: ast.AST, chain: list[Scope]) -> Ref:
    attrs: list[str] = []
    while isinstance(node, ast.Attribute):
        attrs.insert(0, node.attr)
        node = node.value
    if not isinstance(node, ast.Name):
        return None
    base = next((scope[node.id] for scope in chain if node.id in scope), None)
    return (*base, *attrs) if base is not None else None


class _Calls(ast.NodeVisitor):
    """Collects every call whose callee is a Ref, reading each name in the scope it is read in."""

    def __init__(self) -> None:
        self.found: list[Call] = []
        self._chain: list[Scope] = []
        self._classes: list[bool] = []

    def visit_Module(self, node: ast.Module) -> None:
        self._within(node, node.body, is_class=False)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        for child in [*node.decorator_list, *node.bases, *node.keywords]:
            self.visit(child)
        self._within(node, node.body, is_class=True)

    def visit_FunctionDef(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        a = node.args
        for child in [*node.decorator_list, *a.defaults, *(d for d in a.kw_defaults if d)]:
            self.visit(child)
        self._within(node, node.body, is_class=False)

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Lambda(self, node: ast.Lambda) -> None:
        for child in [*node.args.defaults, *(d for d in node.args.kw_defaults if d)]:
            self.visit(child)
        self._within(node, [node.body], is_class=False)

    def _comprehension(self, node: ast.ListComp | ast.SetComp | ast.DictComp | ast.GeneratorExp) -> None:
        first, *rest = node.generators
        self.visit(first.iter)
        parts = [*first.ifs, *(x for g in rest for x in (g.iter, *g.ifs))]
        parts += [node.key, node.value] if isinstance(node, ast.DictComp) else [node.elt]
        self._within(node, parts, is_class=False)

    visit_ListComp = visit_SetComp = visit_DictComp = visit_GeneratorExp = _comprehension

    def _within(self, node: ast.AST, body: list[ast.AST], is_class: bool) -> None:
        outer = [s for s, c in zip(self._chain, self._classes) if not c] if not is_class else self._chain
        outer_classes = [False] * len(outer) if not is_class else self._classes
        saved = self._chain, self._classes
        self._chain, self._classes = [_scope(node), *outer], [is_class, *outer_classes]
        for child in body:
            self.visit(child)
        self._chain, self._classes = saved

    def visit_Call(self, node: ast.Call) -> None:
        func = _ref(node.func, self._chain)
        if func is not None:
            args = tuple(_ref(a, self._chain) for a in node.args if not isinstance(a, ast.Starred))
            keywords = tuple((k.arg, _ref(k.value, self._chain)) for k in node.keywords if k.arg is not None)
            unpacked = any(isinstance(a, ast.Starred) for a in node.args) or any(k.arg is None for k in node.keywords)
            self.found.append(Call(node.lineno, func, args, keywords, unpacked))
        self.generic_visit(node)


def _classes(tree: ast.Module) -> list[Class]:
    scope = [_scope(tree)]
    found: list[Class] = []
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            bases = tuple(_ref(b.value if isinstance(b, ast.Subscript) else b, scope) for b in node.bases)
            methods = tuple(Method(n.lineno, n.name, _annotation(n.returns)) for n in node.body
                            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)))
            found.append(Class(node.lineno, node.name, bases, methods))
    return found


def _annotation(node: ast.expr | None) -> str | None:
    if node is None:
        return None
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return ast.unparse(node)
