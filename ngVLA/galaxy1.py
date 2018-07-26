# -*- python -*-
#
#  Play with the galaxy models
#
#
#
#  To create galaxy models:
# 	- ensure nemo is installed and initialized with the command: source path/to/nemo/nemo_start.sh
# 	- in "models" directory of the QAC repo, run:
#		make test
#
#
#  currently crashes during cleaning
#
#  to run:
#  make gal_bug1ex
#
#
#
#
#
#

pdir 		= 'gal1'                               # name of directory within which everything will reside
model 		= '../models/model0.fits'             
phasecenter  = 'J2000 180.000000deg 40.000000deg'  # where we want this model to be on the sky, at VLA

# pick image and pixel size
# natively the galaxy models are 192 pixels at 5" 
imsize_m 	= 192
pixel_m		= 0.5

# pick the sky imaging parameters (for tclean)
# The product of these typically will be the same as that of the model (but don't need to)
# pick the pixel_s based on the largest array configuration (see below) choosen
# If pixel_s is negative, it will be computed based on imsize*pixel for both _m and _s being same
imsize_s 	= 192
pixel_s 	= -1

# pick a few niter values for tclean to check flux convergence ; need at least two to get feather/ssc
niter 		= [0,1000]
# niter 		= [0,1000]
# niter 		= [0, 500, 1000, 2000, 4000, 8000]

# pick which ngVLA configurations you want (0=SBA, 1=core, 2=plains, 3=all, 4=all+GB+VLBA)
# cfg 		= [0]
cfg 		= [0,1]

# integration times (see also below for alternative equal time per pointing observations)
times 		= [4, 1]	# hrs observing and mins integrations

# grid spacing for mosaic pointings (18m -> 15"   6m -> 50" but 6m is controlled with gfactor)
# -1 = single pointing
grid 		= 15

# tp dish size (18, 45, 100m are the interesting choices to play with)
dish 		= 45

# scaling factors 
wfactor 	= 1      # weight mult for cfg=0 
afactor 	= 1      # not implemented yet
gfactor 	= 3.0    # 18m/6m ratio of core/SBA dishes (should probably remain at 3)
pfactor 	= 1.0    # pixel size factor for both pixel_m and pixel_s
tfactor 	= 2.0    # extra time factor to apply to SBA (not used)

# multi-scale cleaning? - use [0] or None if you don't want it
scales 		= [0]

# simplenoise level
noise 		= 0.0

# clean maps - set to 0 if you just want the ms file(s)
clean 		= 1

# -- do not change parameters below this ---
import sys
for arg in qac_argv(sys.argv):
    exec(arg)

# derived parameters
ptg  = pdir + '.ptg'              # pointing mosaic for the ptg
ptg0 = pdir + '.0.ptg'            # pointing mosaic for the ptg

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
            sn0 = qac_noise(noise,pdir+'/clean3_noise', ms1[c], imsize_s, pixel_s, phasecenter=phasecenter)
            print("QAC_NOISE: %g" % sn0)
            ms1[c] = qac_vla(pdir,model,imsize_m,pixel_m,cfg=c,ptg=ptg0, phasecenter=phasecenter, times=times0, noise=sn0)            
        if wfactor != 1:
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
cdir = pdir + '/clean3'
qac_clean1(cdir, intms, imsize_s, pixel_s, phasecenter=phasecenter, niter=niter, scales=scales, **kwargs_clean1)

# qac_log("BEAM")
# (bmaj,bmin) = qac_beam(cdir+'/dirtymap.psf', plot=cdir+'/dirtymap.beam.png')

# if True:
#     size_m = imsize_m * pixel_m
#     size_s = imsize_s * pixel_s
#     if size_m == size_s:
#         nbin = int(pixel_s/pixel_m)
#         sfac = 1.1331*bmaj*bmin/pixel_m/pixel_m
#         print("Model and Sky size match. Using nbin=%d sfac=%g to create a rebin image" % (nbin,sfac))
#         imrebin(startmodel,cdir+'/skymodel.tmp',[nbin,nbin,1,1])
#         immath(cdir+'/skymodel.tmp','evalexpr',cdir+'/skymodel.rebin.image','IM0*%g'%sfac)
#         qac_plot(cdir+'/skymodel.rebin.image')
#     else:
#         print("Model and Sky size do not match. %g != %g.  No rebinned skymodel" % (size_m,size_s))
#     imsmooth(startmodel,'gaussian','%garcsec'%bmaj,'%garcsec'%bmaj,'0deg',outfile=pdir+'/skymodel.smooth.image')

# qac_log("OTF, SMOOTH and plots")
# # create an OTF TP map using a given dish size
# smo = qac_smooth(cdir, startmodel, name="dirtymap")
# otf = qac_tp_otf(cdir, startmodel, dish, label=dishlabel, template=cdir+'/dirtymap.image')

# # scale, and possibly cheat and flip the OTF in RA
# if afactor != 1:
#     def myflip(image, afactor):
#         """ hack: only works on 2D images....
#         """
#         tb.open(image,nomodify=False)
#         d1 = tb.getcol("map")
#         if abs(afactor) != 1:
#             d1 = d1 * abs(afactor)
#         if afactor < 0:
#             ds = d1.shape
#             d1 = d1.squeeze()
#             nx = d1.shape[0]
#             ny = d1.shape[1]
#             d1 = np.flipud(d1)
#             d1 = d1.reshape(ds)
#         tb.putcol('map',d1)
#         tb.close()
#     print("Non-standard afactor=%g" % afactor)
#     myflip(otf,           afactor)
#     myflip(otf+'.pbcor',  afactor)
