#
# 
#  This test takes about 200 MB of disk space, and needs about 3 GB memory
#
#  238.81user 18.62system 3:08.69elapsed 136%CPU (0avgtext+0avgdata 3383756maxresident)
#

test         = 'test5'
model        = '../models/field000.fits'           # this has phasecenter with dec=-30 for ALMA sims
phasecenter  = 'J2000 180.000000deg 40.000000deg'  # so modify this for ngVLA

# pick the piece of the model to image, and at what pixel size
# natively this model is 4096 pixels at 0.05"
imsize_m     = 512
pixel_m      = 0.1

# pick the sky imaging parameters (for tclean)
imsize_s     = 512
pixel_s      = 0.1

# pick a few niter values for tclean to check flux convergence 
niter        = [0,250,500,1000,2000,4000,6000,8000]
#niter        = [0]

# -- do not change parameters below this ---
import sys
for arg in qac_argv(sys.argv):
    exec(arg)

ptg = test + '.ptg'              # use a single pointing mosaic for the ptg
if type(niter) != type([]): niter = [niter]


# report
qac_log("TEST: %s" % test)
qac_begin(test)
qac_version()

# create a single pointing mosaic
qac_ptg(phasecenter, ptg)

# create a MS based on a model and antenna configuration
qac_log("VLA")
ms1 = qac_vla(test, model, imsize_m, pixel_m, cfg=1, ptg=ptg, phasecenter=phasecenter)

# image and clean this interferometric map a bit
qac_log("CLEAN")
qac_clean1(test+'/clean1', ms1, imsize_s, pixel_s, phasecenter=phasecenter, niter=niter)

# create two example OTF TP maps to contrast
skymodel = ms1.replace('.ms','.skymodel')
qac_log("OTF %s" % skymodel)
qac_tp_otf(test+'/clean1', skymodel, 45.0, label="45")
qac_tp_otf(test+'/clean1', skymodel, 18.0, label="18")

# combine TP + INT using feather, for all niter's used before
qac_log("FEATHER")
for idx in range(len(niter)):
    qac_feather(test+'/clean1', label="45", niteridx=idx)
    qac_feather(test+'/clean1', label="18", niteridx=idx)

skymodel = ms1.replace('.ms','.skymodel')
a=range(len(niter))
b=range(len(niter))
for idx in range(len(niter)):
    if idx==0:
        a[idx] = test + '/clean1/dirtymap.image.pbcor'
    else:
        a[idx] = test + '/clean1/dirtymap_%d.image.pbcor' % (idx+1)
    b[idx] = qac_smooth('test5/clean1',skymodel,'dirtymap',niteridx=idx)


    
cfp=[]
for idx in range(len(niter)):
    cfp.append(a[idx])
    cfp.append(b[idx])
qac_plot_grid(cfp,diff=10,plot=test+'/cmp1.png')

cfp=[]
for idx in range(1,len(niter)):
    cfp.append(a[idx-1])
    cfp.append(a[idx])

qac_plot_grid(cfp,diff=10,plot=test+'/cmp2.png')


qac_stats_grid(a)
qac_stats(b[0])







#
# --------------------------------------------------------------------------------------------------------------
# regression

regress51 = [
    #0.0067413167369070152 0.010552344105428218 0.0 0.10000000149011612 113100.52701950417",   # where did this come from?
    "0.0067413167369069988 0.010552344105427177 0.0 0.10000000149011612 113100.52701950389",
    "376.81918701712272 791.0277433970175 0.25461947454935646 20152.279939787601 0.0",
    "1.5290900359629713 21.309509122997337 -37.884723663330078 85.392372131347656 1218.8355360146788",
    "42668.1077336737 44654.739711457922 13273.1376953125 67745.1171875 70071.789310851134",
    "6570.3070261008925 8953.8105374926636 309.4671630859375 24888.931640625 60026.507913198388",
    "14.774882361675623 23.377433067737787 -7.3271188735961914 137.7615966796875 63317.084178311772",
    "25.239792422269797 33.841414373223429 -36.166255950927734 180.94865417480469 108163.97872576566",
    "9.9542300510560686 17.099277097148892 -17.992568969726562 114.72189331054688 42658.398669071932",
    "19.474530926399115 28.794431828862734 -30.066720962524414 181.16015625 83457.213655954009",
]

r = regress51


qac_log("**** REGRESSION STATS ****")

# regression
qac_stats(model,                                 r[0])
qac_stats('test1/test1.SWcore.ms',               r[1])
qac_stats('test1/clean1/dirtymap.image',         r[2])
qac_stats('test1/clean1/otf18.image.pbcor',      r[3])
qac_stats('test1/clean1/otf45.image.pbcor')
qac_stats('test1/clean1/dirtymap.image.pbcor')
qac_stats('test1/clean1/dirtymap_2.image.pbcor')
qac_stats('test1/clean1/dirtymap_3.image.pbcor')
qac_stats('test1/clean1/feather18.image.pbcor')
qac_stats('test1/clean1/feather18_2.image.pbcor')
qac_stats('test1/clean1/feather18_3.image.pbcor')
qac_stats('test1/clean1/feather45.image.pbcor')
qac_stats('test1/clean1/feather45_2.image.pbcor')
qac_stats('test1/clean1/feather45_3.image.pbcor')

# done
qac_end()
