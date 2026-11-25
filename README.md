[![dotenvx](https://dotenvx.com/banner.png?v2)](https://dotenvx.com)

*A secure dotenv*–from the creator of [`dotenv`](https://github.com/motdotla/dotenv).

* Encrypt
* Commit
* Ship

[Install](https://dotenvx.com/docs/install) · [Quickstart](https://dotenvx.com/docs/quickstart)

## Quickstart

With [uv](https://docs.astral.sh/uv/getting-started/installation/) installed, create a project and add `python-dotenvx`.

```sh
uv init hello-dotenvx
cd hello-dotenvx
uv add python-dotenvx
```

Create these two files in the project directory.

`.env`

```dotenv
HELLO=World
```

`index.py`

```python
import os
from dotenvx import load_dotenv

load_dotenv()

print(f"Hello {os.environ['HELLO']}")
```

Run the script from that directory.

```sh
uv run index.py
```

The script prints `Hello World`.

&nbsp;

## Usage

*Install* dotenvx.

```sh
$ curl -sfS https://dotenvx.sh | sh
◈ installed (2.38.2:/usr/local/bin/dotenvx)
```

*Encrypt* your secrets in `.env` files. The values become ciphertext and only your private key can unlock them.

```sh
$ dotenvx encrypt
◈ encrypted .env (039 BCA) via .env.keys ⛉
```

*Commit* your encrypted `.env` files with your code. It's safe. Now you can securely share secrets through git.

```sh
$ git add .env
$ git commit -m "encrypt .env"
```

*Ship* your code and secrets together. Dotenvx uses your private key to decrypt and inject your secrets just-in-time to your code.

```sh
$ python index.py
⟐ injected env (2) from .env (039 BCA) via .env.keys ⛉
```

&nbsp;

## Design

Three widely used and proven primitives make up Dotenvx's design. Git, .env, and secp256k1.

We chose git because it is the best way to deliver digital goods. It is the container ship of the digital world. All code travels on its ships. Why not secrets? Why invent an inferior secrets delivery mechanism when the world class one is right there at your fingertips.

We chose .env because it is the open standard for loading secrets into code. It represents environment variables, the core primitive that all secrets end up injected into at runtime of code.

Lastly, we needed to choose an encryption algorithm. Encryption of the values inside the .env file would allow us to place those values with code, leveraging git's distribution advantages while still following the twelve-factor config – by separating the decryption key from the code (environment).

It was important that we choose a proven, simple, asymmetric standard with small keys. We chose secp256k1, battle-tested by Bitcoin for more than seventeen years. We made cryptography an opinionated choice so developers wouldn't have to. Encryption just worked.

The result is a system built entirely from primitives, developers already understand, and infrastructure they already use. Secrets can travel with code without becoming part of the code. Git distributes them, .env defines how apps consume them, and secp256k1 keeps their values unreadable. The kicker, all this works by setting a single private key on your infrastructure - no more risky async coordination of secrets, no more centralized downtime risk. Your secrets are always just there with your code, ready to be unlocked at runtime.

[Read the whitepaper →](https://dotenvx.com/dotenvx.pdf?v=README)

&nbsp;
