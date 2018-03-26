# -*- python -*-
#
#  Play with the skymodel for SD2018
#     - one or full pointing set
#     - options for tp2vis, feather, ssc
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

test         = 'sky1'                               # name of directory within which everything will reside
model        = 'skymodel.fits'                      # this has phasecenter with dec=-30 for ALMA sims
phasecenter  = 'J2000 180.0deg -30.0deg'            # where we want this model to be on the sky

# pick the piece of the model to image, and at what pixel size
# natively this model is 4096 pixels at 0.05"
imsize_m     = 4096
pixel_m      = 0.05

# pick the sky imaging parameters (for tclean) 
imsize_s     = 256
pixel_s      = 0.8

# tp stuff
nvgrp        = 4

# pick a few niter values for tclean to check flux convergence 
niter        = [0,500,1000,2000]
#niter        = [0,100]
#niter        = [0,100,1000]
niter        = [0,1000]

# pick which ALMA configurations you want (0=7m ACA , 1,2,3...=12m ALMA)
#cfg          = [0,1,2,3,4,5,6,7,8,9,10]
cfg          = [0,1,2,3]

# also do a run with a startmodel?
# startmodel   = 0

# single pointing?  Set grid to a positive arcsec grid spacing if the field needs to be covered
#                   ALMA normally uses lambda/2D
grid         = 30
#grid         = 12.5    # for the trial 25m dish
#grid         = 50.0
#grid         = 0

# dish size in m; uvmax will be taken as 5/6 of this
dish         = 12.0
#dish         = 25.0

# -- do not change parameters below this ---
import sys
for arg in qac_argv(sys.argv):
    exec(arg)

ptg = test + '.ptg'              # pointing mosaic for the ptg
    

# report, add Dtime
qac_begin(test)
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


qac_log("TP2VIS")

# create TP MS  - this starts a new clean project
if True:
    qac_tpdish('ALMATP',dish)    # e.g. 25m
    qac_tpdish('VIRTUAL',dish)   # e.g. 12m
tpms = qac_tp_vis(test,model,ptg,imsize_s,pixel_s,phasecenter=phasecenter,deconv=False,maxuv=5*dish/6.0,nvgrp=nvgrp,fix=0)
qac_clean1(test + '/clean0', tpms, imsize_s, pixel_s, phasecenter=phasecenter)

# create an MS based on a model and antenna configuration for ACA/ALMA
qac_log("ALMA 7m/12m")
ms1={}
for c in cfg:
    ms1[c] = qac_alma(test,model,imsize_m,pixel_m,cycle=5,cfg=c,ptg=ptg, phasecenter=phasecenter)
# startmodel for later
startmodel = ms1[cfg[0]].replace('.ms','.skymodel')

# find out which MS we got for the INT, or use intms = ms1.values()
intms = ms1.values()

tp2vispl(intms+[tpms],outfig=test+'/tp2vispl.png')
    

# JD clean for tp2vis
qac_log("CLEAN with TP2VIS")
qac_clean(test+'/clean3',tpms,intms,imsize_s,pixel_s,niter=niter,phasecenter=phasecenter,do_int=True,do_concat=False)
for idx in range(1,len(niter)):
    inamed = test+'/clean3/tpint'
    inamec = test+'/clean3/tpint_%d' % (idx+1)
    tp2vistweak(inamed,inamec)
    # really don't need these, check with clean1
    inamed = test+'/clean3/int'
    inamec = test+'/clean3/int_%d' % (idx+1)
    tp2vistweak(inamed,inamec)
    

qac_log("CLEAN")
# clean just interferometric map a bit
qac_clean1(test+'/clean1',intms,  imsize_s, pixel_s, phasecenter=phasecenter,niter=niter)
#qac_clean1(test+'/clean2',intms,  imsize_s, pixel_s, phasecenter=phasecenter,niter=niter,startmodel=startmodel)

qac_log("OTF")
# create an OTF TP map using a 12m dish
qac_tp_otf(test+'/clean1', startmodel, 12.0)
#qac_tp_otf(test+'/clean2', startmodel, 12.0)

qac_log("FEATHER")
# combine TP + INT using feather and ssc, for all niter's
for idx in range(len(niter)):
    qac_feather(test+'/clean1', niteridx=idx)
    qac_ssc(test+'/clean1', niteridx=idx)
    qac_smooth (test+'/clean1', startmodel, niteridx=idx)
    #qac_feather(test+'/clean2', niteridx=idx)
    #qac_smooth (test+'/clean2', startmodel, niteridx=idx)
# the real flux
qac_stats(model)

qac_log("REGRESSION")

qac_stats(model)
qac_stats(test+'/clean3/tpint.image')
qac_stats(test+'/clean1/dirtymap.image.pbcor')
qac_stats(test+'/clean1/dirtymap_2.image.pbcor')
qac_stats(test+'/clean1/dirtymap_3.image.pbcor')
qac_stats(test+'/clean1/dirtymap_4.image.pbcor')
qac_stats(test+'/clean1/feather.image.pbcor')
qac_stats(test+'/clean1/feather_2.image.pbcor')
qac_stats(test+'/clean1/feather_3.image.pbcor')
qac_stats(test+'/clean1/feather_4.image.pbcor')
qac_stats(test+'/clean2/dirtymap.image.pbcor')
qac_stats(test+'/clean2/dirtymap_2.image.pbcor')
qac_stats(test+'/clean2/dirtymap_3.image.pbcor')
qac_stats(test+'/clean2/dirtymap_4.image.pbcor')
qac_stats(test+'/clean2/feather.image.pbcor')
qac_stats(test+'/clean2/feather_2.image.pbcor')
qac_stats(test+'/clean2/feather_3.image.pbcor')
qac_stats(test+'/clean2/feather_4.image.pbcor')

qac_stats(test+'/clean1/skymodel.smooth.image')

qac_log("DONE!")
qac_end()

if True:
    a1 = test+'/clean1/dirtymap.image'
    a2 = test+'/clean1/dirtymap.image.pbcor'
    a3 = test+'/clean1/skymodel.smooth.image'
    a4 = test+'/clean1/feather.image/'
    a5 = test+'/clean1/ssc.image/'
    a6 = test+'/test1-alma.aca.cycle5.skymodel/'
    a7 = test+'/clean3/tpint_2.image'
    a8 = test+'/clean3/tpint_2.tweak.image'
    qac_plot_grid([a1,a3,a4,a5,a7,a8],plot=test+'/plot1.cmp.png')



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
