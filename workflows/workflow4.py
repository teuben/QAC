#  -*- python -*-
#
# regression test version of workflow4.md
#
#
# Example time:
# CPU times: user 2h 24min 2s, sys: 5min 22s, total: 2h 29min 25s
# Wall time: 1h 15min 11s


# model
skymodel    = 'skymodel.fits'
ptg1        = 'skymodel.ptg'
ptg2        = 'test4-12m.ptg'

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

# gridding, using factor
mapsize     = 4096/factor
pixel       = 0.0625*factor     # 0.0625 or 0.075
niter       = 10000

ptg         = ptg1


#   summary
qac_log("SUMMARY-1")
qac_version()
qac_summary(skymodel)

if True:
    importfits(skymodel,'skymodel1.im',overwrite=True)
    qac_ingest('skymodel1.im','skymodel2.im')
    qac_stats('skymodel2.im')
    qac_plot('skymodel2.im')

    imsmooth('skymodel2.im','gaussian','1arcsec','1arcsec',pa='0deg',outfile='skymodel2s.im',overwrite=True)
    imhead('skymodel2s.im',mode='put',hdkey='bunit',hdvalue='Jy/beam')     # weird: needed a fix here, but skymodel3s didn't need it
    qac_stats('skymodel2s.im')
    qac_plot('skymodel2s.im')


    qac_tp('test70','skymodel2.im',ptg,mapsize,pixel,niter=0,phasecenter=phasecenter, deconv=False)
    qac_stats('test70/dirtymap.image/')
    qac_plot('test70/dirtymap.image/')

    qac_tp('test70s','skymodel2s.im',ptg,mapsize,pixel,niter=0,phasecenter=phasecenter, deconv=False)
    qac_stats('test70s/dirtymap.image/')
    qac_plot('test70s/dirtymap.image/')

    imrebin('skymodel2.im','skymodel3.im',factor=[factor,factor],overwrite=True)
    qac_stats('skymodel3.im')
    qac_plot('skymodel3.im')
     
    beam = '%sarcsec' % tp_beam
    imsmooth('skymodel3.im','gaussian',beam,beam,pa='0deg',outfile='skymodel3s.im',overwrite=True)
    qac_stats('skymodel3s.im')
    qac_plot('skymodel3s.im')


if False:    
    qac_tp('test4', 'skymodel3.im',ptg,deconv=False)
    qac_clean1('test4/clean1',mapsize,pixel,niter=[0,1,10,100,1000,10000], phasecenter=phasecenter)
    
    qac_plot('test4/clean1/dirtymap.image')        # 71 series
    qac_plot('test4/clean1/dirtymap_2.image')
    qac_plot('test4/clean1/dirtymap_3.image')
    qac_plot('test4/clean1/dirtymap_4.image')
    qac_plot('test4/clean1/dirtymap_5.image')
    qac_plot('test4/clean1/dirtymap_6.image')
    
    qac_tp('test4s', 'skymodel3s.im',ptg)
    qac_clean1('test4s/clean1',mapsize,pixel,niter=[0,1,10,100,1000,10000], phasecenter=phasecenter)
    
    qac_plot('test4s/clean1/dirtymap.image')        # 72 series
    qac_plot('test4s/clean1/dirtymap_2.image')
    qac_plot('test4s/clean1/dirtymap_3.image')
    qac_plot('test4s/clean1/dirtymap_4.image')
    qac_plot('test4s/clean1/dirtymap_5.image')
    qac_plot('test4s/clean1/dirtymap_6.image')

qac_log("ALMA 7m/12m")


if True:
    # 7m data
    qac_alma('test4a','skymodel3.im', mapsize,pixel,cfg=0, phasecenter=phasecenter,niter=0)
    qac_stats('test4a/dirtymap.image')

    # 12m data
    qac_alma('test4a','skymodel3.im', mapsize,pixel,cfg=1, phasecenter=phasecenter,niter=0)
    qac_stats('test4a/dirtymap.image')
    
    qac_alma('test4a','skymodel3.im', mapsize,pixel,cfg=2, phasecenter=phasecenter,niter=0)
    qac_stats('test4a/dirtymap.image')
    
    qac_alma('test4a','skymodel3.im', mapsize,pixel,cfg=3, phasecenter=phasecenter,niter=0)
    qac_stats('test4a/dirtymap.image')
    
    qac_alma('test4a','skymodel3.im', mapsize,pixel,cfg=4, phasecenter=phasecenter,niter=0)
    qac_stats('test4a/dirtymap.image')

    qac_log("MAP123a")

    # look at 12m pointings 
    os.system('cp test4a/test4a.alma.cycle5.1.ptg.txt %s' % ptg2)

    qac_tp('test4a/tp','skymodel3.im',ptg,mapsize,pixel,niter=0,phasecenter=phasecenter,deconv=False,fix=0)
    qac_stats('test4a/tp/dirtymap.image')
    qac_plot('test4a/tp/dirtymap.image')

import glob
ms0 = 'test4a/tp/tp.ms'
ms1 = glob.glob('test4a/*aca*.ms')
ms2 = glob.glob('test4a/*alma*.ms')

# the ugly bug in tclean() is creeping up again, for *all* sim data we need do_concat=False

qac_log("MAPPING")

qac_clean('test4a/clean1', ms0,ms1+ms2, mapsize,pixel,niter=[0,10000],  phasecenter=phasecenter,do_alma=True, do_concat=False)
qac_stats('test4a/clean1/alma.image')
qac_stats('test4a/clean1/tpalma.image')
qac_plot('test4a/clean1/alma.image')
qac_plot('test4a/clean1/tpalma.image')

qac_stats('test4a/clean1/tpalma_2.image')
qac_plot('test4a/clean1/tpalma_2.image')

tp2vistweak('test4a/clean1/tpalma','test4a/clean1/tpalma_2')
qac_plot('test4a/clean1/tpalma_2.tweak.image')

qac_beam('test4a/clean1/tpalma.psf',plot='test4a/clean1/qac_beam.png',normalized=True)


if False:
    # - final STATS for regression -------------------------------------------------------------------------
    
    qac_log("REGRESSION full map")

    # full map
    qac_stats('skymodel1.im')
    qac_stats('skymodel2.im')
    qac_stats('skymodel2s.im')
    qac_stats('test70/dirtymap.image/')
    qac_stats('test70s/dirtymap.image/')
    qac_stats('skymodel3.im')
    qac_stats('skymodel3s.im')
    
    qac_log("REGRESSION minus edges ")

    # box excluding edges
    qac_stats('skymodel3.im',                box=box)
    qac_stats('skymodel3s.im',               box=box)
    qac_stats('test70/dirtymap.image/',      box=box)
    qac_stats('test70s/dirtymap.image/',     box=box)
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
