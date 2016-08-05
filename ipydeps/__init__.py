# vim: expandtab tabstop=4 shiftwidth=4

from time import sleep

import logging
import os
import pip as _pip
import re
import sys

_logger = logging.getLogger('ipydeps')
_logger.addHandler(logging.NullHandler())

if sys.version_info.major == 3:
    import subprocess as commands
    import importlib
elif sys.version_info.major == 2:
    import commands
else:
    _logger.error('Unknown version of Python: {v}'.format(v=sys.version_info.major))


_per_package_params = ['--allow-unverified', '--allow-external']

def _find_user_home():
    return os.environ['HOME']  # TODO: add support for Windows

def _user_site_packages():
    home = _find_user_home()
    major = sys.version_info.major
    minor = sys.version_info.minor
    path = '/.local/lib/python{major}.{minor}/site-packages'.format(major=major, minor=minor)
    return home+path

def _write_config(path, options):
    with open(path, 'w') as f:
        for option in options:
            f.write(option + '\n')

def _config_location():
    home = _find_user_home()
    config_dir = home + '/.config/ipydeps'
    config_path = config_dir + os.sep + 'ipydeps.conf'

    if not os.path.exists(config_dir):
        try:
            os.makedirs(config_dir, 0o755)
        except FileExistsError:
            pass
        except Exception as e:
            _logger.error('Cannot create config directory: {0}'.format(str(e)))

    if os.path.exists(config_dir):
        if not os.path.exists(config_path):
            _write_config(config_path, [])

        return config_path
    else:
        raise Exception('Unable to determine path to ipydeps.conf')

def _read_config(path):
    options = []

    with open(path, 'r') as f:
        for line in f:
            line = line.strip()

            if line.startswith('--'):
                options.append(line)

    return options

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

def _per_package_args(packages, options):
    new_options = []
    opts = _per_package_params

    for opt in opts:
        if opt in options:
            new_options.extend([ opt+'='+p for p in packages])

    return new_options

def _remove_per_package_options(options):
    return [ opt for opt in options if opt not in _per_package_params ]

def pip(pkg_name, verbose=False):
    args = [
        'install',
        '--user',
    ]

    if verbose:
        args.append('-vvv')

    packages = _pkg_name_list(pkg_name)
    config_options = _read_config(_config_location())
    args.extend(_remove_per_package_options(config_options))
    args.extend(_per_package_args(packages, config_options))

    if len(packages) > 0:
        _pip.main(args + packages)
        _invalidate_cache()
    else:
        _logger.warning('no packages specified')

if not os.path.exists(_user_site_packages()):
    try:
        os.makedirs(_get_user_site_packages(), 0o755)
    except FileExistsError:
        pass  # ignore.  Something snuck in and created it for us
    except Exception as e:
        _logger.error('Cannot create user site-packages directory: {0}'.format(str(e)))

if _user_site_packages() not in sys.path:
    sys.path.append(_user_site_packages())
