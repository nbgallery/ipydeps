# vim: expandtab tabstop=4 shiftwidth=4

import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='ipydeps',
    version='0.2.0',
    author='Bill Allen',
    author_email='photo.allen@gmail.com',
    description='A pip interface wrapper for installing packages from within Jupyter notebooks.',
    license='MIT',
    keywords='pip install setup jupyter notebook dependencies',
    url='https://github.com/jupyter-gallery/ipydeps',
    packages=['ipydeps'],
    install_requires=['pypki2', 'pip'],
    dependency_links=['http://github.com/jupyter-gallery/pypki2/tarball/master#egg=package-1.0'],
    long_description=read('README.md'),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License'
    ]
)
