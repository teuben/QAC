#
#  Example workflow with TP2VIS for "cloud197" project.
#  See also workflow1.md 
#
#  This workflow also serves as a benchmark and regression test
#  where a few parameters can be used to tweak the script and expose
#  certain problems. Use with care.
#
#  Timing:   
#  917.984u 26.556s 11:23.57 138.1%	0+0k 9552+16330568io 4pf+0w    (repeat mode)
#  849.592u 27.276s 11:09.18 131.0%	0+0k 64+16648072io 0pf+0w
#  Space:
#  Creates about 4.3 GB in the test1 directory

#
#  Bootstrap files: cloud197_casa47.spw17.image   6.77 MB
#                   calib_split_07m.ms            0.36 GB
#                   calib_split_12m.ms            2.14 GB
#  Shortcut files:  cloud197_aver_07.ms           6.49 MB
#                   cloud197_aver_12.ms          26.56 MB


# parameters in this workflow
#   some options on how to set **line that we played with for debugging CASA 
line0 = {}
line1 = {'restfreq':'115.271202GHz', 'start':'256km/s', 'width':'-1.0km/s', 'nchan':43}  # native for MS starts at 256
line2 = {'restfreq':'115.271202GHz', 'start':'214km/s', 'width': '1.0km/s', 'nchan':43}  # native for TP starts
#line3 = qac_summary('cloud197_casa47.spw17.image',line=True)                            # starts at '214' forwards
#line4 = qac_summary('cloud197.im',line=True)                                            # starts at '256' backwards
line5 = {'restfreq':'115.271202GHz', 'start':'255km/s', 'width': '-1.0km/s', 'nchan':41} # remove edge channels 
line6 = {'restfreq':'115.271202GHz', 'start':'215km/s', 'width':  '1.0km/s', 'nchan':41} # remove edge channels

#   pick one here if you need a new aver (1,2,3,4 are valid)
#   although the regression is on line1, concat will then complain about:
#       "MSConcat::copySpwAndPol	Negative or zero total bandwidth in SPW 0 of MS to be appended."

line = line1

# set phasecenter from CRPIX in TP
phasecenter = 'J2000 05h39m50.000s -70d07m0.000s'
nsize       = 512
pixel       = 0.5

# done with prep, set filenames for remainder of this workflow
tpim  = 'cloud197_casa47.spw17.image'
ms07  = 'cloud197_aver_07.ms'
ms12  = 'cloud197_aver_12.ms'

ptg   = 'cloud197.ptg'

    
#   report
qac_version()

qac_log("SUMMARY-1")
#   these are the 3 datases we need for this demo
#   though it is also possible if the calib*ms files are present as aver*ms
qac_summary('cloud197_casa47.spw17.image',['calib_split_07m.ms','calib_split_12m.ms'])

#   cut down the big MS files to some common gridding for the TP if you don't have them yet
#   the original MS are large and have 4096 channels about 3x narrower.
if not QAC.iscasa(ms07):
    qac_log("MSTRANSFORM %s" % ms07)
    mstransform('calib_split_07m.ms',ms07,spw='3',
                datacolumn='DATA',outframe='LSRK',mode='velocity',regridms=True,nspw=1,keepflags=False,
                **line)
    tp2viswt(ms07)

if not QAC.iscasa(ms12):
    qac_log("MSTRANSFORM %s" % ms12)
    mstransform('calib_split_12m.ms',ms12,spw='0',
	        datacolumn='DATA',outframe='LSRK',mode='velocity',regridms=True,nspw=1,keepflags=False,
                **line)
    tp2viswt(ms12)

# get pointing (ptg) files [27 pointings in 12m data]
qac_ms_ptg(ms12, ptg)


qac_log("SUMMARY-2")
#  summary again of what goes into tp2vis
qac_summary(tpim,[ms07,ms12])

if False:
    qac_log("WEIGHT 7/12m")
    # set weights for 7m and 12m, classic style
    # mode=5 was removed
    tp2viswt(ms07,mode='constant',value=0.00168259119043)      # old: rms=77.4,mode=5)   -> sigmas = 24.3787
    tp2viswt(ms12,mode='constant',value=0.0103271634451)       # old: rms=24.2,mode=5)   -> sigmas =  9.84033


# the old benchmark is line2, line5/6 are the narrow one to avoid the rounding edge channel(s)
# line = line6


# MODE=3:  weights based on cube rms=0.7 (these two better give the same answer)
qac_log("TP2VIS for rms=0.7; should be wt=0.000492951")
qac_tp('test1',tpim,ptg,nsize,pixel,niter=0,phasecenter=phasecenter,rms=0.7)

#  7m and 12m maps 
qac_log("CLEAN1 7m")
qac_clean1('test1/clean_07',ms07,phasecenter=phasecenter)
qac_log("CLEAN1 12m")
qac_clean1('test1/clean_12',ms12,phasecenter=phasecenter)
qac_log("CLEAN1 7+12m")
qac_clean1('test1/clean_19',ms12,phasecenter=phasecenter,niter=[0,1000])

