#    Various tests for tp2vis and other QAC methods

TESTS = bench bench0 bench1 \
        sky0a sky0b sky1 sky2 \
	cas_11271a cas_11271b \
        test1 test2 test3 test4 test5

#TESTS = bench bench0 bench1 sky1 test1 test2 test3 test4 test5

SLIDES = slide1 slide2 slide3 slide4 slide6 slide7 slide8 slide9 slide10
SLIDES = slide6 slide7 slide8 slide9 slide10

TESTS = bench bench0 bench1 \
        sky0a sky0b \
	sky1 sky1a sky1b sky1c sky1d \
	sky2 \
        test1 test2 test3 test4 test5 \
	sky2_1f \
	$(SLIDES)

.PHONY: $(TESTS)


#  example on Mac:
CASA  = time /Applications/CASA.app/Contents/MacOS/casa --nogui -c 
#  example on Linux: (assuming it's in your $PATH - the portable solution)
CASA  = time casa --nogui -c


help:
	@echo tests = $(TESTS)

all:	$(TESTS)

#  benchmark data are in the QAC/data directory
DATA1   = M100_TP_CO_cube.bl.image
DATA2   = M100_aver_7.ms
DATA3   = M100_aver_12.ms
DATA4   = skymodel.fits

data:	data1 data2 data3 data4

data1:	$(DATA1)

data2:  $(DATA2)

data3:  $(DATA3)

data4:  $(DATA4)

$(DATA1):
	ln -s ../data/$@
$(DATA2):
	ln -s ../data/$@
$(DATA3):
	ln -s ../data/$@
$(DATA4):P
	ln -s ../data/$@

# a few benchmarks

bench:
	$(CASA) bench.py > bench.log 2>&1
	cp bench.log bench
	tail -4 bench.log

benchplot:
	$(CASA) bench.py alma=1 plot=1 > bench.log 2>&1
	cp bench.log bench
	tail -4 bench.log

bench0:
	$(CASA) bench0.py > bench0.log 2>&1
	cp bench0.log bench0
	tail -8 bench0.log

bench1:
	$(CASA) bench1.py > bench1.log 2>&1
	cp bench1.log bench1
	tail -8 bench1.log

bench70:
	$(CASA) bench70.py > bench70.log 2>&1
	cp bench70.log bench70
	tail -8 bench70.log

#       Slides to show off some examples features

slides:	$(SLIDES)

#
#       Various styles of combination of skymodel (TP and ALMA configs)

# 1065.29user 75.13system 6:41.29elapsed 284%CPU
sky1:
	$(CASA) sky1.py > sky1.log 2>&1
	cp sky1.py sky1.log sky1

# 2626.11user 178.04system 15:03.45elapsed 310%CPU
sky1a:
	$(CASA) sky1.py pdir='"sky1a"' otf=1 > sky1a.log 2>&1
	cp sky1.py sky1a.log sky1a

# 1110.98user 82.52system 7:05.84elapsed 280%CPU
sky1b:
	$(CASA) sky1.py pdir='"sky1b"' otf=1 SCHWAB=1 > sky1b.log 2>&1
	cp sky1.py sky1b.log sky1b

# 1093.91user 74.43system 6:45.86elapsed 287%CPU
sky1c:
	$(CASA) sky1.py pdir='"sky1c"' cfg='[0,1,2]'  > sky1c.log 2>&1
	cp sky1.py sky1c.log sky1c

# Adele's polkadot problem?
sky1d:
	$(CASA) sky1.py pdir='"sky1d"' cfg='[0,1,2]' grid=60 > sky1d.log 2>&1
	cp sky1.py sky1d.log sky1d

# make viewing portion smaller: 100" sky (inner 1/4) but the mapsize is 400"
sky1e:
	$(CASA) sky1.py pdir='"sky1e"' imsize_m=1024 pixel_m=0.1   > sky1e.log 2>&1
	cp sky1.py sky1e.log sky1e

# more configs
sky1f:
	$(CASA) sky1.py pdir='"sky1f"' cfg='[0,1,2,3,4,5,6]'   > sky1f.log 2>&1
	cp sky1.py sky1f.log sky1f

# try a bigger SD
sky1g:
	$(CASA) sky1.py pdir='"sky1g"' cfg='[0,1]' niter='[0,1000]' dish=48 > sky1g.log 2>&1
	cp sky1.py sky1g.log sky1g


