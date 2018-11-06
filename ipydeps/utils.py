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

def _stdlib_packages(version=sys.version_info.major):
    stdlib_list = b''

    if version == 3:
        stdlib_list = pkgutil.get_data(__name__, 'data/libs3.txt')
    elif version == 2:
        stdlib_list = pkgutil.get_data(__name__, 'data/libs2.txt')

    stdlib_list = str(stdlib_list, encoding='utf8')
    stdlib_list = [ x.strip() for x in stdlib_list.split('\n') ]
    stdlib_list = [ x for x in stdlib_list if len(x) > 0 ]
    return set(stdlib_list)
