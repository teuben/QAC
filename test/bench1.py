#  -*- python -*-
#
#------------------------------------------------------------------------------------------------------------------------------

# parameters in this benchmark workflow
test        = 'bench1'
phasecenter = 'J2000 12h22m54.900s +15d49m15.000s'
line        = {"restfreq":"115.271202GHz","start":"1500km/s", "width":"5km/s","nchan":5}
tpim        = 'M100_TP_CO_cube.bl.image'
ms07        = 'M100_aver_7.ms'
ms12        = 'M100_aver_12.ms'
nsize       = 800
pixel       = 0.5
niter       = [0,100,300,1000]

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

print "Continuing benchmark with clean=1"
qac_clean(test+'/clean',tpms,[ms12,ms07],nsize,pixel,niter=niter,phasecenter=phasecenter,**line)

print "Continuing benchmark with tweak=1"
# loop over all 2nd and higher iterations and tweak them 
for i in range(1,len(niter)): 
    inamed = test+'/clean/tpint'
    inamec = test+'/clean/tpint_%d' % (i+1)
    tp2vistweak(inamed,inamec)
    inamet = test+'/clean/tpint_%d.tweak.image' % (i+1)
    qac_plot(inamec+'.image')
    qac_plot(inamet)    
    
# regression only valid with no cmdline argument
r1 = "0.0038324075245612802 0.021439737328652425 -0.04851343110203743 0.41929441690444946 383.60319947466479"
r2 = "0.0038324084555372423 0.021439742878458009 -0.048513446003198624 0.41929447650909424 383.60327838373536"   # 5.2.1

qac_stats(test+'/clean/tpint.image')
qac_stats(test+'/clean/tpint_4.tweak.image', r2)

# final plot if enough data was accumulated for this comparison
if True:
    print "Plotting benchmark comparison"
    a1=test+'/clean/tpint.image'
    a2=test+'/clean/tpint_2.image'
    a3=test+'/clean/tpint_3.image'
    a4=test+'/clean/tpint_4.image'
    b2=test+'/clean/tpint_2.tweak.image'
    b3=test+'/clean/tpint_3.tweak.image'
    b4=test+'/clean/tpint_4.tweak.image'

    #                           0              0
    images = [a1,a2,  a2,a3,  a3,a4,  b2,b3,  b3,b4,  b2,a2,  b3,a3,  b4,a4]
    y      = ['tp12', 'tp23', 'tp34', 'tw23', 'tw34', 'ttt2', 'ttt3', 'ttt4']
    x      = ['*','*','-diff*10']
    qac_plot_grid(images,ncol=2,diff=10,box=[200,200,600,600],xgrid=x,ygrid=y,plot=test+'/bench-cmp.png')

