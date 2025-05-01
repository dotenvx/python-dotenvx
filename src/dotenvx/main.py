import os
import json
import shutil
import subprocess

from dotenvx import __file__ as package_path

ERROR_MISSING_BINARY = "[MISSING_BINARY] missing dotenvx binary\n[MISSING_BINARY] https://github.com/dotenvx/dotenvx/issues/576"

def load_dotenvx():
    output = get()

    try:
        parsed = json.loads(output)
        for key, value in parsed.items():
            os.environ[key] = value
        return parsed
    except Exception as e:
        raise RuntimeError(f"Failed to parse dotenvx output: {e}")

def get():
    binpath = binary()
    output = subprocess.run(
        [binpath, "get", "-pp"],
        capture_output=True,
        text=True,
        check=True
    )
    return output.stdout.strip()

def binary():
    local_bin = os.path.join(os.path.dirname(package_path), "bin", "dotenvx")
    candidates = [local_bin, shutil.which("dotenvx")]

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
    bin_dir = os.path.join(os.path.dirname(package_path), "bin")
    os.makedirs(bin_dir, exist_ok=True)

    try:
        subprocess.run(
            ["sh", "-c", f"curl -sfS https://dotenvx.sh?directory={bin_dir} | sh"],
            check=True
        )
    except subprocess.CalledProcessError as e:
        raise SystemExit(e.returncode)
