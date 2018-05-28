# -*- python -*-
#
#  CAS-11271    source amplitudes appear wrong with tclean in mosaic mode when using VI2
#
#  based on sky0
#
#  run this script twice, once with setting the VI1 environment variable set to 1,
#  and once not set at all. VI1 will cause CASA to to not use new features.
#
#  Uses ~340MB 
#


test         = 'cas_11271'                          # name of directory within which everything will reside
model        = 'skymodel.fits'                      # this has phasecenter with dec=-30 for ALMA sims
phasecenter  = 'J2000 180.0deg -30.0deg'            # where we want this model to be on the sky

# pick the piece of the model to image, and at what pixel size
# natively this model is 4096 pixels at 0.05"
# @todo qac_tp_vis handles this differently from simobserve()
imsize_m     = 4096
pixel_m      = 0.05
pixel_m      = 0.02

# pick the sky imaging parameters (for tclean)
# The product of these typically will be the same as that of the model (but don't need to)
# pick the pixel_s based on the largest array configuration (see below) choosen
imsize_s     = 256
pixel_s      = 0.8

# pick a few niter values for tclean to check flux convergence 
niter        = [0]

# pick which ALMA configurations you want (0=7m ACA , 1,2,3...=12m ALMA)
cfg          = [0,1]
cfg          = [1]

# integration times
times        = [2, 1]     # 2 hrs in 1 min integrations
times        = [1, 2]     # 1 hrs in 2 min integrations

# single pointing?  Set grid to a positive arcsec grid spacing if the field needs to be covered
#                  ALMA normally uses lambda/2D   hexgrid is Lambda/sqrt(3)D
grid         = 30
#grid         = 0

#
mosaic       = 1
#mosaic       = 0

# scaling factors
wfactor      = 0.01

# the tp2vis/qac fix on POINTING (1 means no POINTING table)
fix          = 1
#fix          = 0

# for simulation we need concat = False instead of the default True, tclean() will crash otherwise
do_concat       = False
#do_concat       = True

# -- do not change parameters below this ---
import sys
for arg in qac_argv(sys.argv):
    exec(arg)

# derived parameters
ptg = test + '.ptg'              # pointing mosaic for the ptg

# report, add Dtime
qac_begin(test,False)
qac_log("REPORT")
qac_version()
tp2vis_version()

p = qac_im_ptg(phasecenter,imsize_m,pixel_m,grid,rect=True,outfile=ptg)

qac_project(test)    

qac_log("TP2VIS:")
tpms0 = qac_tp_vis(test+'/tp0',model,ptg,pixel_m,phasecenter=phasecenter,deconv=False,fix=0)
tpms1 = qac_tp_vis(test+'/tp1',model,ptg,pixel_m,phasecenter=phasecenter,deconv=False,fix=1)

qac_log("TP2VISWT:")
tp2viswt(tpms0,wfactor,'multiply')
tp2viswt(tpms1,wfactor,'multiply')

qac_log("CLEAN1:")
line = {}
if mosaic == 0:
    line['gridder']     =  'standard'      # 'standard' or 'mosaic' (default)
qac_clean1(test+'/clean0', tpms0, imsize_s, pixel_s, phasecenter=phasecenter, niter=niter, **line)
qac_clean1(test+'/clean1', tpms1, imsize_s, pixel_s, phasecenter=phasecenter, niter=niter, **line)

qac_log("PLOT and STATS:")
for idx in range(len(niter)):
    im1 = test+'/clean0/dirtymap%s.image'       % QAC.label(idx)
    im2 = test+'/clean0/dirtymap%s.image.pbcor' % QAC.label(idx)
    im3 = test+'/clean1/dirtymap%s.image'       % QAC.label(idx)
    im4 = test+'/clean1/dirtymap%s.image.pbcor' % QAC.label(idx)
    qac_plot(im2,mode=1)      # casa based plot w/ colorbar
    qac_stats(im2)            # noise flat
    qac_plot(im4,mode=1)      # casa based plot w/ colorbar
    qac_stats(im4)            # noise flat

if len(cfg) > 0:
    # create an MS based on a model and antenna configuration for ACA/ALMA
    qac_log("ALMA 7m/12m")
    ms1={}
    for c in cfg:
        ms1[c] = qac_alma(test,model,imsize_m,pixel_m,cycle=5,cfg=c,ptg=ptg, phasecenter=phasecenter, times=times, fix=fix)
    intms = ms1.values()

    tp2vispl(intms+[tpms0],outfig=test+'/tp2vispl.png')

    # JD clean for tp2vis
    qac_log("CLEAN with TP2VIS")
    try:
        qac_clean(test+'/clean3',tpms0,intms,imsize_s,pixel_s,niter=niter,phasecenter=phasecenter,do_int=True,do_concat=do_concat,**line)
    except:
        print("QAC_CLEAN clean3 failed")
    try:
        qac_clean(test+'/clean4',tpms1,intms,imsize_s,pixel_s,niter=niter,phasecenter=phasecenter,do_int=True,do_concat=do_concat,**line)
    except:
        print("QAC_CLEAN clean4 failed")        
    for idx in range(len(niter)):
        im1 = test+'/clean3/int%s.image'         % QAC.label(idx)
        im2 = test+'/clean3/int%s.image.pbcor'   % QAC.label(idx)
        im3 = test+'/clean3/tpint%s.image'       % QAC.label(idx)
        im4 = test+'/clean3/tpint%s.image.pbcor' % QAC.label(idx)
        qac_plot(im2,mode=1)      # casa based plot w/ colorbar
        qac_plot(im4,mode=1)      # casa based plot w/ colorbar
        qac_stats(im2)            # noise flat
        qac_stats(im4)            # noise flat
        im5 = test+'/clean4/int%s.image'         % QAC.label(idx)
        im6 = test+'/clean4/int%s.image.pbcor'   % QAC.label(idx)
        im7 = test+'/clean4/tpint%s.image'       % QAC.label(idx)
        im8 = test+'/clean4/tpint%s.image.pbcor' % QAC.label(idx)
        qac_plot(im6,mode=1)      # casa based plot w/ colorbar
        qac_plot(im8,mode=1)      # casa based plot w/ colorbar
        qac_stats(im6)            # noise flat
        qac_stats(im8)            # noise flat

    qac_stats(model)
else:
    qac_log("no INT work to be done")

qac_log("DONE!")
qac_end()

