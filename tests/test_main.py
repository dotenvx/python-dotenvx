import io
import json
import os

import pytest

from dotenvx import dotenv_values, find_dotenv, load_dotenv, load_dotenvx
from dotenvx._native import load_env

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


@pytest.fixture(autouse=True)
def restore_environment():
    previous = dict(os.environ)
    yield
    os.environ.clear()
    os.environ.update(previous)


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


def test_missing_file_warns_and_continues(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    assert load_dotenv() is False
    assert "MISSING_ENV_FILE" in capsys.readouterr().err


def test_decryption_error_warns_and_loads_available_values(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("DOTENV_PRIVATE_KEY", raising=False)
    monkeypatch.delenv("LL_VALUE", raising=False)
    monkeypatch.delenv("LL_SECRET", raising=False)
    (tmp_path / ".env").write_text(f"LL_VALUE=loaded\nLL_SECRET={ENCRYPTED_WORLD}\n")
    assert load_dotenv() is True
    assert os.environ["LL_VALUE"] == "loaded"
    assert os.environ["LL_SECRET"] == ENCRYPTED_WORLD
    assert "DECRYPTION_FAILED" in capsys.readouterr().err


def test_explicit_strictness_raises_before_mutating_environment(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("LL_VALUE", raising=False)
    (tmp_path / ".env").write_text("LL_VALUE=not-loaded\nLL_PORT=invalid\n")
    (tmp_path / "Dotenvxfile").write_text('env "LL_PORT", type: "port"')
    with pytest.raises(RuntimeError, match="INVALID_ENV"):
        load_dotenv(strict=True)
    assert "LL_VALUE" not in os.environ


def test_dotenvxfile_strictness_applies_before_reading(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "Dotenvxfile").write_text("strict true")
    with pytest.raises(RuntimeError, match="MISSING_ENV_FILE"):
        load_dotenv()


def test_policy_validation_warns_by_default(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("LL_VALUE", raising=False)
    (tmp_path / ".env").write_text("LL_VALUE=loaded")
    (tmp_path / "Dotenvxfile").write_text('env "LL_REQUIRED", required: true')
    assert load_dotenv() is True
    assert os.environ["LL_VALUE"] == "loaded"
    assert "INVALID_ENV" in capsys.readouterr().err


def test_ignored_errors_do_not_raise_under_policy_strictness(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("LL_VALUE", raising=False)
    (tmp_path / ".env").write_text("LL_VALUE=loaded")
    (tmp_path / "Dotenvxfile").write_text('strict true\nenv "LL_REQUIRED", required: true')
    assert load_dotenv(ignore=["INVALID_ENV"]) is True
    assert os.environ["LL_VALUE"] == "loaded"
    assert capsys.readouterr().err == ""


def test_file_policy_strictness_raises(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env").write_text("LL_VALUE=not-loaded")
    (tmp_path / "Dotenvxfile").write_text('file ".env" do\n strict true\n env "LL_REQUIRED", required: true\nend')
    with pytest.raises(RuntimeError, match="INVALID_ENV"):
        load_dotenv()


def test_native_loader_returns_redaction_metadata_not_redacted_values(tmp_path):
    (tmp_path / ".env").write_text("LL_SECRET=real-value")
    (tmp_path / "Dotenvxfile").write_text('env "LL_SECRET", redacted: true')
    result = json.loads(load_env(json.dumps({"cwd": str(tmp_path)})))
    assert result["secrets"] == ["real-value"]
    assert result["values"] == {"LL_SECRET": "real-value"}
    assert "LL_SECRET" not in os.environ


def test_stream_loading_uses_shared_rust_parsing(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert dotenv_values(stream=io.StringIO("BARE\nLL_VALUE='literal'\n")) == {"LL_VALUE": "literal"}
    monkeypatch.setenv("LL_PARENT", "expanded")
    assert dotenv_values(stream=io.StringIO("LL_VALUE=$LL_PARENT\n")) == {"LL_VALUE": "expanded"}



def test_malformed_policy_preserves_structured_error_code(tmp_path):
    (tmp_path / "Dotenvxfile").write_text("not_a_setting true")
    previous = dict(os.environ)
    result = json.loads(load_env(json.dumps({"cwd": str(tmp_path)})))
    assert result["fatal"] is True
    assert result["diagnostics"][0]["code"] == "MALFORMED_DOTENVXFILE"
    assert dict(os.environ) == previous


@pytest.mark.parametrize("function", [load_dotenv, dotenv_values])
@pytest.mark.parametrize("option,value", [("interpolate", False), ("encoding", "latin-1"), ("verbose", True)])
def test_removed_compatibility_options_are_rejected(function, option, value):
    with pytest.raises(TypeError, match=option):
        function(**{option: value})


def test_literal_unicode_and_quoted_dollars_are_not_rewritten(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    source = "LL_UNICODE='\ue000'\nLL_DOLLAR='$UNCHANGED'\n"
    assert dotenv_values(stream=io.StringIO(source)) == {"LL_UNICODE": "\ue000", "LL_DOLLAR": "$UNCHANGED"}


def test_stream_loading_updates_environment(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert load_dotenv(stream=io.StringIO("LL_VALUE=stream\n")) is True
    assert os.environ["LL_VALUE"] == "stream"


def test_shared_nextjs_selection_and_optional_files(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env.development.local").write_text("LL_VALUE=first")
    (tmp_path / ".env").write_text("LL_VALUE=base")
    assert load_dotenv(convention="nextjs") is True
    assert os.environ["LL_VALUE"] == "first"
    assert capsys.readouterr().err == ""


def test_shared_convention_environment_and_explicit_precedence(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("DOTENV_CONVENTION", "flow")
    monkeypatch.setenv("NODE_ENV", "test")
    (tmp_path / ".env.local").write_text("LL_LOCAL=flow")
    (tmp_path / ".env.test").write_text("LL_VALUE=test")
    assert load_dotenv(convention="nextjs") is True
    assert os.environ["LL_VALUE"] == "test"
    assert "LL_LOCAL" not in os.environ
    monkeypatch.setenv("DOTENV_CONVENTION", "")
    monkeypatch.setenv("DOTENV_CONFIG_CONVENTION", "flow")
    assert load_dotenv() is True
    assert os.environ["LL_LOCAL"] == "flow"


def test_shared_directory_expansion(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    app = tmp_path / "app"
    app.mkdir()
    (app / ".env").write_text("LL_VALUE=directory")
    assert load_dotenv(app) is True
    assert os.environ["LL_VALUE"] == "directory"


def test_shared_key_based_file_inference(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("DOTENV_PRIVATE_KEY_PRODUCTION", PRIVATE_KEY)
    (tmp_path / ".env.production").write_text(f"LL_SECRET={ENCRYPTED_WORLD}")
    assert load_dotenv() is True
    assert os.environ["LL_SECRET"] == "World"


def test_explicit_key_files_are_forwarded_to_rust(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env").write_text(f"LL_SECRET={ENCRYPTED_WORLD}")
    (tmp_path / "custom.keys").write_text(f"DOTENV_PRIVATE_KEY={PRIVATE_KEY}")
    assert load_dotenv(".env", key_files="custom.keys") is True
    assert os.environ["LL_SECRET"] == "World"


def test_multiple_files_use_shared_ordering(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "first.env").write_text("LL_VALUE=first")
    (tmp_path / "second.env").write_text("LL_VALUE=second")
    assert load_dotenv(["first.env", "second.env"]) is True
    assert os.environ["LL_VALUE"] == "first"
    assert load_dotenv(["first.env", "second.env"], override=True) is True
    assert os.environ["LL_VALUE"] == "second"


def test_shared_file_configuration_and_explicit_precedence(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("DOTENV_FILE", "custom.env")
    (tmp_path / "custom.env").write_text("LL_VALUE=configured")
    (tmp_path / "explicit.env").write_text("LL_VALUE=explicit")
    assert load_dotenv() is True
    assert os.environ["LL_VALUE"] == "configured"
    assert load_dotenv("explicit.env", override=True) is True
    assert os.environ["LL_VALUE"] == "explicit"


def test_shared_ignore_environment_configuration(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("DOTENV_IGNORE", "MISSING_ENV_FILE")
    assert load_dotenv(strict=True) is False
    assert capsys.readouterr().err == ""


def test_invalid_convention_uses_shared_diagnostic(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(RuntimeError, match="INVALID_CONVENTION"):
        load_dotenv(convention="unknown")
