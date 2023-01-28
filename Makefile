# Set the name of your project (looks for DOCUMENT.tex)
DOCUMENT = ofj-template

# Choose your article type (comment / uncomment respectively)
TYPE     = SetTypeInMakefile
# TYPE     = FullPaper
# TYPE     = TNote
# TYPE     = RevPaper

JOBNAME  = ${DOCUMENT}_${TYPE}

FLAGS    = -pdf -halt-on-error

.PHONY:all continuously review clean

all:
	latexmk ${FLAGS} ${DOCUMENT}.tex -jobname=${JOBNAME}

continuously:
	latexmk ${FLAGS} -pvc ${DOCUMENT}.tex -jobname=${JOBNAME}

review:
	latexmk ${FLAGS} ${DOCUMENT}-review.tex -jobname=${JOBNAME}-review

clean:
	latexmk -C ${FLAGS} ${DOCUMENT}.tex -jobname=${JOBNAME}
	latexmk -C ${FLAGS} ${DOCUMENT}-review.tex -jobname=${JOBNAME}-review
	rm -fv ${JOBNAME}.bbl ${JOBNAME}-review.bbl
