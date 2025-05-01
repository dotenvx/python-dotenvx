> [!IMPORTANT]
>
> Warning: work in progress. until complete, please use [github.com/dotenvx/dotenvx](https://github.com/dotenvx/dotenvx) directly.
>
> see [python examples](https://dotenvx.com/docs/languages/python)
>

---

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

Then run `dotenvx-postinstall` to install the `dotenvx` binary (python-dotenvx is a wrapper).

```sh
dotenvx-postinstall

# or to specify the os-arch – useful for building binaries to a specific target such as linux-x86_64 on aws lambda
dotenvx-postinstall --os linux --arch x86_64

# you might also find you need to specify PYTHONPATH depend on how/where dotenvx installs to
PYTHONPATH=. bin/dotenvx-postinstall --os linux --arch x86_64
```

Then use it in code.

```python
# main.py
import os
from dotenvx import load_dotenvx
load_dotenvx() # take environment variables from .env.

print(os.getenv("S3_BUCKET"))
```

&nbsp;
