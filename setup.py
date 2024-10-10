"""setup module"""

from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as f:
    readme = f.read()

with open("LICENSE", encoding="utf-8") as f:
    _license = f.read()

setup(
    name="tinylox",
    version="0.0.1",
    description="Tiny Lox Tree-Walk interpreter",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Théo Bori",
    author_email="nagi@tilde.team",
    url="https://github.com/theobori/tinylox",
    license=_license,
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "tinylox=tinylox.tinylox:main",
        ]
    },
)
