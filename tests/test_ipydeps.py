# vim: expandtab shiftwidth=4 softtabstop=4

import os
import unittest

from ipydeps import _config_location, _per_package_args, _pkg_names, _pkg_name_list, _read_config, _write_config

class PkgNameTests(unittest.TestCase):
    def test_pkg_names(self):
        self.assertEqual(len(_pkg_names('abc DEF hIj')), 3)

    def test_pkg_name_list(self):
        self.assertEqual(len(_pkg_name_list('abc DEF hIj')), 3)
        self.assertEqual(len(_pkg_name_list(['abc', 'DEF', 'hIj'])), 3)

    def test_bad_pkg_name(self):
        self.assertEqual(len(_pkg_name_list(['exec', 'exec()'])), 1)

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
