# vim: expandtab shiftwidth=4 softtabstop=4

import pip as _pip

def pip(pkg_name):
    _pip.main([
        'install',
        '--user',
        pkg_name
    ])
