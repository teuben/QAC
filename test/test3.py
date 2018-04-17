# test3 - short spacing array for total power
#
# has fix from brian mason memo 43 for getting correct primary beam for the short baseline array (6 m antennae)
# get terrible flux recovery when feathered together --> SWcore dirtymap_2 gives 120, SSA dirtymap_2 gives 57, feather_2 gives 67, expected 144
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

# if you want multiscale cleaning, then True. if not, then False
multiscale   = True

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

if multiscale == True:
    scales = [0,5,15]
else:
    scales = None

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

# to get create custom voltage pattern table for SSA (from brian mason memo 43)
# really only have to do this once because the table can then be loaded
# vp.reset()
# vp.setpbairy(telescope='NGVLA', dishdiam=6.0, blockagediam=0.0, maxrad='3.5deg', reffreq='1.0GHz', dopb=True)
# vp.saveastable('sba.tab')

# load vp table
vp.reset()
vp.loadfromtable('sba.tab')
qac_vla(test,model,imsize_m,pixel_m,cfg=0,ptg=ptg, phasecenter=phasecenter)
# second for SWcore
vp.reset()
qac_vla(test,model,imsize_m,pixel_m,cfg=1,ptg=ptg, phasecenter=phasecenter)

# clean this interferometric map a bit
qac_log('CLEAN')
# SSA clean
qac_clean1(test+'/clean_SSA',test+'/'+test+'.'+'ngvlaSA_2b_utm.ms',  imsize_s, pixel_s, phasecenter=phasecenter, niter=niter, restoringbeam='common', scales=scales, vptable='sba.tab')
# SWCore clean
qac_clean1(test+'/clean1', test+'/'+test+'.SWcore.ms', imsize_s, pixel_s, phasecenter=phasecenter, niter=niter, restoringbeam='common', scales=scales)

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
