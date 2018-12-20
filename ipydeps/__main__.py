# vim: expandtab tabstop=4 shiftwidth=4

from . import pip

import sys

if len(sys.argv) >= 2:
    pip(sys.argv[1:])
