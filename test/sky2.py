# -*- python -*-
#
#  compare mapping of tp2vis data vs. OTF/smooth under various situations
#
#
#  12m ALMA dish at 115.271GHz has PB ~ 54" (or 56" ???)
#
#  for grid=0 you get 1 pointing, and tclean reports a 39.5" beam (will get rounder if you use more UV points)
#  for grid=30 you get this "average beam", about 58-60" which does not get rounder with more points
#
#          Flux       Flux         #pnt  cpu'
#          5.1.2      5.3.0   
#
#  -  -    113.1      113.1        -      -
#  1  0.05  55.0/60.1  60.2/60.2   45     2      (fix=0/1)      
#  2  0.1   52.1       58.3        203    10
#  3  0.2   19.4                   853    40
#  4  0.4    6.2        9.5        3433   229
#
#  - flux does not conserve well at all as we scale up - i don't understand this yet
#    it does converge, but the larger pixel scale ones very slow, if ever they reach the expected 113.1
#  - beamsize is confusing from single beam to tclean's idea of an "average beam" in a mosaic
#    in fact, if you undersample (e.g. grid=100) the PSF will see the other shadow beams,
#    and also the PB is not 1 in the fields near the center, but more like 0.7
#  - how does flux behave when the grid is oversampled?
#    Seems the flux behaves pretty good. Below a certain threshold, flux is pretty constant.
#  - is the beam properly sampled and described?
#
#
#  Notes on beamsizes (ALMA technical handbook talks about HPBW and FWHM)
#  ----------------------------------------------------------------------
#  FWHM = 51.5305 * a / D12 / f100
#  51.5305 = cms*apr/12e11
#  a    is 1.22 (or something close to it, manual talks about 1.02 for ideal dish, and 1.13 for alma 12m dish)
#  D12  is diameter in units of 12m
#  f100 is freq in units of 100GHz  (so CO is at 1.152712)
#
#  tp2vis talks about 65.2 at 100 or 56.5 at 115.2 (or do we mean 115.2712???)
#                     105  at 100 for 7m [this ratio doesn't vibe with scaling 12/7, that would predict 112")
#
#  If we believe the a=1.13 value, we would have 58.2", not 65.2
#  Reversing, the 65.2 would mean a=1.265

test         = 'sky2'                               # name of directory within which everything will reside
model        = 'skymodel.fits'                      # this has phasecenter with dec=-30 for ALMA sims
phasecenter  = 'J2000 180.0deg -30.0deg'            # where we want this model to be on the sky

# pick the piece of the model to image, and at what pixel size
# natively this model is 4096 pixels at 0.05"
# @todo qac_tp_vis handles this differently from simobserve()
imsize_m     = 4096
pixel_m      = 0.05

# pick the sky imaging parameters (for tclean)
# The product of these typically will be the same as that of the model (but don't need to)
# pick the pixel_s based on the largest array configuration (see below) choosen
imsize_s     = 256
pixel_s      = 0.8   # imsize_m/imsize_s * pixel_m

# pick a few niter values for tclean to check flux convergence
# although for pure TP2VIS we should not need much cleaning at all (haha)
niter        = [0]
niter        = [0,1000,4000]

# grid spacing in arcsec (use 0 if you want just the phasecenter)
#                  ALMA normally uses lambda/2D   hexgrid is Lambda/sqrt(3)D
grid         = 30

# these don't work with use_vp=True yet
dish         = 12.0
maxuv        = 10.0

# scale up the dish size (and down the spacing)
# this is an alternative to changing the pixel size (pixel_m and pixel_s)
dscale       = 1.0


# -- do not change parameters below this ---
import sys
for arg in qac_argv(sys.argv):
    exec(arg)

# derived parameters
ptg   = test + '.ptg'              # pointing mosaic file
grid  = grid / dscale              # re-scaling the dish/grid
dish  = dish * dscale              # instead of the pixel
maxuv = maxuv * dscale


# report, add Dtime
qac_begin(test,False)
qac_log("REPORT")
qac_version()
tp2vis_version()

# create a mosaic of pointings 
p = qac_im_ptg(phasecenter, imsize_m, pixel_m, grid, rect=True, outfile=ptg)


# tp2vis
qac_log("TP2VIS:")
qac_tpdish('ALMATP', dish)
qac_tpdish('VIRTUAL',dish)
tpms = qac_tp_vis(test, model, ptg, pixel_m, phasecenter=phasecenter, maxuv=maxuv, deconv=False, fix=1)

# cleaning
qac_log("CLEAN1:")
line = {}
qac_clean1(test+'/clean0', tpms, imsize_s, pixel_s, phasecenter=phasecenter, niter=niter, **line)

# analysis
qac_log("PLOT and STATS:")
qac_beam(test+'/clean0/dirtymap.image')
for idx in range(len(niter)):
    im1 = test+'/clean0/dirtymap%s.image'       % QAC.label(idx)
    im2 = test+'/clean0/dirtymap%s.image.pbcor' % QAC.label(idx)
    qac_plot(im1,mode=1)      # casa based plot w/ colorbar
    qac_stats(im2)            # noise flat
qac_plot(model,mode=1,plot=test+'/'+model+'.png')
qac_stats(model)

# qac_smooth('sky2/clean0','sky2/skymodel.im/')
#  ->   "sky2/clean0/skymodel.smooth.image"-"sky2/clean0/dirtymap.image.pbcor"
#  but get: Exception caught was: LatticeExprNode - coordinates of operands mismatch



qac_log("DONE!")
qac_end()

