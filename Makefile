READOMLOGS=$(wildcard *.log )
DATA=$(READOMLOGS:.log=.dat)
PNGS=$(READOMLOGS:.log=.png)
PDFS=$(READOMLOGS:.log=.pdf)

all: $(PNGS) $(PDFS)

%.png %.pdf: %.dat barchart.gnuplot
	gnuplot -e fname=\"$*\" barchart.gnuplot

%.dat: %.log Makefile
	sed -n 's|^C2 in sector: \([0-9]*\) .*:.*total: *\([0-9]*\) *errors.*$$|\1 \2|p' < $< > $@

clean:
	-\rm -v *~
