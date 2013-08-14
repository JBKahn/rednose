redo=0install run --command=redo-ifchange http://gfxmonk.net/dist/0install/redo.xml

default: test

%: phony
	${redo} $@

.PHONY: phony default
