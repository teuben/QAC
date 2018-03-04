#  -*- python -*-
#
# for full model data do_concat=False to make it work?
# Or how is this now related to the POINTING....
#
# Both the simobserve() models from ACA and ALMA have POINTING tables,
# as do our TP2VIS models
#
#   it needs skymodel3.im from workflow4.py

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

# gridding, using factor
mapsize     = 4096/factor
pixel       = 0.0625*factor     # 0.0625 or 0.075

ptg         = ptg1
skymodel    = 'skymodel3.im'

if not QAC.exists('test4-test1'):
    qac_alma('test4-test1',skymodel,cfg=0)
    qac_tp_vis('test4-test1/tp',skymodel,ptg,fix=2)
else:
    print "ASSUMING test4-test1/ is ok to use"

# find all the MS files needed for tclean    
import glob
ms0 = 'test4-test1/tp/tp.ms'   # with POINTING
ms1 = 'test4-test1/tp/tp1.ms'  # with POINTING
ms2 = 'test4-test1/tp/tp2.ms'  # no   POINTING !!
ms3 = 'test4-test1/tp/tp3.ms'  # with POINTING

msa1 = 'test4-test1/test4-test1.aca.cycle5.ms'     # with POINTING
msa2 = 'test4-test1/test4-test1.aca.cycle5.ms2'    # no POINTING

qac_clean('test4-test1/clean01', ms0,msa1, mapsize,pixel,niter=0,phasecenter=phasecenter,do_concat=False)   # ok
# qac_clean('test4-test1/clean02', ms1,msa1, mapsize,pixel,niter=0,phasecenter=phasecenter,do_concat=False)   # segfault
# qac_clean('test4-test1/clean03', ms2,msa1, mapsize,pixel,niter=0,phasecenter=phasecenter,do_concat=False)   # segfault
# qac_clean('test4-test1/clean04', ms3,msa1, mapsize,pixel,niter=0,phasecenter=phasecenter,do_concat=False)   # segfault

# qac_clean('test4-test1/clean05', ms0,msa1, mapsize,pixel,niter=0,phasecenter=phasecenter,do_concat=True)    #fail
# qac_clean('test4-test1/clean06', ms1,msa1, mapsize,pixel,niter=0,phasecenter=phasecenter,do_concat=True)    #fail
# qac_clean('test4-test1/clean07', ms2,msa1, mapsize,pixel,niter=0,phasecenter=phasecenter,do_concat=True)    #fail
# qac_clean('test4-test1/clean08', ms3,msa1, mapsize,pixel,niter=0,phasecenter=phasecenter,do_concat=True)    #fail

qac_clean('test4-test1/clean09', ms0,msa2, mapsize,pixel,niter=0,phasecenter=phasecenter,do_concat=False)   # ok
# qac_clean('test4-test1/clean10', ms1,msa2, mapsize,pixel,niter=0,phasecenter=phasecenter,do_concat=False)   # segfault
# qac_clean('test4-test1/clean11', ms2,msa2, mapsize,pixel,niter=0,phasecenter=phasecenter,do_concat=False)   # segfault
# qac_clean('test4-test1/clean12', ms3,msa2, mapsize,pixel,niter=0,phasecenter=phasecenter,do_concat=False)   # segfault

# qac_clean('test4-test1/clean13', ms0,msa2, mapsize,pixel,niter=0,phasecenter=phasecenter,do_concat=True)    #fail
# qac_clean('test4-test1/clean14', ms1,msa2, mapsize,pixel,niter=0,phasecenter=phasecenter,do_concat=True)    #fail
# qac_clean('test4-test1/clean15', ms2,msa2, mapsize,pixel,niter=0,phasecenter=phasecenter,do_concat=True)    #fail
# qac_clean('test4-test1/clean16', ms3,msa2, mapsize,pixel,niter=0,phasecenter=phasecenter,do_concat=True)    #fail

qac_stats('test4-test1/clean01/tpalma.image')
qac_stats('test4-test1/clean09/tpalma.image')
# QAC_STATS: test4-test1/clean01/tpalma.image 0.23698202387919634 3.8734787944689661 -13.049557685852051 19.693824768066406 21.3320774518949 
# QAC_STATS: test4-test1/clean09/tpalma.image 0.40138945663036213 5.5308646822946006 -15.10496997833252 28.560054779052734 36.136541842861284 
qac_math('test4-test1/clean01/diff.image', 'test4-test1/clean01/tpalma.image', '-', 'test4-test1/clean09/tpalma.image')
qac_math('test4-test1/clean01/diff.pb',    'test4-test1/clean01/tpalma.pb',    '-', 'test4-test1/clean09/tpalma.pb')
exportfits('test4-test1/clean01/diff.pb','test4-test1/clean01/diff.pb.fits')

# this difference map shows a number (not just 2) "pointing" areas where the PB is different.
