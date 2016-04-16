exec >&2
redo-ifchange rednose-local.xml
0launch http://0install.net/2008/interfaces/0test.xml \
	rednose-local.xml \
	http://repo.roscidus.com/python/python \
	2.6,2.8 3.0,4
