# -*- python -*-
#
#  Typical usage (see also Makefile)
#      casa -c sky3.py 
#
#  Play with the skymodel 
#     - one or full pointing set
#     - options for tp2vis, feather, ssc
#
#  Reminder: at 115 GHz we have:
#      12m PB is 50" (FWHM)   [FWHM" ~ 600/DishDiam]
#       7m PB is 85"
#

pdir         = 'sky1'                               # name of directory within which everything will reside
model        = 'skymodel.fits'                      # this has phasecenter with dec=-30 for ALMA sims
phasecenter  = 'J2000 180.0deg -30.0deg'            # where we want this model to be on the sky

# pick the piece of the model to image, and at what pixel size
# natively this model is 4096 pixels at 0.05"
imsize_m     = 4096
pixel_m      = 0.05

# pick the sky imaging parameters (for tclean)
# The product of these typically will be the same as that of the model (but don't need to)
# pick the pixel_s based on the largest array configuration (cfg[], see below) choosen
imsize_s     = 256
pixel_s      = 0.8

# number of TP cycles
nvgrp        = 4

# pick a few niter values for tclean to check flux convergence 
niter        = [0,500,1000,2000]
niter        = [0,1000,4000]


# pick which ALMA configurations you want (0=7m ACA , 1,2,3...=12m ALMA)
#cfg          = [0,1,2,3,4,5,6,7,8,9,10]
cfg          = [0,1,2,3]
cfg          = [1]
times        = [2, 1]     # 2 hrs in 1 min integrations

# TP dish size in m; uvmax will be taken as 5/6 of this
# @todo   don't change this
dish         = 12.0  

# single pointing?  Set grid to a positive arcsec grid spacing if the field needs to be covered
#                   ALMA normally uses lambda/2D   hexgrid is Lambda/sqrt(3)D
grid         = 30       # this can be pointings good for small dish nyquist


# OTF: if selected, tp2vis will get an OTF, instead of the model jy/pixel map
otf          = 0

# advanced features
VP           = 0
SCHWAB       = 0

# scaling factors
wfactor      = 0.01
afactor      = 1      # not implemented yet

# -- do not change parameters below this ---
import sys
for arg in qac_argv(sys.argv):
    exec(arg)

# derived parameters
ptg  = pdir + '.ptg'              # pointing mosaic for the ptg
test = pdir                       # compat

# report, add Dtime
qac_begin(pdir,False)
qac_project(pdir)
qac_log("REPORT")
qac_version()
tp2vis_version()


if grid > 0:
    # create a mosaic of pointings 
    p = qac_im_ptg(phasecenter,imsize_m,pixel_m,grid,rect=True,outfile=ptg)
else:
    # create a single pointing 
    qac_ptg(phasecenter,ptg)
    p = [phasecenter]

qac_log("TP2VIS")

if True:
    qac_tpdish('ALMATP', dish)
    qac_tpdish('VIRTUAL',dish)
    qac_vp(VP,SCHWAB)
    
maxuv = 5.0*dish/6.0     

if otf == 0:
    tpms = qac_tp_vis(pdir,model,ptg,phasecenter=phasecenter,deconv=False,maxuv=maxuv,nvgrp=nvgrp,fix=0)
else:
    tp_beam = 56.7     # @todo
    beam = '%sarcsec' % tp_beam
    otf = model.replace('.fits','.otf')
    print("Creating %s" % otf)
    imsmooth(model,'gaussian',beam,beam,pa='0deg',outfile=otf,overwrite=True)
    tpms = qac_tp_vis(test,otf,ptg,phasecenter=phasecenter,deconv=True,maxuv=maxuv,nvgrp=nvgrp,fix=0)    

qac_log("CLEAN1:")
tp2viswt(tpms,wfactor,'multiply')
line = {'deconvolver' : 'hogbom'}
qac_clean1(test+'/clean0', tpms, imsize_s, pixel_s, phasecenter=phasecenter, niter=niter, **line)

qac_log("PLOT and STATS:")
for idx in range(len(niter)):
    im1 = test+'/clean0/dirtymap%s.image'       % QAC.label(idx)
    im2 = test+'/clean0/dirtymap%s.image.pbcor' % QAC.label(idx)
    qac_plot(im1,mode=1)      # casa based plot w/ colorbar
    qac_stats(im1)            # noise flat
    qac_stats(im2)            # flux flat

