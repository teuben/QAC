#  -*- python -*-
#
#  QAC benchmark for TP2VIS:   based on M100 workflow6 with just 5 channels
#  Based on:           https://casaguides.nrao.edu/index.php/M100_Band3_Combine_5.4
#
#  Grab data from:     http://admit.astro.umd.edu/~teuben/QAC/qac_bench.tar.gz
#        also run:     imtrans('M100_TP_CO_cube.bl.image','M100_TP_CO_cube.blr.image','012-3')
#
#  Benchmark run:      time casa --nogui -c bench.py
#             or:      %time execfile('bench.py')
#
#  Space needs:        ~500MB
#  Memory needed:      ~2.6GB
#
#  Other examples:     casa --nogui -c bench.py niter='[0,100,300,1000,3000,10000]' 
#                      casa --nogui -c bench.py niter='[0,100,300,1000,3000,10000]'  nvgrp=16 test='"bench16"'
#
#  On a Mac you may need to use /Applications/CASA.app/Contents/MacOS/casa
#
#------------------------------------------------------------------------------------------------------------------------------
#  Full bench: (some variations on the same machine I don't understand yet)
#
#  x270:    740.188u 19.676s 5:35.37 226.5%	0+0k 667504+3014296io 1124pf+0w      i7-3630QM CPU @ 2.40GHz
#
#  t480:    449.42   18.94   2:41.23                                                 i7-8550U CPU @ 1.80GHz
#           443.93   18.37   1:43.66
#           911.93   19.32   2:40.82 579%CPU        mar-13
#           929.81   19.20   2:44.03                pre mar-21
#           742.82   19.67   2:13.11 572%CPU        5.6 (aug2019)
#
#  t530:    738.632u 17.956s 5:05.12 247.9%	0+0k 96792+2968744io   578pf+0w      i7-3630QM CPU @ 2.40GHz
#           748.144u 19.440s 5:02.15 254.0%	0+0k 2104+2799288io      2pf+0w
#           803.884u 168.912s 8:11.96 197.7%	0+0k 640496+3091592io 1209pf+0w  530-
#           740.076u 17.432s 5:33.21 227.3%	0+0k 501552+3074184io 1121pf+0w  512
#
#  nikon1   417.135u 23.602s 2:53.37 254.2%     0+0k 0+2158136io 0pf+0w (HDD)        i7-3770K CPU @ 3.50GHz
#           415.320u 22.404s 2:04.46 351.6%     0+0k 0+144io 0pf+0w     (SHM)   
#
#  dante:   385.062u 14.358s 2:42.37 245.9%	0+0k 624+2013376io 0pf+0w            i7-3820 CPU @ 3.60GHz
#           393.835u 17.946s 2:42.70 253.0%	0+0k 218248+2016744io 240pf+0w (HDD)
#           402.181u 14.695s 2:15.24 308.2%	0+0k 616+104io 0pf+0w          (SHM)
#
#  sdp:     1743.867u 66.479s 4:53.99 615.7%	0+0k 409992+2944384io 242pf+0w       Xeon X5550  @ 2.67GH
#            871.961u 56.835s 3:21.61 460.6%	0+0k 146672+2533464io 54pf+0w
#            873.329u 58.793s 3:25.65 453.2%	0+0k 151560+2145232io 198pf+0w
#
#  chara:   1326.660u 24.061s 10:21.12 217.4%	0+0k 521080+104io 304pf+0w           i7 CPU  870  @ 2.93GHz  in /dev/shm
#            673.496u 17.252s 3:46.83 304.5%	0+0k 712+120io 2pf+0w
#            603.262u 17.853s 3:30.83 294.6%	0+0k 768+128io 4pf+0w
#            688.524u 20.112s 3:51.38 306.2%	0+0k 608+128io 0pf+0w
#            678.992u 19.364s 3:44.14 311.5%	0+0k 323240+136io 323pf+0w (SHM)
#            910.227u 20.115s 6:22.68 243.1%	0+0k 912+3244072io 0pf+0w  (HDD)
#            823.509u 31.419s 4:39.69 305.6%    0+0k 248+2221136io 0pf+0w (HDD)      Xeon E31280 @ 3.50GHz (new cpu 2018)
#            711.448u 31.416s 3:39.02 339.1%    0+0k 248+104io 0pf+0w     (SHM)

#
#  cvspost:  709.250u 52.919s 2:51.36 444.7% 0+0k 565664+4425384io 233pf+0w (HDD)    Xeon E5-2640 v3 @ 2.60GHz
#            691.213u 51.565s 2:22.13 522.5% 0+0k 48+80io 0pf+0w            (SHM)
#
#  MacPro:   2m28s    13s     2m35s                                                  i7-2.8GHz  [FLUX BAD]
#
#  UWmach:   2'28" on HDD                                                            Xeon W-2145 CPU @ 3.70GHz
#            1'42" on /dev/shm
#------------------------------------------------------------------------------------------------------------------------------

# parameters in this benchmark workflow
test        = 'bench' 
phasecenter = 'J2000 12h22m54.900s +15d49m15.000s'
line        = {"restfreq":"115.271202GHz","start":"1500km/s", "width":"5km/s","nchan":5}
tpim        = 'M100_TP_CO_cube.blr.image'
tpim        = 'M100_TP_CO_cube.bl.image'
ms07        = 'M100_aver_7.ms'
ms12        = 'M100_aver_12.ms'
nsize       = 800
pixel       = 0.5
niter       = [0,1000]

