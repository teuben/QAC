#  -*- python -*-
#
#  QAC benchmark, based on M100 workflow6 with just 5 channels
#  Grab data from:     http://admit.astro.umd.edu/~teuben/QAC/qac_bench.tar.gz
#  Benchmark run:      time casa --nogui -c bench.py
#
#  Example run:        casa --nogui -c bench.py niter='[0,100,300,1000,3000,10000]'
#
#  Paper shows channels 1465,1485,1505 km/s
#  Online example1 one shows channel 1520 km/s
#
#           clean=0     tweak=0        full bench
#  x270:   38" (29")  2'54" (7'43")   2"57" (7'48")
#  t530:

# parameters in this benchmark workflow
test        = 'bench' 
phasecenter = 'J2000 12h22m54.900s +15d49m15.000s'
line        = {"restfreq":"115.271202GHz","start":"1500km/s", "width":"5km/s","nchan":5}
tpim        = 'M100_TP_CO_cube.bl.image'
ms07        = 'M100_aver_7.ms'
ms12        = 'M100_aver_12.ms'
nsize       = 800
pixel       = 0.5
niter       = [0,1000]
clean       = 1
tweak       = 1

#-- do not change parameters below this ---
import sys
for arg in qac_argv(sys.argv):
    exec(arg)

tpms   = test + '/tp.ms'
ptg    = test + '.ptg'

#   make sure all the files we need are here
QAC.assertf(tpim)
QAC.assertf(ms07)
QAC.assertf(ms12)

#   run a few QAC routines:

# get a pointing from the 12m
qac_ms_ptg(ms12,ptg)

# run tp2vis and plot weights
qac_tp_vis(test,tpim,ptg,rms=0.15)
tp2vispl([tpms,ms07,ms12],outfig=test+'/tp2vispl_rms.png')

if clean == 1:
    print "Continuing benchmark with clean=1"
    qac_clean(test+'/clean',tpms,[ms12,ms07],nsize,pixel,niter=niter,phasecenter=phasecenter,**line)
    if tweak == 1:
        print "Continuing benchmark with tweak=1"
        # loop over all 2nd and higher iterations and tweak them 
        for i in range(1,len(niter)): 
            inamed = test+'/clean/tpalma'
            inamec = test+'/clean/tpalma_%d' % (i+1)
            tp2vistweak(inamed,inamec)
            iname = test+'/clean/tpalma_%d.tweak.image' % (i+1)
            qac_plot(inamec+'.image')
            qac_plot(iname)
    for i in range(0,len(niter)): 
        if i==0:
            iname = test+'/clean/tpalma.image'
        else:
            iname = test+'/clean/tpalma_%d.image' % (i+1)
            qac_stats(iname)
    if tweak == 1:
        for i in range(1,len(niter)): 
            iname = test+'/clean/tpalma_%d.tweak.image' % (i+1)
            qac_stats(iname)

"""
1000 ->      0.0038324084555372432 0.021439742878458137 -0.048513446003198624 0.41929447650909424 383.60327838373536 

"""
