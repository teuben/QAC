# -*- python -*-
#
#     Some tests on qac_mac()
#               
#

pdir         = 'sky40'                              # name of directory within which everything will reside
model        = 'skymodel-b.fits'                    # this has phasecenter with dec=-30 for ALMA sims
phasecenter  = 'J2000 180.0deg -35.0deg'            # where we want this model to be on the sky

# pick the piece of the model to image, and at what pixel size
# natively this model is 4096 pixels at 0.05"
imsize_m     = 4096
pixel_m      = 0.05

# pick the sky imaging parameters (for tclean)
# The product of these typically will be the same as that of the model (but don't need to)
# pick the pixel_s based on the largest array configuration (cfg[], see below) choosen
imsize_s     = 256
pixel_s      = 0.8
# slightly bigger to see edge effect
imsize_s     = 512
pixel_s      = 0.5
# Toshi
imsize_s     = 1120
pixel_s      = 0.21
box          = '150,150,970,970'

# number of TP cycles
nvgrp        = 4

# pick a few niter values for tclean to check flux convergence 
niter        = [0,500,1000,2000]
niter        = [0]
niter        = [0,1000,10000]

# pick which ALMA configurations you want (0=7m ACA ; 1,2,3...=12m ALMA)
cfg          = [0,1,2,3]
cfg          = [0]
cfg          = [0,1,2]  # beam is 3.4 x 2.9
cfg          = [0,1,4]  # beam is 2.4 x 2.0 - shouldn't it be 0.8"?

# pick integration times
# 45 pointings for 1 min 45 x 3 = 2.25hr
# 67 pointings for 1 min 67 * 3 = 3.35 if 1.05 mfactor
times        = [2.25, 1]     # 2 hrs in 1 min integrations for 12m; 7m is 3x
times        = [3.35, 1]     # 2 hrs in 1 min integrations for 12m; 7m is 3x

# TP dish size in m; uvmax will be taken as 5/6 of this
# @todo   don't change this
dish         = 12.0

maxuv        = None

# Set grid to a positive arcsec grid spacing if the field needs to be covered
#                   0 will force a single pointing
#                   ALMA normally uses lambda/2D   hexgrid is Lambda/sqrt(3)D
grid         = 30

# OTF: if selected, tp2vis will get an OTF Jy/beam, instead of the model Jy/pixel map
otf          = 0

# advanced features (0 or 1)
VP           = 0
SCHWAB       = 0

# scaling factor of TP to match the INT
wfactor      = 0.01
# scaling factor to get more mosaic pointings for the edge
mfactor      = 1.0
mfactor      = 1.05

# -- do not change parameters below this ---
import sys
for arg in qac_argv(sys.argv):
    exec(arg)

# derived parameters
ptg   = pdir + '.ptg'              # pointing mosaic for the ptg
test  = pdir                       # compat
psd   = []                         # accumulate images for qac_psd()
if maxuv == None:
    maxuv = 5.0*dish/6.0           # for tp2vis

# extra tclean arguments
args = {}
args['usemask'] = 'pb'
args['pbmask']  = 0.5
args['deconvolver']= 'hogbom'

# hardcoded
Qhybrid = True     # this generates /clean4/
    

# report, add Dtime
qac_begin(pdir,False)
qac_project(pdir)
qac_log("REPORT")
qac_version()
tp2vis_version()


if grid > 0:
    # create a mosaic of pointings (used for both 12m and 7m)
    p = qac_im_ptg(phasecenter,imsize_m,pixel_m,grid,rect=True,factor=mfactor,outfile=ptg)
else:
    # create a single pointing 
    qac_ptg(phasecenter,ptg)
    p = [phasecenter]

if True:
    qac_tpdish('ALMATP', dish)
    qac_tpdish('VIRTUAL',dish)
    qac_vp(VP,SCHWAB)
    

# create a series of MS based on a model and antenna configuration for different ACA/ALMA configurations
# we do the INT first, so we get a better sized startmodel for tp2vis, in case we rescale the model
qac_log("ALMA 7m/12m")

# time ratio between 12m : 7m : TP should be 1 : 3 : 4

ms1={}
for c in cfg:
    if c==0:
        # 3 times integration time in 7m array
        ms1[c] = qac_alma(test,model,imsize_m,pixel_m,cycle=7,cfg=c,ptg=ptg, phasecenter=phasecenter, times=[3*times[0],times[1]])
    else:
        ms1[c] = qac_alma(test,model,imsize_m,pixel_m,cycle=7,cfg=c,ptg=ptg, phasecenter=phasecenter, times=times)
