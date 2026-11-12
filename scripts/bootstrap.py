#!/usr/bin/env python3
"""Install once, apply included migrations, and verify Django. No activation."""
import argparse
import hashlib
import os
from pathlib import Path
import subprocess
import sys
import venv

ROOT = Path(__file__).resolve().parent.parent
ENV_DIR = ROOT / ".venv"
PYTHON = ENV_DIR / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()
    if not (3, 10) <= sys.version_info[:2] <= (3, 14):
        print("Use Python 3.10-3.14. Python 3.12 or 3.13 is recommended.")
        print("Windows example: py -3.12 scripts\\bootstrap.py")
        return 2
    if not PYTHON.exists():
        print("Creating the project's Python environment...")
        venv.EnvBuilder(with_pip=True).create(ENV_DIR)
    probe = subprocess.run([str(PYTHON), "-c", "import sys; print(sys.version_info.major, sys.version_info.minor)"], text=True, capture_output=True)
    if probe.returncode:
        print("The existing .venv cannot run. Rename .venv and run setup again.")
        return 2
    version = tuple(int(x) for x in probe.stdout.split())
    if not (3, 10) <= version <= (3, 14):
        print("The existing .venv uses an unsupported Python. Rename it and run setup again.")
        return 2
    digest = hashlib.sha256((ROOT / "requirements.txt").read_bytes()).hexdigest()
    marker = ENV_DIR / ".flowdesk-requirements"
    dependencies = subprocess.run([str(PYTHON), "-c", "import django, asgiref, sqlparse; assert django.get_version() == '5.2.18'"], capture_output=True)
    if dependencies.returncode or not marker.exists() or marker.read_text().strip() != digest:
        # A uv-created environment has no pip by default. Install the bundled
        # pip first so SETUP.bat and START.bat also work after `uv sync`.
        pip = subprocess.run([str(PYTHON), "-m", "pip", "--version"], capture_output=True)
        if pip.returncode:
            subprocess.run([str(PYTHON), "-m", "ensurepip", "--upgrade"], cwd=ROOT, capture_output=True)
        result = subprocess.run([str(PYTHON), "-m", "pip", "install", "--disable-pip-version-check", "-r", str(ROOT / "requirements.txt")], cwd=ROOT)
        if result.returncode:
            print("Dependency installation failed. Check your internet connection and rerun setup.")
            return result.returncode
        marker.write_text(digest, encoding="utf-8")
    verbosity = "0" if args.quiet else "1"
    for command in [["migrate", "--noinput", "--verbosity", verbosity], ["check", "--verbosity", verbosity]]:
        result = subprocess.run([str(PYTHON), str(ROOT / "manage.py"), *command], cwd=ROOT)
        if result.returncode:
            return result.returncode
    if not args.quiet:
        print("\nSetup complete. Run START.bat or sh start.sh.")
        print("No virtual-environment activation or PowerShell policy change is needed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
