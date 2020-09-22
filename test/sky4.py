# -*- python -*-
#
#  Typical usage (see also Makefile)
#      casa -c sky4.py  [optional parameters]
#
#  Reminder: at 115 GHz we have:
#      12m PB is 50" (FWHM)   [FWHM" ~ 600/DishDiam]
#       7m PB is 85"
#
#  Integration times:
#     TP               uses (nvgrp * npnt) seconds
#     INT (per config) uses times[0] hours in total, times[1] minutes per pointing
#                      thus it is useful to make sure that (times[0]*60) / (times[1]*npnt) is integral
#
#
#  - clean0:    mapping the TP.MS: 
#  - clean3:    mapping the 'int' and 'tpint' from tp2vis
#  - clean4:    hybrid :
#                   with or without tp.ms,   with rescaled otf or skymodel (jy/pix)
#               
#
# @todo    set a mask so it only cleans in the original

pdir         = 'sky4'                               # name of directory within which everything will reside
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
# slightly bigger to see edge effects
imsize_s     = 512
pixel_s      = 0.5
# Toshi
imsize_s     = 1120
pixel_s      = 0.21
box          = '150,150,970,970'

# export smooth in arcsec? 
esmooth      = None
esmooth      = 2.0

# number of TP cycles
nvgrp        = 4

# pick a few niter values for tclean to check flux convergence 
niter        = [0,500,1000,2000]
niter        = [0]
niter        = [0,1000,10000]

# tclean threshold, e.g. '10mJy'. 
threshold    = None
threshold    = '48mJy'

# pick which ALMA configurations you want (0=7m ACA ; 1,2,3...=12m ALMA)
cfg          = [0,1,2,3]
cfg          = [0]
cfg          = [0,1,2]  # beam is 3.4 x 2.9
cfg          = [0,1,4]  # beam is 2.4 x 2.0 - shouldn't it be 0.8"?

# pick integration times (making sure integral number)
times        = [2.5, 1]   # for 45 pointings - mfactor=1.0
times        = [3.35, 1]  # for 67 pointings - mfactor=1.05

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
# ACA times scaling factor
afactor      = 3
# scaling factor to get more mosaic pointings for the edge
mfactor      = 1.0
mfactor      = 1.05

# -- do not change parameters below this ---
import sys
for arg in qac_argv(sys.argv):
    exec(arg)

# derived parameters
cfg.sort()                         # we need them sorted (see code below)
ptg   = pdir + '.ptg'              # pointing mosaic for the ptg
psd   = []                         # accumulate images for qac_psd()
if maxuv == None:
    maxuv = 5.0*dish/6.0           # for tp2vis

# extra tclean arguments
args = {}
args['usemask']     = 'pb'
args['pbmask']      = 0.5
args['deconvolver'] = 'hogbom'
args['threshold']   = threshold

# hardcoded
Qfeather = True
Qhybrid  = True    # this generates /clean4/ - precursor to qac_mac()
Qsdint   = False
Qmac     = True    # new qac_mac
Qexport  = True

    
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
        ms1[c] = qac_alma(pdir,model,imsize_m,pixel_m,cycle=7,cfg=c,ptg=ptg, phasecenter=phasecenter, times=[afactor*times[0],times[1]])
    else:
        ms1[c] = qac_alma(pdir,model,imsize_m,pixel_m,cycle=7,cfg=c,ptg=ptg, phasecenter=phasecenter, times=times)
# startmodel for later
startmodel = ms1[cfg[0]].replace('.ms','.skymodel')
psd.append(startmodel)

# get a list of MS we got for the INT
intms = list(ms1.values())

qac_log("OTFMAP")

tp_beam = 56.7                    # @todo is this really good enough
beam = '%sarcsec' % tp_beam
# otf = model.replace('.fits','.otf')
otfmap = '%s/skymodel_orig.otf' % pdir
print("Creating %s" % otfmap)
imsmooth(model,'gaussian',beam,beam,pa='0deg',outfile=otfmap+'.tmp',overwrite=True)
imtrans(otfmap+'.tmp',otfmap,order='0132')    # make sure it's an RDSF cubee