clean1      = 0             # clean the tp.ms (in 'clean1/')
clean       = 1             # joined deconvolution
tweak       = 1             # compute the tweak map (needs len(niter) > 0)
alma        = 0             # also compute the INT only
plot        = 0             # make some extra plots

#-- do not change parameters below this ---
import sys
for arg in qac_argv(sys.argv):
    exec(arg)

tpms   = test + '/tp.ms'
ptg    = test + '.ptg'
if alma == 1 or plot == 1:
    do_int = True
else:
    do_int = False

#   report
qac_log("TEST: %s" % test)
qac_begin(test)
qac_version()
tp2vis_version()

qac_project(test)


#   make sure all the files we need are here
QAC.assertf(tpim)
QAC.assertf(ms07)
QAC.assertf(ms12)


# get a pointing from the 12m MS data
qac_ms_ptg(ms12,ptg)

# run tp2vis and plot its weights
qac_tp_vis(test,tpim,ptg,rms=0.15)
tp2vispl([tpms,ms07,ms12],outfig=test+'/tp2vispl_rms.png')

# run a clean on just the TP.MS ?
if clean1 == 1:
    qac_clean1(test+'/clean1',tpms,nsize,pixel,niter=niter,phasecenter=phasecenter,**line)
    qac_stats(test+'/clean1/dirtymap.image')
    qac_stats(test+'/clean1/dirtymap_2.image')
    if plot == 1:
        qac_plot(test+'/clean1/dirtymap.image')
    
# run a JD ?
if clean == 1:
    print "Continuing benchmark with clean=1"
    # line['do_cleanup'] = False
    qac_clean(test+'/clean',tpms,[ms12,ms07],nsize,pixel,niter=niter,phasecenter=phasecenter,do_int=do_int,do_concat=True,**line)
    # Jin says we can skip the concat again.... but it's not true (for pure simulated data we do need do_concat=False)
    # in 5.5.0-149 this still crashes 
    if tweak == 1:
        print "Continuing benchmark with tweak=1"
        # loop over all 2nd and higher iterations and tweak them 
        for i in range(1,len(niter)): 
            inamed = test+'/clean/tpint'
            inamec = test+'/clean/tpint_%d' % (i+1)
            tp2vistweak(inamed,inamec)
            iname = test+'/clean/tpint_%d.tweak.image' % (i+1)
            qac_plot(inamec+'.image')
    for i in range(0,len(niter)): 
        if i==0:
            iname = test+'/clean/tpint.image'
        else:
            iname = test+'/clean/tpint_%d.image' % (i+1)
            qac_stats(iname)
    if tweak == 1:
        for i in range(1,len(niter)): 
            iname = test+'/clean/tpint_%d.tweak.image' % (i+1)
            qac_stats(iname)


# final plot if enough data was accumulated for this type of comparison
if plot == 1:
    print "Plotting benchmark comparison"
    a1=test+'/clean/int.image'
    b1=test+'/clean/tpint.image'
    c1=test+'/clean/int_2.image'
    d1=test+'/clean/tpint_2.image'
    e1=test+'/clean/tpint_2.tweak.image'

    images = [a1,b1,   a1,c1,   b1,d1,      e1,d1]
    y      = ['a-tpa', 'a-a_2', 'tpa-tpa_2','tpa_2tweak-tpa_2']
    x      = ['*','*','-diff']
    qac_plot_grid(images,ncol=2,diff=10,box=[200,200,600,600],xgrid=x,ygrid=y,plot=test+'/bench-cmp.png')

    
# regression only valid with the default parameter settings
r1 = "0.0038324075245612802 0.021439737328652425 -0.04851343110203743 0.41929441690444946 383.60319947466479"
r2 = "0.0038324084555372423 0.021439742878458009 -0.048513446003198624 0.41929447650909424 383.60327838373536"   # 5.1.2
r3 = "0.0038308492108101041 0.021409590356922827 -0.048478055745363235 0.41353103518486023 383.4472095101716"    # clark instead of hogbom
r4 = "0.0038472646829610813 0.021499494640955678 -0.047635149210691452 0.4208904504776001 384.45247992991648"    # 5.4
r5 = "0.0047430853598822344 0.021809700773318893 -0.043452214449644089 0.42146685719490051 473.97069588577432"   # 5.5
r6 = "0.004743185253331385 0.02181014437004293 -0.04345422238111496 0.42146903276443481 473.98086630998699"      # 5.6

if False:
    # CASA5 versions
    i1 = '0.5993522068193684 1.3645259947183588 -0.72602438926696777 8.8048715591430664 3561.9630360887845'
    i2 = '2.5704516191133808 1.4169106044781279 0.0011036963438420227 15.982205689901765 0.0'
    i3 = '1.1768639368547504 0.64537772802755577 0.00058940987456351226 7.0547655988877178 0.0'
else:
    # CASA4 versions
    i1 = '0.54682752152594571 1.2847112260328173 -0.89499807357788086 8.8632850646972656 4001.3152006372839'
    i2 = '2.5714851372581906 1.4175336201556363 0.0011051818163008522 15.982229345769259 0.0'
    i3 = '1.177256275796271 0.64576812715900356 0.00059684379497741192 7.0609529505808935 0.0'

qac_stats(tpim,i1)
qac_stats(ms07,i2)
qac_stats(ms12,i3)
qac_stats(test+'/clean/tpint.image')
qac_stats(test+'/clean/tpint_2.tweak.image', r6)
# done
qac_end()
