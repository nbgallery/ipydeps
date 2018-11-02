# vim: expandtab tabstop=4 shiftwidth=4

import pkgutil
import sys

if sys.version_info.major == 3:
    from html import escape
elif sys.version_info.major == 2:
    from cgi import escape
else:
    raise Exception('Invalid version of Python')

def _html_escape(s):
    return escape(s, quote=True)

def _in_ipython():
    try:
        from IPython import get_ipython

        if get_ipython() is not None:
            return True
        else:
            return False

    except ImportError:
        return False

    return False

_stdlib_list = []

def _load_stdlib_packages():
    if sys.version_info.major == 3:
        _stdlib_list = pkgutil.get_data(__name__, 'data/libs3.txt')
    elif sys.version_info.major == 2:
        _stdlib_list = pkgutil.get_data(__name__, 'data/libs2.txt')

    _stdlib_list = [ x.strip() for x in _stdlib_list.split('\n') ]
    _stdlib_list = [ x for x in _stdlib_list if len(x) > 0 ]

def _in_stdlib(package):
    if package.lower().strip() in _stdlib_list:
        return True
    return False
