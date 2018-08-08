# -*- python -*-
#
#  Play with the skymodel and various ngVLA configurations
#     - one or full pointing set
#     - options for feather, ssc
#     - options for dish size of TP
#
#  Reminders: at 115 GHz we have: [PB FWHM" ~ 600/DishDiam]
#
#       6m PB is ~100"
#      18m PB is ~33"
#      25m PB is ~25"
#      45m PB is ~13"
#     100m PB is ~6"
#
#  Timing:
#           ..
#  Memory:
#           ..
#  Space:
#           ..

pdir         = 'map2'                               # name of directory within which everything will reside
model        = '../models/skymodel.fits'            # this has phasecenter with dec=-30 for ALMA sims
dec          = 40.0                                 # Declination

# pick the piece of the model to image, and at what pixel size
# natively this model is 4096 pixels at 0.05" (or a 200" sky) - we use 100" sky to speed things up a bit
imsize_m     = 4096
pixel_m      = 0.005

# pick the sky imaging parameters (for tclean)
# The product of these typically will be the same as that of the model (but don't need to)
# pick the pixel_s based on the largest array configuration (see below) choosen
# If pixel_s is negative, it will be computed based on imsize*pixel for both _m and _s being same
imsize_s     = 512
pixel_s      = -1

# pick a few niter values for tclean to check flux convergence ; need at least two to get feather/ssc
#niter        = [0,100]
#niter        = [0]
niter        = [0,500,1000,2000,4000,8000]
niter        = [0,1000]
#niter = range(0,5000,1000)

# pick which ngVLA configurations you want (0=SBA, 1=core 2=plains 3=all 4=all+GB+VLBA)
#   [0,1,2] needs 0.02 pixels, since we don't have those, can only map inner portion
#   pixel_m = 0.01 imsize_s=2048 pixel_s=0.02
cfg          = [1]

# integration times (see also below for alternative equal time per pointing observations)
times        = [8, 1]     # hrs observing and mins integrations

# grid spacing for mosaic pointings  (18m -> 15"   6m -> 50" but 6m is controlled with gfactor)
grid         = 0

# tp dish size (18, 45, 100m are the interesting choices to play with)
dish         = 45

# scaling factors 
wfactor      = 1      # weight mult for cfg=0 
afactor      = 1      # not implemented yet
gfactor      = 3.0    # 18m/6m ratio of core/SBA dishes (should probably remain at 3)
pfactor      = 1.0    # pixel size factor for both pixel_m and pixel_s
tfactor      = 2.0    # extra time factor to apply to SBA (not used)

# multi-scale? - Use [0] or None if you don't want it
scales       = [0, 10, 30]

# simplenoise level
noise        = 0.0

# clean maps (set to 0 if you just want the ms file(s)
clean        = 1

# fidelity for all iterations? (default is last one only)
fidall       = 0

# -- do not change parameters below this ---
import sys
for arg in qac_argv(sys.argv):
    exec(arg)

# derived parameters
ptg  = pdir + '.ptg'              # pointing mosaic for the ptg
ptg0 = pdir + '.0.ptg'            # pointing mosaic for the ptg

phasecenter  = 'J2000 180.000deg %.3fdeg' % dec    # decode the proper phasecenter


pixel_m = pixel_m * pfactor       # simple rescale model map
pixel_s = pixel_s * pfactor       #

if pixel_s < 0:                   # force the model and sky size the same
    pixel_s = imsize_m * pixel_m / imsize_s

dishlabel = str(dish)             #  can also be ""

if niter==0:   niter=[0]          # be nice to allow this, but below it does need to be a list


# report, add Dtime
qac_begin(pdir,False)
qac_log("REPORT")
qac_version()
tp2vis_version()
# report parameters
qac_par('grid')
qac_par('dish')
qac_par('dec')
qac_par('pixel_m')
qac_par('noise')

# create a mosaic of pointings for the TP 'dish'
p = qac_im_ptg(phasecenter,imsize_m,pixel_m,grid,outfile=ptg)
print "Using %d pointings for 18m and grid=%g on fieldsize %g" % (len(p), grid, imsize_m*pixel_m)

grid0 = grid * gfactor
p0 = qac_im_ptg(phasecenter,imsize_m,pixel_m,grid0,outfile=ptg0)
print "Using %d pointings for  6m and grid0=%g on fieldsize %g" % (len(p0), grid0, imsize_m*pixel_m)

