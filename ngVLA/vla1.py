# -*- python -*-
#
#  Play with the skymodel 
#     - one or full pointing set
#     - options for feather, ssc
#
#  Reminder: at 115 GHz we have:
#      12m PB is 50" (FWHM)   [FWHM" ~ 600/DishDiam]
#       7m PB is 85"
#
#  Timing:
#           30' on T530
#  Memory:
#           1.7GB +  3.0
#  Space:
#           Uses about 1.4 GB

test         = 'vla1'                               # name of directory within which everything will reside
model        = '../models/skymodel.fits'            # this has phasecenter with dec=-30 for ALMA sims
phasecenter  = 'J2000 180.000000deg 40.000000deg'   # where we want this model to be on the sky, at VLA

# pick the piece of the model to image, and at what pixel size
# natively this model is 4096 pixels at 0.05"
# @todo qac_tp_vis handles this differently from simobserve()
imsize_m     = 4096
pixel_m      = 0.05

# pick the sky imaging parameters (for tclean)
# The product of these typically will be the same as that of the model (but don't need to)
# pick the pixel_s based on the largest array configuration (see below) choosen
imsize_s     = 256
pixel_s      = 0.8

# number of TP cycles
nvgrp        = 4

# pick a few niter values for tclean to check flux convergence 
# niter        = [0,500,1000,2000]
#niter        = [0,100]
#niter        = [0,100,1000]
niter        = [0,1000]
# niter        = [0,1000,4000]
# niter        = [0]

# pick which ngVLA configurations you want (0=SSA, 1=core 2=
cfg          = [0]

# integration times
times        = [1, 1]     # 1 hrs in 1 min integrations

# single pointing?  Set grid to a positive arcsec grid spacing if the field needs to be covered
#                   ALMA normally uses lambda/2D   hexgrid is Lambda/sqrt(3)D
grid         =  0        # this can be pointings good for small dish nyquist

# tp dish size
dish         = 12

# scaling factors
wfactor      = 0.01
afactor      = 1      # not implemented yet

# -- do not change parameters below this ---
import sys
for arg in qac_argv(sys.argv):
    exec(arg)

# derived parameters
ptg = test + '.ptg'              # pointing mosaic for the ptg

# imsize_m =  imsize_m / 2       # test w/ smaller portion of grid ?

# report, add Dtime
qac_begin(test,False)
qac_log("REPORT")
qac_version()
tp2vis_version()

if grid > 0:
    # create a mosaic of pointings for 12m, that's overkill for the 7m
    p = qac_im_ptg(phasecenter,imsize_m,pixel_m,grid,rect=True,outfile=ptg)
else:
    # create a single pointing 
    qac_ptg(phasecenter,ptg)
    p = [phasecenter]

qac_project(test)
# create an MS based on a model and antenna configuration for VLA
qac_log("ngVLA")
ms1={}
for c in cfg:
    ms1[c] = qac_vla(test,model,imsize_m,pixel_m,cfg=c,ptg=ptg, phasecenter=phasecenter, times=times)
# startmodel for later
startmodel = ms1[cfg[0]].replace('.ms','.skymodel')

# find out which MS we got for the INT, or use intms = ms1.values()
intms = ms1.values()


qac_log("CLEAN")
qac_clean1(test+'/clean3', intms, imsize_s, pixel_s,phasecenter=phasecenter, niter=niter)

qac_log("OTF")
# create an OTF TP map using a [12m] dish
qac_tp_otf(test+'/clean3', startmodel, dish, template=test+'/clean3/dirtymap.image')


#@todo check naming - int vs dirtymap
qac_log("FEATHER")
# combine TP + INT using feather and ssc, for all niter's
for idx in range(len(niter)):
    qac_feather(test+'/clean3',             niteridx=idx, name="dirtymap")
    qac_ssc    (test+'/clean3',             niteridx=idx, name="dirtymap")
    qac_smooth (test+'/clean3', startmodel, niteridx=idx, name="dirtymap")


# the real flux
qac_log("REGRESSION")
qac_stats(model)
qac_log("Niter = 0 Cleaning")
qac_stats(test+'/clean3/dirtymap.image')
qac_stats(test+'/clean3/dirtymap.image.pbcor')
qac_stats(test+'/clean3/skymodel.smooth.image')
qac_stats(test+'/clean3/otf.image')
qac_stats(test+'/clean3/otf.image.pbcor')
qac_stats(test+'/clean3/ssc.image')
qac_stats(test+'/clean3/feather.image')

qac_log("Niter = 1000 Cleaning")
qac_stats(test+'/clean3/dirtymap_2.image')
qac_stats(test+'/clean3/dirtymap_2.image.pbcor')
qac_stats(test+'/clean3/skymodel_2.smooth.image')
qac_stats(test+'/clean3/otf.image')
qac_stats(test+'/clean3/otf.image.pbcor')
qac_stats(test+'/clean3/ssc_2.image')
qac_stats(test+'/clean3/feather_2.image')


qac_log("PLOT_GRID plots 1 and 2")
a1 = test+'/clean3/dirtymap.image'
a2 = test+'/clean3/dirtymap_2.image'
a3 = test+'/clean3/otf.image'
a4 = test+'/clean3/feather_2.image'
a5 = test+'/clean3/skymodel.smooth.image'
a6 = test+'/clean3/ssc_2.image'

# plot 1:
# niter=0    | niter=1000 | diff
# niter=1000 | otf        | diff
# feather_2  | otf        | diff
qac_plot_grid([a1, a2, a2, a3, a4, a3],diff=10, plot=test+'/plot1.cmp.png')

# plot 2:
# niter=1000 | skymodel | diff
# feather_2  | ssc_2    | diff
qac_plot_grid([a2, a5, a4, a6], diff=10, plot=test+'/plot2.cmp.png')


qac_log("DONE!")
qac_end()

"""
How to compare PDS plot?

p1 = qac_pds()
p2 = qac_pds()
r1 = np.arange(1,len(p1)+1)

plt.figure()
plt.loglog(r1,p1)
plt.loglog(r1,p2)
plt.show()
plt.savefig('cmp12.png')

p1=qac_psd('skymodel1.im')
r1=np.arange(1,len(p1)+1)

p2=qac_psd('skymodel2s.im')
imsmooth('skymodel2.im','gaussian','10arcsec','10arcsec',pa='0deg',outfile='skymodel2ss.im',overwrite=True)
p3=qac_psd('skymodel2ss.im')
imsmooth('skymodel2.im','gaussian','0.1arcsec','0.1arcsec',pa='0deg',outfile='skymodel2sss.im',overwrite=True)
p4=qac_psd('skymodel2sss.im')

plt.figure()
plt.loglog(r1,p1)
plt.loglog(r1,p2)
plt.loglog(r1,p3)
plt.loglog(r1,p4)



"""
