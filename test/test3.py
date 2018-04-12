# test3 - short spacing array
# looks like the _utm config file works (maybe?) hard to tell but it does not give the "# Note: diameters in configuration file will not be used - PB for NGVLA will be used" error in the log
#
# fails at qac_analyze because it can't handle having the tcleaned images in a separate directory as the .ms
# however, cannot have tclean go into same directory as .ms because qac_clean1 automatically deletes everything in that directory
# can either have qac_clean1 not delete everything (which may be an issue because some casa routines have a hard time with overwriting)
# or just copy the *.image into original test directory (because copying the skymodel into the test/clean1 directory doesn't work for some reason)
# 
# another thing - qac_analyze can't handle having separate beams for each channel. requires restoringbeam='common' in tclean
#
#  it is assumed you have done    execfile('qac.py')
#
# 3'26" running /dev/shm for full channels
#
# @todo double check primary beam. what should it be?

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
niter = [0, 1000, 2000]

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
qac_vla(test,model,imsize_m,pixel_m,cfg=0,ptg=ptg, phasecenter=phasecenter)

# clean this interferometric map a bit
qac_log('CLEAN')
qac_clean1(test+'/clean1',test+'/'+test+'.'+'ngvlaSA_2b_utm.ms',  imsize_s, pixel_s, phasecenter=phasecenter, niter=niter)

# create two OTF maps 
qac_log('OTF')
qac_tp_otf(test+'/clean1',test+'/'+test+'.'+'ngvlaSA_2b_utm.skymodel', 45.0, label='45')
qac_tp_otf(test+'/clean1',test+'/'+test+'.'+'ngvlaSA_2b_utm.skymodel', 18.0, label='18')

# combine TP + INT using feather, for all niters
qac_log('FEATHER')
for idx in range(len(niter)):
	qac_feather(test+'/clean1',label='45',niteridx=idx)
	qac_feather(test+'/clean1',label='18',niteridx=idx)


# smooth out skymodel image with feather beam so we can compare feather to original all in jy/beam
# qac_log('SMOOTH')
# for idx in range(len(niter)):
#     qac_smooth(test+'/clean1', test+'/'+test+'.'+cfg_file+'.skymodel', label='18', niteridx=idx)
#     qac_smooth(test+'/clean1', test+'/'+test+'.'+cfg_file+'.skymodel', label='45', niteridx=idx)

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


# --------------------------------------------------------------------------------------------------------------
# regression

# regress51 = [
#     "1.6544389694376587e-05 0.0002642084282218718 0.0 0.0098144030198454857 0.60989238169349846"
#     ]


# r = regress51
    

# # regression
# qac_stats(model,                                 r[0])
# # qac_stats('test2/test2.SWcore.ms',               r[1])
# qac_stats('test2/clean1/dirtymap.image')
# qac_stats('test2/clean1/dirtymap_2.image')
# qac_stats('test2/clean1/otf45.image')
# qac_stats('test2/clean1/otf18.image.pbcor')
# qac_stats('test2/clean1/otf45.image')
# qac_stats('test2/clean1/otf18.image.pbcor')
# qac_stats('test2/clean1/feather18_2.image')
# qac_stats('test2/clean1/feather18_2.image.pbcor')
# qac_stats('test2/clean1/feather45_2.image')
# qac_stats('test2/clean1/feather45_2.image.pbcor')

# qac_stats('test2/clean1/feather18.image.pbcor')
# qac_stats('test2/clean1/feather18_2.image.pbcor')
# qac_stats('test2/clean1/feather45.image.pbcor')
# qac_stats('test2/clean1/feather45_2.image.pbcor')