kwargs_clean1 = {}
if grid <= 0 and len(cfg) == 1:
    print("Single pointing single configuration: no mosaic gridder needed, using standard")
    kwargs_clean1['gridder'] = 'standard'

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
# the emperical procedure using the noise= keyword and using qac_noise()
# is courtesy Carilli et al. (2017)
qac_log("ngVLA")
ms1={}
for c in cfg:
    if c == 0:
        ms1[c] = qac_vla(pdir,model,imsize_m,pixel_m,cfg=c,ptg=ptg0, phasecenter=phasecenter, times=times0, noise=-noise)
        # bootstrap setting noise
        if noise > 0:
            sn0 = qac_noise(noise,pdir+'/clean2_noise', ms1[c], imsize_s, pixel_s, phasecenter=phasecenter)
            print("QAC_NOISE: %g" % sn0)
            ms1[c] = qac_vla(pdir,model,imsize_m,pixel_m,cfg=c,ptg=ptg0, phasecenter=phasecenter, times=times0, noise=sn0)            
        if wfactor != 1:
            # scale down the 6m data based on inspection of tp2vispl() ???
            tp2viswt(ms1[c],mode='mult',value=wfactor)
    else:
        ms1[c] = qac_vla(pdir,model,imsize_m,pixel_m,cfg=c,ptg=ptg,  phasecenter=phasecenter, times=times, noise=-noise)
        # bootstrap setting noise
        if noise > 0:
            sn0 = qac_noise(noise,pdir+'/clean2_noise', ms1[c], imsize_s, pixel_s, phasecenter=phasecenter)
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
cdir = pdir + '/clean2'
qac_clean1(cdir, intms, imsize_s, pixel_s, phasecenter=phasecenter, niter=niter, scales=scales, **kwargs_clean1)

qac_log("BEAM")
(bmaj,bmin) = qac_beam(cdir+'/dirtymap.psf', plot=cdir+'/dirtymap.beam.png')

if True:
    size_m = imsize_m * pixel_m
    size_s = imsize_s * pixel_s
    if size_m == size_s:
        nbin = int(pixel_s/pixel_m)
        sfac = 1.1331*bmaj*bmin/pixel_m/pixel_m
        print("Model and Sky size match. Using nbin=%d sfac=%g to create a rebin image" % (nbin,sfac))
        imrebin(startmodel,cdir+'/skymodel.tmp',[nbin,nbin,1,1])
        immath(cdir+'/skymodel.tmp','evalexpr',cdir+'/skymodel.rebin.image','IM0*%g'%sfac)
        qac_plot(cdir+'/skymodel.rebin.image')
    else:
        print("Model and Sky size do not match. %g != %g.  No rebinned skymodel" % (size_m,size_s))
    imsmooth(startmodel,'gaussian','%garcsec'%bmaj,'%garcsec'%bmaj,'0deg',outfile=pdir+'/skymodel.smooth.image')
        


qac_log("OTF, SMOOTH and plots")
# create an OTF TP map using a given dish size
smo = qac_smooth(cdir, startmodel, name="dirtymap")
otf = qac_tp_otf(cdir, startmodel, dish, label=dishlabel, template=cdir+'/dirtymap.image')

# scale, and possibly cheat and flip the OTF in RA
if afactor != 1:
    def myflip(image, afactor):
        """ hack: only works on 2D images....
        """
        tb.open(image,nomodify=False)
        d1 = tb.getcol("map")
        if abs(afactor) != 1:
            d1 = d1 * abs(afactor)
        if afactor < 0:
            ds = d1.shape
            d1 = d1.squeeze()
            nx = d1.shape[0]
            ny = d1.shape[1]
            d1 = np.flipud(d1)
            d1 = d1.reshape(ds)
        tb.putcol('map',d1)
        tb.close()
    print("Non-standard afactor=%g" % afactor)
    myflip(otf,           afactor)
    myflip(otf+'.pbcor',  afactor)

    

qac_plot(smo)
qac_plot(cdir+'/dirtymap.psf')
qac_plot(cdir+'/dirtymap.pb')
qac_plot(otf + '.pbcor')

if len(niter) == 1:
    qac_log("DONE! (no niters set, only dirty map)")
    qac_end()
    sys.exit(0)

qac_log("FEATHER")
# combine using feather and ssc, for all niter's (even though the first one is not valid)
for idx in range(len(niter)):
    qac_feather(cdir,             niteridx=idx, label=dishlabel, name="dirtymap")
    qac_ssc    (cdir,             niteridx=idx, label=dishlabel, name="dirtymap")
    qac_plot   (cdir+'/dirtymap%s.image.pbcor'  %            QAC.label(idx))
    qac_plot   (cdir+'/feather%s%s.image.pbcor' % (dishlabel,QAC.label(idx)))
    qac_plot   (cdir+'/ssc%s%s.image'           % (dishlabel,QAC.label(idx)))

# check the fluxes
qac_log("REGRESSION")

for idx in range(len(niter)):
    qac_stats(cdir+'/dirtymap%s.image'         %            QAC.label(idx))    
    qac_stats(cdir+'/dirtymap%s.image.pbcor'   %            QAC.label(idx))
    qac_stats(cdir+'/ssc%s%s.image'            % (dishlabel,QAC.label(idx)))
    qac_stats(cdir+'/feather%s%s.image'        % (dishlabel,QAC.label(idx)))
