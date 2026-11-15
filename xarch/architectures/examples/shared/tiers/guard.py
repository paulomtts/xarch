def test_the_dependency_rules_hold():
    assert check(Path("app")).violations == []
