# -*- python -*-
#
#  Play with the skymodel and various ngVLA configurations
#     - one or full pointing set
#     - options for feather, ssc
#     - options for dish size of TP
#
#  Reminders: at 115 GHz we have: [PB FWHM" ~ 600/DishDiam]
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
imsize_s     = 2048
pixel_s      = 0.1

# pick a few niter values for tclean to check flux convergence ; need at least two to get feather/ssc
#niter        = [0,500,1000,2000]
#niter        = [0,100]
#niter        = [0,100,1000]
#niter        = [0]
niter        = [0,500,1000,2000,4000]
#niter        = [0,1000]

# pick which ngVLA configurations you want (0=SBA, 1=core 2=plains 3=all 4=all+GB+VLBA)
#   [0,1,2] needs 0.02 pixels, since we don't have those, can only map inner portion
#   pixel_m = 0.01 imsize_s=2048 pixel_s=0.02
cfg          = [0,1]

# integration times (see also below for alternative equal time per pointing observations)
times        = [4, 1]     # hrs observing and mins integrations

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
tfactor      = 2.0    # extra time factor to apply to SBA

# multi-scale? - Use [0] or None if you don't want it
scales       = [0, 10, 30]

# simplenoise level
noise        = 0.0

# clean maps (set to 0 if you just want the ms file(s)
clean        = 1

# -- do not change parameters below this ---
import sys
for arg in qac_argv(sys.argv):
    exec(arg)

# derived parameters
ptg  = pdir + '.ptg'              # pointing mosaic for the ptg
ptg0 = pdir + '.0.ptg'            # pointing mosaic for the ptg

pixel_m = pixel_m * pfactor       # simple rescale model map
pixel_s = pixel_s * pfactor       #

dishlabel = str(dish)             #  can also be ""

if niter==0:   niter=[0]          # be nice to allow this, but below it does need to be a list


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
if False:
    # test alternative setting of times so each pointing gets one cycle, and the SBA gets more time
    times  = [len(p)/60.0,  0.25]
    times0 = [tfactor*len(p0)/60.0, 0.25]
    print "TIMES: ",times0,times
else:
    # all the same
    times0 = times

# vpmanager for SBA dishes
# to get create custom voltage pattern table for SBA (from brian mason memo 43)
# really only have to do this once because the table can then be loaded
#vp.reset()
#vp.setpbairy(telescope='NGVLA', dishdiam=6.0, blockagediam=0.0, maxrad='3.5deg', reffreq='1.0GHz', dopb=True)
#vp.setpbairy(telescope='NGVLA', dishdiam=18.0, blockagediam=0.0, maxrad='3.5deg', reffreq='1.0GHz', dopb=True)
#vp.saveastable('sba.tab')

# start with a clean project
qac_project(pdir)

# create an MS based on a model and for each ngVLA antenna configuration
# the emperical procedure using the noise= keyword and using qac_noise() is courtesy Carilli et al. (2017)
qac_log("ngVLA")
ms1={}
for c in cfg:
    if c == 0:
        ms1[c] = qac_vla(pdir,model,imsize_m,pixel_m,cfg=c,ptg=ptg0, phasecenter=phasecenter, times=times0, noise=-noise)
        # bootstrap setting noise
        if noise > 0:
            sn0 = qac_noise(noise,pdir+'/clean3_noise', ms1[c], imsize_s, pixel_s, phasecenter=phasecenter)
            print("QAC_NOISE: %g" % sn0)
            ms1[c] = qac_vla(pdir,model,imsize_m,pixel_m,cfg=c,ptg=ptg0, phasecenter=phasecenter, times=times0, noise=sn0)            
        if False:
            # scale down the 6m data based on inspection of tp2vispl() ???
            tp2viswt(ms1[c],mode='mult',value=wfactor)
    else:
        ms1[c] = qac_vla(pdir,model,imsize_m,pixel_m,cfg=c,ptg=ptg,  phasecenter=phasecenter, times=times, noise=-noise)
        # bootstrap setting noise
        if noise > 0:
            sn0 = qac_noise(noise,pdir+'/clean3_noise', ms1[c], imsize_s, pixel_s, phasecenter=phasecenter)
            print("QAC_NOISE: %g" % sn0)
            ms1[c] = qac_vla(pdir,model,imsize_m,pixel_m,cfg=c,ptg=ptg, phasecenter=phasecenter, times=times, noise=sn0)            
        
