#!/usr/bin/env python

from setuptools import *
setup(
	name='rednose',
	version='0.1',
	author_email='tim3d.junk+termstyle@gmail.com',
	author='Tim Cuthbertson',
	url='http://github.com/gfxmonk/rednose/tree',
	description="coloured output for nosetests",
	packages = find_packages(),
	entry_points = {
		'nose.plugins.0.10': ['rednose = rednose:RedNose']
	},
	classifiers=[
		"License :: OSI Approved :: BSD License",
		"Programming Language :: Python",
		"Development Status :: 4 - Beta",
		"Intended Audience :: Developers",
		"Topic :: Software Development :: Libraries :: Python Modules",
		"Topic :: Software Development :: Testing",
	],
	keywords='console ansi color colour terminal xterm',
	license='BSD',
	install_requires=[
		'setuptools',
	],
)
