"""What every test runs with: no key of the decision model in the environment, so that no test can send code to a
service across the network, whatever the shell that runs the tests holds."""
import pytest


@pytest.fixture(autouse=True)
def no_key(monkeypatch):
    monkeypatch.delenv("TYPESAFE_API_KEY", raising=False)
