DOCUMENT = ofj-template
FLAGS    = -pdf -halt-on-error

.PHONY:all continuously clean

all:
	latexmk ${FLAGS} ${DOCUMENT}.tex

continuously:
	latexmk ${FLAGS} -pvc ${DOCUMENT}.tex

clean:
	latexmk -C ${FLAGS} ${DOCUMENT}.tex
	rm -fv ${DOCUMENT}.bbl
