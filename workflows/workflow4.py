#  -*- python -*-
#
# regression test version of workflow4.md
#
# Data needed:    skymodel.fits and skymodel.ptg
#
# Will produce directories test4r (raw pixels based) test4s (OTF style TP)
# and the big one, test4a (all)
#
# Example time:
# CPU times: user 2h 24min 2s, sys: 5min 22s, total: 2h 29min 25s
# Wall time: 1h 15min 11s
#
# The following directories are created:
#   test4r/           using a Jy/pixel deconv=False mapping
#   test4s/           using a Jy/beam  deconv=True mapping
#   test4a/clean1     using the Jy/pixel with alma 7m+12m


# model
skymodel    = 'skymodel.fits'
ptg1        = 'skymodel.ptg'      # our prepared ptg
ptg2        = 'test4-12m.ptg'     # ptg from MS
ptg3        = 'test4-grid.ptg'    # ptg from a grid

phasecenter = 'J2000 12h00m0.000s -30d00m00.000s'

# decimate to a more workable regression (the original is 4096) [pick from: 1, 2, 4]
factor      = 4
#
box1        = '512,512,3584,3584'
box2        = '256,256,1791,1791'
box4        = '128,128,895,895'
# pick the appropriate box 
box         = box4
# TP
tp_beam     = 56.7    # arcsec
tp_scale    = 1.0     # set to a number if you want to scale up/down TP (but not array)

# maxalma is the max configuration number taken in the 12m cfg's
maxalma     = 5

# gridding, using factor
mapsize     = 4096/factor
pixel       = 0.0625*factor     # 0.0625 or 0.075
grid        = 30.0
niter       = 10000
niters1     = [0,1,10,100,1000,10000]      # test4r,test4s
niters2     = [0,1000,3000,6000,10000]     # test4a
niters2     = [0,100,1000]                 # polkadot testing

ptg         = ptg1


#   summary
qac_log("SUMMARY")
qac_version()
qac_summary(skymodel)

if False:
    qac_log("TRIMING MODEL")
    # test4r, test4s : narrow the model down in size
    importfits(skymodel,'skymodel1.im',overwrite=True)
    qac_ingest('skymodel1.im','skymodel2.im')
    qac_stats('skymodel2.im')
    qac_plot('skymodel2.im')

    imsmooth('skymodel2.im','gaussian','1arcsec','1arcsec',pa='0deg',outfile='skymodel2s.im',overwrite=True)
    imhead('skymodel2s.im',mode='put',hdkey='bunit',hdvalue='Jy/beam')     # weird: needed a fix here, but skymodel3s didn't need it
    qac_stats('skymodel2s.im')
    qac_plot('skymodel2s.im')


    qac_tp_vis('test4r','skymodel2.im',ptg,mapsize,pixel,niter=0,phasecenter=phasecenter, deconv=False)
    qac_stats('test4r/dirtymap.image/')
    qac_plot('test4r/dirtymap.image/')

    qac_tp_vis('test4s','skymodel2s.im',ptg,mapsize,pixel,niter=0,phasecenter=phasecenter, deconv=False)
    qac_stats('test4s/dirtymap.image/')
    qac_plot('test4s/dirtymap.image/')

    imrebin('skymodel2.im','skymodel3.im',factor=[factor,factor],overwrite=True)
    qac_stats('skymodel3.im')
    qac_plot('skymodel3.im')
     
    beam = '%sarcsec' % tp_beam
    imsmooth('skymodel3.im','gaussian',beam,beam,pa='0deg',outfile='skymodel3s.im',overwrite=True)
    qac_stats('skymodel3s.im')
    qac_plot('skymodel3s.im')


if False:
    qac_log("CLEANING /pixel and /beam TP")
    # test4r, test4s : convergence of clean?  what's the difference between the /pixel and the /beam TP
    qac_tp_vis('test4r', 'skymodel3.im',ptg,deconv=False)
    qac_clean1('test4r/clean1','test4r/tp.ms',mapsize,pixel,niter=niters1,phasecenter=phasecenter)
    
    for i in range(0,len(niters1)):                     # 71 series
        if i==0:
            iname = 'test4r/clean1/dirtymap.image'
        else:
            iname = 'test4r/clean1/dirtymap_%d.image' % (i+1)
        qac_plot(iname)
        qac_stats(iname)


    qac_tp_vis('test4s', 'skymodel3s.im',ptg)
    qac_clean1('test4s/clean1','test4s/tp.ms',mapsize,pixel,niter=niters1,phasecenter=phasecenter)
    
    for i in range(0,len(niters1)):                     # 72 series
        if i==0:
            iname = 'test4s/clean1/dirtymap.image'
        else:
            iname = 'test4s/clean1/dirtymap_%d.image' % (i+1)
        qac_plot(iname)
        qac_stats(iname)

