#  -*- python -*-
#
#  QAC benchmark, based on M100 workflow6 with just 5 channels
#  Grab data from:     http://admit.astro.umd.edu/~teuben/QAC/qac_bench.tar.gz
#  Benchmark run:      time casa --nogui -c bench.py
#  Space needs:        ~500MB 
#
#  Example run:        casa --nogui -c bench.py niter='[0,100,300,1000,3000,10000]'
#
#  Paper shows channels 1465,1485,1505 km/s
#  Online example1 one shows channel 1520 km/s
#

#
#           clean=0     tweak=0        full bench
#  x270:   38" (29")  2'54" (7'43")   2"57" (7'48")
#          51" (35")  2'56" (7'39")   3"04" (7'47")
#
#
#  x270:    740.188u 19.676s 5:35.37 226.5%	0+0k 667504+3014296io 1124pf+0w      i7-3630QM CPU @ 2.40GHz                                              
#  t530:    738.632u 17.956s 5:05.12 247.9%	0+0k 96792+2968744io 578pf+0w        i7-3630QM CPU @ 2.40GHz
#           748.144u 19.440s 5:02.15 254.0%	0+0k 2104+2799288io 2pf+0w
#  dante:   385.062u 14.358s 2:42.37 245.9%	0+0k 624+2013376io 0pf+0w            i7-3820 CPU @ 3.60GHz
#  sdp:     1743.867u 66.479s 4:53.99 615.7%	0+0k 409992+2944384io 242pf+0w       X5550  @ 2.67GHz
#  chara:   1326.660u 24.061s 10:21.12 217.4%	0+0k 521080+104io 304pf+0w           i7 CPU  870  @ 2.93GHz  in /dev/shmem
#            673.496u 17.252s 3:46.83 304.5%	0+0k 712+120io 2pf+0w
#            603.262u 17.853s 3:30.83 294.6%	0+0k 768+128io 4pf+0w
#            688.524u 20.112s 3:51.38 306.2%	0+0k 608+128io 0pf+0w

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

# regression only valid with no cmdline argument
qac_stats(test+'/clean/tpalma_2.tweak.image', "0.0038324075245612802 0.021439737328652425 -0.04851343110203743 0.41929441690444946 383.60319947466479")
