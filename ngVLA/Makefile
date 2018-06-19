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

# ---------------------------------------------------------------------------------------------
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

#
vla2_0g_18_noise:
	time casa --nogui -c vla2.py pdir='"vla2_0g_18_noise"' cfg='[0]' dish=18 noise=150 > vla2.log 2>&1
	cp vla2.log vla2.py vla2_0g_18_noise.ptg vla2_0g_18_noise
	tail -10 vla2.log

#
vla2_noise:
	time casa --nogui -c vla2.py 'cfg=[0]' noise=0  pdir="'vla2_noise_0'" niter='[0,1000]' > vla2_noise_0.log 2>&1
	time casa --nogui -c vla2.py 'cfg=[0]' noise=25 pdir="'vla2_noise_a'" niter='[0,1000]' > vla2_noise_a.log 2>&1
	time casa --nogui -c vla2.py 'cfg=[0]' noise=50 pdir="'vla2_noise_b'" niter='[0,1000]' > vla2_noise_b.log 2>&1
	time casa --nogui -c vla2.py 'cfg=[0]' noise=75 pdir="'vla2_noise_c'" niter='[0,1000]' > vla2_noise_c.log 2>&1
	time casa --nogui -c vla2.py 'cfg=[0]' noise=100 pdir="'vla2_noise_d'" niter='[0,1000]' > vla2_noise_d.log 2>&1
	time casa --nogui -c vla2.py 'cfg=[0]' noise=125 pdir="'vla2_noise_e'" niter='[0,1000]' > vla2_noise_e.log 2>&1
	time casa --nogui -c vla2.py 'cfg=[0]' noise=150 pdir="'vla2_noise_f'" niter='[0,1000]' > vla2_noise_f.log 2>&1
	time casa --nogui -c vla2.py 'cfg=[0]' noise=175 pdir="'vla2_noise_g'" niter='[0,1000]' > vla2_noise_g.log 2>&1
	time casa --nogui -c vla2.py 'cfg=[0]' noise=200 pdir="'vla2_noise_h'" niter='[0,1000]' > vla2_noise_h.log 2>&1
	time casa --nogui -c vla2.py 'cfg=[0]' noise=225 pdir="'vla2_noise_i'" niter='[0,1000]' > vla2_noise_i.log 2>&1
	time casa --nogui -c vla2.py 'cfg=[0]' noise=250 pdir="'vla2_noise_j'" niter='[0,1000]' > vla2_noise_j.log 2>&1
	time casa --nogui -c vla2.py 'cfg=[0]' noise=500 pdir="'vla2_noise_k'" niter='[0,1000]' > vla2_noise_k.log 2>&1
	time casa --nogui -c vla2.py 'cfg=[0]' noise=1000 pdir="'vla2_noise_l'" niter='[0,1000]' > vla2_noise_l.log 2>&1
	time casa --nogui -c vla2.py 'cfg=[0]' noise=10000 pdir="'vla2_noise_m'" niter='[0,1000]' > vla2_noise_m.log 2>&1
	time casa --nogui -c vla2.py 'cfg=[0]' noise=100000 pdir="'vla2_noise_n'" niter='[0,1000]' > vla2_noise_n.log 2>&1

# test on wider array, but only map inner portion

PLAINS = plains_0 plains_2 plains_02

plains_all: $(PLAINS)

plains_all_clean:
	rm -rf $(PLAINS)

plains_0:
	time casa --nogui -c vla2.py 'cfg=[0]' pdir="'plains_0'" niter='[0,1000]' dish=45 \
	     pixel_m=0.01 imsize_s=2048 pixel_s=0.02 \
	     > plains_0.log 2>&1

plains_2:
	time casa --nogui -c vla2.py 'cfg=[2]' pdir="'plains_2'" niter='[0,1000]' dish=45 \
	     pixel_m=0.01 imsize_s=2048 pixel_s=0.02 \
	     > plains_2.log 2>&1

plains_02:
	time casa --nogui -c vla2.py 'cfg=[0,2]' pdir="'plains_02'" niter='[0,1000]' dish=45 \
	     pixel_m=0.01 imsize_s=2048 pixel_s=0.02 \
	     > plains_02.log 2>&1
