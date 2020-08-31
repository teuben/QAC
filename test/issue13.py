# -*- python -*-
#
#  PB beam of TPMS; derived from sky2
#

pdir         = 'issue13'                            # name of directory within which everything will reside
model        = 'pointmodel.fits'                    # this has phasecenter with dec=-30 for ALMA sims
phasecenter  = 'J2000 180.0deg -35.0deg'            # where we want this model to be on the sky

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
niter        = [0,1000,4000]
niter        = [0]

#
cycleniter   = None

# grid spacing in arcsec (use 0 if you want just the phasecenter)
#                  ALMA normally uses lambda/2D   hexgrid is Lambda/sqrt(3)D
grid         = 30

# how many cycles of vis data
nvgrp        = 4

# these don't work with use_vp=True yet, in meters
dish         = 12.0
maxuv        = None
minuv        = 0.0

#
VP           = 0

# Experiment with dish2?
dish2        = None

# scale up the dish size (and down the spacing)
# this is an alternative to changing the pixel size (pixel_m and pixel_s)
dscale       = 1.0

# also tclean?
clean        = 1


# -- do not change parameters below this ---
import sys
for arg in qac_argv(sys.argv):
    exec(arg)

if maxuv == None:
    maxuv = 5.0*dish/6.0

# derived parameters
ptg   = pdir + '.ptg'              # pointing mosaic file
grid  = grid  / dscale             # re-scaling the dish/grid
dish  = dish  * dscale             # instead of the pixel
maxuv = maxuv * dscale


# report, add Dtime
qac_begin(pdir,False)
qac_log("REPORT:")
qac_project(pdir)
qac_version()
tp2vis_version()

# create a mosaic of pointings 
p = qac_im_ptg(phasecenter, imsize_m, pixel_m, grid, outfile=ptg)

# dish size(s)
qac_log("TPDISH:")
if dish2 == None: dish2 = dish
qac_tpdish('ALMATP', dish)
qac_tpdish('VIRTUAL',dish2)
# TESTING for single pointings - do not use at home!
if True:
    qac_tpdish('ALMA12',dish)
qac_vp(VP)                       # should be after all dishes have been set

# tp2vis
qac_log("TP2VIS:")

# for VP=1, fix=1 doesn't copy our TP2VISVP table
if VP:
    tpms = qac_tp_vis(pdir, model, ptg, pixel_m, phasecenter=phasecenter, maxuv=maxuv, nvgrp=nvgrp, deconv=False, fix=0)
else:
    tpms = qac_tp_vis(pdir, model, ptg, pixel_m, phasecenter=phasecenter, maxuv=maxuv, nvgrp=nvgrp, deconv=False, fix=1)

if clean == 0:
    # print flux at (0,0), the first datapoint of the first pointing
    tb.open(tpms)
    amp0 = tb.getcol('DATA')[0,0,0]
    print("AMP(0,0) = %s" % str(amp0))
    tb.close()
    #
    qac_log("DONE!")
    qac_end()
    sys.exit(0)

if minuv > 0.0:
    print("Warning: keeping only data above minuv = %g m" % minuv)
    flagdata(vis=tpms,uvrange='0~%gm'%minuv)
    tpms2 = tpms + '.copy'
    mstransform(tpms,tpms2,datacolumn='DATA',keepflags=False)
    os.system('rm -rf %s; mv %s %s' % (tpms,tpms2,tpms))

# cleaning
qac_log("CLEAN1:")

# additional parameters for tclean()
line = {}
if True:
    line['usemask']  = 'pb'
    line['pbmask']   = 0.5             # the default appears to be 0.0 !!
    # line['normtype'] = 'flatnoise'     # this is supposed to be the default
if True:
    line['cycleniter'] = cycleniter    # hack for point source because of bad (mismatching) TP beam
if grid == 0:
    line['gridder'] = 'standard'
    
qac_clean1(pdir+'/clean0', tpms, imsize_s, pixel_s, phasecenter=phasecenter, niter=niter, **line)
tp2vispl(tpms,outfig=pdir+'/tp2vispl.png', uvzoom = dish2*1.2)

qac_fits(pdir+'/clean0/dirtymap.image',         stats=True)
qac_fits(pdir+'/clean0/dirtymap.image.pbcor',   stats=True)

# 
qac_log("IMSMOOTH:")
im2 = pdir+'/clean0/dirtymap.image.pbcor'
beam0 = imhead(im2)['restoringbeam']
imsmooth(pdir+'/skymodel.im', outfile=pdir+'/clean0/skymodel.smooth',beam=beam0,overwrite=True)
qac_plot(pdir+'/clean0/skymodel.smooth',mode=1)

# analysis
qac_log("PLOT and STATS:")
qac_beam(pdir+'/clean0/dirtymap.psf', plot=pdir+'/clean0/dirtymap.beam.png')
for idx in range(len(niter)):
    im0 = pdir+'/clean0/skymodel.smooth'
    im0 = pdir+'/skymodel.im'
    im1 = pdir+'/clean0/dirtymap%s.image'       % QAC.label(idx)
    im2 = pdir+'/clean0/dirtymap%s.image.pbcor' % QAC.label(idx)
    im3 = pdir+'/clean0/dirtymap%s.model'       % QAC.label(idx)
    im4 = pdir+'/clean0/dirtymap%s.pb'          % QAC.label(idx)
    im5 = pdir+'/clean0/diffmap%s.image'        % QAC.label(idx)
    im6 = pdir+'/clean0/skymodel%s.smooth.image'% QAC.label(idx)
    im7 = pdir+'/clean0/dirtymap%s.tweak.image' % QAC.label(idx)    

    # make im6
    qac_smooth(pdir+'/clean0', im0, niteridx=idx, name='dirtymap', do_flux=False)

    # make im5
    if QAC.exists(im6):
        immath([im6,im4,im1],expr='IM0*IM1-IM2',outfile=im5)

    # make im7
    #if idx > 0:
    #    qac_tweak(pdir+'/clean0','dirtymap',  idx)

    
    qac_plot(im1,mode=1)      # casa based plot w/ colorbar
    qac_plot(im5,mode=1)      # casa based plot w/ colorbar
    
    qac_stats(im2)            # flux flat
    qac_stats(im3)            # model
    qac_stats(im5)            # difference
    #if idx > 0:
    #    qac_stats(im7)        # difference        
    
    
qac_plot(model,mode=1,plot=pdir+'/'+model+'.png')
qac_stats(model)

qac_log("NITER_FLUX")
qac_niter_flux(pdir+'/clean0')

# ah, wrong grid
# qac_smooth(pdir+'/clean0', startmodel, name="dirtymap")


i1 = pdir+'/clean0/dirtymap.image.png'
i2 = pdir+'/clean0/dirtymap_2.image.png'
i3 = pdir+'/clean0/dirtymap_3.image.png'
i4 = pdir+'/clean0/skymodel.smooth.png'
i0 = pdir+'/clean0/montage1.png'
cmd  = "montage -title %s %s %s %s %s -tile 2x2 -geometry +0+0 %s" % (pdir,i1,i2,i3,i4,i0)
os.system(cmd)

# not the right gridding
# qac_fidelity(pdir+'/clean0/skymodel.smooth',pdir+'/clean0/dirtymap_3.image.png')


# qac_smooth('sky2/clean0','sky2/skymodel.im/')
#  ->   "sky2/clean0/skymodel.smooth.image"-"sky2/clean0/dirtymap.image.pbcor"
#  but get: Exception caught was: LatticeExprNode - coordinates of operands mismatch



qac_log("DONE!")
qac_end()

