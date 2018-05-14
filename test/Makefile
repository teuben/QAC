#

TESTS = bench bench0 bench1 \
        sky0a sky0b sky1 \
	cas_11271a cas_11271b \
        test1 test2 test3 test4 test5

#  on Mac: (usually can't assume it's in the $PATH)
CASA  = /Applications/CASA.app/Contents/MacOS/casa
#  on Linux: (here we assume it's in your $PATH)
CASA  = casa

help:
	@echo tests = $(TESTS)

.PHONY: $(TESTS)

bench:
	@echo running bench.py ...
	time $(CASA) --nogui -c bench.py > bench.log 2>&1
	tail -4 bench.log

benchplot:
	@echo running bench.py ...
	time $(CASA) --nogui -c bench.py alma=1 plot=1 > bench.log 2>&1
	tail -4 bench.log

bench0:
	@echo running bench0.py ...
	time $(CASA) --nogui -c bench0.py > bench0.log 2>&1
	tail -8 bench0.log

bench1:
	@echo running bench1.py ...
	time $(CASA) --nogui -c bench1.py > bench1.log 2>&1
	tail -8 bench1.log

sky1:
	@echo running sky1.py ...
	time $(CASA) --nogui -c sky1.py > sky1.log 2>&1
	cp sky1.py sky1.log sky1
	tail -20 sky1.log

# expose the mosaicing flux bug in CASA 5.1 (April 2018) - gridder='standard'  is not affected
sky0:   sky0a sky0b
	@echo vi1 results:
	grep QAC_STATS sky0a.log
	@echo vi2 results:
	grep QAC_STATS sky0b.log

sky0a:
	VI1=1 $(CASA) --nogui -c sky0.py test='"sky0a"' > sky0a.log 2>&1

sky0b:
	$(CASA)       --nogui -c sky0.py test='"sky0b"' > sky0b.log 2>&1

cas_11271: cas_11271a cas_11271b
	@grep ^CASA cas_11271a.log
	@echo vi1 results:
	grep QAC_STATS cas_11271a.log
	@echo vi2 results:
	grep QAC_STATS cas_11271b.log


cas_11271a:
	VI1=1 $(CASA) --nogui -c cas_11271.py test='"cas_11271a"' > cas_11271a.log 2>&1

cas_11271b:
	$(CASA)       --nogui -c cas_11271.py test='"cas_11271b"' > cas_11271b.log 2>&1

test1:
	@echo running test1.py ...
	rm -fr test1
	time $(CASA) --nogui -c test1.py > test1.log 2>&1
	tail -8 test1.log

test2:
	@echo running test2.py ...
	rm -fr test2
	time $(CASA) --nogui -c test2.py > test2.log 2>&1
	tail -8 test2.log

test3:
	@echo running test3.py ...
	rm -fr test3
	time $(CASA) --nogui -c test3.py > test3.log 2>&1
	tail -8 test3.log

test4:
	export VI1=1
	@echo running test4.py ...
	rm -fr test4
	time $(CASA) --nogui -c test4.py > test4.log 2>&1
	tail -8 test4.log

test5:
	@echo running test5.py ...
	rm -fr test5
	time $(CASA) --nogui -c test5.py > test5.log 2>&1
	tail -8 test5.log
