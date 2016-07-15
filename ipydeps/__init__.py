# vim: expandtab shiftwidth=4 softtabstop=4

from time import sleep

import logging
import os
import pip as _pip
import re
import sys

if sys.version_info.major == 3:
    import subprocess as commands
    import importlib
elif sys.version_info.major == 2:
    import commands
else:
    logging.error('Unknown version of Python: {v}'.format(v=sys.version_info.major))

def _user_site_packages():
    home = os.environ['HOME']
    major = sys.version_info.major
    minor = sys.version_info.minor
    path = '/.local/lib/python{major}.{minor}/site-packages'.format(major=major, minor=minor)
    return home+path

def _invalidate_cache():
    '''
    Invalidates the import cache so the next attempt to import a package
    will look for new import locations.
    '''
    if sys.version_info.major == 3:
        importlib.invalidate_cache()
    sleep(2)

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
    packages = list(set([ p for p in packages if len(p) > 0 ]))
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
        _invalidate_cache()
    else:
        logging.warning('no packages specified')

if not os.path.exists(_user_site_packages()):
    try:
        os.makedirs(_get_user_site_packages(), 0o755)
    except FileExistsError:
        pass  # ignore.  Something snuck in and created it for us
    except Exception as e:
        logging.error('Error creating user site-packages directory: {0}'.format(str(e)))

if _user_site_packages() not in sys.path:
    sys.path.append(_user_site_packages())
