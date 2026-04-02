#!/usr/bin/env python3
import os
import subprocess
import sys
from pathlib import Path


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    target = repo_root / "skills" / "landing-page-factory-orchestrator" / "scripts" / "page-admin.py"
    env = os.environ.copy()
    env.setdefault("LPF_ROOT", str(repo_root))
    completed = subprocess.run([sys.executable, str(target), *sys.argv[1:]], env=env)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
