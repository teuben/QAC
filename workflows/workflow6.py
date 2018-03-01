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


# parameters in this workflow
phasecenter = 'J2000  12h22m54.900s +15d49m15.000s'

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

boxlist = QAC.iarray(box)          # convert to a list of ints [219,148,612,579]
    

#   report
qac_log("QAC_VERSION")
qac_version()

#   make sure all the files we need are here
QAC.assertf(tpim)
QAC.assertf(ms07)
QAC.assertf(ms12)

# summary
qac_log("SUMMARY-1")
qac_summary('tp.im',['aver_12.ms','aver_7.ms'])
qac_ms_ptg('aver_12.ms','aver_12.ptg')

qac_log("TP2VIS")
qac_tp('test6',tpim,'aver_12.ptg',nsize,pixel,niter=0,rms=0.15,phasecenter=phasecenter)          # PSF is blank for[C69:P0]
qac_log("TP2VISWT - should show no change; about 0.0107354")
tp2viswt('test6/tp.ms',value=0.15,mode='rms')

if True:
    # Look at the difference between TP and dirty map from TP2VIS
    temp_dict = imregrid(imagename='test6/dirtymap.image', template="get")
    imregrid(imagename='M100_TP_CO_cube.bl.image',output='M100_TP_CO_cube.bl.smo',template=temp_dict,overwrite=True)
    os.system('rm -rf temp.diff')
    immath(imagename=['test6/dirtymap.image','M100_TP_CO_cube.bl.smo'],expr='IM0-0.915684045023*IM1',outfile='temp.diff')

if True:
    # plot comparing flux of TP
    f0a =  imstat('M100_TP_CO_cube.bl.image',axes=[0,1])['flux']
    f1a =  imstat('test6/dirtymap.image',    axes=[0,1])['flux']
    f1b =  imstat('M100_TP_CO_cube.bl.smo',  axes=[0,1])['flux']
    f1c =  imstat('M100_TP_CO_cube.bl.smo',  axes=[0,1], box=box)['flux']    
    plot2a([f0a,f1a,f1b,f1c],'Flux Comparison %d %g' % (nsize,pixel),'plot2a0.png')
        
qac_log("CLEAN clean1: TP+7m")
qac_clean('test6/clean1','test6/tp.ms',ms07,nsize,pixel,niter=0,phasecenter=phasecenter,do_alma=True,**line)
qac_beam('test6/clean1/tpalma.psf',plot='test6/clean1/qac_beam.png',normalized=True)
# QAC_BEAM: test2c/tpalma.psf  14.8567 11.6334 0.5 783.349 783.349
# QAC_BEAM: Max/Last/PeakLoc 1.34796753314 1.18801575148 43.5

qac_log("CLEAN clean2: TP+12m")
qac_clean('test6/clean2','test6/tp.ms',ms12,nsize,pixel,niter=0,phasecenter=phasecenter,do_alma=True,**line)
qac_beam('test6/clean2/tpalma.psf',plot='test6/clean2/qac_beam.png',normalized=True)
# QAC_BEAM: test2d/tpalma.psf  3.99421 2.63041 0.5 47.6187 47.6187
# QAC_BEAM: Max/Last/PeakLoc 4.11547851528 3.62032676416 76.5

qac_log("CLEAN clean3: TP+7m+12m")
qac_clean('test6/clean3','test6/tp.ms',[ms12,ms07],nsize,pixel,niter=[0,1000,3000],phasecenter=phasecenter,do_alma=True,**line)
qac_beam('test6/clean3/tpalma.psf',plot='test6/clean3/qac_beam.png',normalized=True)
# QAC_BEAM: test2e/tpalma.psf  4.4261 2.94494 0.5 59.0776 59.0776
# QAC_BEAM: Max/Last/PeakLoc 2.95162277943 2.47391209456 76.0
tp2vistweak('test6/clean3/tpalma','test6/clean3/tpalma_2')
# scale  0.7455
tp2vistweak('test6/clean3/tpalma','test6/clean3/tpalma_3')
# scale  0.732610

