0:
	mkzero-gfxmonk -p setup.py -p rednose.py rednose.xml

pypi:
	./setup.py register sdist upload

clean:
	rm -rf *.egg-info

rednose-local.xml: rednose.xml
	0launch http://gfxmonk.net/dist/0install/0local.xml rednose.xml rednose-local.xml

test: rednose-local.xml
	0launch http://0install.net/2008/interfaces/0test.xml \
		rednose-local.xml \
		http://repo.roscidus.com/python/python \
		2.6,2.7 2.7,2.8 3.0,4
	
.PHONY: 0 pypi
