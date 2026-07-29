[![dotenvx](https://dotenvx.com/better-banner.png)](https://dotenvx.com)

*a better dotenv*–from the creator of [`dotenv`](https://github.com/motdotla/dotenv).

* run anywhere (cross-platform)
* multi-environment
* encrypted envs

&nbsp;


### Quickstart [![PyPI version](https://badge.fury.io/py/python-dotenvx.svg)](http://badge.fury.io/py/python-dotenvx)

Install and use it in code just like `python-dotenv`.

```sh
pip install python-dotenvx
```

The wheel includes native dotenvx Rust primitives. No dotenvx executable or
post-install download is required.

```python
# main.py
import os
from dotenvx import load_dotenv

load_dotenv()  # take environment variables from .env

print(os.getenv("S3_BUCKET"))
```

You can also parse values without changing the environment:

```python
from dotenvx import dotenv_values

values = dotenv_values(".env")
```

Encrypted values are decrypted using `DOTENV_PRIVATE_KEY` from the environment
or a neighboring `.env.keys` file.

&nbsp;
