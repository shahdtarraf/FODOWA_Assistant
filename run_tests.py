"""Run tests script."""
import subprocess
import sys
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))
result = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v"])
sys.exit(result.returncode)
