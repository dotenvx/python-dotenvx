import io
import os

from dotenvx import dotenv_values, find_dotenv, load_dotenv, load_dotenvx

PRIVATE_KEY = (
    "a4547dcd9d3429615a3649bb79e87edb62ee6a74b007075e9141ae44f5fb412c"
)
PUBLIC_KEY = (
    "03da6adce70a0e5b1b518357e8b5ecc9d85e79284908b4a87ed0c9974bcae60fa4"
)
ENCRYPTED_WORLD = (
    "encrypted:BE9Y7LKANx77X1pv1HnEoil93fPa5c9rpL/1ps48uaRT9zM8VR6mHx9y"
    "M+HktKdsPGIZELuZ7rr2mn1gScsmWitppAgE/1lVprNYBCqiYeaTcKXjDUXU5"
    "LfsEsflnAsDhT/kWG1l"
)


def test_dotenv_values_uses_native_parser(monkeypatch):
    monkeypatch.setenv("HOST", "example.com")

    values = dotenv_values(stream=io.StringIO(
        "GREETING=hello\nURL=https://${HOST}\n"
    ))

    assert values == {
        "GREETING": "hello",
        "URL": "https://example.com",
    }
    assert "GREETING" not in os.environ


def test_load_dotenv_respects_override(tmp_path, monkeypatch):
    path = tmp_path / ".env"
    path.write_text("EXISTING=file\nADDED=value\n", encoding="utf-8")
    monkeypatch.setenv("EXISTING", "environment")
    monkeypatch.delenv("ADDED", raising=False)

    assert load_dotenv(path) is True
    assert os.environ["EXISTING"] == "environment"
    assert os.environ["ADDED"] == "value"

    assert load_dotenv(path, override=True) is True
    assert os.environ["EXISTING"] == "file"


def test_load_dotenvx_returns_values(tmp_path, monkeypatch):
    path = tmp_path / ".env"
    path.write_text("HELLO=world\n", encoding="utf-8")
    monkeypatch.delenv("HELLO", raising=False)

    assert load_dotenvx(path) == {"HELLO": "world"}
    assert os.environ["HELLO"] == "world"


def test_find_dotenv_walks_to_parent(tmp_path, monkeypatch):
    env_path = tmp_path / ".env"
    env_path.write_text("HELLO=world\n", encoding="utf-8")
    child = tmp_path / "one" / "two"
    child.mkdir(parents=True)
    monkeypatch.chdir(child)

    assert find_dotenv() == str(env_path)


def test_load_dotenv_decrypts_with_neighboring_key_file(tmp_path, monkeypatch):
    env_path = tmp_path / ".env"
    env_path.write_text(
        f"DOTENV_PUBLIC_KEY={PUBLIC_KEY}\nSECRET={ENCRYPTED_WORLD}\n",
        encoding="utf-8",
    )
    (tmp_path / ".env.keys").write_text(
        f"DOTENV_PRIVATE_KEY={PRIVATE_KEY}\n",
        encoding="utf-8",
    )
    monkeypatch.delenv("SECRET", raising=False)

    assert load_dotenv(env_path) is True
    assert os.environ["SECRET"] == "World"


def test_load_dotenv_decrypts_with_process_environment_only(tmp_path, monkeypatch):
    env_path = tmp_path / ".env"
    env_path.write_text(
        f"DOTENV_PUBLIC_KEY={PUBLIC_KEY}\nSECRET={ENCRYPTED_WORLD}\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("DOTENV_PRIVATE_KEY", PRIVATE_KEY)
    monkeypatch.delenv("SECRET", raising=False)

    assert not (tmp_path / ".env.keys").exists()
    assert load_dotenv(env_path) is True
    assert os.environ["SECRET"] == "World"