qac_log("TP2VIS")
if otf == 0:
    tpms = qac_tp_vis(pdir,model,ptg,pixel_m,phasecenter=phasecenter,deconv=False,maxuv=maxuv,nvgrp=nvgrp,fix=0)
else:
    tpms = qac_tp_vis(pdir,otfmap,ptg,pixel_m,phasecenter=phasecenter,deconv=True,maxuv=maxuv,nvgrp=nvgrp,fix=0)
    psd.append(otfmap)
tp2viswt(tpms,wfactor,'multiply')

if True:
    qac_log("CLEAN1:")
    qac_clean1(pdir+'/clean0', tpms, imsize_s, pixel_s, phasecenter=phasecenter, **args)
    print("ARGS:",args)
    # im.advice vs au.pickCellSize()   NOTE:pickCellSize()  cannot handle a list of vis
    a,b,c = aU.pickCellSize(tpms, imsize=True, cellstring=True)
    print("pickCellSize(TP)",a,b,c)
    a,b,c = aU.pickCellSize(intms[-1], imsize=True, cellstring=True)
    print("pickCellSize(INT)",a,b,c)

tp2vispl(intms+[tpms],outfig=pdir+'/tp2vispl.png')    


qac_log("PLOT and STATS:")
for idx in range(1):
    im1 = pdir+'/clean0/dirtymap%s.image'       % QAC.label(idx)
    im2 = pdir+'/clean0/dirtymap%s.image.pbcor' % QAC.label(idx)
    qac_plot(im1,mode=1)      # casa based plot w/ colorbar
    qac_stats(im1)            # noise flat
    qac_stats(im2)            # flux flat
    if idx==0: psd.append(im2)
    

tp2vispl(intms+[tpms],outfig=pdir+'/tp2vispl.png')

if Qsdint:
    # not working yet
    qac_log("SDINT")
    sdimage = pdir + '/clean0/dirtymap.image.pbcor'
    sdpsf = pdir + '/clean0/dirtymap.psf'
    qac_sd_int(pdir+'/clean5',sdimage,intms,sdpsf, imsize_s,pixel_s,niter=niter,phasecenter=phasecenter, **args)

qac_log("MAC")
if Qmac:
    sdimage = pdir + '/clean0/dirtymap.image.pbcor'     # RDSF cube
    test = pdir + '/clean6'
    qac_mac(test,sdimage,intms, imsize_s,pixel_s,niter=niter,phasecenter=phasecenter, **args)
    if True:
        qac_fits(sdimage,                      test+'/sky_sdimage_box1.fits',        box=box, stats=True)        
        qac_fits(test+'/int1.image',           test+'/sky_int0.image_box1.fits',     box=box, stats=True, smooth=esmooth)
        qac_fits(test+'/int1.image.pbcor',     test+'/sky_int1.image_box1.fits',     box=box, stats=True, smooth=esmooth)
        qac_fits(test+'/int1.model',           test+'/sky_int1.model_box1.fits',     box=box, stats=True, smooth=esmooth)
        qac_fits(test+'/int2.model',           test+'/sky_int2.model_box1.fits',     box=box, stats=True, smooth=esmooth)
        qac_fits(test+'/int2.image',           test+'/sky_int2.image_box1.fits',     box=box, stats=True, smooth=esmooth)
        qac_fits(test+'/int2.feather',         test+'/sky_int2.feather_box1.fits',   box=box, stats=True, smooth=esmooth)
        qac_fits(test+'/int2.sm',              test+'/sky_int2.sm_box1.fits',        box=box, stats=True, smooth=esmooth)
        qac_fits(test+'/macint.image.pbcor',   test+'/sky_int3.image_box1.fits',     box=box, stats=True, smooth=esmooth)

    imregrid(imagename=otfmap,                    # input SD needs to be regridded, kind of silly, qac_mac could do that
             template=sdimage,
             output=pdir + '/skymodel.otf',
             overwrite=True)
    sdimage = pdir + '/skymodel.otf'
    # make sure this image is RDSF (stokes before freq)

    test = pdir + '/clean7'
    qac_mac(test,sdimage,intms, imsize_s,pixel_s,niter=niter,phasecenter=phasecenter, **args)
    if True:
        qac_fits(sdimage,                      test+'/sky_sdimage_box1.fits',        box=box, stats=True)
        qac_fits(test+'/int1.image',           test+'/sky_int0.image_box1.fits',     box=box, stats=True, smooth=2)
        qac_fits(test+'/int1.image.pbcor',     test+'/sky_int1.image_box1.fits',     box=box, stats=True, smooth=2)
        qac_fits(test+'/int1.model',           test+'/sky_int1.model_box1.fits',     box=box, stats=True, smooth=2)
        qac_fits(test+'/int2.model',           test+'/sky_int2.model_box1.fits',     box=box, stats=True, smooth=2)
        qac_fits(test+'/int2.image',           test+'/sky_int2.image_box1.fits',     box=box, stats=True, smooth=2)
        qac_fits(test+'/int2.feather',         test+'/sky_int2.feather_box1.fits',   box=box, stats=True, smooth=2)
        qac_fits(test+'/int2.sm',              test+'/sky_int2.sm_box1.fits',        box=box, stats=True, smooth=2)
        qac_fits(test+'/macint.image.pbcor',   test+'/sky_int3.image_box1.fits',     box=box, stats=True, smooth=2)

