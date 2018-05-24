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

# dish diam
dish         = 8
#dish         = 16

# grid size for mosaic
grid         = 30
#grid         = 45
#grid         = 60

# pick a few niter values for tclean to check flux convergence 
niter = [0,4000]

# integration times
times  = [8, 0.5]
times0 = [1, 1]
times1 = [4, 1]

# decide if you want the whole cube (chans=-1) or just a specific channel
chans  = '-1' # must be a string. for a range of channels --> '24~30'

# if you want multiscale clean, then True. if not, then False
scales = None
scale  = [0,5,15]

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
vp.setpbairy(telescope='CARMA', dishdiam=dish, blockagediam=0.0, maxrad='3.5deg', reffreq='1.0GHz', dopb=True)
vp.saveastable('CARMA.vp')

# create the pointing mosaic file, a full grid, or single pointing
if grid > 0:
    p = qac_im_ptg(phasecenter,imsize_m,pixel_m,grid,rect=True,outfile=ptg)
else:    
    qac_ptg(phasecenter,ptg)
    p = [phasecenter]

# Create E and D array 
ms0 = qac_carma(test,model,imsize_m,pixel_m,cfg=0,ptg=ptg, phasecenter=phasecenter,times=times0)
ms1 = qac_carma(test,model,imsize_m,pixel_m,cfg=1,ptg=ptg, phasecenter=phasecenter,times=times1)

# clean this interferometric map a bit
qac_log('CLEAN')
qac_clean1(test+'/clean0', ms0, imsize_s, pixel_s, phasecenter=phasecenter, niter=niter, restoringbeam='common', scales=scales,vptable='CARMA.vp')
qac_clean1(test+'/clean1', ms1, imsize_s, pixel_s, phasecenter=phasecenter, niter=niter, restoringbeam='common', scales=scales,vptable='CARMA.vp')

qac_clean1(test+'/clean2', [ms0,ms1], imsize_s, pixel_s, phasecenter=phasecenter, niter=niter, restoringbeam='common', scales=scales,vptable='CARMA.vp')



if False:
    qac_log('ANALYZE')
    for idx in range(len(niter)):
        qac_analyze(test, 'feather', skymodel='%s/%s.SWcore.skymodel'%(test,test), niteridx=idx)
        os.system('mv %s/%s.analysis.png %s/feather_%s.analysis.png'% (test, test, test, idx))

# define model for the a mask
d0 = test+'/carma1.carma.e.skymodel.mom0'
v0 = test+'/carma1.carma.e.skymodel.mom1'

# run some moments, but using that model density mask 
qac_mom(test+'/carma1.carma.e.skymodel',  [0,11,48,59])
qac_mom(test+'/clean0/dirtymap.image',    [0,11,48,59], d0, 0.0)
qac_mom(test+'/clean0/dirtymap_2.image',  [0,11,48,59], d0, 0.0)
qac_mom(test+'/clean1/dirtymap_2.image',  [0,11,48,59], d0, 0.0)
qac_mom(test+'/clean2/dirtymap_2.image',  [0,11,48,59], d0, 0.0)

v1 = test+'/clean0/dirtymap.image.mom1'
v2 = test+'/clean0/dirtymap_2.image.mom1'
v3 = test+'/clean1/dirtymap_2.image.mom1'
v4 = test+'/clean2/dirtymap_2.image.mom1'

d1 = test+'/clean0/dirtymap.image.mom0'
d2 = test+'/clean0/dirtymap_2.image.mom0'
d3 = test+'/clean1/dirtymap_2.image.mom0'
d4 = test+'/clean2/dirtymap_2.image.mom0'

# comparisons
qac_plot_grid([v0,v1,v1,v2,v2,v3,v3,v4],plot=test+'/velcmp1.png',diff=1)
qac_plot_grid([d0,d1,d1,d2,d2,d3,d3,d4],plot=test+'/dencmp1.png',diff=1)


# smooth out skymodel image with feather beam so we can compare feather to original all in jy/beam
qac_log('SMOOTH')
skymodel = ms1.replace('.ms','.skymodel')
sm0 = qac_smooth(test+'/clean0', skymodel,'dirtymap')

qac_mom(sm0, [0,11,48,59])
d5 = 'carma1/clean0/skymodel.smooth.image.mom0'
v5 = 'carma1/clean0/skymodel.smooth.image.mom1'
qac_plot(d5,plot=test+'/tp-den.png')
qac_plot(v5,plot=test+'/tp-vel.png')

# combine
qac_log('FEATHER')
qac_feather(test, highres=test+'/clean2/dirtymap_2.image', lowres=sm0, niteridx=1)


qac_mom(test+'/feather_2.image',    [0,11,48,59], d0, 0.0)

d6 = test+'/feather_2.image.mom0'
v6 = test+'/feather_2.image.mom1'

qac_plot_grid([v0,v2,v0,v6],plot=test+'/velcmp2.png',diff=1)

qac_plot(d0,plot=test+'/model-vel.png')
qac_plot(v0,plot=test+'/model-den.png')

if False:
    exportfits(a0,a0+'.fits')
    exportfits(b0,b0+'.fits')

if True:    
    m0='carma1/carma1.carma.e.skymodel'
    m1='carma1/clean0/dirtymap.image'
    m2='carma1/clean0/dirtymap_2.image'
    m3='carma1/clean1/dirtymap_2.image'
    m4='carma1/clean2/dirtymap_2.image'
    m5=sm0
    m6='carma1//feather_2.image'
    ch = 14
    qac_plot(m0,channel=ch,plot='carma1/m0.png')
    qac_plot(m1,channel=ch,plot='carma1/m1.png')
    qac_plot(m2,channel=ch,plot='carma1/m2.png')
    qac_plot(m3,channel=ch,plot='carma1/m3.png')
    qac_plot(m4,channel=ch,plot='carma1/m4.png')
    qac_plot(m5,channel=ch,plot='carma1/m5.png')        
    qac_plot(m6,channel=ch,plot='carma1/m6.png')        


if True:
    qac_plot(d0,plot='carma1/d0.png')    
    qac_plot(d1,plot='carma1/d1.png')    
    qac_plot(d2,plot='carma1/d2.png')    
    qac_plot(d3,plot='carma1/d3.png')    
    qac_plot(d4,plot='carma1/d4.png')    
    qac_plot(d5,plot='carma1/d5.png')    
    qac_plot(d6,plot='carma1/d6.png')    

    qac_plot(v0,plot='carma1/v0.png')    
    qac_plot(v1,plot='carma1/v1.png')    
    qac_plot(v2,plot='carma1/v2.png')    
    qac_plot(v3,plot='carma1/v3.png')    
    qac_plot(v4,plot='carma1/v4.png')    
    qac_plot(v5,plot='carma1/v5.png')    
    qac_plot(v6,plot='carma1/v6.png')

if True:
    qac_fits([v0,v1,v2,v3,v4,v5,v6])

    

qac_stats(test+'/clean0/dirtymap.image')
qac_stats(test+'/clean1/dirtymap.image')


qac_end()

