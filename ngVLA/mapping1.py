# -*- python -*-
#
#  Simple ngVLA mapping, using only the core (cfg=1)
#
#  Reminders: at 115 GHz we have: [PB FWHM" ~ 600/DishDiam]
#
#      18m PB is ~33"
#       6m PB is ~100"
#      25m PB is ~25"
#      50m PB is ~12"
#     100m PB is ~6"
#

pdir         = 'map1'                               # name of directory within which everything will reside
model        = '../models/skymodel.fits'            # this has phasecenter with dec=-30 for ALMA sims
phasecenter  = 'J2000 180.0deg 40.0deg'             # where we want this model to be on the sky, at VLA

# pick the piece of the model to image, and at what pixel size
# natively this model is 4096 pixels at 0.05"
imsize_m     = 4096
pixel_m      = 0.005

# pick the sky imaging parameters (for tclean)
# The product of these typically will be the same as that of the model (but don't need to)
# pick the pixel_s based on the largest array configuration (see below) choosen
imsize_s     = 1024
pixel_s      = 0.02

# pick a few niter values for tclean to check flux convergence ; need at least two to get feather/ssc
niter        = [0,1000,2000]

# pick which ngVLA configurations you want (0=SBA, 1=core 2=plains 3=all 4=all+GB+VLBA)
#   [0,1,2] needs 0.02 pixels, since we don't have those, can only map inner portion
#   pixel_m = 0.01 imsize_s=2048 pixel_s=0.02
cfg          = 1

# integration times (see also below for alternative equal time per pointing observations)
times        = [4, 1]     # hrs observing and mins integrations

# grid spacing for mosaic pointings  (18m -> 15"   6m -> 50")
# pick 0 if you only select a single pointing, i.e. no mosaic
grid         = 0

# multi-scale? - Use [0] or None if you don't want it
scales       = [0, 10, 30]

# -- do not change parameters below this ---
import sys
for arg in qac_argv(sys.argv):
    exec(arg)

# derived parameters
ptg  = pdir + '.ptg'              # pointing mosaic for the ptg

if niter==0:   niter=[0]          # be nice to allow this, but below it does need to be a list


# report, add Dtime
qac_begin(pdir,False)
qac_log("REPORT")
qac_version()

# create a mosaic of pointings for the TP 'dish'
p = qac_im_ptg(phasecenter,imsize_m,pixel_m,grid,rect=True,outfile=ptg)
print "Using %d pointings for 18m and grid=%g on fieldsize %g" % (len(p), grid, imsize_m*pixel_m)

# start with a clean project
qac_project(pdir)

# create an MS based on a model and for each ngVLA antenna configuration
# the emperical procedure using the noise= keyword and using qac_noise() is courtesy Carilli et al. (2017)
qac_log("ngVLA")

ms1 = qac_vla(pdir,model,imsize_m,pixel_m,cfg=cfg,ptg=ptg, phasecenter=phasecenter, times=times)
        
# save a startmodel name for later
startmodel = ms1.replace('.ms','.skymodel')


# @todo  use **args e.g. args['gridder'] = 'standard' if only one pointing in one config

qac_log("CLEAN")
qac_clean1(pdir+'/clean3', ms1, imsize_s, pixel_s, phasecenter=phasecenter, niter=niter, scales=scales)

qac_log("BEAM")
qac_beam(pdir+'/clean3/dirtymap.psf', plot=pdir+'/clean3/dirtymap.beam.png')

qac_log("SMOOTH")
qac_smooth (pdir+'/clean3', startmodel, name="dirtymap")

qac_log("PLOT")
qac_plot(pdir+'/clean3/skymodel.smooth.image')
qac_plot(pdir+'/clean3/dirtymap.psf')
qac_plot(pdir+'/clean3/dirtymap.pb')

# check the fluxes
qac_log("REGRESSION")

for idx in range(len(niter)):
    qac_stats(pdir+'/clean3/dirtymap%s.image'         %            QAC.label(idx))    
    qac_stats(pdir+'/clean3/dirtymap%s.image.pbcor'   %            QAC.label(idx))
    qac_plot (pdir+'/clean3/dirtymap%s.image.pbcor'   %            QAC.label(idx))    
qac_stats(pdir+'/clean3/skymodel.smooth.image')
qac_stats(model)

# make a bunch of plots
idx0 = len(niter)-1    # index of last niter[] for plotting
a0 = pdir+'/clean3/dirtymap.image'                  
a1 = pdir+'/clean3/dirtymap%s.image'                  %            QAC.label(idx0)
a2 = pdir+'/clean3/skymodel.smooth.image'

qac_log("POWER SPECTRUM DENSITY")
try:
    qac_psd([startmodel, a0, a1, a2], plot=pdir+'/'+pdir+'.psd.png')
except:
    print "qac_psd failed"

qac_log("FIDELITY")
qac_fidelity(pdir+'/clean3/skymodel.smooth.image',pdir+'/clean3/dirtymap%s.image'% QAC.label(idx0), figure_mode=[1,2,3,4,5])

qac_log("DONE!")
qac_end()
