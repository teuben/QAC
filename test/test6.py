#  -*- python -*-
#
#  Example workflow with TP2VIS for "M100" project.
#  See workflow6.md for a more detailed explanation with figures 
#
#  Prepared smaller datasets on: http://admit.astro.umd.edu/~teuben/TP2VIS/
#
#  Timing:  takes about 2h10m on dante
#           takes about 20-30m on nemo2 with the 5 km/s prepared smaller datasets
#
# 7504.900u 176.808s 1:11:48.52 178.2%	0+0k 17703128+123968584io 2512pf+0w
#
#  Uses about 21GB when symlinks to small data are used.
#
#  Within test6/ the following directories are:
#   test6/clean1    TP+7m
#   test6/clean2    TP+12m 
#   test6/clean3    TP+7m12m   rms weights   (5.584021/GHz)
#   test6/clean4    -same- but with 10*rms   (55.840208/GHz)
#   test6/clean6    TP+7m12m   beammatch weights   (1.409106/GHz)


# parameters in this workflow
phasecenter = 'J2000 12h22m54.900s +15d49m15.000s'

line1 = {"restfreq":'115.271202GHz','start':'1400km/s', 'width':'5km/s','nchan':70}
line2 = {"restfreq":'115.271202GHz','start':'1405km/s', 'width':'5km/s','nchan':68}
line  = line1

tpim  = 'M100_TP_CO_cube.bl.image'
ms07  = 'M100_aver_7.ms'
ms12  = 'M100_aver_12.ms'

nsize = 800
pixel = 0.5

box1  = '219,148,612,579'       # same box as in workflow6a where we want to compare fluxes (depends on nsize=800, pixel=0.5)
box   = box1

boxlist = QAC.iarray(box)       # convert to an ascii list of ints [219,148,612,579] for qac_plot()
    

#   report
qac_log("QAC_VERSION")
qac_version()

#   make sure all the files we need are here
QAC.assertf(tpim)
QAC.assertf(ms07)
QAC.assertf(ms12)

# summary
qac_log("SUMMARY-1")
qac_summary(tpim,[ms12,ms07])
qac_ms_ptg(ms12,'M100_aver_12.ptg')

if not QAC.exists('test6'):
    qac_log("TP2VIS with rms=0.15 and weigh down by 1e-3")   
    qac_tp_vis('test6',tpim,'M100_aver_12.ptg',rms=0.15)               #  wt = 0.0107354  (5.584021 per GHz)
    

niter = [0,1000,3000]

for wt in np.logspace(-4,0,5):
    tp2viswt('test6/tp.ms',mode='const',value=wt)
    cleandir = 'test6/clean_%g' % wt
    cleandir = 'test6/clean0'    # keep overwriting this, no space for all this
    qac_clean(cleandir,'test6/tp.ms',[ms12,ms07],nsize,pixel,niter=niter,phasecenter=phasecenter,**line)
    qac_beam(cleandir+'/tpint.psf',plot='test6/qac_beam_%g.png' % wt,   normalized=True)
    qac_stats(cleandir+'/tpint.image')
    qac_stats(cleandir+'/tpint.image',box=box)
    qac_stats(cleandir+'/tpint.image.pbcor',box=box)
    for i in range(1,len(niter)):
        tp2vistweak(cleandir+'tpint',cleandir+'/tpint_%d' % (i+1))
        qac_stats(cleandir+'/tpint_%d.image'              % (i+1) ,box=box)
        qac_stats(cleandir+'/tpint_%d.image.pbcor'        % (i+1) ,box=box)
        qac_stats(cleandir+'/tpint_%d.tweak.image'        % (i+1) ,box=box)
        qac_stats(cleandir+'/tpint_%d.tweak.image.pbcor'  % (i+1) ,box=box)