#  sky2 is the generic TP2VIS-only mapping testsuite, the "sky2_all" runs a variety of tests
sky2:
	$(CASA) sky2.py > sky2.log 2>&1
	cp sky2.py sky2.log sky2.ptg sky2

#  all the sky2 based simulations, I'm not adding these to the earlier TESTS=
SKY2_ALL = sky2_1 sky2_2 sky2_3 sky2_4 sky2_5 \
	   sky2_1a sky2_1b sky2_1c sky2_1d sky2_1e sky2_1f \
	   sky2_2a sky2_2b sky2_2c sky2_2d sky2_2e sky2_2f

sky2_all: $(SKY2_ALL)

sky2_all_clean:
	rm -rf $(SKY2_ALL)

sky2_all_tar:
	tar cf sky2_all.tar $(SKY2_ALL)

# flux as function of pixel size
# 200" sky, 50" beam
sky2_1:
	$(CASA) sky2.py pdir='"sky2_1"' pixel_m=0.05 pixel_s=0.8  > sky2_1.log 2>&1
	cp sky2.py sky2_1.log sky2_1.ptg sky2_1
	tail -20 sky2_1.log

# 400" sky
sky2_2:
	$(CASA) sky2.py pdir='"sky2_2"' pixel_m=0.1 pixel_s=1.6  > sky2_2.log 2>&1
	cp sky2.py sky2_2.log sky2_2.ptg sky2_2
	tail -20 sky2_2.log

# 800" sky
sky2_3:
	$(CASA) sky2.py pdir='"sky2_3"' pixel_m=0.2 pixel_s=3.2  > sky2_3.log 2>&1
	cp sky2.py sky2_3.log sky2_3.ptg sky2_3
	tail -20 sky2_3.log

# 1600" sky
sky2_4:
	$(CASA) sky2.py pdir='"sky2_4"' pixel_m=0.4 imsize_s=512 pixel_s=3.2  > sky2_4.log 2>&1
	cp sky2.py sky2_4.log sky2_4.ptg sky2_4
	tail -20 sky2_4.log

# 1600" sky
sky2_5:
	$(CASA) sky2.py pdir='"sky2_5"' pixel_m=0.4 pixel_s=6.4  > sky2_5.log 2>&1
	cp sky2.py sky2_5.log sky2_5.ptg sky2_5
	tail -20 sky2_5.log

# the flux loss in sky2_1,2,3,4/5 is due to large pixel size? Here in 20,30,40 we keep the pixel size (pixel_s) the same
# 400" sky
sky2_20:
	$(CASA) sky2.py pdir='"sky2_20"' pixel_m=0.1 imsize_s=512 > sky2_20.log 2>&1
	cp sky2.py sky2_20.log sky2_20.ptg sky2_20
	tail -20 sky2_20.log

# 800" sky
sky2_30:
	$(CASA) sky2.py pdir='"sky2_30"' pixel_m=0.2 imsize_s=1024  > sky2_30.log 2>&1
	cp sky2.py sky2_30.log sky2_30.ptg sky2_30
	tail -20 sky2_30.log

# 1600" sky
sky2_40:
	$(CASA) sky2.py pdir='"sky2_40"' pixel_m=0.4 imsize_s=2048  > sky2_40.log 2>&1
	cp sky2.py sky2_40.log sky2_40.ptg sky2_40
	tail -20 sky2_40.log

# flux as function of small gridding step
# 400" sky
sky2_2a:
	$(CASA) sky2.py pdir='"sky2_2a"' pixel_m=0.1 pixel_s=1.6 grid=25 > sky2_2a.log 2>&1
	cp sky2.py sky2_2a.log sky2_2a.ptg sky2_2a
	tail -20 sky2_2a.log

# 400" sky
sky2_2b:
	$(CASA) sky2.py pdir='"sky2_2b"' pixel_m=0.1 pixel_s=1.6 grid=20 > sky2_2b.log 2>&1
	cp sky2.py sky2_2b.log sky2_2b.ptg sky2_2b
	tail -20 sky2_2b.log

# 400" sky
sky2_2c:
	$(CASA) sky2.py pdir='"sky2_2c"' pixel_m=0.1 pixel_s=1.6 grid=15 > sky2_2c.log 2>&1
	cp sky2.py sky2_2c.log sky2_2c.ptg sky2_2c
	tail -20 sky2_2c.log

