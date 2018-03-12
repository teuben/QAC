#
#
#  Play with the skymodel for SD2018
#     - one or full pointing set
#     - JD/tp2vis , feather, ssc
#
#  Reminders:
#  The 12m PB is 50" (FWHM)   [FWHM" ~ 600/DishDiam]
#       7m PB is 85"
#
#  Timing:
#           38'++
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

# pick a few niter values for tclean to check flux convergence 
niter        = [0,500,1000,2000]
niter        = [0,100]
niter        = [0,100,1000]

# pick which ALMA configurations you want (0=7m ACA , 1,2,3...=12m ALMA)
#cfg          = [0,1,2,3,4,5,6,7,8,9,10]
cfg          = [0,1]

# also do a run with a startmodel?
#startmodel   = 0

# single pointing?  Set grid to a positive arcsec grid spacing if the field needs to be covered
grid         = 25

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
    # create a mosaic of pointings
    qac_im_ptg(phasecenter,imsize_m,pixel_m,grid,outfile=ptg)
    # no support for ptg = 
else:
    # create a single pointing 
    qac_ptg(phasecenter,ptg)
    # ptg = [phasecenter]



# start with clean new project
os.system('rm -rf %s' % test)


# create an MS based on a model and antenna configuration for ACA/ALMA
qac_log("QAC_ALMA")
ms1={}
for c in cfg:
    ms1[c] = qac_alma(test,model,imsize_m,pixel_m,cycle=5,cfg=c,ptg=ptg, phasecenter=phasecenter,niter=-1)
# startmodel (a cheat) for later
startmodel = ms1[0].replace('.ms','.skymodel')

# create TP MS
tpms = qac_tp_vis(test + '/tp2vis',model,ptg,imsize_s,pixel_s,niter=-1,phasecenter=phasecenter,fix=0)



# find out which MS we got for the INT, or use intms = ms1.values()
import glob
intms = glob.glob(test+"/*.ms")
print "MS files found: ",intms

# JD clean for tp2vis
qac_log("CLEAN with TP2VIS")
qac_clean(test+'/jd1',tpms,intms,imsize_s,pixel_s,niter=niter,phasecenter=phasecenter,do_concat=False)
for idx in range(1,len(niter)):
    inamed = test+'/jd1/tpalma'
    inamec = test+'/jd1/tpalma_%d' % (idx+1)
    tp2vistweak(inamed,inamec)

qac_log("CLEAN")
# clean this interferometric map a bit
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
    a1 = 'sky1/clean1/dirtymap.image'
    a2 = 'sky1/clean1/dirtymap.image.pbcor'
    a3 = 'sky1/clean1/skymodel.smooth.image'
    a4 = 'sky1/clean1/feather.image/'
    a5 = 'sky1/clean1/ssc.image/'
    a6 = 'sky1/test1-alma.aca.cycle5.skymodel/'
    qac_plot_grid([a1,a3,a4,a5])



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
