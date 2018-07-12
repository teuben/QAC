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
dec          = 40.0                                 # Declination

# pick the piece of the model to image, and at what pixel size
# natively this model is 4096 pixels at 0.05"
imsize_m     = 4096
pixel_m      = 0.005

# pick the sky imaging parameters (for tclean)
# The product of these typically will be the same as that of the model (but don't need to)
# pick the pixel_s based on the largest array configuration (see below) choosen
# negativ pixel will force the _m and _s size to be the same
imsize_s     = 512
pixel_s      = -1

# pick a few niter values for tclean to check flux convergence
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

phasecenter  = 'J2000 180.000deg %.3fdeg' % dec    # decode the proper phasecenter


if niter==0:   niter=[0]          # be nice to allow this, but below it does need to be a list

if pixel_s < 0:                   # force the model and sky size the same
    pixel_s = imsize_m * pixel_m / imsize_s


# report, add Dtime
qac_begin(pdir,False)
qac_log("REPORT")
qac_version()

# create a mosaic of pointings for the TP 'dish'
p = qac_im_ptg(phasecenter,imsize_m,pixel_m,grid,outfile=ptg)
print "Using %d pointings for 18m and grid=%g on fieldsize %g arcsec" % (len(p), grid, imsize_m*pixel_m)

# start with a clean project, and use the clean1 directory for all tclean results
qac_project(pdir)
cdir = pdir + '/clean1'

# create an MS based on a model and for each ngVLA antenna configuration
# the emperical procedure using the noise= keyword and using qac_noise() is courtesy Carilli et al. (2017)
qac_log("ngVLA")

ms1 = qac_vla(pdir,model,imsize_m,pixel_m,cfg=cfg,ptg=ptg, phasecenter=phasecenter, times=times)
        
# save a startmodel name for later
startmodel = ms1.replace('.ms','.skymodel')

qac_log("CLEAN")
if grid > 0:
    # the default is mosaicing
    qac_clean1(cdir, ms1, imsize_s, pixel_s, phasecenter=phasecenter, niter=niter, scales=scales)
else:
    # but for single pointing we can use the standard gridder
    qac_clean1(cdir, ms1, imsize_s, pixel_s, phasecenter=phasecenter, niter=niter, scales=scales, gridder='standard')

qac_log("BEAM")
qac_beam(cdir+'/dirtymap.psf', plot=cdir+'/dirtymap.beam.png')

qac_log("SMOOTH")
qac_smooth (cdir, startmodel, name="dirtymap")

qac_log("PLOT")
qac_plot(cdir+'/skymodel.smooth.image')
qac_plot(cdir+'/dirtymap.psf')
qac_plot(cdir+'/dirtymap.pb')

# check the fluxes
qac_log("REGRESSION")

for idx in range(len(niter)):
    qac_stats(cdir+'/dirtymap%s.image'         %            QAC.label(idx))    
    qac_stats(cdir+'/dirtymap%s.image.pbcor'   %            QAC.label(idx))
    qac_plot (cdir+'/dirtymap%s.image'         %            QAC.label(idx))        
    qac_plot (cdir+'/dirtymap%s.image.pbcor'   %            QAC.label(idx))    
qac_stats(cdir+'/skymodel.smooth.image')
qac_stats(model)

# make a bunch of plots
idx0 = len(niter)-1    # index of last niter[] for plotting
a0 = cdir+'/dirtymap.image'                  
a1 = cdir+'/dirtymap%s.image'                  %            QAC.label(idx0)
a2 = cdir+'/skymodel.smooth.image'

qac_plot_grid([a0,a1,a0,a2,a1,a2],diff=10, plot=pdir+'/plot1.cmp.png', labels=True)  

qac_log("POWER SPECTRUM DENSITY")
try:
    qac_psd([startmodel, a0, a1, a2], plot=pdir+'/'+pdir+'.psd.png')
except:
    print "qac_psd failed"

qac_log("FIDELITY")
qac_fidelity(cdir+'/skymodel.smooth.image',cdir+'/dirtymap%s.image'% QAC.label(idx0), figure_mode=[1,2,3,4,5])

qac_log("DONE!")
qac_end()
