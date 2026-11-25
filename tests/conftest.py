"""What every test runs with: no key of the decision model in the environment, so that no test can send code to a
service across the network, whatever the shell that runs the tests holds. The reader keeps what it reads in a folder of
the run's own, removed after it, never in the user's cache folder; a check run in a subprocess inherits it."""
import os
import shutil
import tempfile

import pytest

CACHE = "XARCH_CACHE_DIR"


def pytest_configure(config):
    config.xarch_cache = tempfile.mkdtemp(prefix="xarch-test-cache-")
    os.environ[CACHE] = config.xarch_cache


def pytest_unconfigure(config):
    shutil.rmtree(config.xarch_cache, ignore_errors=True)


@pytest.fixture(autouse=True)
def no_key(monkeypatch):
    monkeypatch.delenv("TYPESAFE_API_KEY", raising=False)
