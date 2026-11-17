"""A profile at a glance: its folder tree with the role of each folder, and its import table."""
from tests.modules.spec.profiles import layered, parsed
from xarch.modules.spec.application.logic.profile_view import view


def test_the_view_is_the_folder_tree_with_roles_and_the_table_of_what_each_part_may_import():
    tree, imports = view(parsed(layered()))
    assert tree == ("├── src/\n│   └── <module>/\n│       ├── api/       HTTP handlers\n"
                    "│       ├── service/   business logic\n│       └── store/     database access\n"
                    "└── shared/            shared code")
    assert imports == ("| Part | May import |\n|---|---|\n| `api/` | its own module's `service/` |\n"
                       "| `service/` | its own module's `store/`, `shared/` |\n| `store/` | `shared/` |\n"
                       "| `shared/` | nothing |")