# bigger gridding steps to see the beam problem
# 400" sky
sky2_2d:
	$(CASA) sky2.py pdir='"sky2_2d"' pixel_m=0.1 pixel_s=1.6 grid=60 > sky2_2d.log 2>&1
	cp sky2.py sky2_2d.log sky2_2d.ptg sky2_2d
	tail -20 sky2_2d.log

# 400" sky
sky2_2e:
	$(CASA) sky2.py pdir='"sky2_2e"' pixel_m=0.1 pixel_s=1.6 grid=120 > sky2_2e.log 2>&1
	cp sky2.py sky2_2e.log sky2_2e.ptg sky2_2e
	tail -20 sky2_2e.log

# 400" sky
sky2_2f:
	$(CASA) sky2.py pdir='"sky2_2f"' pixel_m=0.1 pixel_s=1.6 grid=180 > sky2_2f.log 2>&1
	cp sky2.py sky2_2f.log sky2_2f.ptg sky2_2f
	tail -20 sky2_2f.log


# dscale range
# 200" sky, 30" beam
sky2_1a:
	$(CASA) sky2.py pdir='"sky2_1a"' pixel_m=0.05 pixel_s=0.8 dscale=2 > sky2_1a.log 2>&1
	cp sky2.py sky2_1a.log sky2_1a.ptg sky2_1a
	tail -20 sky2_1a.log

# 200" sky, 15" beam
sky2_1b:
	$(CASA) sky2.py pdir='"sky2_1b"' pixel_m=0.05 pixel_s=0.8 dscale=4 > sky2_1b.log 2>&1
	cp sky2.py sky2_1b.log sky2_1b.ptg sky2_1b
	tail -20 sky2_1b.log

# 200" sky, 8" beam
sky2_1c:
	$(CASA) sky2.py pdir='"sky2_1c"' pixel_m=0.05 pixel_s=0.8 dscale=8 > sky2_1c.log 2>&1
	cp sky2.py sky2_1c.log sky2_1c.ptg sky2_1c
	tail -20 sky2_1c.log

# bigger gridding step and the dish3 usage
# 200" sky, 60" beam
sky2_1d:
	$(CASA) sky2.py pdir='"sky2_1d"' dish=12 maxuv=12  > sky2_1d.log 2>&1
	cp sky2.py sky2_1d.log sky2_1d.ptg sky2_1d
	tail -20 sky2_1d.log

# 200" sky, 30" beam
sky2_1e:
	$(CASA) sky2.py pdir='"sky2_1e"' dish=24 maxuv=24 > sky2_1e.log 2>&1
	cp sky2.py sky2_1e.log sky2_1e.ptg sky2_1e
	tail -20 sky2_1e.log

# 200" sky, 15" beam
sky2_1f:
	$(CASA) sky2.py pdir='"sky2_1f"' dish=48 minuv=5 maxuv=48 > sky2_1f.log 2>&1
	cp sky2.py sky2_1f.log sky2_1f.ptg sky2_1f
	tail -20 sky2_1f.log

# varying dish, fixed dish3 with the same resolution?
sky2_1g:
	$(CASA) sky2.py pdir='"sky2_1g"' dish=48 dish3=12 maxuv=10 > sky2_1g.log 2>&1
	cp sky2.py sky2_1g.log sky2_1g.ptg sky2_1g
	tail -20 sky2_1g.log

sky2_1h:
	$(CASA) sky2.py pdir='"sky2_1h"' dish=48 dish3=24 maxuv=20 > sky2_1h.log 2>&1
	cp sky2.py sky2_1h.log sky2_1h.ptg sky2_1h
	tail -20 sky2_1h.log

sky2_1i:
	$(CASA) sky2.py pdir='"sky2_1i"' dish=48 dish3=48 maxuv=40 > sky2_1i.log 2>&1
	cp sky2.py sky2_1i.log sky2_1i.ptg sky2_1i
	tail -20 sky2_1i.log



# older version of cas_11271
sky0:   sky0a sky0b
	@echo vi1 results:
	grep QAC_STATS sky0a.log
	@echo vi2 results:
	grep QAC_STATS sky0b.log

sky0a:
	VI1=1 $(CASA) sky0.py test='"sky0a"' > sky0a.log 2>&1

sky0b:
	$(CASA)       sky0.py test='"sky0b"' > sky0b.log 2>&1


# this will show that Amp(uv=0,0) is indeed approaches the full flux, 113100.572 Jy
sky2_000:
	$(CASA) sky2.py pdir='"sky2_000"' pixel_m=0.005 grid=0 clean=0 > sky2_000.log 2>&1
	grep ^AMP sky2_000.log

