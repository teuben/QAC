# -*- python -*-
#
#  Play with the skymodel and various ngVLA configurations
#     - one or full pointing set
#     - options for feather, ssc
#
#  Reminder: at 115 GHz we have: [FWHM" ~ 600/DishDiam]
#
#      18m PB is ~33"
#       6m PB is ~100"
#      25m PB is ~25"
#      50m PB is ~12"
#
#  Timing:
#           ..
#  Memory:
#           ..
#  Space:
#           ..

pdir         = 'vla2'                               # name of directory within which everything will reside
model        = '../models/skymodel.fits'            # this has phasecenter with dec=-30 for ALMA sims
phasecenter  = 'J2000 180.000000deg 40.000000deg'   # where we want this model to be on the sky, at VLA

# pick the piece of the model to image, and at what pixel size
# natively this model is 4096 pixels at 0.05"
# @todo qac_tp_vis handles this differently from simobserve()
imsize_m     = 4096
pixel_m      = 0.05

# pick the sky imaging parameters (for tclean)
# The product of these typically will be the same as that of the model (but don't need to)
# pick the pixel_s based on the largest array configuration (see below) choosen
imsize_s     = 1024
pixel_s      = 0.2

# pick a few niter values for tclean to check flux convergence ; need at least two to get feather/ssc
#niter        = [0,500,1000,2000]
#niter        = [0,100]
#niter        = [0,100,1000]
#niter        = [0]
niter        = [0,500,1000,2000,4000]
niter        = [0,1000]

# pick which ngVLA configurations you want (0=SSA, 1=core 2=plains 3=all 4=all+GB+VLBA)
cfg          = [0,1]

# integration times
times        = [2, 1]     # hrs observing and mins integrations

# grid spacing for mosaic pointings  (18m -> 15"   6m -> 50" but 6m is controlled with gfactor)
grid         = 15
grid         = 20

# tp dish size (18, 45, 100m are the interesting choices to play with)
dish         = 45

# scaling factors 
wfactor      = 0.01   # (only needed for tp2vis)
afactor      = 1      # not implemented yet
gfactor      = 3.0    # 18m/6m ratio of core/SBA dishes (should probably remain at 3)
pfactor      = 1.0    # pixel size factor for both pixel_m and pixel_s

# -- do not change parameters below this ---
import sys
for arg in qac_argv(sys.argv):
    exec(arg)

# derived parameters
ptg  = pdir + '.ptg'              # pointing mosaic for the ptg
ptg0 = pdir + '.0.ptg'            # pointing mosaic for the ptg

pixel_m = pixel_m * pfactor
pixel_s = pixel_s * pfactor

# report, add Dtime
qac_begin(pdir,False)
qac_log("REPORT")
qac_version()
tp2vis_version()

# create a mosaic of pointings for the TP 'dish'
p = qac_im_ptg(phasecenter,imsize_m,pixel_m,grid,rect=True,outfile=ptg)
print "Using %d pointings for 18m and grid=%g on fieldsize %g" % (len(p), grid, imsize_m*pixel_m)

grid0 = grid * gfactor
p0 = qac_im_ptg(phasecenter,imsize_m,pixel_m,grid0,rect=True,outfile=ptg0)
print "Using %d pointings for  6m and grid0=%g on fieldsize %g" % (len(p0), grid0, imsize_m*pixel_m)

#
if True:
    # test alternative setting of times so each pointing gets one cycle, and the SBA gets more time
    times  = [len(p)/60.0, 1.0/gfactor]
    times0 = [len(p)/60.0, 1.0]
else:
    times0 = times

# vpmanager for SSA dishes
# to get create custom voltage pattern table for SSA (from brian mason memo 43)
# really only have to do this once because the table can then be loaded
#vp.reset()
#vp.setpbairy(telescope='NGVLA', dishdiam=6.0, blockagediam=0.0, maxrad='3.5deg', reffreq='1.0GHz', dopb=True)
#vp.setpbairy(telescope='NGVLA', dishdiam=18.0, blockagediam=0.0, maxrad='3.5deg', reffreq='1.0GHz', dopb=True)
#vp.saveastable('sba.tab')

qac_project(pdir)
# create an MS based on a model and antenna configuration for VLA
qac_log("ngVLA")
ms1={}
for c in cfg:
    if c == 0:
        # could consider multiplying times by gfactor^2
        print "qac_vla times=",times0
        ms1[c] = qac_vla(pdir,model,imsize_m,pixel_m,cfg=c,ptg=ptg0, phasecenter=phasecenter, times=times0)
    else:
        print "qac_vla times=",times
        ms1[c] = qac_vla(pdir,model,imsize_m,pixel_m,cfg=c,ptg=ptg,  phasecenter=phasecenter, times=times)
# startmodel for later
startmodel = ms1[cfg[0]].replace('.ms','.skymodel')

# find out which MS we got for the INT, or use intms = ms1.values()
intms = ms1.values()