#
qac_log("CLEAN clean1")
qac_clean('test1/clean1','test1/tp.ms',[ms07,ms12],nsize,pixel,niter=0,phasecenter=phasecenter,do_alma=True,**line)
# -> 0.0016825911589 0.0103271631524 0.000492950784974
qac_beam('test1/clean1/tpalma.psf',plot='test1/clean1/qac_beam.png',normalized=True)


qac_log("TP2VISTWEAK")
tp2viswt([ms07,ms12,'test1/tp.ms'],makepsf=True,mode='beammatch')
tp2viswt('test1/tp.ms')
# -> 6.06322100793e-06
# -> 6.02673352617e-06
# -> 0.000004
# -> 0.0154292894853 (/GHz/arcmin2)
# -> 0.010785 
qac_log("CLEAN clean2")
qac_clean('test1/clean2', 'test1/tp.ms',[ms07,ms12],nsize,pixel,niter=[0,1000,3000,6000],phasecenter=phasecenter,**line)
qac_beam('test1/clean2/tpalma.psf',plot='test1/clean2/qac_beam.png',normalized=True)

tp2vistweak('test1/clean2/tpalma','test1/clean2/tpalma_2')
tp2vistweak('test1/clean2/tpalma','test1/clean2/tpalma_3')
tp2vistweak('test1/clean2/tpalma','test1/clean2/tpalma_4')


# standard plot (figure 5 in paper)
qac_log("TP2VISPL")
tp2vispl(['test1/tp.ms',ms07,ms12],outfig='cloud197_tp2viswt.png')

# figure 6 in the paper  (this would be ch. 10,12,14 instead of 32,30,28 if the counting the other way)
im1 = 'test1/clean_19/dirtymap_2.image'
qac_plot(im1, channel=32, range=[-0.1,0.7],plot='cloud197_fig6a.png')
qac_plot(im1, channel=30, range=[-0.1,0.7],plot='cloud197_fig6c.png')
qac_plot(im1, channel=28, range=[-0.1,0.7],plot='cloud197_fig6e.png')
im2 = 'test1/clean2/tpalma_2.tweak.image'
qac_plot(im2, channel=32, range=[-0.1,0.7],plot='cloud197_fig6b.png')
qac_plot(im2, channel=30, range=[-0.1,0.7],plot='cloud197_fig6d.png')
qac_plot(im2, channel=28, range=[-0.1,0.7],plot='cloud197_fig6f.png')



regres53 = [
    '9.877570407926104 6.5851462532089871 0.024031112244953266 68.426556567708786 0.0',
    '2.8247867816317078 1.5330676646622985 0.0033501510908012359 22.397469684140297 0.0',
    '11.989481698171243 19.321066930843013 0.00084640056317551 146.9541015625 0.0',
    '11.163420726184935 24.116404990046043 -5.2444772720336914 171.04049682617188 8296.5438525100362',
    '-0.035441727826304614 1.6549102460006135 -8.153564453125 12.290260314941406 -57.188675012915816',
    '1.8729262188544882e-05 0.055904175866136503 -0.3652036190032959 0.43035393953323364 2.1027231614271478',
    '11.616423569272547 22.881044821120195 -3.2347774505615234 116.06232452392578 1458.0533728181081',
    '-0.00083630229668520465 0.066161901221909208 -0.43350163102149963 0.5077061653137207 -90.332437173674265',
    '13.032492092947464 25.006721096615184 -3.5918662548065186 123.89888000488281 2975.304467219139',
    '1.1632156629021462 2.2462526685203232 -0.37595739960670471 13.236411094665527 106451.80247994595',
    'n/a',
    '0.0096026261940988979 0.069120621897063583 -0.38126686215400696 0.54493969678878784 1036.0245280584602',
    '0.010037090581118662 0.064678222714314754 -0.35336583852767944 0.47007161378860474 1082.8987635459323',
    '0.010037090581118662 0.064678222714314754 -0.35336583852767944 0.47007161378860474 1082.8987635459323',
    '0.011165944569510238 0.059245882183152437 -0.56456035375595093 0.50258070230484009 1204.6904897810948',
    '0.01665769771776791 0.12163394580363467 -0.65271222591400146 0.82595819234848022 5306.5685615435877',
    '0.01665769771776791 0.12163394580363467 -0.65271222591400146 0.82595819234848022 5306.5685615435877',
    '0.01724487125931046 0.11138953541636044 -0.65136933326721191 0.91245687007904053 5493.6218211543892',   
    ]