qac_log("TP2VISWT wt*10")
tp2viswt('test6/tp.ms',mode='multiply',value=10)
# wt -> 0.1073537

qac_log("CLEAN clean4")
qac_clean('test6/clean4','test6/tp.ms',[ms12,ms07],nsize,pixel,niter=0,phasecenter=phasecenter,**line)
qac_beam('test6/clean4/tpalma.psf',plot='test6/clean4/qac_beam.png',normalized=True)
# QAC_BEAM: test2f/tpalma.psf  4.73778 3.16311 0.5 67.9224 67.9224
# QAC_BEAM: Max/Last/PeakLoc 20.2581768937 19.8506027809 76.5

qac_log("CLEAN clean5 - why?")
qac_clean('test6/clean5','test6/tp.ms',[ms12,ms07],nsize,pixel,niter=0,phasecenter=phasecenter,**line)
qac_beam('test6/clean5/tpalma.psf',plot='test6/clean5/qac_beam.png',normalized=True)
# QAC_BEAM: test2g/tpalma.psf  54.2112 51.2846 0.5 12600.9 12600.9
# QAC_BEAM: Max/Last/PeakLoc 1.16708248354 1.16100111055 89.0

# beam size weights 
qac_log("TP2VISTWEAK")
tp2viswt(['test6/tp.ms',ms07,ms12], makepsf=True, mode='beammatch')
# wt -> 0.0044103029511 -> 0.00433382295945 -> 0.00465955996837  -> 0.002709 

qac_log("CLEAN clean6")
qac_clean('test6/clean6','test6/tp.ms',[ms12,ms07],nsize,pixel,niter=[0,1000,3000],phasecenter=phasecenter,**line)
qac_beam('test6/clean6/tpalma.psf',plot='test6/clean6/qac_beam.png',normalized=True)
# -> QAC_BEAM: test2h/tpalma.psf  4.40321 2.92833 0.5 58.4404 58.4404
#    QAC_BEAM: Max/Last/PeakLoc 1.86142086595 0.623532966042 7.5


if False:
    # check the Jorsater & van Moorsel procedure
    qac_log("CLEAN test2h1")
    qac_clean('test2h1','test1/tp.ms',[ms12,ms07],nsize,pixel,niter=1000,phasecenter=phasecenter,do_alma=False,**line)
    tp2vistweak('test2h/tpalma','test2h1/tpalma')
    # -> Stat:     Bmaj     Bmin Sum(dirty) Sum(clean) dirty/clean
    #              4.407    2.932    21.4464    67.1569     0.3193
    qac_log("CLEAN test2h2")
    qac_clean('test2h2','test1/tp.ms',[ms12,ms07],nsize,pixel,niter=3000,phasecenter=phasecenter,do_alma=False,**line)
    tp2vistweak('test2h/tpalma','test2h2/tpalma')
    #
    f0  =  imstat('M100_TP_CO_cube.regrid',    axes=[0,1],box=box)['flux'][1:-1]
    f1  =  imstat('test2h/tpalma.image',       axes=[0,1],box=box)['flux']
    f2  =  imstat('test2h1/tpalma.image',      axes=[0,1],box=box)['flux']
    f3  =  imstat('test2h2/tpalma.image',      axes=[0,1],box=box)['flux']
    f4  =  imstat('test2h1/tpalma.tweak.image',axes=[0,1],box=box)['flux']
    f5  =  imstat('test2h2/tpalma.tweak.image',axes=[0,1],box=box)['flux']
    #
    plot2a([f0,f1,f2,f3],  'plot2h1',       'plot2h1.png')
    plot2a([f0,f1,f4,f5],  'plot2h2 tweak', 'plot2h2.png')

tp2vistweak('test6/clean6/tpalma','test6/clean6/tpalma_2')
# scale 3.129287
tp2vistweak('test6/clean6/tpalma','test6/clean6/tpalma_3')
# scale 2.939141

