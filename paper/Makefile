.PHONY: all clean

MAIN = main

LATEX = ~/Library/TinyTeX/bin/universal-darwin/pdflatex
BIBTEX = ~/Library/TinyTeX/bin/universal-darwin/bibtex

all: $(MAIN).pdf

$(MAIN).pdf: $(MAIN).tex sections/*.tex references.bib
	$(LATEX) -interaction=nonstopmode $(MAIN).tex
	$(BIBTEX) $(MAIN)
	$(LATEX) -interaction=nonstopmode $(MAIN).tex
	$(LATEX) -interaction=nonstopmode $(MAIN).tex

clean:
	rm -f *.aux *.bbl *.blg *.log *.out *.toc *.pdf sections/*.aux
