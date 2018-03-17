#  -*- python -*-
# Resources:   MEM: 2.2 GB   DISK: 230MB  CPU: ~8'
#
# parameters in this workflow (derived from bench.py)
phasecenter = 'J2000 12h22m54.900s +15d49m15.000s'
line        = {"restfreq":"115.271202GHz","start":"1500km/s", "width":"5km/s","nchan":1}
chans       = '20'                   # must agree with the line={}    @todo casa regrid bug?
tpim        = 'M100_TP_CO_cube.bl.image'
ms07        = 'M100_aver_7.ms'
ms12        = 'M100_aver_12.ms'
nsize       = 800
pixel       = 0.5
niter       = [0,1000]

#-- do not change parameters below this ---
import sys
for arg in qac_argv(sys.argv):
    exec(arg)

#-- hardcoded for this demo
tpms   = 'bench0/tp.ms'
ptg    = 'bench0.ptg'

#-- take subimage so we only have 1 channel (our later regrid in doesn't seem to follow the spectral axis, bug?)
if False:
    tpim2 = tpim+'_'+chans
    imsubimage(tpim,tpim2,chans=chans,overwrite=True)
else:
    tpim2 = tpim

# get a pointing text file from the 12m array
qac_ms_ptg(ms12,ptg)

# run tp2vis and plot weights to compare to 12m/7m - this is where a new bench0 directory is created
qac_tp_vis('bench0',tpim2,ptg,rms=0.15)
tp2vispl([tpms,ms07,ms12],outfig='bench0/tp2vispl_rms.png')
if True:
    imsubimage(tpim,'bench0/tp.im',chans=chans)
    tpim2 = 'bench0/tp.im'

# joint deconvolution tclean (use the **line dictionary to pass other parameters to tclean)
line['scales'] = [0]
qac_clean('bench0/clean',tpms,[ms12,ms07],nsize,pixel,niter=niter,phasecenter=phasecenter,do_alma=True,**line)
# JvM tweak
tp2vistweak('bench0/clean/tpalma', 'bench0/clean/tpalma_2')
# classic feather
qac_feather('bench0','bench0/clean/alma_2.image',tpim2)
# Faridani's SSC
qac_ssc('bench0','bench0/clean/alma_2.image',tpim2, regrid=True, cleanup=False)

# plot various comparisons; difference maps are in the 3rd column of the plot_grid
i1    = 'bench0/clean/alma.image'
i2    = 'bench0/clean/tpalma.image'
i3    = 'bench0/clean/alma_2.image'
i4    = 'bench0/clean/tpalma_2.image'
i5    = 'bench0/clean/tpalma_2.tweak.image'
i6    = 'bench0/feather.image'
i7    = 'bench0/ssc.image'
ygrid = ['7&12 + tp', '7&12 iter','7&12&tp iter','tweak', 'feather', 'ssc']
box   = [300,300,600,600]
qac_plot_grid([i1,i2, i1,i3, i2,i4, i5,i4, i6,i4, i6,i7],box=box,ygrid=ygrid,plot='bench0/bench0.cmp.png',diff=10.0)

# regression for casa 5.2.2-4 on RHEL7; the last column is the flux in Jy.km/s
r = [
    '0.76510686740198042 1.4994149478897942 -0.43156760931015015 6.4568653106689453 15.995818049860048',
    '0.00015477320920210852 0.036285694517807124 -0.12811994552612305 0.37910208106040955 0.30861407063317348',
    '0.0081229104489462297 0.039351242931759012 -0.084907762706279755 0.42440503835678101 16.006177593355094',
    '0.0034475503699085723 0.019158814084816258 -0.036495275795459747 0.35947218537330627 13.804154300264859',
    '0.0036214721951210163 0.020606721088766405 -0.042894229292869568 0.35897329449653625 14.714903120723477',
    '0.0036216214701859607 0.020609756591263156 -0.042896430939435959 0.35902613401412964 14.715509660826687',
    ]

eps = None
qac_stats('bench0/tp.im',                     r[0], eps)
qac_stats('bench0/clean/alma.image',          r[1], eps)
qac_stats('bench0/clean/tpalma.image',        r[2], eps)
qac_stats('bench0/clean/tpalma_2.tweak.image',r[3], eps)
qac_stats('bench0/ssc.image',                 r[4], eps)
qac_stats('bench0/feather.image',             r[5], eps)