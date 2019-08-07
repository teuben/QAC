# -*- python -*-
#
#  Play with a skymodel for DC2019
#     - one or full pointing set
#     - options for tp2vis, feather, ssc
#
#  Reminder: at 115 GHz we have:
#      12m PB is 50" (FWHM)   [FWHM" ~ 600/DishDiam]
#       7m PB is 85"
#

pdir         = 'sky3'                               # name of project directory within which (nearly) everything will reside
model        = 'skymodel.fits'                      # this has phasecenter with dec=-30 for ALMA sims
phasecenter  = 'J2000 180.0deg -30.0deg'            # where we want this model to be on the sky

# pick the piece of the model to image, and at what pixel size
# natively this model is 4096 pixels at 0.05" = 204.8"
imsize_m     = 4096
pixel_m      = 0.05

# pick the sky imaging parameters (for tclean) 
imsize_s     = 256
pixel_s      = 0.8

# tp repeat parameter
nvgrp        = 4

# pick a few niter values for tclean to check flux convergence 
niter        = [0,500,1000,2000]
niter        = [0]

# grid or single pointing?  Set grid to a positive arcsec grid spacing if the field needs to be covered
#                           ALMA normally uses lambda/2D
grid         = 30
grid         = 0

# dish size in maxuv will be taken as 5/6 of this
dish         = 12.0

# Experiment with Voltage Pattern (vp was taken, hence VP)
VP           = 0

# Experiment with dish3?
dish3        = None

# amp and weight factor for TPVIS data
wfactor      = 0.05    # weight factor

# -- do not change parameters below this ---
import sys
for arg in qac_argv(sys.argv):
    exec(arg)

# report, add Dtime
qac_begin(pdir)
qac_log("REPORT")
qac_version()
tp2vis_version()

qac_project(pdir)

ptg  = "%s/%s.ptg" % (pdir,pdir)      # pointing mosaic for the ptg

if grid > 0:
    # create a mosaic of pointings 
    p = qac_im_ptg(phasecenter,imsize_m,pixel_m,grid,rect=True,outfile=ptg)
else:
    # create a single pointing 
    qac_ptg(phasecenter,ptg)
    p = [phasecenter]

qac_log("TP2VIS")

if True:
    qac_tpdish('ALMATP', dish)      # default in tp2vis is 12m
    qac_tpdish('VIRTUAL',dish)      # default in tp2vis is 12m
    qac_vp(VP)                      # VP=1 means True

if grid == 0:
    qac_plot(model, mode=1, plot=pdir + '/' + model + '.png')

tpms = qac_tp_vis(pdir,model,ptg,phasecenter=phasecenter,deconv=False,maxuv=5*dish/6.0,nvgrp=nvgrp,fix=0)
tp2viswt(tpms,wfactor,'multiply')
tp2vispl(tpms,outfig=pdir+'/tp2vispl.png')

qac_clean1(pdir + '/clean0', tpms, imsize_s, pixel_s, phasecenter=phasecenter, niter=niter)
qac_plot(pdir+'/clean0/dirtymap.image',      mode=1,plot=pdir+'/dirtymap.png')
qac_plot(pdir+'/clean0/dirtymap.image.pbcor',mode=1,plot=pdir+'/dirtymap.pbcor.png')

# smooth our skymodel to the resolution in the dirtymap, but we need a compliant RA-DEC-POL-FREQ cube
# two ways to do it
if False:
    print("Using QAC tools to check the axes order")
    pmodel = pdir + '/skymodel.im'
    qac_ingest('skymodel.fits',pmodel,[1,2,3])
else:
    print("Using TP2VIS tools to check the axes order")
    if axinorder(model):
        pmodel = model
    else:
        pmodel = arangeax(model)
    print("Using pmodel=%s" % pmodel)

qac_smooth(pdir + '/clean0', pmodel, "dirtymap")
qac_plot(pdir + '/clean0/skymodel.smooth.image', mode=1, plot=pdir+'/skymodel.smooth.png')


if False:
    pdir2 = pdir + '/tp2'
    qac_project(pdir2)
    
    tpms = qac_tp_vis(pdir2,model,ptg,phasecenter=phasecenter,deconv=True,maxuv=5*dish/6.0,nvgrp=nvgrp,fix=0)
    tp2viswt(tpms,wfactor,'multiply')
    tp2vispl(tpms,outfig=pdir2+'/tp2vispl.png')

    qac_clean1(pdir2 + '/clean0', tpms, imsize_s, pixel_s, phasecenter=phasecenter, niter=niter)
    qac_plot(pdir2+'/clean0/dirtymap.image',      plot=pdir2+'/dirtymap.png')
    qac_plot(pdir2+'/clean0/dirtymap.image.pbcor',plot=pdir2+'/dirtymap.pbcor.png')

if False:
    pdir2 = pdir + '/tp3'
    qac_project(pdir2)
    qac_vp(VP, my_schwab=True)
    
    tpms = qac_tp_vis(pdir2,model,ptg,phasecenter=phasecenter,deconv=False,maxuv=5*dish/6.0,nvgrp=nvgrp,fix=0)
    tp2viswt(tpms,wfactor,'multiply')
    tp2vispl(tpms,outfig=pdir2+'/tp2vispl.png')

    qac_clean1(pdir2 + '/clean0', tpms, imsize_s, pixel_s, phasecenter=phasecenter, niter=niter)
    qac_plot(pdir2+'/clean0/dirtymap.image',      plot=pdir2+'/dirtymap.png')
    qac_plot(pdir2+'/clean0/dirtymap.image.pbcor',plot=pdir2+'/dirtymap.pbcor.png')


#   some issues with using the fits/im file, it needs to come from the modeling software (axis 2 and 3 issue)
# qac_tp_otf(pdir+'/clean0', 'skymodel.im', dish,      label='a')
# qac_tp_otf(pdir+'/clean0', model, dish*2,  label='b')


# ERR:   sky_999/clean0/otfa.image.pbcor"*"sky_999/clean0/dirtymap.pb"
#        freq-pol                          pol-freq


# Problems
#     for simple mapping, the dirtymap.image.pbcor does not look like the map, there is some beam mis-match
#     how the UV samples are created ?
