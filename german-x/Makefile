# This Makefile prepares documentation for package german-x.

PDFLATEX = pdflatex
RM = rm -f


.PHONY: all doc clean note

note:
	@echo "*** Makefile for german-x package documentation ***"
	@echo "Please type:"
	@echo "make doc    to build documentation."
	@echo "make clean  to clean this directory."

all: doc

doc: german-x.pdf

clean:
	$(RM) *.aux *.log *.out *.toc

german-x.pdf: german-x.tex
	$(PDFLATEX) $<
	$(PDFLATEX) $<

# EOF
