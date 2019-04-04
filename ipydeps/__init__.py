# vim: expandtab tabstop=4 shiftwidth=4

from .utils import _bytes_to_str, _in_ipython, _stdlib_packages

from functools import partial
from time import sleep

import json
import logging
import os
import pkg_resources
import re
import site
import subprocess
import sys

if _in_ipython():
    from .logger import _IPythonLogger
    _logger = _IPythonLogger()
else:
    _logger = logging.getLogger('ipydeps')
    _logger.addHandler(logging.StreamHandler())
    _logger.setLevel(logging.DEBUG)

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

if sys.version_info.major == 3:
    from urllib.request import urlopen
    from urllib.error import HTTPError
    from importlib import invalidate_caches as importlib_invalidate_caches
elif sys.version_info.major == 2:
    from urllib2 import urlopen, HTTPError

    def importlib_invalidate_caches():
        pass
else:
    _logger.error('Unknown version of Python: {v}'.format(v=sys.version_info.major))


_per_package_params = ['--allow-unverified', '--allow-external']
_internal_params = ['--use-pypki2']
_pip_run_args = [sys.executable, '-m', 'pip']

def _get_pip_exec(config_options):
    def _pip_exec(args1, args2):
        return _run_get_stderr(_pip_run_args+args1+args2)

    if '--use-pypki2' in config_options:
        import pypki2pip

        def _pip_pki_exec(args):
            f = partial(_pip_exec, args)
            return pypki2pip.pip_pki_exec(f)

        return _pip_pki_exec

    return partial(_pip_exec, [])

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
    importlib_invalidate_caches()
    sleep(2)

def _refresh_available_packages():
    '''
    Forces a rescan of available packages in pip's vendored pkg_resources
    and the main pkg_resources package, also used by pbr.
    '''
    for entry in sys.path:
        pkg_resources.working_set.add_entry(entry)

def _pkg_names(s):
    '''
    Finds potential package names using a regex
    so weird strings that might contain code
    don't get through.  This also allows version
    specifiers.
    '''
    pat = re.compile(r'([A-Za-z][A-Za-z0-9_\-]+((<|>|<=|>=|==)[0-9]+\.[0-9]+(\.[0-9]+)?)?)')
    return [ x[0] for x in pat.findall(s) ]

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

def _get_urlopener(config_options):
    if '--use-pypki2' in config_options:
        import pypki2config
        ctx = pypki2config.ssl_context()
        return lambda url: urlopen(url, context=ctx)

    return urlopen

def _read_dependencies_json(dep_link):
    dep_link = dep_link.strip()

    if len(dep_link) == 0:
        return {}

    urlopener = _get_urlopener(_config_options)

    try:
        resp = urlopener(dep_link)
    except HTTPError as e:
        _logger.error(_bytes_to_str(e.read()))
        return {}

    d = _bytes_to_str(resp.read())

    try:
        j = json.loads(d)
    except Exception as e:
        _logger.error(str(e))
        j = {}

    return _case_insensitive_dependencies_json(j)

def _find_overrides(packages, dep_link):
    if len(packages) == 0:
        return {}

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

def _run_get_stderr(cmd):
    returncode = 0
    err = None

    try:
        subprocess.check_output(cmd, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        returncode = e.returncode

        if sys.version_info.major == 3:
            err = _bytes_to_str(e.stderr)
        elif sys.version_info.major == 2:
            err = e.output
        else:
            raise Exception('Invalid version of Python')

    return returncode, err

def _get_freeze_package_name(info):
    name, version = info.split('==')
    return name.strip()

def _process_pip_freeze_output(pkgs):
    pkgs = _bytes_to_str(pkgs).split('\n')
    pkgs = [ p for p in pkgs if len(p) > 0 and '==' in p ]
    pkgs = [ _get_freeze_package_name(p) for p in pkgs ]
    return pkgs

def _pip_freeze_packages():
    pkgs = subprocess.check_output(_pip_run_args + ['freeze','--all'])
    return _process_pip_freeze_output(pkgs)

def _already_installed():
    pr = set([ pkg.project_name for pkg in pkg_resources.working_set ])
    pf = set(_pip_freeze_packages())
    return { p.lower() for p in pr.union(pf) }

def _subtract_installed(packages):
    packages = set(( p.lower() for p in packages))  # removes duplicates
    return packages - _already_installed()

def _subtract_stdlib(stdlib_packages, packages):
    return packages - stdlib_packages

def _run_and_log_error(cmd):
    returncode, err = _run_get_stderr(cmd)

    if returncode != 0 and err is not None:
        _logger.error(err)

def package(pkg_name):
    packages = _pkg_name_list(pkg_name)

    for pkg in packages:
        _logger.debug('apk update')
        _run_and_log_error(['apk', 'update'])
        _logger.debug('apk add '+pkg)
        _run_and_log_error(['apk', 'add', pkg])

def _run_overrides(overrides):
    for name, cmds in overrides.items():
        _logger.info('Executing overrides for {0}'.format(name))

        for command in cmds:
            if command[0] == 'package' and len(command) > 1:
                package(command[1:])
            elif len(command) > 0:
                _logger.debug(' '.join(command))
                _run_and_log_error(command)

def _log_already_installed(before, requested):
    already_installed = before.intersection(requested)

    if len(already_installed) > 0:
        _logger.info('Packages already installed: {0}'.format(', '.join(sorted(list(already_installed)))))

def _log_stdlib_packages(stdlib_packages, packages):
    for package in packages:
        if package in stdlib_packages:
            _logger.warning('{0} is part of the Python standard library and will be skipped.  Remove it from the list to remove this warning.'.format(package))

def _log_before_after(before, after):
    new_packages = after - before

    if len(new_packages) == 0:
        _logger.warning('No new packages installed')
    elif len(new_packages) > 0:
        _logger.info('New packages installed: {0}'.format(', '.join(sorted(list(new_packages)))))

def pip(pkg_name, verbose=False):
    args = [
        'install',
    ]

    packages_before_install = _already_installed()

    if not _in_virtualenv():
        args.append('--user')

    if verbose:
        args.append('-vvv')

    packages = set(_pkg_name_list(pkg_name))

    # ignore items from the standard library
    stdlib_packages = _stdlib_packages()
    _log_stdlib_packages(stdlib_packages, packages)
    packages = _subtract_stdlib(stdlib_packages, packages)

    # ignore items that have already been installed
    _log_already_installed(packages_before_install, packages)
    packages = _subtract_installed(packages)

    overrides = _find_overrides(packages, _read_dependencies_link(_dependencies_link_location()))
    _run_overrides(overrides)

    _refresh_available_packages()

    # calculate and subtract what's installed again after overrides installed
    packages = _subtract_installed(packages)

    packages = list(packages)
    args.extend(_remove_internal_options(_remove_per_package_options(_config_options)))
    args.extend(_per_package_args(packages, _config_options))

    if len(packages) > 0:
        _logger.debug('Running pip to install {0}'.format(', '.join(sorted(packages))))
        pip_exec = _get_pip_exec(_config_options)
        returncode, err = pip_exec(args + packages)

        if returncode != 0 and err is not None:
            _logger.error(err)

        _invalidate_cache()
        _refresh_available_packages()

    packages_after_install = _already_installed()
    _log_before_after(packages_before_install, packages_after_install)
    _logger.debug('Done')

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