qac_log("CLEAN with TP2VIS")
if False:
    qac_clean(pdir+'/clean3',tpms,intms,imsize_s,pixel_s,niter=niter,phasecenter=phasecenter,do_int=True,do_concat=False, **args)
    qac_tweak(pdir+'/clean3','int',  niter)
    qac_tweak(pdir+'/clean3','tpint',niter)
else:
    qac_clean(pdir+'/clean3',tpms,intms,imsize_s,pixel_s,niter=niter,phasecenter=phasecenter,do_int=True,do_concat=False, **args)
    qac_tweak(pdir+'/clean3','tpint',niter)
    
psd.append(pdir+'/clean3/tpint.image.pbcor')
psd.append(pdir+'/clean3/skymodel.smooth.image')        


if Qhybrid:
    # this is a big cheat. The niter=0 solution will be pretty good. After that it's downhill.
    qac_clean(pdir+'/clean4',tpms,intms,imsize_s,pixel_s,niter=niter,phasecenter=phasecenter,do_int=True,do_concat=False,startmodel=startmodel)
    qac_tweak(pdir+'/clean4','int',niter)
    qac_tweak(pdir+'/clean4','tpint',niter)

if False:
    # clean instead of tclean()
    qac_clean(pdir+'/clean5',tpms,intms,imsize_s,pixel_s,niter=niter,phasecenter=phasecenter,do_int=True,do_concat=False,t=True)
    qac_tweak(pdir+'/clean5','int',niter)
    qac_tweak(pdir+'/clean5','tpint',niter)

qac_log("OTF")
# create an OTF TP map using a [12m] dish
qac_tp_otf(pdir+'/clean3', startmodel, dish, template=pdir+'/clean3/tpint.image')
if Qhybrid:
    qac_tp_otf(pdir+'/clean4', startmodel, dish,template=pdir+'/clean4/tpint.image')

if Qfeather:
    qac_log("FEATHER")
    # combine TP + INT using feather and ssc, for all niter's
    for idx in range(len(niter)):
        qac_feather(pdir+'/clean3',             niteridx=idx, name="int")
        qac_ssc    (pdir+'/clean3',             niteridx=idx, name="int")
        qac_smooth (pdir+'/clean3', startmodel, niteridx=idx, name="int")
        if Qhybrid:
            qac_feather(pdir+'/clean4',             niteridx=idx, name="int")
            qac_ssc    (pdir+'/clean4',             niteridx=idx, name="int")
            qac_smooth (pdir+'/clean4', startmodel, niteridx=idx, name="int")