# save a startmodel name for later
startmodel = ms1[cfg[0]].replace('.ms','.skymodel')

# find out which MS we got for the INT, or use intms = ms1.values()
intms = ms1.values()

# tp2vispl - doesn't plot in multiple colors yet
tp2vispl(intms, outfig=pdir+'/tp2vispl.png')

if clean == 0:
    qac_log("DONE! (no cleaning requested)")
    qac_end()
    sys.exit(0)
    

# @todo  use **args e.g. args['gridder'] = 'standard' if only one pointing in one config

qac_log("CLEAN")
qac_clean1(pdir+'/clean3', intms, imsize_s, pixel_s, phasecenter=phasecenter, niter=niter, scales=scales)

qac_log("BEAM")
qac_beam(pdir+'/clean3/dirtymap.psf', plot=pdir+'/clean3/dirtymap.beam.png')

qac_log("OTF, SMOOTH and plots")
# create an OTF TP map using a given dish size
otf = qac_tp_otf(pdir+'/clean3', startmodel, dish, label=dishlabel, template=pdir+'/clean3/dirtymap.image')

qac_smooth (pdir+'/clean3', startmodel, name="dirtymap")
qac_plot(pdir+'/clean3/skymodel.smooth.image')
qac_plot(pdir+'/clean3/dirtymap.psf')
qac_plot(pdir+'/clean3/dirtymap.pb')
qac_plot(otf + '.pbcor')

if len(niter) == 1:
    qac_log("DONE! (no niters set, only dirty map)")
    qac_end()
    sys.exit(0)

qac_log("FEATHER")
# combine using feather and ssc, for all niter's (even though the first one is not valid)
for idx in range(len(niter)):
    qac_feather(pdir+'/clean3',             niteridx=idx, label=dishlabel, name="dirtymap")
    qac_ssc    (pdir+'/clean3',             niteridx=idx, label=dishlabel, name="dirtymap")
    qac_plot   (pdir+'/clean3/dirtymap%s.image.pbcor'  %            QAC.label(idx))
    qac_plot   (pdir+'/clean3/feather%s%s.image.pbcor' % (dishlabel,QAC.label(idx)))
    qac_plot   (pdir+'/clean3/ssc%s%s.image'           % (dishlabel,QAC.label(idx)))

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

# make a bunch of plots
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

b=range(len(niter))
for idx in range(len(niter)):
    b[idx] = pdir+'/clean3/dirtymap%s.image' %            QAC.label(idx)
bg = []
for idx in range(len(niter)-1):
    bg.append(b[idx])
    bg.append(b[idx+1])
bg.append(b[0])
bg.append(b[idx0])
    

try:
    qac_plot_grid([a1, a2, a2, a3, a4, a3], diff=10, plot=pdir+'/plot1.cmp.png', labels=True)
    qac_plot_grid([a2, a5, a4, a6, a4, a5], diff=10, plot=pdir+'/plot2.cmp.png', labels=True)
    qac_plot_grid(bg,                       diff=10, plot=pdir+'/plot3.cmp.png', labels=True)    
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

qac_log("FIDELITY")
qac_fidelity(pdir+'/clean3/skymodel.smooth.image',pdir+'/clean3/dirtymap%s.image'% QAC.label(idx0), figure_mode=[1,2,3,4,5])
qac_fidelity(pdir+'/clean3/skymodel.smooth.image',pdir+'/clean3/feather%s%s.image'% (dishlabel,QAC.label(idx0)), figure_mode=[1,2,3,4,5])

qac_log("DONE!")
qac_end()
