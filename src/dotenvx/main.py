from typing import Optional, IO
import dotenv

import ecies
import base64
import os

def decrypt_value(value: str, private_key: str) -> str:
    private_key       = ecies.PrivateKey.from_hex(private_key)
    base64_ciphertext = value.lstrip('encrypted:')
    ciphertext        = base64.b64decode(base64_ciphertext)
    decrypted_value   = ecies.decrypt(private_key.to_hex(), ciphertext)
    return decrypted_value.decode()

def load_dotenvx(
    dotenv_path: Optional[str]     = None,
    stream     : Optional[IO[str]] = None,
    verbose    : bool              = False,
    override   : bool              = False,
    interpolate: bool              = True,
    encoding   : Optional[str]     = "utf-8",
) -> bool:

    return_value = False  # Set to True if at least one variable is set, otherwise False

    env_values = dotenv.dotenv_values(
        dotenv_path = dotenv_path,
        stream      = stream,
        verbose     = verbose,
        interpolate = interpolate,
        encoding    = encoding)
    
    env_keys_values = dotenv.dotenv_values('.env.keys')
    dotenv_private_key = env_keys_values['DOTENV_PRIVATE_KEY']
    
    # Decrypt encrypted values
    for key, value in env_values.items():
        if value.startswith('encrypted:'):
            env_values[key] = decrypt_value(value, dotenv_private_key)
    
    # Set environment variables
    for key, value in env_values.items():
        if key in os.environ and not override:
            continue
        os.environ[key] = value
        return_value = True
    
    return return_value