for idx in range(len(niter)):
    qac_smooth (pdir+'/clean3', startmodel, niteridx=idx, name="tpint")


qac_log("REGRESSION")

qac_stats(model)
qac_stats(pdir+'/clean0/dirtymap.image')
qac_stats(pdir+'/clean0/dirtymap.image.pbcor')
qac_stats(pdir+'/clean3/int.image')

qac_stats(pdir+'/clean3/int.image.pbcor')
qac_stats(pdir+'/clean3/int_3.image.pbcor')

qac_stats(pdir+'/clean3/tpint.image')
qac_stats(pdir+'/clean3/tpint_2.image')
qac_stats(pdir+'/clean3/tpint_3.image')

qac_stats(pdir+'/clean3/tpint.image.pbcor')
qac_stats(pdir+'/clean3/tpint_2.image.pbcor')
qac_stats(pdir+'/clean3/tpint_3.image.pbcor')

qac_stats(pdir+'/clean3/tpint_2.tweak.image.pbcor')
qac_stats(pdir+'/clean3/tpint_3.tweak.image.pbcor')

qac_stats(pdir+'/clean3/feather.image.pbcor')
qac_stats(pdir+'/clean3/feather_2.image.pbcor')
qac_stats(pdir+'/clean3/feather_3.image.pbcor')

qac_stats(pdir+'/clean3/ssc.image')
qac_stats(pdir+'/clean3/ssc_2.image')
qac_stats(pdir+'/clean3/ssc_3.image')

qac_stats(pdir+'/clean3/skymodel.smooth.image')
qac_stats(pdir+'/clean3/skymodel_2.smooth.image')
qac_stats(pdir+'/clean3/skymodel_3.smooth.image')

qac_stats(pdir+'/clean3/otf.image')
qac_stats(pdir+'/clean3/otf.image.pbcor')



if Qfeather and Qmac and Qhybrid:
    qac_log("PLOT_GRID plot2/3")    
    a1 = pdir+'/clean1/dirtymap.image'       # INT
    a2 = pdir+'/clean1/dirtymap_2.image'

    a3 = pdir+'/clean2/dirtymap.image'       # INT w/ startmodel
    a4 = pdir+'/clean2/dirtymap_2.image'

    a31 = pdir+'/clean3/int.image'           # INT/TPINT
    a32 = pdir+'/clean3/int_3.image'
    a33 = pdir+'/clean3/tpint.image'
    a34 = pdir+'/clean3/tpint_3.image'
    a35 = pdir+'/clean3/feather.image'    
    a36 = pdir+'/clean3/feather_3.image'
    a37 = pdir+'/clean3/ssc.image'    
    a38 = pdir+'/clean3/ssc_3.image'

    a5 = []
    a5.append(pdir+'/clean3/int.image')
    a5.append(pdir+'/clean3/int_2.image')
    a5.append(pdir+'/clean3/int_3.image')
    a5.append(pdir+'/clean3/tpint.image')
    a5.append(pdir+'/clean3/tpint_2.image')
    a5.append(pdir+'/clean3/tpint_3.image')
    a5.append(pdir+'/clean3/feather.image' )   
    a5.append(pdir+'/clean3/feather_2.image')
    a5.append(pdir+'/clean3/feather_3.image')
    a5.append(pdir+'/clean3/ssc.image')
    a5.append(pdir+'/clean3/ssc_2.image')
    a5.append(pdir+'/clean3/ssc_3.image')

    a6 = []
    a6.append(pdir+'/clean3/int_3.image.pbcor')
    a6.append(pdir+'/clean3/skymodel.smooth.image')
    a6.append(pdir+'/clean3/tpint_3.image.pbcor')
    a6.append(pdir+'/clean3/skymodel.smooth.image')
    a6.append(pdir+'/clean3/tpint_3.tweak.image.pbcor')
    a6.append(pdir+'/clean3/skymodel.smooth.image')
    a6.append(pdir+'/clean3/feather_3.image.pbcor')
    a6.append(pdir+'/clean3/skymodel.smooth.image')
    a6.append(pdir+'/clean3/ssc_3.image')
    a6.append(pdir+'/clean3/skymodel.smooth.image')
    
    
    a41 = pdir+'/clean4/int.image'           # INT/TPINT w/ startmodel
    a42 = pdir+'/clean4/int_3.image'
    a43 = pdir+'/clean4/tpint.image'
    a44 = pdir+'/clean4/tpint_3.image'


    #qac_tp_otf(test+'/clean1', startmodel, 12.0)

    # nitering
    qac_plot_grid([a31,a32,a41,a42,a31,a32,a33,a34],diff=10, plot=pdir+'/plot1.cmp.png')
    #
    qac_plot_grid([a31,a41,a32,a42],diff=1,  plot=pdir+'/plot2.cmp.png')
    qac_plot_grid([a33,a43,a34,a44],diff=10, plot=pdir+'/plot3.cmp.png')
    #
    qac_plot_grid(a5, ncol=3, diff=0, plot=pdir+'/plot5.cmp.png')

    qac_plot_grid(a6, diff=10, plot=pdir+'/plot6.cmp.png')
    
    

    # qac_plot_grid([a1,a31,a2,a32,a3,a41,a4,a42],diff=1)     these are all 0, as they should be



