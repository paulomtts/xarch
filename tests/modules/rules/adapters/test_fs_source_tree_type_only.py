"""FsSourceTree on real files: an import made only for the type checker, under `if TYPE_CHECKING:`, is marked type_only;
every other import, the `else` of that `if` included, is not."""
import sys
from pathlib import Path

import pytest

from xarch.modules.rules.adapters.fs_source_tree import FsSourceTree
from xarch.platform.filesystem import FileSystem


def imports(tmp_path: Path, text: str) -> list[tuple[int, bool]]:
    (tmp_path / "x.py").write_text(text)
    found = FsSourceTree(FileSystem()).read(tmp_path, [("x.py",)], standard=frozenset(sys.stdlib_module_names),
                                            private="_", special=r"(?=__)\w*(?<=__)")[0]
    return sorted((i.line, i.type_only) for i in found.imports)


@pytest.mark.parametrize("text, expected", [
    pytest.param("from typing import TYPE_CHECKING\nif TYPE_CHECKING:\n    from app.web import Page\n",
                 [(1, False), (3, True)], id="a from import under if TYPE_CHECKING"),
    pytest.param("import typing\nif typing.TYPE_CHECKING:\n    import app.web\n    from app import db\n",
                 [(1, False), (3, True), (4, True)], id="under typing.TYPE_CHECKING, each import of the block"),
    pytest.param("from typing import TYPE_CHECKING\nif TYPE_CHECKING:\n    from app.web import Page\n"
                 "else:\n    Page = None\n    import json\n",
                 [(1, False), (3, True), (6, False)], id="the else of the if runs, and is no type-only import"),
    pytest.param("from typing import TYPE_CHECKING\nif TYPE_CHECKING:\n    if True:\n        import json\n",
                 [(1, False), (4, True)], id="nested in the block"),
    pytest.param("def f():\n    from typing import TYPE_CHECKING\n    if TYPE_CHECKING:\n        import json\n",
                 [(2, False), (4, True)], id="in a function too"),
    pytest.param("DEBUG = True\nif DEBUG:\n    import json\nimport os\n", [(3, False), (4, False)],
                 id="any other if is no type-only import"),
    pytest.param("from typing import TYPE_CHECKING\nif not TYPE_CHECKING:\n    import json\n", [(1, False), (3, False)],
                 id="nor one that is not TYPE_CHECKING alone"),
])
def test_an_import_under_type_checking_is_type_only(tmp_path, text, expected):
    assert imports(tmp_path, text) == expected