# sky2 with a hole in the UV distribution
sky2_uvmin: sky2_uvmin1 sky2_uvmin2 sky2_uvmin4 sky2_uvmin8

sky2_uvmin1:
	$(CASA) sky2.py pdir='"sky2_uvmin1"'  dish=50 minuv=1 maxuv=50 > sky2_uvmin1.log  2>&1

sky2_uvmin2:
	$(CASA) sky2.py pdir='"sky2_uvmin2"'  dish=50 minuv=2 maxuv=50 > sky2_uvmin2.log  2>&1

sky2_uvmin4:
	$(CASA) sky2.py pdir='"sky2_uvmin4"'  dish=50 minuv=4 maxuv=50 > sky2_uvmin4.log  2>&1

sky2_uvmin8:
	$(CASA) sky2.py pdir='"sky2_uvmin8"'  dish=50 minuv=8 maxuv=50 > sky2_uvmin8.log  2>&1

pjt:
	$(CASA) sky2.py pdir='"sky2_uvmin1a"' minuv=1 > sky2_uvmin1a.log grid=25 2>&1
	$(CASA) sky2.py pdir='"sky2_uvmin1b"' minuv=1 > sky2_uvmin1b.log grid=20 2>&1
	$(CASA) sky2.py pdir='"sky2_uvmin1c"' minuv=1 > sky2_uvmin1c.log niter='range(0,5000,500)' 2>&1
	$(CASA) sky2.py pdir='"sky2_uvmin1d"' minuv=1 > sky2_uvmin1d.log grid=15 dish=24 maxuv=24 niter='range(0,5000,500)' 2>&1
	$(CASA) sky2.py pdir='"sky2_uvmin1e"' minuv=2 > sky2_uvmin1e.log grid=15 dish=24 maxuv=24 niter='range(0,5000,500)' 2>&1
	$(CASA) sky2.py pdir='"sky2_uvmin1f"' minuv=1 > sky2_uvmin1f.log grid=22 dish=18 maxuv=18 niter='range(0,5000,500)' 2>&1

# expose the mosaicing flux bug in CASA 5.1 (April 2018) - gridder='standard'  is not affected
cas_11271: cas_11271a cas_11271b
	@grep ^CASA cas_11271a.log
	@echo vi1 results:
	grep QAC_STATS cas_11271a.log
	@echo vi2 results:
	grep QAC_STATS cas_11271b.log

cas_11271a:
	VI1=1 $(CASA) cas_11271.py pdir='"cas_11271a"' > cas_11271a.log 2>&1
	cp cas_11271.py cas_11271a

cas_11271b:
	$(CASA)       cas_11271.py pdir='"cas_11271b"' > cas_11271b.log 2>&1
	cp cas_11271.py cas_11271b

# ngVLA examples

test1:
	$(CASA) test1.py > test1.log 2>&1
	tail -8 test1.log

test2:
	$(CASA) test2.py > test2.log 2>&1
	tail -8 test2.log

test3:
	$(CASA) test3.py > test3.log 2>&1
	tail -8 test3.log

test4:
	export VI1=1
	$(CASA) test4.py > test4.log 2>&1
	tail -8 test4.log

test5:
	$(CASA) test5.py > test5.log 2>&1
	tail -8 test5.log


#

# 26.42user 2.87system 0:22.91elapsed 127%CPU
sky3:
	$(CASA) sky3.py pdir='"sky3"' > sky3.log  2>&1
	cp sky3.log sky3

dish3:
	casa -c sky3.py test='"sky_12"' pixel_m=0.025
	casa -c sky3.py test='"sky_25"' pixel_m=0.025 dish=25
	casa -c sky3.py test='"sky_50"' pixel_m=0.025 dish=25 dish3=50
	casa -c sky3.py test='"sky_99"' pixel_m=0.025 dish=99

dish4:
	casa -c sky3.py pdir='"sky3a"' dish=20             > sky3a.log
	casa -c sky3.py pdir='"sky3b"' dish=40             > sky3b.log
	casa -c sky3.py pdir='"sky3c"' dish=40 dish3=20    > sky3c.log
	casa -c sky3.py pdir='"sky3d"' dish=20 dish3=40    > sky3d.log
	casa -c sky3.py pdir='"sky3e"'                     > sky3e.log
#	casa -c sky3.py pdir='"sky3f"'                     > sky3f.log    # without qac_tpdish()

