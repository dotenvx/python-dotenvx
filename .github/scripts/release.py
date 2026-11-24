"""Validate the immutable Python wheel release and prepare only missing uploads."""
import argparse
from email.parser import BytesParser
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import urllib.error
import urllib.request
from zipfile import ZipFile

FAMILIES = {"linux-x86_64", "linux-aarch64", "macos-x86_64", "macos-arm64", "windows-x86_64"}
REPOSITORY = "https://github.com/dotenvx/forge"


def fail(message):
    raise SystemExit(message)


def wheel_family(filename, version):
    match = re.fullmatch(r"python_dotenvx-" + re.escape(version) + r"-cp38-abi3-(.+)\.whl", filename)
    if not match:
        fail("Unexpected wheel name or ABI: " + filename)
    families = set()
    for tag in match[1].split("."):
        if re.fullmatch(r"manylinux(?:2014|_\d+_\d+)_x86_64", tag):
            families.add("linux-x86_64")
        elif re.fullmatch(r"manylinux(?:2014|_\d+_\d+)_aarch64", tag):
            families.add("linux-aarch64")
        elif re.fullmatch(r"macosx_\d+_\d+_x86_64", tag):
            families.add("macos-x86_64")
        elif re.fullmatch(r"macosx_\d+_\d+_arm64", tag):
            families.add("macos-arm64")
        elif tag == "win_amd64":
            families.add("windows-x86_64")
        else:
            fail("Unsupported wheel platform: " + tag)
    if len(families) != 1:
        fail("Ambiguous wheel platforms: " + filename)
    return families.pop(), {"cp38-abi3-" + tag for tag in match[1].split(".")}


def check_wheel(path, version):
    family, tags = wheel_family(path.name, version)
    prefix = "python_dotenvx-" + version + ".dist-info/"
    with ZipFile(path) as wheel:
        if wheel.testzip() is not None:
            fail("Corrupt wheel: " + path.name)
        metadata = BytesParser().parsebytes(wheel.read(prefix + "METADATA"))
        if metadata.get_all("Name") != ["python-dotenvx"] or metadata.get_all("Version") != [version]:
            fail("Wheel package identity mismatch: " + path.name)
        info = BytesParser().parsebytes(wheel.read(prefix + "WHEEL"))
        if set(info.get_all("Tag", [])) != tags or info.get("Root-Is-Purelib", "").lower() != "false":
            fail("Wheel tags or native-library metadata mismatch: " + path.name)
        extension = ".pyd" if family.startswith("windows-") else ".so"
        native = [name for name in wheel.namelist() if name.startswith("dotenvx/_native") and name.endswith(extension)]
        if len(native) != 1 or not wheel.getinfo(native[0]).file_size:
            fail("Missing native extension: " + path.name)
    return family


def verify(root, tag):
    root = Path(root)
    source = json.loads((root / "FORGE_SOURCE.json").read_text())
    version = source["version"]
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        fail("Invalid Python release version")
    if tag != "v" + version or source["tag"] != "python-v" + version:
        fail("Release tag/version mismatch")
    if source["repository"] != REPOSITORY or not re.fullmatch(r"[0-9a-f]{40}", source["commit"]):
        fail("Invalid Forge source identity")
    files = sorted((root / "dist").iterdir())
    if len(files) != 5 or {p.name for p in files} != set(source["wheels"]):
        fail("Expected exactly five supported wheels")
    families = []
    for path in files:
        if hashlib.sha256(path.read_bytes()).hexdigest() != source["wheels"][path.name]:
            fail("Wheel checksum mismatch: " + path.name)
        families.append(check_wheel(path, version))
    if set(families) != FAMILIES:
        fail("Missing or duplicate wheel platform")
    return source


def stage(source, destination, wheels, tests):
    source, destination, wheels = Path(source), Path(destination), Path(wheels)
    tag, commit = os.environ["GITHUB_REF_NAME"], os.environ["GITHUB_SHA"]
    match = re.fullmatch(r"python-v(\d+\.\d+\.\d+)", tag)
    if not match:
        fail("Expected an exact Forge Python release tag")
    version = match[1]
    # Read the package version without executing any package or loading a DLL.
    package = source.joinpath("Cargo.toml").read_text()
    package_section = re.search(r"(?ms)^\[package\]\s*\n(.*?)(?=^\[|\Z)", package)
    actual = re.search(r'(?m)^version\s*=\s*"([^"]+)"', package_section[1]) if package_section else None
    if not actual or actual[1] != version:
        fail("Forge source/tag version mismatch")
    destination.mkdir(parents=True, exist_ok=True)
    shutil.copytree(wheels, destination / "dist")
    for name in ("README.md", "CHANGELOG.md", "LICENSE"):
        shutil.copyfile(source / name, destination / name)
    shutil.copytree(source / "src", destination / "src", ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.so", "*.pyd"))
    shutil.copytree(source / ".github", destination / ".github", ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    shutil.copytree(tests, destination / "tests", ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache", "*.pyc"))
    manifest = {"repository": REPOSITORY, "commit": commit, "tag": tag, "version": version,
                "wheels": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((destination / "dist").iterdir()) if p.is_file()}}
    (destination / "FORGE_SOURCE.json").write_text(json.dumps(manifest, indent=2) + "\n")
    verify(destination, "v" + version)


def pypi_files(version):
    request = urllib.request.Request("https://pypi.org/pypi/python-dotenvx/" + version + "/json", headers={"User-Agent": "python-dotenvx-release"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)["urls"]
    except urllib.error.HTTPError as error:
        if error.code == 404:
            return []
        raise


def prepare_upload(root, tag, fetch=pypi_files):
    root = Path(root)
    source = verify(root, tag)
    env = os.environ
    authorized = env.get("GITHUB_ACTIONS") == "true" and env.get("GITHUB_REPOSITORY") == "dotenvx/python-dotenvx" and (
        (env.get("GITHUB_EVENT_NAME") == "push" and env.get("GITHUB_REF") == "refs/tags/" + tag) or
        (env.get("GITHUB_EVENT_NAME") == "workflow_dispatch" and env.get("PUBLISH") == "true"))
    if not authorized:
        fail("Prepare uploads only from the matching public Python release workflow")
    existing = {item["filename"]: item["digests"]["sha256"] for item in fetch(source["version"])}
    pending = []
    for name, digest in source["wheels"].items():
        if name in existing:
            if existing[name] != digest:
                fail("Already published with different contents: " + name)
            print("Already published " + name + " (matching SHA-256)")
        else:
            pending.append(name)
    # All checks complete before making any files available to the upload action.
    upload = root / ".pypi-upload"
    if upload.exists():
        shutil.rmtree(upload)
    upload.mkdir()
    for name in pending:
        shutil.copyfile(root / "dist" / name, upload / name)
    if env.get("GITHUB_OUTPUT"):
        with open(env["GITHUB_OUTPUT"], "a") as output:
            output.write("count=" + str(len(pending)) + "\n")
    return pending


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    stage_args = commands.add_parser("stage")
    for name in ("source", "destination", "wheels", "tests"):
        stage_args.add_argument(name)
    commands.add_parser("verify")
    commands.add_parser("prepare-upload")
    args = parser.parse_args()
    if args.command == "stage":
        stage(args.source, args.destination, args.wheels, args.tests)
    elif args.command == "verify":
        verify(".", os.environ["RELEASE_TAG"])
        print("Python release contents verified")
    else:
        prepare_upload(".", os.environ["RELEASE_TAG"])


if __name__ == "__main__":
    main()
