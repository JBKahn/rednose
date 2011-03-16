0:
	mkzero-gfxmonk -p setup.py -p rednose.py rednose.xml

pypi:
	./setup.py register sdist upload
	
.PHONY: 0 pypi
