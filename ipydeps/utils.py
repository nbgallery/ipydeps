# vim: expandtab tabstop=4 shiftwidth=4

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
