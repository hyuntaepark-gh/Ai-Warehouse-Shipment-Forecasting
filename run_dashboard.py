"""Start Warehouse IQ on loopback or with Render's assigned port."""
import argparse
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent


def launch_settings(mode, env):
    if mode == "local":
        return "127.0.0.1", 8507
    value = env.get("PORT", "8507" if mode == "preview" else "")
    if not value.isascii() or not value.isdigit() or not 1 <= int(value) <= 65535:
        raise ValueError("PORT must be an integer between 1 and 65535.")
    return ("0.0.0.0" if mode in {"render", "horizons-release"} else "127.0.0.1"), int(value)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("local", "preview", "render", "horizons-release"), nargs="?", default="local")
    args = parser.parse_args()
    env = os.environ.copy()
    try:
        address, port = launch_settings(args.mode, env)
    except ValueError as exc:
        parser.error(str(exc))
    if args.mode != "local":
        env["WIQ_RELEASE_MODE"] = "horizons_display" if args.mode == "horizons-release" else "public"
        env["STREAMLIT_CLIENT_SHOW_ERROR_DETAILS"] = "none"
    entry = "deployment/public_horizons_app.py" if args.mode == "horizons-release" else "app.py"
    command = [
        sys.executable, "-m", "streamlit", "run", str(ROOT / entry),
        "--server.address", address, "--server.port", str(port),
        "--server.headless", "true", "--browser.gatherUsageStats", "false",
    ]
    if os.name == "posix":
        os.chdir(ROOT)
        os.execve(sys.executable, command, env)
    return subprocess.call(command, cwd=ROOT, env=env)


if __name__ == "__main__":
    raise SystemExit(main())