dish5:
	@echo Single pointing
	casa -c sky3.py pdir='"sky3_1"' dish=20  grid=0
	@echo 7 point pointing
	@echo 115 pointings
	casa -c sky3.py pdir='"sky3_2"' dish=20  grid=10 pixel_m=0.025
	@echo 23 pointings
	casa -c sky3.py pdir='"sky3_2"' dish=20  grid=10 pixel_m=0.01


# new version with the Schwab option, needs deconv=True and Jy/beam maps



# Here are some slides for the QAC examples talk

slide1:
	$(CASA) sky3.py pdir='"slide1"' > slide1.log  2>&1

# try and emulate the most compact C43-1 ALMA 12m configuration, should have a 3.38" beam
# but has a beam of 4.46"
slide2:
	$(CASA) sky3.py pdir='"slide2"' dish=160 > slide2.log  2>&1

# this one will get about 3.4"
# but the comparison with the smooth TP map is pretty bad due to TP vis dropoff?
slide3:
	$(CASA) sky3.py pdir='"slide3"' dish=211 > slide3.log  2>&1

# try iterating  43"
slide4:
	$(CASA) sky3.py pdir='"slide4"' dish=211 niter='[0,100,500,2000]' > slide4.log  2>&1


# works :-)   qac_ingest() also does the trick; now broken?
slide5:
	$(CASA) sky3.py pdir='"slide5"' dish=211 model='"skymodel.im"' > slide5.log  2>&1

# do some mosaicing, understand the two imsize_/pixel_ variables
slide6:
	$(CASA) sky3.py pdir='"slide6a"' dish=20 grid=20 imsize_m=1024 > slide6a.log  2>&1
	$(CASA) sky3.py pdir='"slide6b"' dish=20 grid=20 imsize_m=2048 > slide6b.log  2>&1
	$(CASA) sky3.py pdir='"slide6c"' dish=40 grid=10 imsize_m=1024 > slide6c.log  2>&1
	$(CASA) sky3.py pdir='"slide6d"' dish=40 grid=10 imsize_m=2048 > slide6d.log  2>&1


# slide7a: 27'
slide7:
	$(CASA) sky3.py pdir='"slide7a"' dish=20 grid=20 imsize_m=1024 VP=1 > slide7a.log  2>&1
#	$(CASA) sky3.py pdir='"slide6b"' dish=20 grid=20 imsize_m=2048 > slide6b.log  2>&1
	$(CASA) sky3.py pdir='"slide7c"' dish=40 grid=10 imsize_m=1024 VP=1 > slide7c.log  2>&1
#	$(CASA) sky3.py pdir='"slide6d"' dish=40 grid=10 imsize_m=2048 > slide6d.log  2>&1


#  big dish and big grid spacing see the different pointings (27 pointings)    37.4 kJy   42.6 kJy (pbcor)
#  big dish and big grid spacing see the different pointings (now 203 pointings) 
#  aug 17: (old one was wrong)   10' each on cpu
#
slide8:
	$(CASA) sky3.py pdir='"slide8a"' dish=24 grid=15 VP=0 > slide8a.log  2>&1
	$(CASA) sky3.py pdir='"slide8b"' dish=24 grid=15 VP=1 > slide8b.log  2>&1

#  big dish and big grid spacing see the different pointings (7 pointings)
#  37" with no bug028 "fix", 11' wiht the bug028 'fix'
slide8ab:
	$(CASA) sky3.py pdir='"slide8a"' dish=211 grid=40 imsize_m=2048 VP=0 > slide8a.log  2>&1
	$(CASA) sky3.py pdir='"slide8b"' dish=211 grid=40 imsize_m=2048 VP=1 > slide8b.log  2>&1

slide9:
	$(CASA) sky3.py pdir='"slide9a"' dish=211 grid=50 VP=0 > slide9a.log  2>&1
	$(CASA) sky3.py pdir='"slide9b"' dish=211 grid=40 VP=0 > slide9b.log  2>&1
	$(CASA) sky3.py pdir='"slide9c"' dish=211 grid=30 VP=0 > slide9c.log  2>&1
	$(CASA) sky3.py pdir='"slide9d"' dish=211 grid=20 VP=0 > slide9d.log  2>&1
	$(CASA) sky3.py pdir='"slide9e"' dish=211 grid=10 VP=0 > slide9e.log  2>&1

