0:
	mkzero-gfxmonk -p setup.py -p rednose.py rednose.xml

pypi:
	./setup.py register sdist upload

rednose-local.xml: rednose.xml
	0launch http://gfxmonk.net/dist/0install/0local.xml rednose.xml rednose-local.xml

test: rednose-local.xml
	0launch http://0install.net/2008/interfaces/0test.xml \
		rednose-local.xml \
		http://repo.roscidus.com/python/python \
		2.7.3-6 3.2.3-5
	
.PHONY: 0 pypi
