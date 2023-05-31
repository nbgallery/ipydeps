# vim: expandtab tabstop=4 shiftwidth=4

from collections import namedtuple
from pathlib import Path
from typing import Optional

from .logger import logger

Config = namedtuple(
    'Config',
    [
        'dependencies_link',
        'dependencies_link_requires_pki',
    ],
)

def config_dir(environ):
    user_config_dir = Path.home() / '.config/ipydeps'

    if 'IPYDEPS_CONFIG_DIR' in environ:
        config_dirs = [Path('IPYDEPS_CONFIG_DIR')]
    else:
        config_dirs = []

    config_dirs += [
        user_config_dir,
        Path('/etc/ipydeps'),
    ]

    for path in config_dirs:
        if path.exists():
            logger.debug('Using ipydeps config dir %s', path)
            return path

    logger.debug('Using ipydeps config dir %s', user_config_dir)
    return user_config_dir

def load_config(path: Path) -> Config:
    config_parser = ConfigParser()
    config_parser.read(path)
    config = Config(
        dependencies_link=config_parser.get('ipydeps', {}).get('dependencies_link'),
        dependencies_link_requires_pki=config_parser.get('ipydeps', {}).getboolean('dependencies_link_requires_pki'),
    )
    return config
