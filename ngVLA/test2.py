"""
ngVLA simulated observation of input galaxy model
feathering INT with 45 and 18 m single dish  for TP

Variable    Description                     Default value   Notes
--------------------------------------------------------------------------------
model       input model                     model0
imsize_m    model image size                192 pixels 
pixel_m     model image pixel size          0.1             this with image size controls effective galaxy size on the sky
imsize_s    image size passed to TCLEAN     512
pixel_s     pixel size passed to TCLEAN     0.1
niter       iterations for TCLEAN           [0,1000]
chans       channels of input model to use  '-1'            '-1' uses all channels in input model
cfg         ngVLA ant config for INT        1               0=SBA, 1=core 94 ant, 2=plains 168 ant, 3=full 214 ant, 4=full ngVLA + VLBI + GBO
mosiac      toggle mosiac imaging           False           True gives automatic mosiac pointings as determined by simobserve
scales      multiscale cleaning values      [0,5,15]        for no multiscale cleaning set scales = None

qac_feather and qac_analyze requires restoringbeam='common' for tclean

2'02" running in /dev/shm at uwyo for default values

it is assumed you have done execfile('qac.py')

to run from casa shell with default values:
execfile('test2.py')

to run from bash/csh shell with default values for variables described above:
casa --nogui -c test2.py

to run from Makefile with default values and output to a log file
make test2

to run from bash/csh shell with modified variable values:
casa --nogui -c test2.py "test='test000'" "imsize_m=256"
"""

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
niter = [0,1000]
# niter = [0,100,200,300,400,500,600,700,800,900,1000,1500,2000,2500]   # for testing cleaning iterations (i.e. flux vs. niter)

# decide if you want the whole cube (chans='-1') or just a specific channel
chans        = '-1' # must be a string. for a range of channels --> '24~30'

# choose ngVLA antennae configuation
cfg          = 1

# integration time
times        = [1, 1]   # 1 hr in 1 min integrations

# tp dish sizes
dish         = [6, 12, 18, 24, 30, 36, 45]

# # change this if you want mosiac (True) or not (False)
# mosiac       = False
# if mosiac == False:
#     ptg = test + '.ptg'              # use a single pointing mosaic for the ptg
# else:
#     ptg = None
#     os.system('export VI1=1')

# multiscale cleaning? -- if no, set scale=None, otherwise set the scales
scales = [0,5,15]

# single pointing?  Set grid to a positive arcsec grid spacing if the field needs to be covered
#                   ALMA normally uses lambda/2D   hexgrid is Lambda/sqrt(3)D
grid         =  0        # this can be pointings good for small dish nyquist

# derived parameters
ptg = test + '.ptg'              # pointing mosaic for the ptg

if grid > 0:
    # create a mosaic of pointings for 12m, that's overkill for the 7m
    p = qac_im_ptg(phasecenter,imsize_m,pixel_m,grid,rect=True,outfile=ptg)
else:
    # create a single pointing 
    qac_ptg(phasecenter,ptg)
    p = [phasecenter]

# check the type of niter - if just an int, put it into a list
if type(niter) != type([]): niter = [niter]

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

# report
qac_begin(test,False)
qac_log('TEST: %s' % test)
qac_version()

qac_project(test)

# create a MS based on a model and antenna configuration
qac_log('VLA')
ms1 = {}
ms1[cfg] = qac_vla(test,model,imsize_m,pixel_m,cfg=cfg,ptg=ptg, phasecenter=phasecenter, times=times)

# clean this interferometric map a bit
qac_log('CLEAN')
qac_clean1(test+'/clean1', ms1[cfg], imsize_s, pixel_s, phasecenter=phasecenter, niter=niter, scales=scales, restoringbeam='common')

# grab name of start/input model
startmodel = ms1[cfg].replace('.ms','.skymodel')

# create two OTF maps 
qac_log('OTF')
for d in dish:
    qac_tp_otf(test+'/clean1', startmodel, d, label='%s'%d)

