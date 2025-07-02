# vim: expandtab tabstop=4 shiftwidth=4

import pytest
import sys

from ipydeps.ipydeps import subtract_stdlib
from ipydeps.utils import get_stdlib_packages

def test_stdlib_py2():
    packages = get_stdlib_packages(version=2)
    assert len(packages) == 277

def test_stdlib_py3():
    packages = get_stdlib_packages(version=3)
    if sys.version_info.minor >= 10:
        assert len(packages) >= 303
    else:
        assert len(packages) == 203

def test_without_stdlib_packages():
    stdlib_packages = get_stdlib_packages()
    packages = set(['bokeh', 'pandas', 'yourmom'])
    remaining = subtract_stdlib(stdlib_packages, packages)
    assert len(remaining) == 3

def test_with_stdlib_packages():
    stdlib_packages = get_stdlib_packages()
    packages = set(['bokeh', 'pandas', 'yourmom', 'multiprocessing', 're'])
    remaining = subtract_stdlib(stdlib_packages, packages)
    assert len(remaining) == 3
