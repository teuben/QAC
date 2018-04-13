# test3 - short spacing array for total power
# looks like the _utm config file works (maybe?) hard to tell but it does not give the "# Note: diameters in configuration file will not be used - PB for NGVLA will be used" error in the log
#
#
#  it is assumed you have done    execfile('qac.py')
#
# 3'18" running /dev/shm for full channels
#

test         = 'test3'
model        = '../models/model0.fits'           # this as phasecenter with dec=-30 for ALMA sims
phasecenter  = 'J2000 180.000000deg 40.000000deg'

# pick the piece of the model to image, and at what pixel size
imsize_m     = 192
pixel_m      = 0.1

# pick the sky imaging parameters (for tclean)
imsize_s     = 512
pixel_s      = 0.1

# pick a few niter values for tclean to check flux convergence 
niter = [0,1000]

# decide if you want the whole cube (chans=-1) or just a specific channel
chans        = '-1' # must be a string. for a range of channels --> '24~30'


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

ptg = test + '.ptg'              # use a single pointing mosaic for the ptg
if type(niter) != type([]): niter = [niter]


# report
qac_log('TEST: %s' % test)
qac_begin(test)
qac_version()

# create a single pointing mosaic
qac_ptg(phasecenter,ptg)

# create a MS based on a model and antenna configuration
qac_log('VLA')
# first for SSA cfg
qac_vla(test,model,imsize_m,pixel_m,cfg=0,ptg=ptg, phasecenter=phasecenter)
# second for SWcore
qac_vla(test,model,imsize_m,pixel_m,cfg=1,ptg=ptg, phasecenter=phasecenter)

# clean this interferometric map a bit
qac_log('CLEAN')
# SSA clean
qac_clean1(test+'/clean_SSA',test+'/'+test+'.'+'ngvlaSA_2b_utm.ms',  imsize_s, pixel_s, phasecenter=phasecenter, niter=niter, restoringbeam='common')
# SWCore clean
qac_clean1(test+'/clean1', test+'/'+test+'.SWcore.ms', imsize_s, pixel_s, phasecenter=phasecenter, niter=niter, restoringbeam='common')

# combine SSA + SWCore using feather, for all niters
qac_log('FEATHER')
qac_feather(test, highres=test+'/clean1/dirtymap.image', lowres=test+'/clean_SSA/dirtymap.image')
qac_feather(test, highres=test+'/clean1/dirtymap_2.image', lowres=test+'/clean_SSA/dirtymap_2.image', niteridx=1)

# smooth out skymodel image with feather beam so we can compare feather to original all in jy/beam
qac_log('SMOOTH')
qac_smooth(test, test+'/'+test+'.SWcore.skymodel')


qac_log('ANALYZE')
for idx in range(len(niter)):
    qac_analyze(test, 'feather', skymodel='%s/%s.SWcore.skymodel'%(test,test), niteridx=idx)
    os.system('mv %s/%s.analysis.png %s/feather_%s.analysis.png'% (test, test, test, idx))

#
qac_end()

# check fluxes
qac_stats('test3/skymodel.residual')
qac_stats('test3/skymodel.smooth.image')
qac_stats('test3/feather.image')
qac_stats('test3/feather.image.pbcor')
qac_stats('test3/feather_2.image')
qac_stats('test3/feather_2.image.pbcor')
