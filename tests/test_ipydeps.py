# vim: expandtab tabstop=4 shiftwidth=4

import json

import pytest

from ipydeps.config import Config
from ipydeps.ipydeps import find_overrides
from ipydeps.ipydeps import get_freeze_package_name
from ipydeps.ipydeps import get_pkg_names
from ipydeps.ipydeps import process_pip_freeze_output
from ipydeps.ipydeps import py_name_major
from ipydeps.ipydeps import py_name_minor
from ipydeps.ipydeps import py_name_micro
from ipydeps.ipydeps import subtract_installed
from ipydeps.utils import normalize_package_names

def test_get_pkg_names():
    assert len(get_pkg_names('abc DEF hIj')) == 3

def test_pkg_name_list():
    assert len(get_pkg_names('abc DEF hIj')) == 3
    assert len(get_pkg_names(['abc', 'DEF', 'hIj'])) == 3

def test_bad_pkg_name():
    assert len(get_pkg_names(['exec', 'exec()'])) == 1

def test_subtract_installed():
    packages = subtract_installed(set(['pip']), set(['pip', 'foofizz']))
    assert 'foofizz' in packages
    assert 'pip' not in packages

def test_version_specifier():
    packages = get_pkg_names('foo>=0.10.1')
    assert len(packages) == 1
    assert 'foo>=0.10.1' in packages

def test_version_specifier_no_micro():
    packages = get_pkg_names('foo>=0.10')
    assert len(packages) == 1
    assert 'foo>=0.10' in packages

def test_version_specifier_sub_micro():
    packages = get_pkg_names('foo>=0.10.11.12')
    assert len(packages) == 1
    assert 'foo>=0.10.11.12' in packages

def test_version_specifier_super_sub_micro():
    packages = get_pkg_names('foo>=0.10.11.12.13.14.15.16.17.18.19.42')
    assert len(packages) == 1
    assert 'foo>=0.10.11.12.13.14.15.16.17.18.19.42' in packages

def test_version_specifier_list():
    packages = get_pkg_names(['foo==10.1', 'bar', 'baz<5.5.5'])
    assert len(packages) == 3
    assert 'foo==10.1' in packages
    assert 'bar' in packages
    assert 'baz<5.5.5' in packages

def test_freeze_name_parsing():
    name = get_freeze_package_name('six==1.10.0')
    assert name == 'six'

def test_freeze_editable_name_filtering():
    pkgs = b'''arrow==0.12.1
-e git+git@gitserver.com:kafonek/package_name@githash#egg-package
asn1crypto==0.23.0'''
    pkgs = process_pip_freeze_output(pkgs)
    assert len(pkgs) == 2
    assert 'arrow' in pkgs
    assert 'asn1crypto' in pkgs

def test_normalize_package_names():
    packages = get_pkg_names(['foo==10.1', 'bar', 'baz<5.5.5', 'foo-bar', 'foo_baz'])
    packages = normalize_package_names(packages)
    assert len(packages) == 5
    assert 'foo-bar' in packages
    assert 'foo-baz' in packages

def test_empty_overrides():
    names = set()
    overrides = find_overrides(names, '')
    assert len(overrides) == 0

def test_no_overrides():
    names = set(['foo', 'bar', 'baz'])
    overrides = find_overrides(names, '')

    for name in names:
        assert name not in overrides

def test_all_overrides(tmp_path):
    path = tmp_path / 'overrides.json'

    with path.open('w') as f:
        j = {
                py_name_major(): {
                    'foo': [
                        [ 'package', 'foo' ]
                    ],
                    'bar': [
                        [ 'package', 'foo' ],
                        [ 'package', 'bar' ]
                    ],
                    'baz': [
                        [ 'package', 'foo', 'baz' ]
                    ]
                },
                py_name_minor(): {
                    'foo': [
                        [ 'package', 'foo' ],
                        [ 'package', 'bar' ]
                    ],
                    'Foo': [  # should cause a warning because duplicate entry
                        [ 'package', 'foo' ],
                        [ 'package', 'bar' ]
                    ],
                },
                py_name_micro(): {
                    'bar': [
                        [ 'package', 'bar' ]
                    ]
                }
        }

        f.write(json.dumps(j))
        f.flush()

    config = Config(
        dependencies_link='file://'+path.as_posix(),
        dependencies_link_requires_pki=False,
    )

    names = set(['foo', 'bar', 'baz'])
    overrides = find_overrides(names, config)

    for name in names:
        assert name in overrides

    assert len(overrides['foo']) == 2
    assert len(overrides['bar']) == 1