qac_stats(smo)
qac_stats(otf + '.pbcor')
qac_stats(model)

# two final difference maps
cm1   = cdir+'/dirtymap%s.image.pbcor'   %            QAC.label(idx)
fm1   = cdir+'/feather%s%s.image.pbcor'  %            (dishlabel,QAC.label(idx))
dcm1  = cdir+'/dirtymap%s.diff.pbcor'    %            QAC.label(idx)
dfm1  = cdir+'/feather%s%s.diff.pbcor'   %            (dishlabel,QAC.label(idx))
qac_math(dcm1,smo,'-',cm1)
qac_math(dfm1,smo,'-',fm1)
if True:
    qac_plot(dcm1)   # for kicks
    qac_plot(dfm1)   # for flow diagram


# make a bunch of plots
idx0 = len(niter)-1    # index of last niter[] for plotting

qac_log("MONTAGE1")

i1 = cdir+'/dirtymap%s.image.pbcor.png'   %            QAC.label(idx0)
i2 = otf + '.pbcor.png'
i3 = cdir+'/feather%s%s.image.pbcor.png'  % (dishlabel,QAC.label(idx0))
i4 = smo + '.png'
i0 = cdir+'/montage1.png'
cmd  = "montage -title %s %s %s %s %s -tile 2x2 -geometry +0+0 %s" % (pdir,i1,i2,i3,i4,i0)
os.system(cmd)

qac_log("PLOT_GRID plots 1 and 2")

a1 = cdir+'/dirtymap.image'
a2 = cdir+'/dirtymap%s.image'        %            QAC.label(idx0)
a3 = otf
a4 = cdir+'/feather%s%s.image'       % (dishlabel,QAC.label(idx0))
a5 = smo
a6 = cdir+'/ssc%s%s.image'           % (dishlabel,QAC.label(idx0))

b=range(len(niter))
c=range(len(niter))
for idx in range(len(niter)):
    b[idx] = cdir+'/dirtymap%s.image'  %            QAC.label(idx)
    c[idx] = cdir+'/feather%s%s.image' % (dishlabel,QAC.label(idx)) 
    
bg = []
for idx in range(len(niter)-1):
    bg.append(b[idx])
    bg.append(b[idx+1])
bg.append(b[0])
bg.append(b[idx0])

cg = []
for idx in range(len(niter)-1):
    cg.append(c[idx])
    cg.append(c[idx+1])
cg.append(c[0])
cg.append(c[idx0])

dg = []
for idx in range(len(niter)):
    dg.append(b[idx])
    dg.append(c[idx])

try:
    #qac_plot_grid([a1, a2, a2, a3, a4, a3], diff=10, plot=pdir+'/plot1.cmp.png', labels=True)
    qac_plot_grid([a2, a3, a4, a3],         diff=10, plot=pdir+'/plot1.cmp.png', labels=True)
    qac_plot_grid([a2, a5, a4, a6, a4, a5], diff=10, plot=pdir+'/plot2.cmp.png', labels=True)
    qac_plot_grid(bg,                       diff=10, plot=pdir+'/plot3.cmp.png', labels=True)
    qac_plot_grid(cg,                       diff=10, plot=pdir+'/plot4.cmp.png', labels=True)
    qac_plot_grid(dg,                       diff=1,  plot=pdir+'/plot5.cmp.png', labels=True)    
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
    if True:
        s1 = pdir+'/skymodel.smooth.image'
        s2 = cdir+'/skymodel.rebin.image' 
        qac_psd([startmodel, s1, s2, a5], plot=pdir+'/'+pdir+'.psd_2.png')
        qac_psd([startmodel, s1], plot=pdir+'/'+pdir+'.psd_3.png')
    
except:
    print("qac_psf failed")

qac_log("FIDELITY")
if fidall == 0:
    # do only the last iteration
    try:
        qac_fidelity(smo,cdir+'/dirtymap%s.image.pbcor' % QAC.label(idx0),              figure_mode=[1,2,3,4,5])
        qac_fidelity(smo,cdir+'/feather%s%s.image.pbcor' % (dishlabel,QAC.label(idx0)), figure_mode=[1,2,3,4,5])
    except:
        print("qac_fidelity failed")
else:
    # loop over all iterations
    for idx in range(len(niter)-1):
        f0 = qac_fidelity(smo,cdir+'/dirtymap%s.image.pbcor' % QAC.label(idx),              figure_mode=[1,2,3,4,5])
        f1 = qac_fidelity(smo,cdir+'/feather%s%s.image.pbcor' % (dishlabel,QAC.label(idx)), figure_mode=[1,2,3,4,5])
        qac_par(["idx","f0","f1"])

qac_log("DONE!")
qac_end()
