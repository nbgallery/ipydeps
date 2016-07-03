# vim: expandtab shiftwidth=4 softtabstop=4

import logging
import pip as _pip
import re
import unittest

def _pkg_names(s):
    '''
    Finds potential package names using a regex
    so weird strings that might contain code
    don't get through.
    '''
    pat = re.compile('[A-Za-z0-9_]+')
    return pat.findall(s)

def _pkg_name_list(x):
    if type(x) is list:
        x = ' '.join(x)

    packages = _pkg_names(x)
    packages = [ p.strip() for p in packages ]
    packages = [ p for p in packages if len(p) > 0 ]
    return packages

def pip(pkg_name, verbose=False):
    options = [
        'install',
        '--user',
    ]

    if verbose:
        options.append('-vvv')

    packages = _pkg_name_list(pkg_name)

    if len(packages) > 0:
        _pip.main(options + packages)
    else:
        logging.warning('no packages specified')

class PkgNameTests(unittest.TestCase):
    def test_pkg_names(self):
        self.assertTrue(len(_pkg_names('abc DEF hIj')) == 3)

    def test_pkg_name_list(self):
        self.assertTrue(len(_pkg_name_list('abc DEF hIj')) == 3)
        self.assertTrue(len(_pkg_name_list(['abc', 'DEF', 'hIj'])) == 3)

if __name__ == "__main__":
    unittest.main()