# same as sky2_uvmin* series:  punch a hole in the UV and using the "bug" in tp2vis alma only dishes
slide10:
	$(CASA) sky2.py pdir='"slide10a"'  dish=50  minuv=5 maxuv=50 > slide10a.log  2>&1
	$(CASA) sky2.py pdir='"slide10b"'  dish=211         maxuv=50 > slide10b.log  2>&1
	$(CASA) sky2.py pdir='"slide10c"'  dish=211 minuv=5 maxuv=50 > slide10c.log  2>&1


#   show that picking a new dish is the same as picking a new pixel-size with the 12m dish
slide11:
	$(CASA) sky3.py pdir='"slide11a"'  dish=24 grid=15  imsize_m=2048 VP=1 > slide11a.log  2>&1

#   check convergence of the PSF of the tp.ms imaged 
slide12:
	$(CASA) sky3.py pdir='"slide12a"'           > slide12a.log  2>&1
	$(CASA) sky3.py pdir='"slide12b"'  nvgrp=32 > slide12b.log  2>&1
	$(CASA) sky3.py pdir='"slide12c"'  maxuv=12 > slide12c.log  2>&1

# check flux two ways with smaller beams
# ? use box region in inner quarter to prevent edge effects ?
slide13:
	$(CASA) sky3.py pdir='"slide13a"'  dish=24 grid=15 VP=0 > slide13a.log  2>&1
	$(CASA) sky3.py pdir='"slide13b"'  dish=24 grid=15 VP=1 > slide13b.log  2>&1

# check niter convergence, even niter=100 shows divergence
slide14:
	$(CASA) sky3.py pdir='"slide14a"' niter='[0,100]' VP=0 cycleniter=10 > slide14a.log  2>&1
	$(CASA) sky3.py pdir='"slide14b"' niter='[0,100]' VP=1 cycleniter=10 > slide14b.log  2>&1


# comparing sky2 and sky3
slide15:
	$(CASA) sky2.py pdir='"slide15a"' grid=0 niter='[0,100]' cycleniter=10 > slide15a.log  2>&1
	$(CASA) sky3.py pdir='"slide15b"' grid=0 niter='[0,100]' cycleniter=10 > slide15b.log  2>&1

#   slide16a:  45 pointings  skymodel->97.7  clean0,1=> 60.4 , 61.4
#   slide16b:  45                                       73.0   80.7
#   slide16c: 203 pointings                             60.1   -
slide16:
	#	$(CASA) sky3.py pdir='"slide16a"' grid=30 niter='[0,100]' > slide16a.log  2>&1
	#	$(CASA) sky3.py pdir='"slide16b"' grid=30 pixel_s=1.0 niter='[0,100]' > slide16b.log  2>&1
	#	$(CASA) sky3.py pdir='"slide16c"' grid=30 pixel_m=0.1 pixel_s=1.6 niter='[0,100]' > slide16c.log  2>&1
	#	$(CASA) sky3.py pdir='"slide16d"' grid=30 pixel_m=0.1 pixel_s=1.6 niter='[0,100,200,400,800,1600,3200,6400,128000]' > slide16d.log  2>&1
	$(CASA) sky3.py pdir='"slide16e"' grid=30 pixel_m=0.1 pixel_s=1.6 VP=1 niter='[0,100,200,400,800,1600,3200,6400,128000]' > slide16e.log  2>&1

#  experiment with cycleniter to get better flux recovery
slide17:
	#$(CASA) sky2.py pdir='"slide17a"' grid=30 niter='[0,100,1000]' cycleniter=10 > slide17a.log  2>&1
	$(CASA) sky2.py pdir='"slide17b"' grid=30 niter='[0,100,1000,3000]' cycleniter=100 > slide17b.log  2>&1
	#$(CASA) sky2.py pdir='"slide17a0"' grid=30 niter='[0,100,1000]' > slide17a0.log  2>&1
	#$(CASA) sky2.py pdir='"slide17c"' grid=30 niter='[0,100,1000,3000,10000]' cycleniter=10 > slide17c.log  2>&1

slide18:
	$(CASA) sky2.py pdir='"slide18b"' VP=1 grid=0  dish=24 niter='[0,100,300,1000,3000]' cycleniter=100 > slide18b.log  2>&1
	$(CASA) sky2.py pdir='"slide18a"' VP=1 grid=15 dish=24 niter='[0,100,300,1000,3000]' cycleniter=100 > slide18a.log  2>&1
	#$(CASA) sky2.py pdir='"slide18c"' VP=1 grid=0 dish=24 niter='[0,100,300,1000,3000]' cycleniter=100 > slide18c.log  2>&1