# tp2vispl - doesn't plot in multiple colors yet
tp2vispl(intms, outfig=pdir+'/tp2vispl.png')

qac_log("CLEAN")
qac_clean1(pdir+'/clean3', intms, imsize_s, pixel_s, phasecenter=phasecenter, niter=niter)

qac_log("BEAM")
qac_beam(pdir+'/clean3/dirtymap.psf', plot=pdir+'/clean3/dirtymap.psf.png')

qac_log("OTF")
# create an OTF TP map using a given dish size
qac_tp_otf(pdir+'/clean3', startmodel, dish, template=pdir+'/clean3/dirtymap.image')


#@todo check naming - int vs dirtymap
qac_log("FEATHER")
# combine TP + INT using feather and ssc, for all niter's
for idx in range(len(niter)):
    qac_feather(pdir+'/clean3',             niteridx=idx, name="dirtymap")
    qac_ssc    (pdir+'/clean3',             niteridx=idx, name="dirtymap")
    qac_smooth (pdir+'/clean3', startmodel, niteridx=idx, name="dirtymap")
    qac_plot   (pdir+'/clean3/dirtymap%s.image.pbcor' % QAC.label(idx))
    qac_plot   (pdir+'/clean3/feather%s.image.pbcor' % QAC.label(idx))
    qac_plot   (pdir+'/clean3/ssc%s.image' % QAC.label(idx))
    
qac_plot(pdir+'/clean3/skymodel.smooth.image')
qac_plot(pdir+'/clean3/dirtymap.pb')
qac_plot(pdir+'/clean3/otf.image.pbcor')

# the real flux
qac_log("REGRESSION")

qac_stats(model)
qac_log("Niter = 0 Cleaning")
qac_stats(pdir+'/clean3/dirtymap.image')
qac_stats(pdir+'/clean3/dirtymap.image.pbcor')
qac_stats(pdir+'/clean3/skymodel.smooth.image')
qac_stats(pdir+'/clean3/otf.image')
qac_stats(pdir+'/clean3/otf.image.pbcor')
qac_stats(pdir+'/clean3/ssc.image')
qac_stats(pdir+'/clean3/feather.image')

qac_log("Niter = 1000 Cleaning")
qac_stats(pdir+'/clean3/dirtymap_2.image')
qac_stats(pdir+'/clean3/dirtymap_2.image.pbcor')
qac_stats(pdir+'/clean3/skymodel_2.smooth.image')
qac_stats(pdir+'/clean3/otf.image')
qac_stats(pdir+'/clean3/otf.image.pbcor')
qac_stats(pdir+'/clean3/ssc_2.image')
qac_stats(pdir+'/clean3/feather_2.image')


qac_log("PLOT_GRID plots 1 and 2")
a1 = pdir+'/clean3/dirtymap.image'
a2 = pdir+'/clean3/dirtymap_2.image'
a3 = pdir+'/clean3/otf.image'
a4 = pdir+'/clean3/feather_2.image'
a5 = pdir+'/clean3/skymodel.smooth.image'
a6 = pdir+'/clean3/ssc_2.image'

# plot 1:
# niter=0    | niter=1000 | diff
# niter=1000 | otf        | diff
# feather_2  | otf        | diff
qac_plot_grid([a1, a2, a2, a3, a4, a3],diff=10, plot=pdir+'/plot1.cmp.png', labels=True)

# plot 2:
# niter=1000 | skymodel | diff
# feather_2  | ssc_2    | diff
# feather_2  | skymodel | diff
qac_plot_grid([a2, a5, a4, a6, a4, a5], diff=10, plot=pdir+'/plot2.cmp.png', labels=True)

qac_log("POWER SPECTRUM DENSITY")
qac_psd([startmodel, pdir+'/clean3/dirtymap_2.image',pdir+'/clean3/feather_2.image'], plot=pdir+'/'+pdir+'.psd.png')

qac_log("DONE!")
qac_end()

"""
How to compare PDS plot?

p1 = qac_pds()
p2 = qac_pds()
r1 = np.arange(1,len(p1)+1)

plt.figure()
plt.loglog(r1,p1)
plt.loglog(r1,p2)
plt.show()
plt.savefig('cmp12.png')

p1=qac_psd('skymodel1.im')
r1=np.arange(1,len(p1)+1)

p2=qac_psd('skymodel2s.im')
imsmooth('skymodel2.im','gaussian','10arcsec','10arcsec',pa='0deg',outfile='skymodel2ss.im',overwrite=True)
p3=qac_psd('skymodel2ss.im')
imsmooth('skymodel2.im','gaussian','0.1arcsec','0.1arcsec',pa='0deg',outfile='skymodel2sss.im',overwrite=True)
p4=qac_psd('skymodel2sss.im')

plt.figure()
plt.loglog(r1,p1)
plt.loglog(r1,p2)
plt.loglog(r1,p3)
plt.loglog(r1,p4)



"""
