# vim: expandtab tabstop=4 shiftwidth=4

from time import sleep

import json
import logging
import os
import pip as _pip
import pypki2
import re
import sys

_logger = logging.getLogger('ipydeps')
_logger.addHandler(logging.NullHandler())

if sys.version_info.major == 3:
    from urllib.request import urlopen
    from urllib.error import HTTPError
    import subprocess as commands
    import importlib
elif sys.version_info.major == 2:
    from urllib2 import urlopen, HTTPError
    import commands
else:
    _logger.error('Unknown version of Python: {v}'.format(v=sys.version_info.major))


_per_package_params = ['--allow-unverified', '--allow-external']

def _bin_to_utf8(d):
    if sys.version_info.major == 3:
        return str(d, encoding='utf8')
    elif sys.version_info.major == 2:
        return unicode(d)
    else:
        return d

def _str_to_bin(s):
    if sys.version_info.major == 3:
        return bin(s, encoding='utf8')
    elif sys.version_info.major == 2:
        return s
    else:
        return s

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

def _config_dir():
    home = _find_user_home()
    config_dir = home + '/.config/ipydeps'

    if not os.path.exists(config_dir):
        try:
            os.makedirs(config_dir, 0o755)
        except FileExistsError:
            pass
        except Exception as e:
            _logger.error('Cannot create config directory: {0}'.format(str(e)))

    if os.path.exists(config_dir):
        return config_dir
    else:
        raise Exception('Unable to determine config directory')

def _config_location():
    config_dir = _config_dir()
    config_path = config_dir + os.sep + 'ipydeps.conf'

    if os.path.exists(config_dir):
        if not os.path.exists(config_path):
            _write_config(config_path, [])

        return config_path
    else:
        raise Exception('Unable to determine path to ipydeps.conf')

def _write_dependencies_link(path, url):
    url = url.strip()

    with open(path, 'w') as f:
        if len(url) > 0:
            f.write(url)

def _dependencies_link_location():
    config_dir = _config_dir()
    dep_path = config_dir + os.sep + 'dependencies.link'

    if os.path.exists(config_dir):
        if not os.path.exists(dep_path):
            _write_dependencies_link(dep_path, '')

        return dep_path
    else:
        raise Exception('Unable to determine path to dependencies.link')

def _read_dependencies_link(path):
    link = ''

    with open(path, 'r') as f:
        link = f.read().split('\n')
        link = link[0].strip()

    return link

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
        importlib.invalidate_caches()
    sleep(2)

def _pkg_names(s):
    '''
    Finds potential package names using a regex
    so weird strings that might contain code
    don't get through.
    '''
    pat = re.compile('[A-Za-z0-9_-]+')
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

def _py_name():
    major = sys.version_info.major
    minor = sys.version_info.minor
    micro = sys.version_info.micro
    return 'python-{major}.{minor}.{micro}'.format(major=major, minor=minor, micro=micro)

def _read_dependencies_json(dep_link):
    dep_link = dep_link.strip()

    if len(dep_link) == 0:
        return {}

    try:
        resp = urlopen(dep_link)
    except HTTPError as e:
        _logger.error(_bin_to_utf8(e.read()))
        return {}

    d = _bin_to_utf8(resp.read())

    try:
        j = json.loads(d)
    except Exception as e:
        _logger.error(str(e))
        return {}

    return j

def _find_overrides(packages, dep_link):
    dep_json = _read_dependencies_json(dep_link)
    py_name = _py_name()

    overrides = {}

    if py_name in dep_json:
        for pkg in packages:
            if pkg in dep_json[py_name]:
                overrides[pkg] = dep_json[py_name][pkg]

    return overrides

def package(pkg_name):
    packages = _pkg_name_list(pkg_name)

    for pkg in packages:
        _logger.debug(commands.getoutput('apk update'))
        _logger.debug(commands.getoutput('apk add '+pkg))

def _run_overrides(overrides):
    for name, commands in overrides:
        _logger.debug('Working overrides for {0}'.format(name))

        for command in commands:
            if command[0] == 'package' and len(command) > 1:
                package(command[1:])
            elif len(command) > 0:
                _logger.debug(command.getoutput(' '.join(command)))

def _in_virtualenv():
    # based on http://stackoverflow.com/questions/1871549/python-determine-if-running-inside-virtualenv
    if hasattr(sys, 'real_prefix'):
        return True
    return False

def pip(pkg_name, verbose=False):
    args = [
        'install',
    ]

    if not _in_virtualenv():
        args.append('--user')

    if verbose:
        args.append('-vvv')

    packages = _pkg_name_list(pkg_name)
    overrides = _find_overrides(packages, _read_dependencies_link(_dependencies_link_location()))

    _run_overrides(overrides)

    packages = list(set(packages) - set(overrides.keys()))
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
