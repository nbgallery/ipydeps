# vim: expandtab tabstop=4 shiftwidth=4

import logging
import unittest

_logger = logging.getLogger('ipydeps')
_log_handler = logging.StreamHandler()
_log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
_log_handler.setLevel(logging.DEBUG)
_logger.addHandler(_log_handler)

from ipydeps import _subtract_stdlib
from ipydeps.utils import _stdlib_packages

class StdlibTests(unittest.TestCase):
    def test_stdlib_py2(self):
        packages = _stdlib_packages(version=2)
        self.assertEqual(len(packages), 277)

    def test_stdlib_py3(self):
        packages = _stdlib_packages(version=3)
        self.assertEqual(len(packages), 203)

    def test_without_stdlib_packages(self):
        stdlib_packages = _stdlib_packages()
        packages = set(['bokeh', 'pandas', 'yourmom'])
        remaining = _subtract_stdlib(stdlib_packages, packages)
        self.assertEqual(len(remaining), 3)

    def test_with_stdlib_packages(self):
        stdlib_packages = _stdlib_packages()
        packages = set(['bokeh', 'pandas', 'yourmom', 'multiprocessing', 're'])
        remaining = _subtract_stdlib(stdlib_packages, packages)
        self.assertEqual(len(remaining), 3)
