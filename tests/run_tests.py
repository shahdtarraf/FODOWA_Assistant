"""Simple test runner that works from the tests directory."""
import subprocess
import sys
import os

# Change to backend directory
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(backend_dir)

# Add backend to path
sys.path.insert(0, backend_dir)

# Run pytest
print(f"Running tests from: {backend_dir}")
print("=" * 60)
result = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"])
sys.exit(result.returncode)