# casa 5.1.1-5   5.1.2- 5.1.0  
regres51 = [
    '9.877570407926104 6.5851462532089871 0.024031112244953266 68.426556567708786 0.0',
    '2.8247867816317078 1.5330676646622985 0.0033501510908012359 22.397469684140297 0.0',
    '11.989481698171243 19.321066930843013 0.00084640056317551 146.9541015625 0.0',
    '11.163420726184935 24.116404990046142 -5.2444772720336914 171.04049682617188 8296.5438525100362',
    '-0.036330356927820551 1.6607772927016984 -8.1663198471069336 12.327886581420898 -58.25972124053898',
    '-2.0915530825166225e-05 0.05358438743886932 -0.34954068064689636 0.41259616613388062 -2.3574292667507866',
    '11.983797069334358 23.51549844847785 -3.3448171615600586 118.739013671875 1424.8722054499115',
    'n/a',
    'n/a',
    '1.0611690595175243 2.1038598095124437 -1.0768193006515503 12.77895450592041 101587.30862181276',
    'n/a',
    '0.0070407065794689094 0.10378673247925574 -1.0768193006515503 1.1990959644317627 996.75837580318023',
    '0.013908774534664279 0.11433659681117944 -0.64769566059112549 1.7931338548660278 1033.3034295008188',
    '0.031769212125766076 0.30328606185389689 -0.64070063829421997 6.3540000915527344 1035.0506260654918',
    '0.059226289590482872 0.63682954852334184 -0.64305591583251953 13.560781478881836 1037.7366135096604',
    '0.02492396794697091 0.27294697835444254 -7.3966202735900879 1.5716098546981812 3499.5557926532701',
    '0.02125762633328631 0.41344099956466074 -21.223834991455078 2.788668155670166 2993.7986642026285',
    '0.020624674702782196 0.74810558932459337 -42.852672576904297 5.2685871124267578 2906.4855263245058',
    ]

# 5.0 is different yet again
regres50 = [
    '9.877570407926104 6.5851462532089871 0.024031112244953266 68.426556567708786 0.0',
    '2.8247867816317078 1.5330676646622985 0.0033501510908012359 22.397469684140297 0.0',
    '11.989481698171243 19.321066930843013 0.00084640056317551 146.9541015625 0.0',
    '11.163420726184935 24.116404990046142 -5.2444772720336914 171.04049682617188 8296.5438525100362',
    '-0.036472596575242142 1.6236285850974788 -7.9984612464904785 12.044713020324707 -58.555653966900294',
    '8.2350595030209075e-05 0.056177741355130886 -0.36660990118980408 0.43067702651023865 9.594487445365143',
    '12.519957675485461 24.633425313411088 -3.6731371879577637 125.13173675537109 1640.571937531854',
    'n/a',
    'n/a',
    '1.1220940801494657 2.2443008328800165 -1.1801495552062988 13.493011474609375 113489.64388755898',
    'n/a',    
    '0.0078148010392986335 0.11193670236987134 -1.1801495552062988 1.3113205432891846 1095.94976613821',
    '0.013383764572551922 0.11125993432888001 -0.66656875610351562 1.7141790390014648 1134.0676984917807',
    '0.020502341183792402 0.16946567022854803 -0.66546446084976196 3.5497148036956787 1134.8080412082832',
    '-0.36110709604885549 4.3755928090764522 -96.181510925292969 1.0185606479644775 1208.4817123198286',
    '0.017910462998345155 0.18998250609220915 -4.6762723922729492 1.4853593111038208 2512.6533850276155',
    '0.017454687367723397 0.24644413323122516 -10.315751075744629 2.2756485939025879 2450.3900345016618',
    '0.016973476546834655 5.0353456471091818 -39.86724853515625 283.76797485351562 2401.6858441991862',
]

r = regres51

eps = 0.0001
eps = None
                     
# regression
qac_stats(ms07,                               r[0], eps)
qac_stats(ms12,                               r[1], eps)
qac_stats('test1/tp.ms',                      r[2], eps)
qac_stats(tpim,                               r[3], eps)
qac_stats('test1/clean_07/dirtymap.image',    r[4], eps)
qac_stats('test1/clean_12/dirtymap.image',    r[5], eps)
qac_stats('test1/dirtymap.image',             r[6], eps)
qac_stats('test1/clean1/tpalma.image',        r[9], eps)
qac_stats('test1/clean2/tpalma.image',        r[11], eps)
qac_stats('test1/clean2/tpalma_2.image',      r[12], eps)
qac_stats('test1/clean2/tpalma_3.image',      r[13], eps)
qac_stats('test1/clean2/tpalma_4.image',      r[14], eps)
qac_stats('test1/clean2/tpalma_2.tweak.image',r[15], eps, pb='test1/clean2/tpalma.pb')
qac_stats('test1/clean2/tpalma_3.tweak.image',r[16], eps, pb='test1/clean2/tpalma.pb')
qac_stats('test1/clean2/tpalma_4.tweak.image',r[17], eps, pb='test1/clean2/tpalma.pb')

