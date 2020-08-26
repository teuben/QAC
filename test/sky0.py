# -*- python -*-
#
#  compare fluxes with or without the mosaicing bug in casa 5.1
#  derived from a simplified sky1
#
#  run this script twice, once with setting the VI1 environment variable set to 1,
#  and once not set at all. VI1 will cause CASA to to not use new features.
#

test         = 'sky0'                               # name of directory within which everything will reside
model        = 'skymodel.fits'                      # this has phasecenter with dec=-30 for ALMA sims
phasecenter  = 'J2000 180.0deg -30.0deg'            # where we want this model to be on the sky

# pick the piece of the model to image, and at what pixel size
# natively this model is 4096 pixels at 0.05"
imsize_m     = 4096
pixel_m      = 0.05

# pick the sky imaging parameters (for tclean)
# The product of these typically will be the same as that of the model (but don't need to)
# pick the pixel_s based on the largest array configuration (see below) choosen
imsize_s     = 256
pixel_s      = 0.8

imsize_s     = 1120
pixel_s      = 0.21
box          = '150,150,970,970'

# pick a few niter values for tclean to check flux convergence and be able to tweak
niter        = [0,1000,3000,10000]

# pick which ALMA configurations you want (0=7m ACA , 1,2,3...=12m ALMA)
cfg          = [0,1]
cfg          = [1]
cfg          = [0,1,4]

# integration times
times        = [2, 1]     # 2 hrs in 1 min integrations

# single pointing?  Set grid to a positive arcsec grid spacing if the field needs to be covered
#                  ALMA normally uses lambda/2D   hexgrid is Lambda/sqrt(3)D
grid         = 30

# mosaic mode?
mosaic       = 1
mosaic       = 0

# plotting [min:max] if override autoscaling
vrange       = None

# scaling factors
wfactor      = 0.01

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

qac_project(test)

p = qac_im_ptg(phasecenter,imsize_m,pixel_m,grid,rect=True,outfile=ptg)

qac_log("TP2VIS:")
tpms = qac_tp_vis(test,model,ptg,phasecenter=phasecenter,deconv=False,fix=0)

qac_log("CLEAN1:")
tp2viswt(tpms,wfactor,'multiply')
line = {}
if mosaic == 0:
    line['gridder']     =  'standard'      # 'standard' or 'mosaic' 
qac_clean1(test+'/clean0', tpms, imsize_s, pixel_s, phasecenter=phasecenter, niter=niter, **line)

qac_log("PLOT and STATS:")
for idx in range(len(niter)):
    im1 = test+'/clean0/dirtymap%s.image'       % QAC.label(idx)
    im2 = test+'/clean0/dirtymap%s.image.pbcor' % QAC.label(idx)
    qac_plot(im1,mode=1)      # casa based plot w/ colorbar
    qac_stats(im2)            # noise flat

if len(cfg) > 0:
    # create an MS based on a model and antenna configuration for ACA/ALMA
    qac_log("ALMA 7m/12m")
    ms1={}
    for c in cfg:
        ms1[c] = qac_alma(test,model,imsize_m,pixel_m,cycle=5,cfg=c,ptg=ptg, phasecenter=phasecenter, times=times)
    intms = ms1.values()

    tp2vispl(intms+[tpms],outfig=test+'/tp2vispl.png')

    # JD clean for tp2vis
    qac_log("CLEAN with TP2VIS")
    qac_clean(test+'/clean3',tpms,intms,imsize_s,pixel_s,niter=niter,phasecenter=phasecenter,do_int=False,do_concat=False)    
    #qac_clean(test+'/clean3',tpms,intms,imsize_s,pixel_s,niter=niter,phasecenter=phasecenter,do_int=True,do_concat=False)
    #qac_clean(test+'/clean3',tpms,intms,imsize_s,pixel_s,niter=niter,phasecenter=phasecenter,do_int=True,do_concat=True)
    for idx in range(len(niter)):
        im1 = test+'/clean3/int%s.image'         % QAC.label(idx)
        im2 = test+'/clean3/int%s.image.pbcor'   % QAC.label(idx)
        im3 = test+'/clean3/tpint%s.image'       % QAC.label(idx)
        im4 = test+'/clean3/tpint%s.image.pbcor' % QAC.label(idx)
        if vrange == None:
            qac_plot(im1,mode=1)      # casa based plot w/ colorbar
            qac_plot(im3,mode=1)      # casa based plot w/ colorbar
        else:
            qac_plot(im1,mode=2,range=vrange)
            qac_plot(im3,mode=2,range=vrange)
        qac_stats(im2)            # noise flat
        qac_stats(im4)            # noise flat
        qac_fits(im4,box=box,stats=True)

    qac_stats(model)
else:
    qac_log("no INT work to be done")

qac_log("DONE!")
qac_end()


"""
 Wt  Flux(kJy)
0       -704      0.199  
0.001     11.7    0.208
0.005     61.0    0.247
0.01     121.5    0.296
0.03     352.9    0.488
0.04     462.4
0.06     669.6    0.780
0.08     862.3    0.987
0.2     1761.4    2.15
0.8     2235      5.9
1       2176
2       1762      9.5
10       634.6   14.0
100      129.0   15.7
1000      69.5   15.9
10000     63.5
100000    62.5

"""
