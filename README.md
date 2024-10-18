>
> Warning: work in progress. until complete, please use [github.com/dotenvx/dotenvx](https://github.com/dotenvx/dotenvx)
>

[![dotenvx](https://dotenvx.com/better-banner.png)](https://dotenvx.com)

*a better dotenv*–from the creator of [`dotenv`](https://github.com/motdotla/dotenv).

* run anywhere (cross-platform)
* multi-environment
* encrypted envs

&nbsp;


### Quickstart [![PyPI version](https://badge.fury.io/py/python-dotenvx.svg)](http://badge.fury.io/py/python-dotenvx) 

Install and use it in code just like `python-dotenv`.

```sh
pip install python-dotenv
```
```python
# main.py
import os
from dotenvx import load_dotenvx
load_dotenvx()  # take environment variables from .env.

print(os.getenv("S3_BUCKET"))
```

&nbsp;

