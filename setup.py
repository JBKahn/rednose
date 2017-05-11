from os import path
from setuptools import setup, find_packages


def read(fname):
    try:
        return open(path.join(path.dirname(__file__), fname)).read()
    except IOError:
        return """A module for making nose pretty using colors."""

setup(
    packages=find_packages(exclude=['test', 'test.*']),
    description='coloured output for nosetests',
    entry_points={'nose.plugins.0.10': ['NOSETESTS_PLUGINS = rednose:RedNose']},
    install_requires=['setuptools', 'termstyle >=0.1.7', 'colorama'],
    tests_require=['six==1.10.0'],
    long_description=read('README.rst'),
    name='rednose',
    py_modules=['rednose'],
    url='https://github.com/JBKahn/rednose',
    version='1.2.3',
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Testing",
    ],
    keywords='test nosetests nose nosetest output colour console',
    license='BSD',
    test_suite='test_files.new_tests',
)
