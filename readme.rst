=========
rednose
=========

rednose is a `nosetests <http://somethingaboutorange.com/mrl/projects/nose/>`
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

	export NOSE_REDNOSE=1 # you can put this in your .profile, .bashrc or similar
	nosetests

Nose by default uses auto-colouring, which will only use colour if you're running it on a terminal
(i.e not piping it to a file). To control colouring, use one of::

	nosetests --rednose-color=off
	nosetests --rednose-color=on
	nosetests --rednose-color=auto

(you can also set this in the environment variable NOSE_REDNOSE_COLOR)

