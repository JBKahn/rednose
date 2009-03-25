#!/usr/bin/env python

from setuptools import *
setup(
	name='rednose plugin for nosetests',
	packages = find_packages(),
	entry_points = {
		'nose.plugins.0.10': ['rednose = rednose:RedNose']
	},
)
