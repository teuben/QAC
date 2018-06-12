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

VLA2_ALL = vla2_0     vla2_1     vla2_01 \
	   vla2_0g_45 vla2_1g_45 vla2_01g_45 \
	   vla2_0g_18 vla2_1g_18 vla2_01g_18

vla2_all:	$(VLA2_ALL)

vla2_all_clean:
	rm -rf 	$(VLA2_ALL)

# single pointing tests
vla2_0:
	time casa --nogui -c vla2.py pdir='"vla2_0"' cfg='[0]' grid=0 > vla2.log 2>&1
	cp vla2.log vla2.py vla2_0.ptg vla2_0
	tail -10 vla2.log

vla2_1:
	time casa --nogui -c vla2.py pdir='"vla2_1"' cfg='[1]' grid=0 > vla2.log 2>&1
	cp vla2.log vla2.py vla2_1.ptg vla2_1
	tail -10 vla2.log

vla2_01:
	time casa --nogui -c vla2.py pdir='"vla2_01"' cfg='[0,1]' grid=0 > vla2.log 2>&1
	cp vla2.log vla2.py vla2_01.ptg vla2_01
	tail -10 vla2.log

# same, for default filled grid, with TP=45m
vla2_0g_45:
	time casa --nogui -c vla2.py pdir='"vla2_0g_45"' cfg='[0]' dish=45 > vla2.log 2>&1
	cp vla2.log vla2.py vla2_0g_45.ptg vla2_0g_45
	tail -10 vla2.log

vla2_1g_45:
	time casa --nogui -c vla2.py pdir='"vla2_1g_45"' cfg='[1]' dish=45 > vla2.log 2>&1
	cp vla2.log vla2.py vla2_1g_45.ptg vla2_1g_45
	tail -10 vla2.log

vla2_01g_45:
	time casa --nogui -c vla2.py pdir='"vla2_01g_45"' cfg='[0,1]' dish=45 > vla2.log 2>&1
	cp vla2.log vla2.py vla2_01g_45.ptg vla2_01g_45
	tail -10 vla2.log

# same, for default filled grid, with TP=18m
vla2_0g_18:
	time casa --nogui -c vla2.py pdir='"vla2_0g_18"' cfg='[0]' dish=18 > vla2.log 2>&1
	cp vla2.log vla2.py vla2_0g_18.ptg vla2_0g_18
	tail -10 vla2.log

vla2_1g_18:
	time casa --nogui -c vla2.py pdir='"vla2_1g_18"' cfg='[1]' dish=18 > vla2.log 2>&1
	cp vla2.log vla2.py vla2_1g_18.ptg vla2_1g_18
	tail -10 vla2.log

vla2_01g_18:
	time casa --nogui -c vla2.py pdir='"vla2_01g_18"' cfg='[0,1]' dish=18 > vla2.log 2>&1
	cp vla2.log vla2.py vla2_01g_18.ptg vla2_01g_18
	tail -10 vla2.log

# simple noise test on cfg=0
noise:  vla2_noise0 vla2_noise1

vla2_noise0:
	time casa --nogui -c vla2.py 'cfg=[0]' noise=1000000 pdir="'vla2_noise0'" niter='[0,1000]' > vla2_noise0.log 2>&1

vla2_noise1:
	time casa --nogui -c vla2.py 'cfg=[1]' noise=1000000 pdir="'vla2_noise1'" niter='[0,1000]' > vla2_noise1.log 2>&1