if len(cfg) > 0:
    # create a series of MS based on a model and antenna configuration for different ACA/ALMA confirgurations
    qac_log("ALMA 7m/12m")
    ms1={}
    for c in cfg:
        ms1[c] = qac_alma(test,model,imsize_m,pixel_m,cycle=7,cfg=c,ptg=ptg, phasecenter=phasecenter, times=times)
    # startmodel for later
    startmodel = ms1[cfg[0]].replace('.ms','.skymodel')

    # find out which MS we got for the INT, or use intms = ms1.values()
    intms = ms1.values()

    tp2vispl(intms+[tpms],outfig=test+'/tp2vispl.png')



    # JD clean for tp2vis
    qac_log("CLEAN with TP2VIS")
    if False:
        qac_clean(test+'/clean3',tpms,intms,imsize_s,pixel_s,niter=niter,phasecenter=phasecenter,do_int=True,do_concat=False)
        qac_tweak(test+'/clean3','int',  niter)
        qac_tweak(test+'/clean3','tpint',niter)
    else:
        qac_clean(test+'/clean3',tpms,intms,imsize_s,pixel_s,niter=niter,phasecenter=phasecenter,do_int=True,do_concat=False)
        qac_tweak(test+'/clean3','tpint',niter)


    if False:
        qac_clean(test+'/clean4',tpms,intms,imsize_s,pixel_s,niter=niter,phasecenter=phasecenter,do_int=True,do_concat=False,startmodel=startmodel)
        qac_tweak(test+'/clean4','int',niter)
        qac_tweak(test+'/clean4','tpint',niter)

    if False:
        # clean instead of tclean()
        qac_clean(test+'/clean5',tpms,intms,imsize_s,pixel_s,niter=niter,phasecenter=phasecenter,do_int=True,do_concat=False,t=True)
        qac_tweak(test+'/clean5','int',niter)
        qac_tweak(test+'/clean5','tpint',niter)



    qac_log("OTF")
    # create an OTF TP map using a [12m] dish
    qac_tp_otf(test+'/clean3', startmodel, dish, template=test+'/clean3/tpint.image')
    if False:
        qac_tp_otf(test+'/clean4', startmodel, dish,template=test+'/clean4/tpint.image')

    if False:
        qac_log("FEATHER")
        # combine TP + INT using feather and ssc, for all niter's
        for idx in range(len(niter)):
            qac_feather(test+'/clean3',             niteridx=idx, name="int")
            qac_ssc    (test+'/clean3',             niteridx=idx, name="int")
            qac_smooth (test+'/clean3', startmodel, niteridx=idx, name="int")
            if False:
                qac_feather(test+'/clean4',             niteridx=idx, name="int")
                qac_ssc    (test+'/clean4',             niteridx=idx, name="int")
                qac_smooth (test+'/clean4', startmodel, niteridx=idx, name="int")

    for idx in range(len(niter)):
        qac_smooth (test+'/clean3', startmodel, niteridx=idx, name="tpint")


    # the real flux
    qac_stats(model)

    qac_log("REGRESSION")

    qac_stats(model)
    qac_stats(test+'/clean0/dirtymap.image')
    qac_stats(test+'/clean0/dirtymap.image.pbcor')
    qac_stats(test+'/clean3/int.image')
    qac_stats(test+'/clean3/tpint.image')
    qac_stats(test+'/clean3/tpint_2.image')
    qac_stats(test+'/clean3/tpint_3.image')
    qac_stats(test+'/clean3/tpint.image.pbcor')
    qac_stats(test+'/clean3/tpint_2.image.pbcor')
    qac_stats(test+'/clean3/tpint_3.image.pbcor')
    qac_stats(test+'/clean3/skymodel.smooth.image')
    qac_stats(test+'/clean3/skymodel_2.smooth.image')
    qac_stats(test+'/clean3/skymodel_3.smooth.image')
    qac_stats(test+'/clean3/otf.image')
    qac_stats(test+'/clean3/otf.image.pbcor')



    if False:
        qac_log("PLOT_GRID plot2/3")    
        a1 = test+'/clean1/dirtymap.image'       # INT
        a2 = test+'/clean1/dirtymap_2.image'

        a3 = test+'/clean2/dirtymap.image'       # INT w/ startmodel
        a4 = test+'/clean2/dirtymap_2.image'

        a31 = test+'/clean3/int.image'           # INT/TPINT
        a32 = test+'/clean3/int_2.image'
        a33 = test+'/clean3/tpint.image'
        a34 = test+'/clean3/tpint_2.image'

        a41 = test+'/clean4/int.image'           # INT/TPINT w/ startmodel
        a42 = test+'/clean4/int_2.image'
        a43 = test+'/clean4/tpint.image'
        a44 = test+'/clean4/tpint_2.image'


        qac_tp_otf(test+'/clean1', startmodel, 12.0)

        # nitering
        qac_plot_grid([a31,a32,a41,a42,a31,a32,a33,a34],diff=10, plot=test+'/plot1.cmp.png')
        #
        qac_plot_grid([a31,a41,a32,a42],diff=1,  plot=test+'/plot2.cmp.png')
        qac_plot_grid([a33,a43,a34,a44],diff=10, plot=test+'/plot3.cmp.png')

        # qac_plot_grid([a1,a31,a2,a32,a3,a41,a4,a42],diff=1)     these are all 0, as they should be



    if False:
        qac_log("PLOT_GRID plot1")
        a1 = test+'/clean1/dirtymap.image'
        a2 = test+'/clean1/dirtymap.image.pbcor'
        a3 = test+'/clean1/skymodel.smooth.image'
        a4 = test+'/clean1/feather.image/'
        a5 = test+'/clean1/ssc.image/'
        a6 = test+'/test1-alma.aca.cycle5.skymodel/'
        a7 = test+'/clean3/tpint_2.image'
        a8 = test+'/clean3/tpint_2.tweak.image'
        qac_plot_grid([a1,a3,a4,a5,a7,a8],plot=test+'/plot1.cmp.png')

else:
    qac_log("no INT work to be done")

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
