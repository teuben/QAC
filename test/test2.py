# galaxy model
#
# qac_feather and qac_analyze requires restoringbeam='common' for tclean
#
# 3'43" running in /dev/shm for full channels
#
# it is assumed you have done    execfile('qac.py')
#
# @todo figure out regression for this test

test 		 = 'test2'
model        = '../models/model0.fits'           # this as phasecenter with dec=-30 for ALMA sims
phasecenter  = 'J2000 180.000000deg 40.000000deg'

# pick the piece of the model to image, and at what pixel size
imsize_m     = 192
pixel_m      = 0.1

# pick the sky imaging parameters (for tclean)
imsize_s     = 512
pixel_s      = 0.1

# pick a few niter values for tclean to check flux convergence 
niter = [0,1000, 2000]

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
qac_vla(test,model,imsize_m,pixel_m,cfg=1,ptg=ptg, phasecenter=phasecenter)

# clean this interferometric map a bit
qac_log('CLEAN')
qac_clean1(test+'/clean1', test+'/'+test+'.SWcore.ms', imsize_s, pixel_s, phasecenter=phasecenter, niter=niter, restoringbeam='common')

# create two OTF maps 
qac_log('OTF')
qac_tp_otf(test+'/clean1',test+'/'+test+'.SWcore.skymodel', 45.0, label='45')
qac_tp_otf(test+'/clean1',test+'/'+test+'.SWcore.skymodel', 18.0, label='18')

# combine TP + INT using feather, for all niters
qac_log('FEATHER')
for idx in range(len(niter)):
	qac_feather(test+'/clean1',label='45',niteridx=idx)
	qac_feather(test+'/clean1',label='18',niteridx=idx)

# smooth out skymodel image with feather beam so we can compare feather to original all in jy/beam
qac_log('SMOOTH')
qac_smooth(test+'/clean1', test+'/'+test+'.SWcore.skymodel', label='18', niteridx=0)
qac_smooth(test+'/clean1', test+'/'+test+'.SWcore.skymodel', label='45', niteridx=0)

qac_log('ANALYZE')
os.system('mv %s/clean1/dirtymap*image %s'%(test, test))
os.system('mv %s/clean1/feather*image %s'%(test, test))
for idx in range(len(niter)):
    qac_analyze(test, 'dirtymap', niteridx=idx)
    os.system('mv %s/%s.analysis.png %s/dirtymap_%s.analysis.png'% (test, test, test, idx))
    qac_analyze(test, 'feather18', niteridx=idx)
    os.system('mv %s/%s.analysis.png %s/feather18_%s.analysis.png'% (test, test, test, idx))
    qac_analyze(test, 'feather45', niteridx=idx)
    os.system('mv %s/%s.analysis.png %s/feather45_%s.analysis.png'% (test, test, test, idx))
os.system('mv %s/dirtymap* %s/clean1'%(test, test))
os.system('mv %s/feather* %s/clean1'%(test, test))

#
qac_end()

# check fluxes
qac_stats('test2/clean1/skymodel18_3.residual')
qac_stats('test2/clean1/skymodel18_3.smooth.image')
qac_stats('test2/clean1/feather18_3.image')
qac_stats('test2/clean1/feather18_3.image.pbcor')
qac_stats('test2/clean1/skymodel45_3.residual')
qac_stats('test2/clean1/skymodel45_3.smooth.image')
qac_stats('test2/clean1/feather45_3.image')
qac_stats('test2/clean1/feather45_3.image.pbcor')