f0  =  imstat('M100_TP_CO_cube.regrid',           axes=[0,1],box=box)['flux']
f1  =  imstat('test6/clean6/tpalma.image',        axes=[0,1],box=box)['flux']
f2  =  imstat('test6/clean6/tpalma_2.image',      axes=[0,1],box=box)['flux']
f3  =  imstat('test6/clean6/tpalma_3.image',      axes=[0,1],box=box)['flux']
f4  =  imstat('test6/clean6/tpalma_2.tweak.image',axes=[0,1],box=box)['flux']
f5  =  imstat('test6/clean6/tpalma_3.tweak.image',axes=[0,1],box=box)['flux']
#
plot2a([f0,f1,f2,f3],  'plot2h1',       'plot2h1.png')
plot2a([f0,f1,f4,f5],  'plot2h2 tweak', 'plot2h2.png')

    

qac_log("BEAMCHECK")
# execfile('../beamcheck.py')
# beamcheck('test2h/tpalma','test2i/tpalma')
# -> Dirty (sum,bmaj,bmin):  105.019738839 4.40320777893 2.92832803726
# -> Clean (sum,bmaj,bmin):  269.662882205 4.40320777893 2.92832803726


regres51 = [
    '1.177256275796271 0.64576812715900356 0.00059684379497741192 7.0609529505808935 0.0',
    '2.5714851372581906 1.4175336201556363 0.0011051818163008522 15.982229345769259 0.0',
    '1.2121874534129664 1.0706370322706797 8.9894598086921097e-05 8.7439785003662109 0.0',
    '0.54682752152594571 1.2847112260328173 -0.89499807357788086 8.8632850646972656 4001.3152006372839',
    '0.17502567644205042 0.29636334974068906 -0.01874225027859211 1.7939578294754028 2023.238938154813',
    '6.4967219206392597e-05 0.090095439430921576 -0.69042855501174927 2.4988367557525635 8.8767026718845621',
    '0.059620662274210548 0.12235698788056612 -0.34523037075996399 2.8235268592834473 7438.3130660632951',
    '-3.2805637128240005e-07 0.015227907834553262 -0.14608184993267059 0.5679050087928772 -0.53773300295131066',
    '0.013743010664281271 0.023264746531751569 -0.082932926714420319 0.63548052310943604 22370.573155800837',
    '4.28581407936708e-06 0.022631811368684605 -0.16905108094215393 0.80271512269973755 5.9360460777592285',
    '0.011506625277348154 0.027128265548915627 -0.11467967182397842 0.8589213490486145 15655.015453119462',
    '0.10499524607530433 0.13873541620859353 -0.024327397346496582 1.3373793363571167 124148.60653471657',
    '1.1068966126089719 1.4509619468478017 0.096944719552993774 7.6039481163024902 6955.9456422021731',
    '0.0050268122414183491 0.023549383849050268 -0.14197352528572083 0.82724666595458984 6896.2735193530361',
    ]

r = regres51

qac_stats(ms12,                       r[0])
qac_stats(ms07,                       r[1])
qac_stats('test6/tp.ms',              r[2])
qac_stats(tpim,                       r[3])
qac_stats('test6/dirtymap.image',     r[4])

qac_stats('test6/clean1/alma.image',        r[5])     # test2c
qac_stats('test6/clean1/tpalma.image',      r[6])

qac_stats('test6/clean2/alma.image',        r[7])     # test2d
qac_stats('test6/clean2/tpalma.image',      r[8])

qac_stats('test6/clean3/alma.image',        r[9])     # test2d
qac_stats('test6/clean3/tpalma.image',      r[10])

qac_stats('test6/clean4/tpalma.image',      r[11])      # test2f

qac_stats('test6/clean5/tpalma.image',      r[12])     # test2g

qac_stats('test6/clean6/tpalma.image',      r[13])             # test2h series
qac_stats('test6/clean6/tpalma_2.image')
qac_stats('test6/clean6/tpalma_3.image')
qac_stats('test6/clean6/tpalma_2.tweak.image',pb='test6/clean6/tpalma.pb')
qac_stats('test6/clean6/tpalma_3.tweak.image',pb='test6/clean6/tpalma.pb')
