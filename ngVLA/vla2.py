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
#niter        = [0,1000]

# pick which ngVLA configurations you want (0=SSA, 1=core 2=plains 3=all 4=all+GB+VLBA)
cfg          = [0,1]

# integration times (see also below for alternative equal time per pointing observations)
times        = [2, 1]     # hrs observing and mins integrations

# grid spacing for mosaic pointings  (18m -> 15"   6m -> 50" but 6m is controlled with gfactor)
grid         = 15
#grid         = 20

# tp dish size (18, 45, 100m are the interesting choices to play with)
dish         = 45

# scaling factors 
wfactor      = 0.01   # weight mult for cfg=0 (@todo)
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

dishlabel = str(dish)             #  can also be ""


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
        # scale down the 6m data based on inspection of tp2vispl()
        tp2viswt(ms1[c],mode='mult',value=wfactor)
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
otf = qac_tp_otf(pdir+'/clean3', startmodel, dish, label=dishlabel, template=pdir+'/clean3/dirtymap.image')


#@todo check naming - int vs dirtymap
qac_log("FEATHER")
# combine TP + INT using feather and ssc, for all niter's (even though the first one is not valid)
for idx in range(len(niter)):
    qac_feather(pdir+'/clean3',             niteridx=idx, label=dishlabel, name="dirtymap")
    qac_ssc    (pdir+'/clean3',             niteridx=idx, label=dishlabel, name="dirtymap")
    qac_plot   (pdir+'/clean3/dirtymap%s.image.pbcor'  %            QAC.label(idx))
    qac_plot   (pdir+'/clean3/feather%s%s.image.pbcor' % (dishlabel,QAC.label(idx)))
    qac_plot   (pdir+'/clean3/ssc%s%s.image'           % (dishlabel,QAC.label(idx)))
qac_smooth (pdir+'/clean3', startmodel, name="dirtymap")
    
qac_plot(pdir+'/clean3/skymodel.smooth.image')
qac_plot(pdir+'/clean3/dirtymap.pb')
qac_plot(otf + '.pbcor')

# check the fluxes
qac_log("REGRESSION")

for idx in range(len(niter)):
    qac_stats(pdir+'/clean3/dirtymap%s.image'         %            QAC.label(idx))    
    qac_stats(pdir+'/clean3/dirtymap%s.image.pbcor'   %            QAC.label(idx))
    qac_stats(pdir+'/clean3/ssc%s%s.image'            % (dishlabel,QAC.label(idx)))
    qac_stats(pdir+'/clean3/feather%s%s.image'        % (dishlabel,QAC.label(idx)))
qac_stats(pdir+'/clean3/skymodel.smooth.image')
qac_stats(otf + '.pbcor')
qac_stats(model)

# a bunch of plots
idx0 = len(niter)-1    # index of last niter[] for plotting

qac_log("MONTAGE1")

i1 = pdir+'/clean3/dirtymap%s.image.pbcor.png'   %            QAC.label(idx0)
i2 = otf + '.pbcor.png'
i3 = pdir+'/clean3/feather%s%s.image.pbcor.png'  % (dishlabel,QAC.label(idx0))
i4 = pdir+'/clean3/skymodel.smooth.image.png'
i0 = pdir+'/clean3/montage1.png'
cmd  = "montage -title %s %s %s %s %s -tile 2x2 -geometry +0+0 %s" % (pdir,i1,i2,i3,i4,i0)
os.system(cmd)

qac_log("PLOT_GRID plots 1 and 2")

a1 = pdir+'/clean3/dirtymap.image'
a2 = pdir+'/clean3/dirtymap%s.image'        %            QAC.label(idx0)
a3 = otf
a4 = pdir+'/clean3/feather%s%s.image'       % (dishlabel,QAC.label(idx0))
a5 = pdir+'/clean3/skymodel.smooth.image'
a6 = pdir+'/clean3/ssc%s%s.image'           % (dishlabel,QAC.label(idx0))

try:
    qac_plot_grid([a1, a2, a2, a3, a4, a3], diff=10, plot=pdir+'/plot1.cmp.png', labels=True)
    qac_plot_grid([a2, a5, a4, a6, a4, a5], diff=10, plot=pdir+'/plot2.cmp.png', labels=True)
except:
    print "qac_plot_grid failed"

# plot1:
# niter=0    | niter=1000 | diff
# niter=1000 | otf        | diff
# feather_2  | otf        | diff
    
# plot2:
# niter=1000 | skymodel | diff
# feather_2  | ssc_2    | diff
# feather_2  | skymodel | diff

qac_log("POWER SPECTRUM DENSITY")
try:
    qac_psd([startmodel, a2, a4, a5], plot=pdir+'/'+pdir+'.psd.png')
except:
    print "qac_psf failed"

qac_log("DONE!")
qac_end()
