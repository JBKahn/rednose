#!/usr/bin/env python

try:
	desc = file.read(open('readme.rst'))
except StandardError:
	desc = 'see readme.rst'

from setuptools import *
setup(
	name='rednose',
	version='0.1.5',
	author_email='tim3d.junk+rednose@gmail.com',
	author='Tim Cuthbertson',
	url='http://github.com/gfxmonk/rednose/tree',
	description="coloured output for nosetests",
	long_description=desc,
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
	keywords='test nosetests nose nosetest output colour console',
	license='BSD',
	install_requires=[
		'setuptools',
	],
)