# how does the PSF depend on the UV distribution and why is single pointing vs. mosaic so different?
# minuv only works with VP=0
slide19:
	$(CASA) sky2.py pdir='"slide19a"' grid=0  minuv=0 niter='[0]' > slide19a.log  2>&1
	$(CASA) sky2.py pdir='"slide19b"' grid=0  minuv=1 niter='[0]' > slide19b.log  2>&1
	$(CASA) sky2.py pdir='"slide19c"' grid=0  minuv=2 niter='[0]' > slide19c.log  2>&1
	$(CASA) sky2.py pdir='"slide19d"' grid=30 minuv=0 niter='[0]' > slide19d.log  2>&1
	$(CASA) sky2.py pdir='"slide19e"' grid=30 minuv=1 niter='[0]' > slide19e.log  2>&1
	$(CASA) sky2.py pdir='"slide19f"' grid=30 minuv=2 niter='[0]' > slide19f.log  2>&1

# how does the PSF depens on maxuv ?  the default is 5/6dish
slide20:
	$(CASA) sky2.py pdir='"slide20a"' grid=0  maxuv=10 niter='[0]' > slide20a.log  2>&1
	$(CASA) sky2.py pdir='"slide20b"' grid=0  maxuv=12 niter='[0]' > slide20b.log  2>&1
	$(CASA) sky2.py pdir='"slide20c"' grid=0  maxuv=14 niter='[0]' > slide20c.log  2>&1
	$(CASA) sky2.py pdir='"slide20d"' grid=30 maxuv=10 niter='[0]' > slide20d.log  2>&1
	$(CASA) sky2.py pdir='"slide20e"' grid=30 maxuv=12 niter='[0]' > slide20e.log  2>&1
	$(CASA) sky2.py pdir='"slide20f"' grid=30 maxuv=14 niter='[0]' > slide20f.log  2>&1

# does the PSF get smaller in a mosaic when beams don't overlap
slide20-1:
	$(CASA) sky2.py pdir='"slide20g"' grid=40 niter='[0]' > slide20g.log  2>&1
	$(CASA) sky2.py pdir='"slide20h"' grid=50 niter='[0]' > slide20h.log  2>&1
	$(CASA) sky2.py pdir='"slide20i"' grid=60 niter='[0]' > slide20i.log  2>&1
	$(CASA) sky2.py pdir='"slide20j"' grid=70 niter='[0]' > slide20j.log  2>&1
	$(CASA) sky2.py pdir='"slide20k"' grid=80 niter='[0]' > slide20k.log  2>&1
	$(CASA) sky2.py pdir='"slide20l"' grid=90 niter='[0]' > slide20l.log  2>&1

# shape of single pointing beam;
#    - does it get rounding as nvgrp goes up
#    - do the sidelobes go down
slide21:
	$(CASA) sky2.py pdir='"slide21a"' grid=0 niter='[0]' nvgrp=4             > slide21a.log  2>&1
	$(CASA) sky2.py pdir='"slide21b"' grid=0 niter='[0]' nvgrp=16            > slide21b.log  2>&1
	$(CASA) sky2.py pdir='"slide21c"' grid=0 niter='[0]' nvgrp=64            > slide21c.log  2>&1
	$(CASA) sky2.py pdir='"slide21d"' grid=0 niter='[0]' nvgrp=64  maxuv=12  > slide21d.log  2>&1
	$(CASA) sky2.py pdir='"slide21e"' grid=0 niter='[0]' nvgrp=64  maxuv=14  > slide21e.log  2>&1

# convergence of mosaic'd PSF as function of nvgrp
slide22:
	$(CASA) sky2.py pdir='"slide22a"' grid=30 niter='[0]' nvgrp=4             > slide22a.log  2>&1
	$(CASA) sky2.py pdir='"slide22b"' grid=30 niter='[0]' nvgrp=16            > slide22b.log  2>&1
	$(CASA) sky2.py pdir='"slide22c"' grid=30 niter='[0]' nvgrp=64            > slide22c.log  2>&1
	$(CASA) sky2.py pdir='"slide22d"' grid=30 niter='[0]' nvgrp=256           > slide22d.log  2>&1

