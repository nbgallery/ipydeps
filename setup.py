# vim: expandtab tabstop=4 shiftwidth=4

from setuptools import setup

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), 'r') as f:
    long_description = f.read()

setup(
    name='ipydeps',
    version='0.8.2',
    author='Bill Allen',
    author_email='photo.allen@gmail.com',
    description='A pip interface wrapper for installing packages from within Jupyter notebooks.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='MIT',
    keywords='pip install setup jupyter notebook dependencies'.split(),
    url='https://github.com/nbgallery/ipydeps',
    packages=['ipydeps'],
    package_data={'ipydeps': ['data/*.txt']},
    install_requires=['pip', 'setuptools', 'pypki2>=0.10.1'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License'
    ]
)