# startmodel for later
startmodel = ms1[cfg[0]].replace('.ms','.skymodel')
psd.append(startmodel)

# get a list of MS we got for the INT
intms = ms1.values()

qac_log("TP2VIS")
if otf == 0:
    tpms = qac_tp_vis(pdir,model,ptg,pixel_m,phasecenter=phasecenter,deconv=False,maxuv=maxuv,nvgrp=nvgrp,fix=0)
else:
    tp_beam = 56.7     # @todo
    beam = '%sarcsec' % tp_beam
    otf = pdir + '/' + model.replace('.fits','.otf')
    print("Creating %s" % otf)
    imsmooth(model,'gaussian',beam,beam,pa='0deg',outfile=otf,overwrite=True)
    tpms = qac_tp_vis(test,otf,ptg,pixel_m,phasecenter=phasecenter,deconv=True,maxuv=maxuv,nvgrp=nvgrp,fix=0)
    psd.append(otf)
tp2viswt(tpms,wfactor,'multiply')

qac_log("CLEAN1:")
qac_clean1(test+'/clean0', tpms, imsize_s, pixel_s, phasecenter=phasecenter, **args)
print("ARGS:",args)

qac_log("PLOT and STATS:")
for idx in range(1):
    im1 = test+'/clean0/dirtymap%s.image'       % QAC.label(idx)
    im2 = test+'/clean0/dirtymap%s.image.pbcor' % QAC.label(idx)
    qac_plot(im1,mode=1)      # casa based plot w/ colorbar
    qac_stats(im1)            # noise flat
    qac_stats(im2)            # flux flat
    if idx==0: psd.append(im2)
    

tp2vispl(intms+[tpms],outfig=test+'/tp2vispl.png')

qac_log("MAC")

sdimage1 = test + '/clean0/dirtymap.image.pbcor'
qac_mac(test+'/clean6',sdimage1,intms, imsize_s,pixel_s,niter=niter,phasecenter=phasecenter, **args)
qac_fits(sdimage1,                            test+'/clean6/sky_dirtymap1_box1.fits',      box=box, stats=True)
qac_fits(test+'/clean6/int1.image',           test+'/clean6/sky_int0.image_box1.fits',     box=box, stats=True)
qac_fits(test+'/clean6/int1.image.pbcor',     test+'/clean6/sky_int1.image_box1.fits',     box=box, stats=True)
qac_fits(test+'/clean6/int1.model',           test+'/clean6/sky_int1.model_box1.fits',     box=box, stats=True)
qac_fits(test+'/clean6/int2.model',           test+'/clean6/sky_int2.model_box1.fits',     box=box, stats=True)
qac_fits(test+'/clean6/int2.image',           test+'/clean6/sky_int2.image_box1.fits',     box=box, stats=True)
qac_fits(test+'/clean6/int2.feather',         test+'/clean6/sky_int2.feather_box1.fits',   box=box, stats=True)
qac_fits(test+'/clean6/int2.sm',              test+'/clean6/sky_int2.sm_box1.fits',        box=box, stats=True)
qac_fits(test+'/clean6/macint.image.pbcor',   test+'/clean6/sky_int3.image_box1.fits',     box=box, stats=True)

if otf != 0:
    sdimage2 = otf
    qac_mac(test+'/clean7',sdimage2,intms, imsize_s,pixel_s,niter=niter,phasecenter=phasecenter, **args)
    qac_fits(test+'/clean7/int1.image.pbcor',     test+'/clean7/sky_int1.image_box1.fits',     box=box, stats=True)
    qac_fits(test+'/clean7/int1.model',           test+'/clean7/sky_int1.model_box1.fits',     box=box, stats=True)
    qac_fits(test+'/clean7/int2.model',           test+'/clean7/sky_int2.model_box1.fits',     box=box, stats=True)
    qac_fits(test+'/clean7/int2.image',           test+'/clean7/sky_int2.image_box1.fits',     box=box, stats=True)
    qac_fits(test+'/clean7/int2.feather',         test+'/clean7/sky_int2.feather_box1.fits',   box=box, stats=True)
    qac_fits(test+'/clean7/int2.sm',              test+'/clean7/sky_int2.sm_box1.fits',        box=box, stats=True)
    qac_fits(test+'/clean7/macint.image.pbcor',   test+'/clean7/sky_int3.image_box1.fits',     box=box, stats=True)
    
qac_log("DONE!")
qac_end()
