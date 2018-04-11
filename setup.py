# vim: expandtab tabstop=4 shiftwidth=4

from setuptools import setup

setup(
    name='ipydeps',
    version='0.6.0',
    author='Bill Allen',
    author_email='photo.allen@gmail.com',
    description='A pip interface wrapper for installing packages from within Jupyter notebooks.',
    license='MIT',
    keywords='pip install setup jupyter notebook dependencies'.split(),
    url='https://github.com/nbgallery/ipydeps',
    packages=['ipydeps'],
    install_requires=['pip', 'setuptools', 'pypki2>=0.10.0'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License'
    ]
)
