# vim: expandtab shiftwidth=4 softtabstop=4

import unittest

from ipydeps import _pkg_names, _pkg_name_list

class PkgNameTests(unittest.TestCase):
    def test_pkg_names(self):
        self.assertEqual(len(_pkg_names('abc DEF hIj')), 3)

    def test_pkg_name_list(self):
        self.assertEqual(len(_pkg_name_list('abc DEF hIj')), 3)
        self.assertEqual(len(_pkg_name_list(['abc', 'DEF', 'hIj'])), 3)

    def test_bad_pkg_name(self):
        self.assertEqual(len(_pkg_name_list(['exec', 'exec()'])), 1)
