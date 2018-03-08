#  -*- python -*-
#
#  QAC benchmark for TP2VIS:   based on M100 workflow6 with just 5 channels
#
#  Grab data from:     http://admit.astro.umd.edu/~teuben/QAC/qac_bench.tar.gz
#  Benchmark run:      time casa --nogui -c bench.py
#             or:      %time execfile('bench.py')
#  Space needs:        ~500MB
#  Memory needed:      ~2.6GB
#
#  Example run:        casa --nogui -c bench.py niter='[0,100,300,1000,3000,10000]'  nvgrp=16
#
#  On a Mac you may need to use  /Applications/CASA.app/Contents/MacOS/casa
#
#  Paper shows channels 1465,1485,1505 km/s
#  Online example1 one shows channel 1520 km/s
#------------------------------------------------------------------------------------------------------------------------------
#           clean=0     tweak=0        full bench
#  x270:   38" (29")  2'54" (7'43")   2"57" (7'48")
#          51" (35")  2'56" (7'39")   3"04" (7'47")
#
#  Full bench: (some variations on the same machine I don't understand yet)
#
#  x270:    740.188u 19.676s 5:35.37 226.5%	0+0k 667504+3014296io 1124pf+0w      i7-3630QM CPU @ 2.40GHz
#
#  t530:    738.632u 17.956s 5:05.12 247.9%	0+0k 96792+2968744io 578pf+0w        i7-3630QM CPU @ 2.40GHz
#           748.144u 19.440s 5:02.15 254.0%	0+0k 2104+2799288io 2pf+0w
#           803.884u 168.912s 8:11.96 197.7%	0+0k 640496+3091592io 1209pf+0w  530
#           740.076u 17.432s 5:33.21 227.3%	0+0k 501552+3074184io 1121pf+0w  512




#  dante:   385.062u 14.358s 2:42.37 245.9%	0+0k 624+2013376io 0pf+0w            i7-3820 CPU @ 3.60GHz
#           393.835u 17.946s 2:42.70 253.0%	0+0k 218248+2016744io 240pf+0w (HDD)
#           402.181u 14.695s 2:15.24 308.2%	0+0k 616+104io 0pf+0w (SHM)
#
#  sdp:     1743.867u 66.479s 4:53.99 615.7%	0+0k 409992+2944384io 242pf+0w       X5550  @ 2.67GH
#            871.961u 56.835s 3:21.61 460.6%	0+0k 146672+2533464io 54pf+0w
#            873.329u 58.793s 3:25.65 453.2%	0+0k 151560+2145232io 198pf+0w
#
#  chara:   1326.660u 24.061s 10:21.12 217.4%	0+0k 521080+104io 304pf+0w           i7 CPU  870  @ 2.93GHz  in /dev/shmem
#            673.496u 17.252s 3:46.83 304.5%	0+0k 712+120io 2pf+0w
#            603.262u 17.853s 3:30.83 294.6%	0+0k 768+128io 4pf+0w
#            688.524u 20.112s 3:51.38 306.2%	0+0k 608+128io 0pf+0w
#            678.992u 19.364s 3:44.14 311.5%	0+0k 323240+136io 323pf+0w (SHM)
#            910.227u 20.115s 6:22.68 243.1%	0+0k 912+3244072io 0pf+0w  (HDD)
#
#  cvspost:  709.250u 52.919s 2:51.36 444.7% 0+0k 565664+4425384io 233pf+0w   (HDD)  E5-2640 v3 @ 2.60GHz
#            691.213u 51.565s 2:22.13 522.5% 0+0k 48+80io 0pf+0w (SHM)
#
#  MacPro:   2m28s    13s     2m35s                                                  i7-2.8GHz  [FLUX BAD]
#------------------------------------------------------------------------------------------------------------------------------

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
alma        = 0
plot        = 0

#-- do not change parameters below this ---
import sys
for arg in qac_argv(sys.argv):
    exec(arg)

tpms   = test + '/tp.ms'
ptg    = test + '.ptg'
if alma == 1:
    do_alma = True
else:
    do_alma = False

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
    qac_clean(test+'/clean',tpms,[ms12,ms07],nsize,pixel,niter=niter,phasecenter=phasecenter,do_alma=do_alma,**line)
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
qac_stats(test+'/clean/tpalma.image',         "")
qac_stats(test+'/clean/tpalma_2.tweak.image', "0.0038324075245612802 0.021439737328652425 -0.04851343110203743 0.41929441690444946 383.60319947466479")

if plot == 1:
    print "Plotting benchmark comparison"
    a1=test+'/clean/alma.image'
    b1=test+'/clean/tpalma.image'
    c1=test+'/clean/alma_2.image'
    d1=test+'/clean/tpalma_2.image'
    e1=test+'/clean/tpalma_2.tweak.image'

    qac_plot_grid([a1,a2],ncol=2,cmp=10,box=[200,200,600,600])  # alma: casa diff
    qac_plot_grid([b1,b2],ncol=2,cmp=10,box=[200,200,600,600])  # tpalma: casa diff
    qac_plot_grid([c1,c2],ncol=2,cmp=10,box=[200,200,600,600])
    qac_plot_grid([d1,d2],ncol=2,cmp=10,box=[200,200,600,600])
    qac_plot_grid([e1,e2],ncol=2,cmp=10,box=[200,200,600,600])

    qac_plot_grid([a1,b1],ncol=2,cmp=10,box=[200,200,600,600])  # alma and tpalma
    qac_plot_grid([a1,c1],ncol=2,cmp=10,box=[200,200,600,600])  # same....
    qac_plot_grid([b1,d1],ncol=2,cmp=10,box=[200,200,600,600])  # wow
    qac_plot_grid([e1,d1],ncol=2,cmp=10,box=[200,200,600,600]) 

    images = [a1,b1,a1,c2,b1,d1,e1,d1]
    x=['*','*','-diff']
    y=['a-tpa', 'a-a_2', 'tpa-tpa_2','tpa_2tweak-tpa_2']
    qac_plot_grid(images,ncol=2,cmp=10,box=[200,200,600,600],xgrid=x,ygrid=y,plot=test+'/bench-cmp.png')

