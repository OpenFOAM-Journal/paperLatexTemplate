DOCUMENT = ofj-template
FLAGS    = -pdf -halt-on-error

.PHONY:all continuously clean

all:
	latexmk ${FLAGS} ${DOCUMENT}.tex

continuously:
	latexmk ${FLAGS} -pvc ${DOCUMENT}.tex

review:
	latexmk ${FLAGS} ${DOCUMENT}-review.tex

clean:
	latexmk -C ${FLAGS} ${DOCUMENT}.tex
	latexmk -C ${FLAGS} ${DOCUMENT}-review.tex
	rm -fv ${DOCUMENT}.bbl ${DOCUMENT}-review.bbl
