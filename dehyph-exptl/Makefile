# This Makefile prepares documentation for package dehyph-exptl.

BIBTEX = bibtex
PDFLATEX = pdflatex
RM = rm -f


.PHONY: all doc clean note

note:
	@echo "*** Makefile for dehyph-exptl package documentation ***"
	@echo "Please type:"
	@echo "make doc    to build documentation."
	@echo "make clean  to clean this directory."

all: doc

doc: dehyph-exptl.pdf

clean:
	$(RM) *.aux *.bbl *.blg *.log *.out *.toc

dehyph-exptl.pdf: dehyph-exptl.tex dehyph-exptl.bib
	$(PDFLATEX) dehyph-exptl
	$(BIBTEX) dehyph-exptl
	$(PDFLATEX) dehyph-exptl
	$(PDFLATEX) dehyph-exptl

# EOF
