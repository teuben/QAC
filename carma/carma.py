#
# carma EDGE simulations
#     Only D+E array with relatively short observations, so poor sampling in UV
#     - get combined D+E maps
#     - get moment maps
#     - compare with inut

test         = 'carma1'
model        = '../models/model0.fits'           # this as phasecenter with dec=-30 for ALMA sims
phasecenter  = 'J2000 180.000000deg 40.000000deg'

# pick the piece of the model to image, and at what pixel size
imsize_m     = 192
pixel_m      = 1

# pick the sky imaging parameters (for tclean)
imsize_s     = 256
imsize_s     = 192
pixel_s      = 1

# grid size for mosaic
grid         = 30

# pick a few niter values for tclean to check flux convergence 
niter = [0,1000]

# integration times
times = [4, 1]

# decide if you want the whole cube (chans=-1) or just a specific channel
chans        = '-1' # must be a string. for a range of channels --> '24~30'

# if you want multiscale clean, then True. if not, then False
scales  = None
scales  = [0,5,15]

# -- do not change parameters below this ---
import sys
for arg in qac_argv(sys.argv):
    exec(arg)

# rename model variable if single channel (or range) has been chosen so we don't overwrite models 
if chans != '-1':
    model_out = '%sa.image'%model[:model.rfind('.fits')]
    # delete any previously made models otherwise imsubimage won't run
    os.system('rm -fr %s'%model_out)
    # imsubimage to pull out the selected channel(s)
    imsubimage(model, model_out, chans=chans)
    # rewrite the model variable with our new model
    model = model_out


ptg = test + '.ptg'     
if type(niter) != type([]): niter = [niter]


# report
qac_log('CARMA: %s' % test)
qac_project(test)
# qac_begin(test)
qac_version()

# make vp
vp.reset()
vp.setpbairy(telescope='CARMA', dishdiam=8.0, blockagediam=0.0, maxrad='3.5deg', reffreq='1.0GHz', dopb=True)
vp.saveastable('CARMA.vp')

# create the pointing mosaic file, a full grid, or single pointing
if grid > 0:
    p = qac_im_ptg(phasecenter,imsize_m,pixel_m,grid,rect=True,outfile=ptg)
else:    
    qac_ptg(phasecenter,ptg)
    p = [phasecenter]

# Create E and D array 
ms0 = qac_carma(test,model,imsize_m,pixel_m,cfg=0,ptg=ptg, phasecenter=phasecenter,times=times)
ms1 = qac_carma(test,model,imsize_m,pixel_m,cfg=1,ptg=ptg, phasecenter=phasecenter,times=times)

# clean this interferometric map a bit
qac_log('CLEAN')
qac_clean1(test+'/clean0', ms0, imsize_s, pixel_s, phasecenter=phasecenter, niter=niter, restoringbeam='common', scales=scales,vptable='CARMA.vp')
qac_clean1(test+'/clean1', ms1, imsize_s, pixel_s, phasecenter=phasecenter, niter=niter, restoringbeam='common', scales=scales,vptable='CARMA.vp')

qac_clean1(test+'/clean2', [ms0,ms1], imsize_s, pixel_s, phasecenter=phasecenter, niter=niter, restoringbeam='common', scales=scales,vptable='CARMA.vp')


# combine D and E
qac_log('FEATHER')
if False:
    qac_feather(test, highres=test+'/clean1/dirtymap.image',   lowres=test+'/clean0/dirtymap.image')
qac_feather(test, highres=test+'/clean1/dirtymap_2.image', lowres=test+'/clean0/dirtymap_2.image', niteridx=1)

# smooth out skymodel image with feather beam so we can compare feather to original all in jy/beam
qac_log('SMOOTH')
skymodel = ms1.replace('.ms','.skymodel')
qac_smooth(test, skymodel)


if False:
    qac_log('ANALYZE')
    for idx in range(len(niter)):
        qac_analyze(test, 'feather', skymodel='%s/%s.SWcore.skymodel'%(test,test), niteridx=idx)
        os.system('mv %s/%s.analysis.png %s/feather_%s.analysis.png'% (test, test, test, idx))

#
qac_mom(test+'/clean0/dirtymap.image',    [0,11,48,59], test+'/clean0/dirtymap.pb')
qac_mom(test+'/clean0/dirtymap_2.image',  [0,11,48,59], test+'/clean0/dirtymap.pb')
qac_mom(test+'/clean1/dirtymap_2.image',  [0,11,48,59], test+'/clean1/dirtymap.pb')
qac_mom(test+'/clean2/dirtymap_2.image',  [0,11,48,59], test+'/clean2/dirtymap.pb')
qac_mom(test+'/carma1.carma.e.skymodel',[0,11,48,59])
a1 = test+'/carma1.carma.e.skymodel.mom1'
a2 = test+'/clean0/dirtymap.image.mom1'
qac_plot_grid([a1,a2])


qac_stats(test+'/clean0/dirtymap.image')
qac_stats(test+'/clean1/dirtymap.image')


qac_end()

