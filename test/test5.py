# galaxy model
#
# qac_feather and qac_analyze requires restoringbeam='common' for tclean
#
# 3'43" running in /dev/shm for full channels
#
# it is assumed you have done    execfile('qac.py')
#
# @todo figure out regression for this test

pdir         = 'test5'
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
# niter = [0,100,200,300,400,500,600,700,800,900,1000,1500,2000,2500]

# decide if you want the whole cube (chans=-1) or just a specific channel
chans        = '-1' # must be a string. for a range of channels --> '24~30'

# choose ngVLA antennae configuation
cfg          = 1

# change this if you want mosaic (True) or not (False)
mosaic       = False

if mosaic == False:
    ptg = test + '.ptg'              # use a single pointing mosaic for the ptg
else:
    ptg = None
    os.system('export VI1=1')

if type(niter) != type([]): niter = [niter]

# -- do not change parameters below this ---
import sys
for arg in qac_argv(sys.argv):
    exec(arg)

test = pdir    

# rename model variable if single channel (or range) has been chosen so we don't overwrite models 
if chans != '-1':
    model_out = '%sa.image'%model[:model.rfind('.fits')]
    # delete any previously made models otherwise imsubimage won't run
    os.system('rm -fr %s'%model_out)
    # imsubimage to pull out the selected channel(s)
    imsubimage(model, model_out, chans=chans)
    # rewrite the model variable with our new model
    model = model_out

# report
qac_log('TEST: %s' % test)
qac_begin(test)
qac_version()

# create a single pointing mosaic
qac_ptg(phasecenter,ptg)

# create a MS based on a model and antenna configuration
qac_log('VLA')
ms1 = {}
ms1[cfg] = qac_vla(test,model,imsize_m,pixel_m,cfg=cfg,ptg=ptg, phasecenter=phasecenter)

# clean this interferometric map a bit
qac_log('CLEAN')
qac_clean1(test+'/clean1', ms1[cfg], imsize_s, pixel_s, phasecenter=phasecenter, niter=niter, scales=[0,5,15], restoringbeam='common')

# grab name of start/input model
startmodel = ms1[cfg].replace('.ms','.skymodel')

# create two OTF maps 
qac_log('OTF')
qac_tp_otf(test+'/clean1', startmodel, 45.0, label='45')
qac_tp_otf(test+'/clean1', startmodel, 18.0, label='18')

# combine TP + INT using feather, for all niters
qac_log('FEATHER')
for idx in range(len(niter)):
	qac_feather(test+'/clean1',label='45',niteridx=idx)
	qac_feather(test+'/clean1',label='18',niteridx=idx)

# smooth out skymodel image with feather beam so we can compare feather to original all in jy/beam
qac_log('SMOOTH')
qac_smooth(test+'/clean1', startmodel, label='18', niteridx=0)
qac_smooth(test+'/clean1', startmodel, label='45', niteridx=0)

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
qac_stats(test+'/clean1/skymodel18.residual')
qac_stats(test+'/clean1/skymodel18.smooth.image')
qac_stats(test+'/clean1/feather18_2.image')
qac_stats(test+'/clean1/feather18_2.image.pbcor')
qac_stats(test+'/clean1/skymodel45.residual')
qac_stats(test+'/clean1/skymodel45.smooth.image')
qac_stats(test+'/clean1/feather45_2.image')
qac_stats(test+'/clean1/feather45_2.image.pbcor')

# plot of flux vs niter
clean_dir = test+'/clean1/'
niter_label = [QAC.label(i) for i in np.arange(0, len(niter), 1)]
flux_dm = np.array([ imstat(clean_dir+'dirtymap%s.image'%(n))['flux'][0] for n in niter_label])
flux_18 = np.array([ imstat(clean_dir+'feather18%s.image'%(n))['flux'][0] for n in niter_label])
flux_45 = np.array([ imstat(clean_dir+'feather45%s.image'%(n))['flux'][0] for n in niter_label])

plt.figure()
plt.plot(niter, flux_dm, 'k^-', label='dirtymap')
plt.plot(niter, flux_18, 'm^-', label='feather 18m')
plt.plot(niter, flux_45, 'c^-', label='feather 45m')
plt.xlabel('niter', size=18)
plt.ylabel('Flux (Jy/beam)', size=18)
plt.title(test, size=18)
plt.legend(loc='best')
plt.savefig(clean_dir+'flux_vs_niter.png')
plt.show()
