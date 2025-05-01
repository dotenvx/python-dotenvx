import os
import subprocess
from setuptools import setup, find_packages
from setuptools.command.install import install

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

class InstallBinary(install):
    def run(self):
        bin_dir = os.path.join(dir, 'src', 'dotenvx', 'bin')
        os.makedirs(bin_dir, exist_ok=True)

        # install dotenvx binary using your install script into bin/
        subprocess.run([
            'sh', '-c',
            f'curl -sfS "https://dotenvx.sh?directory={bin_dir}" | sh'
        ], check=True)

        super().run()

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
    package_data={'dotenvx': ['bin/dotenvx']},
    include_package_data=True,
    cmdclass={'install': InstallBinary},
)
