# vim: expandtab shiftwidth=4 softtabstop=4

from tempfile import NamedTemporaryFile

import json
import logging
import os
import unittest

_logger = logging.getLogger('ipydeps')
_log_handler = logging.StreamHandler()
_log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
_log_handler.setLevel(logging.DEBUG)
_logger.addHandler(_log_handler)

from ipydeps import _config_location
from ipydeps import _find_overrides
from ipydeps import _per_package_args
from ipydeps import _pkg_names
from ipydeps import _pkg_name_list
from ipydeps import _py_name
from ipydeps import _read_config
from ipydeps import _str_to_bin
from ipydeps import _write_config

class PkgNameTests(unittest.TestCase):
    def test_pkg_names(self):
        self.assertEqual(len(_pkg_names('abc DEF hIj')), 3)

    def test_pkg_name_list(self):
        self.assertEqual(len(_pkg_name_list('abc DEF hIj')), 3)
        self.assertEqual(len(_pkg_name_list(['abc', 'DEF', 'hIj'])), 3)

    def test_bad_pkg_name(self):
        self.assertEqual(len(_pkg_name_list(['exec', 'exec()'])), 1)

class OverrideTests(unittest.TestCase):
    def test_no_overrides(self):
        names = ['foo', 'bar', 'baz']
        overrides = _find_overrides(names, '')

        for name in names:
            self.assertTrue(name not in overrides)

    def test_all_overrides(self):
        with NamedTemporaryFile('w') as f:
            j = {
                    _py_name(): {
                        'foo': [
                            [ 'package', 'foo' ]
                        ],
                        'bar': [
                            [ 'package', 'foo' ],
                            [ 'package', 'bar' ]
                        ],
                        'baz': [
                            [ 'package', 'foo', 'baz' ]
                        ]
                    }
            }

            f.write(_str_to_bin(json.dumps(j)))
            f.flush()

            names = ['foo', 'bar', 'baz']
            overrides = _find_overrides(names, 'file://'+f.name)

            for name in names:
                self.assertTrue(name in overrides)

class ConfigTests(unittest.TestCase):
    path = '/tmp/ipydeps_test.conf'

    def tearDown(self):
        if os.path.exists(self.path):
            os.remove(self.path)

    def test_config_location(self):
        self.assertGreater(len(_config_location()), 0)

    def test_write_read(self):
        _write_config(self.path, ['--allow-unverified','--allow-external'])
        options = _read_config(self.path)
        self.assertTrue('--allow-unverified' in options)
        self.assertTrue('--allow-external' in options)

    def test_per_package_args(self):
        args = _per_package_args(['foo', 'bar'], ['--allow-unverified', '--allow-external'])
        self.assertTrue('--allow-unverified=foo' in args)
        self.assertTrue('--allow-external=foo' in args)
        self.assertTrue('--allow-unverified=bar' in args)
        self.assertTrue('--allow-external=bar' in args)
