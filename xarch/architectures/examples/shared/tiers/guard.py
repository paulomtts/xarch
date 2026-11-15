import subprocess
import sys
from pathlib import Path

PROJECT = Path(__file__).parents[2]


def test_the_architecture_holds():
    check = subprocess.run([sys.executable, "-m", "xarch", "check", "--app", str(PROJECT / "{{app}}")],
                           capture_output=True, text=True)
    assert check.returncode == 0, check.stdout + check.stderr