# what really is dish3 doing?
slide23:
	$(CASA) sky2.py pdir='"slide23a"' grid=0 niter='[0]' VP=0           > slide23a.log  2>&1
	$(CASA) sky2.py pdir='"slide23b"' grid=0 niter='[0]' VP=0 dish3=24  > slide23b.log  2>&1
	$(CASA) sky2.py pdir='"slide23c"' grid=0 niter='[0]' VP=1 dish3=24  > slide23c.log  2>&1

# PSF size for INT and TPINT single  vs. mosaic - 12m only
# also carefully setting the weights in both the same by picking nvgrp= and times=
# in this case all configurations get 1800 secs.
slide24:
	$(CASA) sky1.py pdir='"slide24a"' grid=0  niter='[0]' cfg='[0,1]' nvgrp=1800 times='[0.5,30]'      > slide24a.log 2>&1
	$(CASA) sky1.py pdir='"slide24b"' grid=30 niter='[0]' cfg='[0,1]' nvgrp=40   times='[0.5,4.0/6.0]' > slide24b.log 2>&1


# need to test a pure gauss beam, since tp2vis has gauss beam

# lgm homework; default is clark

point1:
	$(CASA) sky1.py pdir='"point1"' model='"pointmodel.fits"' grid=0 niter='[0,1,2,3,4,5,6,7,8,9,10,20,30,40,50,60,70,80,90,100,110,120,130]' cfg='[1]' wfactor=1 > point1.log 2>&1


point2:
	# at niter=100 start dotting the beam
	$(CASA) sky2.py pdir='"point2"' model='"pointmodel.fits"' grid=0 niter='[0,1,2,3,10,20,30,100,200,300,1000]' VP=1 > point2.log 2>&1
	#$(CASA) sky2.py pdir='"point2"' model='"pointmodel.fits"' grid=0 niter='[0,1,2,3,4,5,6,7,8,9,10,20,30,40,50,60,70,80,90,100,110,120,130]' > point2.log 2>&1
	cp sky2.py point2.log point2

point3:
	#$(CASA) sky1.py pdir='"point3"' model='"pointmodel.fits"' grid=0 niter='[0,1,2,3,4,5,6,7,8,9,10,20,30,40,50,60,70,80,90,100,110,120,130]' cfg='[0,1]' > point3.log 2>&1
	$(CASA) sky1.py pdir='"point3"' model='"pointmodel.fits"' grid=0 niter='[0,1,2,3,4,5,6,7,8,9,10,20,30,40,50,60,70,80,90,100,110,120,130]' cfg='[0,1]' wfactor=1 > point3.log 2>&1

point4:
	$(CASA) sky1.py pdir='"point4"' model='"pointmodel.fits"' grid=0 niter='[0,1,2,3,4,5,6,7,8,9,10,20,30,40,50,60,70,80,90,100,110,120,130]' cfg='[0,1,2]' wfactor=1 > point4.log 2>&1

point5:
	$(CASA) sky1.py pdir='"point5"' model='"pointmodel.fits"' grid=0 niter='[0,1,2,3,4,5,6,7,8,9,10,20,30,40,50,60,70,80,90,100,110,120,130]' cfg='[0,1,2]' wfactor=1 > point5.log 2>&1

point6:
	$(CASA) sky1.py pdir='"point6"' model='"pointmodel.fits"' grid=0 niter='[0,1,2,3,4,5,6,7,8,9,10,20,30,40,50,60,70,80,90,100,110,120,130]' cfg='[0,1,2,3]' wfactor=1 > point6.log 2>&1

point7:
	$(CASA) sky1.py pdir='"point7"' model='"pointmodel.fits"' grid=0 niter='[0,1,2,3,4,5,6,7,8,9,10,20,30,40,50,60,70,80,90,100,110,120,130]' cfg='[0,1,2,3]' wfactor=100 > point7.log 2>&1


#       see if beamsize difference between single pointing and mosaic differ?
#       and how does flux converge - needs cycleniter=1
point8:
	$(CASA) sky2.py pdir='"point8a"' model='"pointmodel.fits"' grid=0  niter='[0,1,2,3,4,5,6,7,8,9,10,20,30,40,50,60,70,80,90,100,110,120,130]' cycleniter=1 > point8a.log 2>&1
	$(CASA) sky2.py pdir='"point8b"' model='"pointmodel.fits"' grid=30 niter='[0,1,2,3,4,5,6,7,8,9,10,20,30,40,50,60,70,80,90,100,110,120,130]' cycleniter=1 > point8b.log 2>&1
