# vim: expandtab tabstop=4 shiftwidth=4

import sys

from . import pip

if len(sys.argv) >= 2:
    pip(sys.argv[1:])
