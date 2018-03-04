#
#     show different flux for the fix=0 and fix=1 in qac_tp_vis()
#     this is where we do a mstransform and concat. Turns out concat is
#     the cause, in particular two pointings caused a slight difference
#     in everything.
#
#     It is assumed you have run workflow1, which has prepared files.
#
#     Timing x270: quick mode: (80/140)    [full mode: 7min/13min]
#
    
#   report
qac_version()

# set phasecenter from CRPIX in TP
phasecenter = 'J2000 05h39m50.000s -70d07m0.000s'
phasecenter = 'J2000 84.9583333333deg -70.1166666666deg'
nsize       = 512
pixel       = 0.5

# done with prep, set filenames for remainder of this workflow
tpim  = 'cloud197_casa47.spw17.image'

ptg0 = 'cloud197.ptg'       # the default from the 12m MS
ptg1 = 'cloud197-4.ptg'     # the one with variable grid

grid = 50.0
qac_im_ptg(phasecenter,nsize,pixel,grid,rect=True,outfile=ptg1)

ptg = ptg0

if False:
    qac_tp('test1-4a',tpim,ptg0,rms=0.7,fix=2)
    qac_clean1('test1-4a/clean0','test1-4a/tp.ms',nsize,pixel,niter=0,phasecenter=phasecenter)
    qac_clean1('test1-4a/clean1','test1-4a/tp1.ms',nsize,pixel,niter=0,phasecenter=phasecenter)
    qac_clean1('test1-4a/clean2','test1-4a/tp2.ms',nsize,pixel,niter=0,phasecenter=phasecenter)
    qac_clean1('test1-4a/clean3','test1-4a/tp3.ms',nsize,pixel,niter=0,phasecenter=phasecenter)

    qac_stats('test1-4a/clean0/dirtymap.image')
    qac_stats('test1-4a/clean1/dirtymap.image')
    qac_stats('test1-4a/clean2/dirtymap.image')
    qac_stats('test1-4a/clean3/dirtymap.image')
    
    p1 = 'test1-4a/clean1/dirtymap.pb'
    p2 = 'test1-4a/clean2/dirtymap.pb'
    immath([p1,p2],'evalexpr','test1-4a/diff.pb','IM0-IM1')

if False:
    # see all tp.ms results
    qac_tp_vis('test1-4b',tpim,ptg1,rms=0.7,fix=2)
    qac_clean1('test1-4b/clean0','test1-4b/tp.ms',nsize,pixel,niter=0,phasecenter=phasecenter)
    qac_clean1('test1-4b/clean1','test1-4b/tp1.ms',nsize,pixel,niter=0,phasecenter=phasecenter)
    qac_clean1('test1-4b/clean2','test1-4b/tp2.ms',nsize,pixel,niter=0,phasecenter=phasecenter)
    qac_clean1('test1-4b/clean3','test1-4b/tp3.ms',nsize,pixel,niter=0,phasecenter=phasecenter)
    
    qac_stats('test1-4b/clean0/dirtymap.image')
    qac_stats('test1-4b/clean1/dirtymap.image')
    qac_stats('test1-4b/clean2/dirtymap.image')
    qac_stats('test1-4b/clean3/dirtymap.image')
    
    p3 = 'test1-4b/clean1/dirtymap.pb'
    p4 = 'test1-4b/clean2/dirtymap.pb'
    immath([p3,p4],'evalexpr','test1-4b/diff.pb','IM0-IM1')


if True:
    # this is the quickest way to see the pattern
    qac_tp_vis('test1-4b',tpim,ptg,rms=0.7,fix=2)
    qac_clean1('test1-4b/clean1','test1-4b/tp1.ms',nsize,pixel,niter=0,phasecenter=phasecenter)
    qac_clean1('test1-4b/clean2','test1-4b/tp2.ms',nsize,pixel,niter=0,phasecenter=phasecenter)
    
    qac_stats('test1-4b/clean1/dirtymap.image')
    qac_stats('test1-4b/clean2/dirtymap.image')

    p3 = 'test1-4b/clean1/dirtymap.pb'
    p4 = 'test1-4b/clean2/dirtymap.pb'
    qac_math('test1-4b/diff.pb', p3, '-', p4)

#  viewer('test1-4b/diff.pb')

# the clean2 pb shows nice symmetry, the clean1 is wrong, the first and last field have a wrong PB
# first one too nigh, last one too low

