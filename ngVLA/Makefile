#
#

TESTS = test1 test1a test2 test1-alma test1-SSA test5 vla1 vla2

help:	
	@echo no help

.PHONY:   $(TESTS)

all:	$(TESTS)

test1:
	time casa --nogui -c test1.py > test1.log 2>&1

test1a:
	time casa --nogui -c test1a.py > test1a.log 2>&1

test1-alma:
	rm -rf test1-alma
	time casa --nogui -c test1-alma.py > test1-alma.log 2>&1

test1-SSA:
	rm -rf test1-SSA
	time casa --nogui -c test1-SSA.py > test1-SSA.log 2>&1

test2:
	rm -rf test2
	time casa --nogui -c test2.py > test2.log 2>&1

test5:
	rm -rf test5
	time casa --nogui -c test5.py > test5.log 2>&1

vla1:
	rm -rf vla1
	time casa --nogui -c vla1.py > vla1.log 2>&1

vla2:
	rm -rf vla2
	time casa --nogui -c vla2.py > vla2.log 2>&1
	cp vla2.log vla2.py vla2.ptg vla2
	tail -10 vla2.log

VLA2_ALL = vla2_0 vla2_1

vla2_all:	$(VLA2_ALL)

vla2_0:
	time casa --nogui -c vla2.py pdir='"vla2_0"' cfg='[0]' > vla2_0.log 2>&1
	cp vla2_0.log vla2.py vla2_0.ptg vla2_0
	tail -10 vla2_0.log

vla2_1:
	time casa --nogui -c vla2.py pdir='"vla2_1"' cfg='[1]' > vla2_1.log 2>&1
	cp vla2_1.log vla2.py vla2_1.ptg vla2_1
	tail -10 vla2_1.log
