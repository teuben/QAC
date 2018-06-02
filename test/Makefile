#

TESTS = bench bench0 bench1 \
        sky0a sky0b sky1 sky2 \
	cas_11271a cas_11271b \
        test1 test2 test3 test4 test5

#  example on Mac:
CASA  = /Applications/CASA.app/Contents/MacOS/casa
#  example on Linux if you used the install_casa script
CASA  = ../casa/casa-release-5.1.2-4.el7/bin/casa
#  example on Linux: (assuming it's in your $PATH - the portable solution)
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

#  sky2 is the generic TP2VIS-only mapping testsuite
sky2:
	@echo running sky2.py ...
	time $(CASA) --nogui -c sky2.py > sky2.log 2>&1
	cp sky2.py sky2.log sky2.ptg sky2
	tail -20 sky2.log

#  all the sky2 based simulations
SKY2_ALL = sky2_1 sky2_2 sky2_3 sky2_4 sky2_5 \
	   sky2_1a sky2_1b sky2_1c sky2_1d sky2_1e sky2_1f \
	   sky2_2a sky2_2b sky2_2c sky2_2d sky2_2e sky2_2f

sky2_all: $(SKY2_ALL)

sky2_all_clean:
	rm -rf $(SKY2_ALL)

# flux as function of pixel size
sky2_1:
	@echo running sky2.py ...
	time $(CASA) --nogui -c sky2.py pdir='"sky2_1"' pixel_m=0.05 pixel_s=0.8  > sky2_1.log 2>&1
	cp sky2.py sky2_1.log sky2_1.ptg sky2_1
	tail -20 sky2_1.log

sky2_2:
	@echo running sky2.py ...
	time $(CASA) --nogui -c sky2.py pdir='"sky2_2"' pixel_m=0.1 pixel_s=1.6  > sky2_2.log 2>&1
	cp sky2.py sky2_2.log sky2_2.ptg sky2_2
	tail -20 sky2_2.log

sky2_3:
	@echo running sky2.py ...
	time $(CASA) --nogui -c sky2.py pdir='"sky2_3"' pixel_m=0.2 pixel_s=3.2  > sky2_3.log 2>&1
	cp sky2.py sky2_3.log sky2_3.ptg sky2_3
	tail -20 sky2_3.log

sky2_4:
	@echo running sky2.py ...
	time $(CASA) --nogui -c sky2.py pdir='"sky2_4"' pixel_m=0.4 imsize_s=512 pixel_s=3.2  > sky2_4.log 2>&1
	cp sky2.py sky2_4.log sky2_4.ptg sky2_4
	tail -20 sky2_4.log

sky2_5:
	@echo running sky2.py ...
	time $(CASA) --nogui -c sky2.py pdir='"sky2_5"' pixel_m=0.4 pixel_s=6.4  > sky2_5.log 2>&1
	cp sky2.py sky2_5.log sky2_5.ptg sky2_5
	tail -20 sky2_5.log
#

sky2_20:
	@echo running sky2.py ...
	time $(CASA) --nogui -c sky2.py pdir='"sky2_20"' pixel_m=0.1 imsize_s=512 > sky2_20.log 2>&1
	cp sky2.py sky2_20.log sky2_20.ptg sky2_20
	tail -20 sky2_20.log

sky2_30:
	@echo running sky2.py ...
	time $(CASA) --nogui -c sky2.py pdir='"sky2_30"' pixel_m=0.2 imsize_s=1024  > sky2_30.log 2>&1
	cp sky2.py sky2_30.log sky2_30.ptg sky2_30
	tail -20 sky2_30.log

sky2_40:
	@echo running sky2.py ...
	time $(CASA) --nogui -c sky2.py pdir='"sky2_40"' pixel_m=0.4 imsize_s=2048  > sky2_40.log 2>&1
	cp sky2.py sky2_40.log sky2_40.ptg sky2_40
	tail -20 sky2_40.log

# flux as function of small gridding step
sky2_2a:
	@echo running sky2.py ...
	time $(CASA) --nogui -c sky2.py pdir='"sky2_2a"' pixel_m=0.1 pixel_s=1.6 grid=25 > sky2_2a.log 2>&1
	cp sky2.py sky2_2a.log sky2_2a.ptg sky2_2a
	tail -20 sky2_2a.log

sky2_2b:
	@echo running sky2.py ...
	time $(CASA) --nogui -c sky2.py pdir='"sky2_2b"' pixel_m=0.1 pixel_s=1.6 grid=20 > sky2_2b.log 2>&1
	cp sky2.py sky2_2b.log sky2_2b.ptg sky2_2b
	tail -20 sky2_2b.log

