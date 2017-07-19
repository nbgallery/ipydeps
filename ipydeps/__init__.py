# vim: expandtab tabstop=4 shiftwidth=4

from time import sleep

import json
import logging
import os
import pip as _pip
import re
import site
import sys

_logger = logging.getLogger('ipydeps')
_logger.addHandler(logging.NullHandler())

def _find_user_home():
    return os.path.expanduser('~')

def _in_virtualenv():
    # based on http://stackoverflow.com/questions/1871549/python-determine-if-running-inside-virtualenv
    if hasattr(sys, 'real_prefix'):
        return True
    return False

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

def _read_config(path):
    options = []

    with open(path, 'r') as f:
        for line in f:
            line = line.strip()

            if line.startswith('--'):
                options.append(line)

    return options

_config_options = _read_config(_config_location())

if '--use-pypki2' in _config_options:
    import pypki2
    import pypki2.pipwrapper

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
_internal_params = ['--use-pypki2']

def _bin_to_utf8(d):
    if sys.version_info.major == 3:
        return str(d, encoding='utf8')
    elif sys.version_info.major == 2:
        return unicode(d)
    else:
        return d

def _str_to_bytes(s):
    if sys.version_info.major == 3:
        return bytes(s, encoding='utf8')
    elif sys.version_info.major == 2:
        return s
    else:
        return s

def _user_site_packages():
    if not _in_virtualenv():
        return site.getusersitepackages()
    else:
        home = _find_user_home()
        major = sys.version_info.major
        minor = sys.version_info.minor
        path = '/.local/lib/python{major}.{minor}/site-packages'.format(major=major, minor=minor)
        return home+path

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

def _invalidate_cache():
    '''
    Invalidates the import cache so the next attempt to import a package
    will look for new import locations.
    '''
    if sys.version_info.major == 3:
        importlib.invalidate_caches()
    sleep(2)

def _refresh_available_packages():
    '''
    Forces a rescan of available packages in pip's vendored pkg_resources.
    '''
    _pip.utils.pkg_resources._initialize_master_working_set()

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

def _remove_internal_options(options):
    return [ opt for opt in options if opt not in _internal_params ]

def _py_name_micro():
    major = sys.version_info.major
    minor = sys.version_info.minor
    micro = sys.version_info.micro
    return 'python-{major}.{minor}.{micro}'.format(major=major, minor=minor, micro=micro)

def _py_name_minor():
    major = sys.version_info.major
    minor = sys.version_info.minor
    return 'python-{major}.{minor}'.format(major=major, minor=minor)

def _py_name_major():
    major = sys.version_info.major
    return 'python-{major}'.format(major=major)

def _case_insensitive_dependencies_json(dep_json):
    lowercased = {}

    for version in dep_json:
        lowercased[version] = {}
        packages = dep_json[version]

        for pkg in packages:
            pkg = pkg.lower()
            cmds = packages[pkg]

            if pkg in lowercased[version]:
                _logger.warning('Duplicate package name {0} in dependencies JSON.  Package names are case-insensitive.  Overwriting!'.format(pkg))

            lowercased[version][pkg] = cmds

    return lowercased

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
        j = {}

    return _case_insensitive_dependencies_json(j)

def _find_overrides(packages, dep_link):
    dep_json = _read_dependencies_json(dep_link)
    py_name_micro = _py_name_micro()
    py_name_minor = _py_name_minor()
    py_name_major = _py_name_major()

    overrides = {}

    if py_name_major in dep_json:
        for pkg in packages:
            if pkg in dep_json[py_name_major]:
                overrides[pkg] = dep_json[py_name_major][pkg]

    if py_name_minor in dep_json:
        for pkg in packages:
            if pkg in dep_json[py_name_minor]:
                overrides[pkg] = dep_json[py_name_minor][pkg]

    if py_name_micro in dep_json:
        for pkg in packages:
            if pkg in dep_json[py_name_micro]:
                overrides[pkg] = dep_json[py_name_micro][pkg]

    return overrides

def _already_installed():
    return set([ pkg.project_name for pkg in _pip.get_installed_distributions() ])

def _subtract_installed(packages):
    packages = set(( p.lower() for p in packages))  # removes duplicates
    installed = [ x.lower() for x in _already_installed() ]  # lowercase everything for comparison
    ret = set()

    # This could be done with simple set() math, but we want to log each
    # package that's already installed.
    for pkg in packages:
        if pkg in installed:
            _logger.info('{0} already installed... skipping'.format(pkg))
        else:
            _logger.info('{0} will be installed'.format(pkg))
            ret.add(pkg)

    return ret

def package(pkg_name):
    packages = _pkg_name_list(pkg_name)

    for pkg in packages:
        _logger.debug(commands.getoutput('apk update'))
        _logger.debug(commands.getoutput('apk add '+pkg))

def _run_overrides(overrides):
    for name, cmds in overrides.items():
        _logger.debug('Working overrides for {0}'.format(name))

        for command in cmds:
            if command[0] == 'package' and len(command) > 1:
                package(command[1:])
            elif len(command) > 0:
                _logger.debug(commands.getoutput(' '.join(command)))

def pip(pkg_name, verbose=False):
    args = [
        'install',
    ]

    if not _in_virtualenv():
        args.append('--user')

    if verbose:
        args.append('-vvv')

    packages = set(_pkg_name_list(pkg_name))
    orig_package_list_len = len(packages)
    packages = _subtract_installed(packages)
    overrides = _find_overrides(packages, _read_dependencies_link(_dependencies_link_location()))

    _run_overrides(overrides)
    _refresh_available_packages()

    packages = _subtract_installed(packages)
    packages = list(packages)
    args.extend(_remove_internal_options(_remove_per_package_options(_config_options)))
    args.extend(_per_package_args(packages, _config_options))

    if len(packages) > 0:
        _pip.main(args + packages)
        _invalidate_cache()
        _refresh_available_packages()
    elif orig_package_list_len > 0:
        _logger.info('All requested packages already installed')
    else:
        _logger.warning('no packages specified')

def _make_user_site_packages():
    if not _in_virtualenv():
        if not os.path.exists(_user_site_packages()):
            try:
                os.makedirs(_user_site_packages(), 0o755)
            except FileExistsError:
                pass  # ignore.  Something snuck in and created it for us
            except Exception as e:
                _logger.error('Cannot create user site-packages directory: {0}'.format(str(e)))

        if _user_site_packages() not in sys.path:
            sys.path.append(_user_site_packages())

_make_user_site_packages()
