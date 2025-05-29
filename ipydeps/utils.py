# vim: expandtab tabstop=4 shiftwidth=4

from pathlib import Path
from typing import Set

import pkgutil
import sys

def combine_key_and_cert(combined_path: Path, key_path: Path, cert_path: Path) -> None:
    with combined_path.open('wb') as outfile:
        outfile.write(key_path.read_bytes())
        outfile.write(cert_path.read_bytes())

def in_virtualenv():
    # https://stackoverflow.com/questions/1871549/determine-if-python-is-running-inside-virtualenv
    return sys.prefix != sys.base_prefix

def normalize_package_names(packages: Set) -> Set:
    # normalize underscores to dashes to line
    # up with pip freeze output
    packages = {p.replace('_', '-') for p in packages}
    packages = {p.lower() for p in packages}
    return packages

def get_stdlib_packages(version=sys.version_info.major, minor=sys.version_info.minor) -> Set:
    stdlib_list = ''

    if version == 3:
        if minor >= 10 and hasattr(sys, "stdlib_module_names"):
            stdlib_list = sys.stdlib_module_names  # pylint: disable=no-member
            return normalize_package_names(set(stdlib_list))
        stdlib_list = pkgutil.get_data(__name__, 'data/libs3.txt')
    elif version == 2:
        stdlib_list = pkgutil.get_data(__name__, 'data/libs2.txt')

    stdlib_list = str(stdlib_list, encoding='utf8')
    stdlib_list = (x.strip() for x in stdlib_list.split('\n'))
    stdlib_list = (x for x in stdlib_list if len(x) > 0)
    return set(stdlib_list)
