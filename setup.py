import io
import os
import re
from setuptools import setup


def read(*paths):
    with io.open(os.path.join(*paths), encoding="utf_8") as f:
        return f.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


HERE = os.path.abspath(os.path.dirname(__file__))

setup(
    name="foolaunch",
    version=find_version("src", "foolaunch", "__init__.py"),
    description="A utility for launching an ec2 server from a repository of templates.",
    long_description=read(HERE, "README.md"),
    long_description_content_type="text/markdown",
    url="https://github.com/ldgabbay/foolaunch",
    author="Lynn Gabbay",
    author_email="gabbay@gmail.com",
    license="MIT",
    classifiers = [
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    packages=["foolaunch"],
    package_dir={"foolaunch": "src/foolaunch"},
    package_data={"foolaunch": ["prices.txt"]},
    entry_points={
        "console_scripts": [
            "foolaunch = foolaunch.__main__:main",
        ],
    },
    test_suite="tests",
    install_requires=[
        "ujson~=1.35",
        "foostache~=1.2",
        "boto",
    ],
    python_requires=">=3.6, <4",
)
