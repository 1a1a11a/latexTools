PAPERNAME=main

all : $(PAPERNAME).pdf

# .PHONY: figures
# figures:
# 	$(MAKE) -C figures -j

fast : figures
	pdflatex $(PAPERNAME) </dev/null | tail -n 32
	killall -s 1 -r mupdf ; true

$(PAPERNAME).pdf : 
	pdflatex $(PAPERNAME) </dev/null | tail -n 32
	killall -s 1 -r mupdf ; true
	bibtex -min-crossrefs=30000 $(PAPERNAME) </dev/null >/dev/null
	pdflatex $(PAPERNAME) </dev/null >/dev/null
	pdflatex $(PAPERNAME) </dev/null >/dev/null
	pdflatex $(PAPERNAME) </dev/null >/dev/null
	killall -s 1 -r mupdf ; true

clean :
	rm $(PAPERNAME).bbl $(PAPERNAME).blg $(PAPERNAME).log $(PAPERNAME).out $(PAPERNAME).pdf