sky2_2c:
	@echo running sky2.py ...
	time $(CASA) --nogui -c sky2.py pdir='"sky2_2c"' pixel_m=0.1 pixel_s=1.6 grid=15 > sky2_2c.log 2>&1
	cp sky2.py sky2_2c.log sky2_2c.ptg sky2_2c
	tail -20 sky2_2c.log

# bigger gridding steps to see the beam problem
sky2_2d:
	@echo running sky2.py ...
	time $(CASA) --nogui -c sky2.py pdir='"sky2_2d"' pixel_m=0.1 pixel_s=1.6 grid=60 > sky2_2d.log 2>&1
	cp sky2.py sky2_2d.log sky2_2d.ptg sky2_2d
	tail -20 sky2_2d.log

sky2_2e:
	@echo running sky2.py ...
	time $(CASA) --nogui -c sky2.py pdir='"sky2_2e"' pixel_m=0.1 pixel_s=1.6 grid=120 > sky2_2e.log 2>&1
	cp sky2.py sky2_2e.log sky2_2e.ptg sky2_2e
	tail -20 sky2_2e.log

sky2_2f:
	@echo running sky2.py ...
	time $(CASA) --nogui -c sky2.py pdir='"sky2_2f"' pixel_m=0.1 pixel_s=1.6 grid=180 > sky2_2f.log 2>&1
	cp sky2.py sky2_2f.log sky2_2f.ptg sky2_2f
	tail -20 sky2_2f.log


# dscale range
sky2_1a:
	@echo running sky2.py ...
	time $(CASA) --nogui -c sky2.py pdir='"sky2_1a"' pixel_m=0.05 pixel_s=0.8 dscale=2 > sky2_1a.log 2>&1
	cp sky2.py sky2_1a.log sky2_1a.ptg sky2_1a
	tail -20 sky2_1a.log

sky2_1b:
	@echo running sky2.py ...
	time $(CASA) --nogui -c sky2.py pdir='"sky2_1b"' pixel_m=0.05 pixel_s=0.8 dscale=4 > sky2_1b.log 2>&1
	cp sky2.py sky2_1b.log sky2_1b.ptg sky2_1b
	tail -20 sky2_1b.log

sky2_1c:
	@echo running sky2.py ...
	time $(CASA) --nogui -c sky2.py pdir='"sky2_1c"' pixel_m=0.05 pixel_s=0.8 dscale=8 > sky2_1c.log 2>&1
	cp sky2.py sky2_1c.log sky2_1c.ptg sky2_1c
	tail -20 sky2_1c.log

# bigger gridding step and the dish3 usage
sky2_1d:
	@echo running sky2.py ...
	time $(CASA) --nogui -c sky2.py pdir='"sky2_1d"' pixel_m=0.05 pixel_s=0.8 dish=12 maxuv=12 dish3=12 > sky2_1d.log 2>&1
	cp sky2.py sky2_1d.log sky2_1d.ptg sky2_1d
	tail -20 sky2_1d.log

sky2_1e:
	@echo running sky2.py ...
	time $(CASA) --nogui -c sky2.py pdir='"sky2_1e"' pixel_m=0.05 pixel_s=0.8 dish=24 maxuv=24 dish3=12 > sky2_1e.log 2>&1
	cp sky2.py sky2_1e.log sky2_1e.ptg sky2_1e
	tail -20 sky2_1e.log

sky2_1f:
	@echo running sky2.py ...
	time $(CASA) --nogui -c sky2.py pdir='"sky2_1f"' pixel_m=0.05 pixel_s=0.8 dish=48 maxuv=48 dish3=12 > sky2_1f.log 2>&1
	cp sky2.py sky2_1f.log sky2_1f.ptg sky2_1f
	tail -20 sky2_1f.log

# proper dish3 with the same resolution?


# older version of cas_11271
sky0:   sky0a sky0b
	@echo vi1 results:
	grep QAC_STATS sky0a.log
	@echo vi2 results:
	grep QAC_STATS sky0b.log

sky0a:
	VI1=1 $(CASA) --nogui -c sky0.py test='"sky0a"' > sky0a.log 2>&1

sky0b:
	$(CASA)       --nogui -c sky0.py test='"sky0b"' > sky0b.log 2>&1

# expose the mosaicing flux bug in CASA 5.1 (April 2018) - gridder='standard'  is not affected
cas_11271: cas_11271a cas_11271b
	@grep ^CASA cas_11271a.log
	@echo vi1 results:
	grep QAC_STATS cas_11271a.log
	@echo vi2 results:
	grep QAC_STATS cas_11271b.log


cas_11271a:
	VI1=1 $(CASA) --nogui -c cas_11271.py pdir='"cas_11271a"' > cas_11271a.log 2>&1
	cp cas_11271.py cas_11271a

cas_11271b:
	$(CASA)       --nogui -c cas_11271.py pdir='"cas_11271b"' > cas_11271b.log 2>&1
	cp cas_11271.py cas_11271b

#
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