# combine TP + INT using feather, for the last niter
qac_log('FEATHER')
for d in dish:
    qac_feather(test+'/clean1',label='%s'%d, niteridx=range(len(niter))[-1])
    qac_smooth(test+'/clean1', startmodel, niteridx=range(len(niter))[-1], name='feather', label='%s'%d)

# smooth out startmodel with beam of the dirtymap for comparison
qac_log('SMOOTH')
qac_smooth(test+'/clean1', startmodel, name='dirtymap')

# qac_log('ANALYZE')
# os.system('mv %s/clean1/dirtymap*image %s'%(test, test))
# os.system('mv %s/clean1/feather*image %s'%(test, test))
# for idx in range(len(niter)):
#     qac_analyze(test, 'dirtymap', niteridx=idx)
#     os.system('mv %s/%s.analysis.png %s/dirtymap_%s.analysis.png'% (test, test, test, idx))
#     qac_analyze(test, 'feather18', niteridx=idx)
#     os.system('mv %s/%s.analysis.png %s/feather18_%s.analysis.png'% (test, test, test, idx))
#     qac_analyze(test, 'feather45', niteridx=idx)
#     os.system('mv %s/%s.analysis.png %s/feather45_%s.analysis.png'% (test, test, test, idx))
# os.system('mv %s/dirtymap* %s/clean1'%(test, test))
# os.system('mv %s/feather* %s/clean1'%(test, test))

qac_end()

# check fluxes
qac_log('REGRESSION')
qac_stats(model)
qac_stats(test+'/clean1/dirtymap.image')
qac_stats(test+'/clean1/dirtymap.image.pbcor')
qac_stats(test+'/clean1/dirtymap_2.image')
qac_stats(test+'/clean1/dirtymap_2.image.pbcor')
qac_stats(test+'/clean1/skymodel.smooth.image')
for d in dish:
    qac_stats(test+'/clean1/feather%s_2.image'%d)
    qac_stats(test+'/clean1/feather%s_2.image.pbcor'%d)

# can't do this yet because qac_plot_grid doesn't understand channels

# qac_log('Grid Plots')
# d1 = test+'/clean1/dirtymap.image'
# d2 = test+'/clean1/dirtymap_2.image'
# otf = [test+'/clean1/otf%s.image'%d for d in dish]
# fth = [test+'/clean1/feather%s_2.image'%d for d in dish]
# sky = test+'/clean1/skymodel.smooth.image'

# qac_plot_grid([d1, d2, d2, sky], diff=1, plot=test+'/plot1.cmp.png', labels=True)
# grid_list = [[d2, o] for o in otf]
# qac_plot_grid([item for sublist in grid_list for item in sublist], diff=1, plot=test+'/plot2.cmp.png', labels=True)
# grid_list = [[f, sky] for f in fth]
# qac_plot_grid([item for sublist in grid_list for item in sublist], diff=1, plot=test+'/plot3.cmp.png', labels=True)



# # plot of flux vs niter
# clean_dir = test+'/clean1/'
# niter_label = [QAC.label(i) for i in np.arange(0, len(niter), 1)]
# flux_dm = np.array([ imstat(clean_dir+'dirtymap%s.image'%(n))['flux'][0] for n in niter_label])
# flux_18 = np.array([ imstat(clean_dir+'feather18%s.image'%(n))['flux'][0] for n in niter_label])
# flux_45 = np.array([ imstat(clean_dir+'feather45%s.image'%(n))['flux'][0] for n in niter_label])

# plt.figure()
# plt.plot(niter, flux_dm, 'k^-', label='dirtymap')
# plt.plot(niter, flux_18, 'm^-', label='feather 18m')
# plt.plot(niter, flux_45, 'c^-', label='feather 45m')
# plt.xlabel('niter', size=18)
# plt.ylabel('Flux (Jy/beam)', size=18)
# plt.title(test, size=18)
# plt.legend(loc='best')
# plt.savefig(clean_dir+'flux_vs_niter.png')