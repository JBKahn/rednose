exec >&2
set -eu
0install run http://gfxmonk.net/dist/0install/0local.xml rednose.xml.template
mv "$1" "$3"
