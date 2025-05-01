import os
import subprocess

from dotenvx import __file__ as package_path

def load_dotenvx():
    binary = dotenvx_binary()
    try:
        return dotenvx_get(binary)
    except FileNotFoundError:
        print("⚠️ 'dotenvx' binary not found. Attempting to install it now...")
        postinstall()
        return dotenvx_get(binary)

def dotenvx_get(binary):
    result = subprocess.run(
        [binary, "get", "-pp"],
        capture_output=True,
        text=True,
        check=True
    )
    return result.stdout.strip()

def dotenvx_binary():
    local_bin = os.path.join(os.path.dirname(package_path), "bin", "dotenvx")
    if os.path.isfile(local_bin) and os.access(local_bin, os.X_OK):
        return local_bin

    system_bin = shutil.which("dotenvx")
    if system_bin:
        return system_bin

    raise FileNotFoundError("dotenvx binary not found locally or in PATH")

def postinstall():
    bin_dir = os.path.join(os.path.dirname(package_path), "bin")
    os.makedirs(bin_dir, exist_ok=True)

    try:
        subprocess.run(
            ["sh", "-c", f"curl -sfS https://dotenvx.sh?directory={bin_dir} | sh"],
            check=True
        )
    except subprocess.CalledProcessError as e:
        print("❌ Failed to install dotenvx binary.")
        raise SystemExit(e.returncode)
