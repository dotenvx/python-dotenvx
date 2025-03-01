import os
from setuptools import setup, find_packages

src = {}
dir = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(dir, "src/dotenvx", "__version__.py"), "r") as f:
    exec(f.read(), src)

def read_files(files):
    data = []
    for file in files:
        with open(file, encoding='utf-8') as f:
            data.append(f.read())
    return "\n".join(data)

readme = read_files(['README.md', 'CHANGELOG.md'])

setup(
    name='python-dotenvx',
    description=src['__description__'],
    long_description=readme,
    long_description_content_type='text/markdown',
    version=src['__version__'],
    license=src['__license__'],
    author=src['__author__'],
    author_email=src['__author_email__'],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url=src['__url__'],
    keywords=[
    'environment',
    'environment variables',
    'deployments',
    'settings',
    'env',
    'dotenv',
    'configurations',
    'python',
    'dotenvx'
    ],
    install_requires=[
    ],
)
