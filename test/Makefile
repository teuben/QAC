#

TESTS = bench bench0

#  on Mac:
CASA  = /Applications/CASA.app/Contents/MacOS/casa
#  on Linux: (assuming it's in your $PATH)
CASA  = casa

help:
	@echo no help

.PHONY: $(TESTS)

bench:
	@echo running bench.py ...
	time casa --nogui -c bench.py > bench.log 2>&1
	tail -4 bench.log

benchplot:
	@echo running bench.py ...
	time casa --nogui -c bench.py alma=1 plot=1 > bench.log 2>&1
	tail -4 bench.log

bench0:
	@echo running bench0.py ...
	time casa --nogui -c bench0.py > bench0.log 2>&1
	tail -8 bench0.log
