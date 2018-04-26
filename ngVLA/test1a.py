
#  test1 with more configurations
#
#

test         = 'test1a'
model        = '../models/skymodel.fits'           # this has phasecenter with dec=-30 for ALMA sims
phasecenter  = 'J2000 180.000000deg 40.000000deg'  # so modify this for ngVLA

# pick the piece of the model to image, and at what pixel size
# natively this model is 4096 pixels at 0.05"
imsize_m     = 4096
pixel_m      = 0.01

# pick the sky imaging parameters (for tclean)
imsize_s     = 512
pixel_s      = 0.25

# pick a few niter values for tclean to check flux convergence 
niter        = [0,1000,2000]
#niter        = [0]

# pick a cfg
cfg          = [0,1]
#cfg          = [0,2]

# -- do not change parameters below this ---
import sys
for arg in qac_argv(sys.argv):
    exec(arg)

ptg = test + '.ptg'              # use a single pointing mosaic for the ptg
if type(niter) != type([]): niter = [niter]


# report
qac_log("TEST: %s" % test)
qac_begin(test)
qac_version()

# create a single pointing mosaic
qac_ptg(phasecenter, ptg)

# begin clean project
qac_project(test)

# create a MS based on a model and antenna configuration
qac_log("VLA")
ms1 = {}
for c in cfg:
    ms1[c] = qac_vla(test, model, imsize_m, pixel_m, cfg=c, ptg=ptg, phasecenter=phasecenter)
    cdir = test + '/clean1_%d' % c
    qac_clean1(cdir, ms1[c], imsize_s, pixel_s, phasecenter=phasecenter, niter=niter)
    qac_plot(cdir + '/dirtymap.image')
intms = ms1.values()

# clean combined
qac_log("CLEAN %s" % str(intms))
cdir = test+'/clean2'
qac_clean1(cdir, intms, imsize_s, pixel_s, phasecenter=phasecenter, niter=niter)
qac_plot(cdir + '/dirtymap.image')
tp2vispl(intms, outfig=test+'/tp2vispl.png')


