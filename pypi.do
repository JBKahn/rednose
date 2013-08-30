exec >&2
redo-ifchange setup.py
./setup.py register sdist upload
