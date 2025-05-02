import os
import json
import shutil
import subprocess
import argparse

from dotenvx import __file__ as package_path

ERROR_MISSING_BINARY = "[MISSING_BINARY] missing dotenvx binary\n[MISSING_BINARY] https://github.com/dotenvx/dotenvx/issues/576"

def load_dotenvx(
        dotenv_path=None,
        override=False
):
    output = dotenvx_get(
        dotenv_path=dotenv_path,
        override=override
    )

    try:
        parsed = json.loads(output)
        for key, value in parsed.items():
            os.environ[key] = value
        return parsed
    except Exception as e:
        raise RuntimeError(f"Failed to parse dotenvx output: {e}")

def dotenvx_get(
        dotenv_path=None,
        override=False
):
    binpath = binary()
    cmd = [binpath, "get", "-pp"]

    if dotenv_path:
        cmd += ["-f", dotenv_path]
    if override:
        cmd.append("--overload")

    output = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=True
    )
    return output.stdout.strip()

def binary():
    candidates = [
        os.path.join(os.path.dirname(__file__), "bin", "dotenvx"),  # package-local
        os.path.join(os.getcwd(), "bin", "dotenvx"),                # project-local
        shutil.which("dotenvx")                                     # global/system
    ]

    for candidate in candidates:
        if candidate and os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            if is_stub_file(candidate):
                continue
            return candidate

    print("[MISSING_BINARY] missing dotenvx binary")
    print("[MISSING_BINARY] https://github.com/dotenvx/dotenvx/issues/576")
    raise SystemExit(1)

def is_stub_file(path, max_stub_size=1024):
    try:
        return os.path.getsize(path) < max_stub_size
    except OSError:
        return False

def postinstall():
    parser = argparse.ArgumentParser()
    parser.add_argument("--os", help="Override OS", default="")
    parser.add_argument("--arch", help="Override architecture", default="")
    args = parser.parse_args()

    bin_dir = os.path.join(os.path.dirname(__file__), "bin")
    os.makedirs(bin_dir, exist_ok=True)

    url = f"https://dotenvx.sh?directory={bin_dir}&force=true"
    if args.os:
        url += f"&os={args.os}"
    if args.arch:
        url += f"&arch={args.arch}"

    try:
        subprocess.run(
            ["sh", "-c", f'curl -sfS "{url}" | sh'],
            check=True
        )
    except subprocess.CalledProcessError as e:
        raise SystemExit(e.returncode)