if False:
    qac_log("PLOT_GRID plot1")
    a1 = pdir+'/clean1/dirtymap.image'
    a2 = pdir+'/clean1/dirtymap.image.pbcor'
    a3 = pdir+'/clean1/skymodel.smooth.image'
    a4 = pdir+'/clean1/feather.image/'
    a5 = pdir+'/clean1/ssc.image/'
    a6 = pdir+'/test1-alma.aca.cycle5.skymodel/'
    a7 = pdir+'/clean3/tpint_2.image'
    a8 = pdir+'/clean3/tpint_2.tweak.image'
    qac_plot_grid([a1,a3,a4,a5,a7,a8],plot=pdir+'/plot1.cmp.png')

# PSD plot comparison of the images we accumulated in psd[]
if len(psd) > 0:
    qac_log("QAC_PSD")
    p2=qac_psd(psd, plot=pdir+'/psd.png')

if Qexport:
    os.chdir(pdir)
    qac_project('export')
    qac_fits('clean3/skymodel_3.smooth.image',         'export/sky_model_box1.fits',   box=box, stats=True, smooth=esmooth)
    qac_fits('clean3/int_3.image.pbcor',               'export/sky_int_box1.fits',     box=box, stats=True, smooth=esmooth)
    qac_fits('clean3/tpint_3.image.pbcor',             'export/sky_tpint_box1.fits',   box=box, stats=True, smooth=esmooth)
    qac_fits('clean3/tpint_3.tweak.image.pbcor',       'export/sky_tweak_box1.fits',   box=box, stats=True, smooth=esmooth)
    qac_fits('clean3/feather_3.image.pbcor',           'export/sky_feather_box1.fits', box=box, stats=True, smooth=esmooth)
    qac_fits('clean3/ssc_3.image',                     'export/sky_ssc_box1.fits',     box=box, stats=True, smooth=esmooth)
    qac_fits('clean4/int.image.pbcor',                 'export/sky_cheat1_box1.fits',  box=box, stats=True, smooth=esmooth)
    qac_fits('clean4/tpint.image.pbcor',               'export/sky_cheat2_box1.fits',  box=box, stats=True, smooth=esmooth)
    qac_fits('clean4/feather.image.pbcor',             'export/sky_cheat3_box1.fits',  box=box, stats=True, smooth=esmooth)
    qac_fits('clean4/ssc.image',                       'export/sky_cheat4_box1.fits',  box=box, stats=True, smooth=esmooth)
    qac_fits('clean7/int1.image.pbcor',                'export/sky_mac1_box1.fits',    box=box, stats=True, smooth=esmooth)
    qac_fits('clean7/macint.image.pbcor',              'export/sky_mac3_box1.fits',    box=box, stats=True, smooth=esmooth)
    


qac_log("DONE!")
qac_end()
