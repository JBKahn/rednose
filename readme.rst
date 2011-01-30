=========
rednose
=========

rednose is a `nosetests`_
plugin for adding colour (and readability) to nosetest console results.

Installation:
-------------
::

	easy_install rednose
	
or from the source::

	./setup.py develop

Usage:
------
::

	nosetests --rednose

or::

	export NOSE_REDNOSE=1
	nosetests

Rednose by default uses auto-colouring, which will only use
colour if you're running it on a terminal (i.e not piping it
to a file). To control colouring, use one of::

	nosetests --rednose --force-color
	nosetests --no-color

(you can also set this in the environment variable NOSE_REDNOSE_COLOR)

.. _nosetests: http://somethingaboutorange.com/mrl/projects/nose/
