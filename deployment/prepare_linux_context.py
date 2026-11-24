"""Prepare a build context with the release allowlist and the Linux smoke test."""
import argparse
from pathlib import Path
import shutil
import sys

DEPLOYMENT = Path(__file__).resolve().parent
sys.path.insert(0, str(DEPLOYMENT.parent))

from verify_public_stage import prepare_stage


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path, help="New Docker build directory")
    args = parser.parse_args()
    root = args.directory.resolve()
    root.mkdir(parents=True, exist_ok=False)
    count = prepare_stage(root / "app")
    for name in ("Dockerfile", "linux-constraints.txt"):
        shutil.copyfile(DEPLOYMENT / name, root / name)
    shutil.copyfile(DEPLOYMENT / "linux_smoke.py", root / "app" / "linux_smoke.py")
    print(f"Prepared {count} runtime files and the Linux smoke test. No study data.")


if __name__ == "__main__":
    main()