if True:
    # make sure it's clean, since qac_alma() accumulates
    os.system('rm -rf %s' % 'test4a')
    skymodel = 'skymodel3.im'

    # 7m data
    qac_log("ALMA 7m")
    qac_alma('test4a',skymodel, mapsize,pixel,cfg=0, phasecenter=phasecenter,niter=0)
    qac_stats('test4a/dirtymap.image')

    # 12m data
    qac_log("ALMA 12m")
    for cfg in range(0,maxalma):
        qac_alma('test4a',skymodel,cfg=cfg)

    # look at 12m pointings from the 1st 12m cfg
    os.system('cp test4a/test4a.alma.cycle5.1.ptg.txt %s' % ptg2)

    # scale the TP for just tp2vis so we can check what can go wrong if tp_scale not 1
    immath([skymodel],'evalexpr','test4a/skymodel3_scaled.im','IM0*%g' % tp_scale)
    qac_tp_vis('test4a/tp','test4a/skymodel3_scaled.im',ptg,deconv=False,fix=0)
    #qac_stats('test4a/tp/dirtymap.image')
    #qac_plot('test4a/tp/dirtymap.image')

# find all the MS files needed for tclean    
import glob
ms0 = 'test4a/tp/tp.ms'
ms1 = glob.glob('test4a/*aca*.ms')
ms2 = glob.glob('test4a/*alma*.ms')

tp2vispl([ms0]+ms1+ms2)

# the ugly bug in tclean() is creeping up again, for *all* sim data we need do_concat=False

qac_log("MAPPING")

qac_clean('test4a/clean1', ms0,ms1+ms2, mapsize,pixel,niter=niters2,phasecenter=phasecenter,do_alma=True, do_concat=False)

# do the 7m/12, : odd, they don't converge, all the same
for i in range(0,len(niters2)): 
    if i==0:
        iname = 'test4a/clean1/alma.image'
    else:
        iname = 'test4a/clean1/alma_%d.image' % (i+1)
    qac_plot(iname)
    qac_stats(iname)

#  TP+7m/12m:  creates a polka dot pattern, also odd
for i in range(0,len(niters2)): 
    if i==0:
        iname = 'test4a/clean1/tpalma.image'
    else:
        iname = 'test4a/clean1/tpalma_%d.image' % (i+1)
    qac_plot(iname)
    qac_stats(iname)

for i in range(1,len(niters2)): 
    inamed = 'test4a/clean1/tpalma'
    inamec = 'test4a/clean1/tpalma_%d' % (i+1)
    tp2vistweak(inamed,inamec)
    iname = 'test4a/clean1/tpalma_%d.tweak.image' % (i+1)
    qac_plot(iname)
    qac_stats(iname)

qac_beam('test4a/clean1/tpalma.psf',plot='test4a/clean1/qac_beam.png',normalized=True)


if True:
    qac_log("REGRESSION full map")

    # full map
    qac_stats('skymodel1.im')
    qac_stats('skymodel2.im')
    qac_stats('skymodel2s.im')
    qac_stats('test4r/dirtymap.image/')
    qac_stats('test4s/dirtymap.image/')
    qac_stats('skymodel3.im')
    qac_stats('skymodel3s.im')
    
    qac_log("REGRESSION minus edges ")

    # box excluding edges
    qac_stats('skymodel3.im',                box=box)
    qac_stats('skymodel3s.im',               box=box)
    qac_stats('test4r/dirtymap.image',       box=box)
    qac_stats('test4s/dirtymap.image',       box=box)
    
    qac_stats('test71/dirtymap.image',       box=box)
    qac_stats('test71a/dirtymap.image',      box=box)
    qac_stats('test71b/dirtymap.image',      box=box)
    qac_stats('test71c/dirtymap.image',      box=box)
    qac_stats('test71d/dirtymap.image',      box=box)
    qac_stats('test71e/dirtymap.image',      box=box)
    qac_stats('test72/dirtymap.image',       box=box)
    qac_stats('test72a/dirtymap.image',      box=box)
    qac_stats('test72b/dirtymap.image',      box=box)
    qac_stats('test72c/dirtymap.image',      box=box)
    qac_stats('test72d/dirtymap.image',      box=box)
    qac_stats('test72e/dirtymap.image',      box=box)
    
    qac_stats('map123a/dirtymap.image',      box=box)
    qac_stats('map123b/alma.image',          box=box)
    qac_stats('map123b/tpalma.image',        box=box)
    qac_stats('map123b1/alma.image',         box=box)
    qac_stats('map123b1/tpalma.image',       box=box)
    qac_stats('map123b1/tpalma.tweak.image', box=box)
