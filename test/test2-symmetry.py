#
# test the difference between clean and tclean in clean a strong signal,
# Nico showed a similar situation where tclean() did not recover back
# to 0 flux after the integration of the spectrum
#
# Some models tried
# ./mkgalcube run=model11 beam=0 vrange=150 nvel=9 mirror=1
# ./mkgalcube run=model12 beam=0 vrange=150 nvel=15 beam=0.2 noise=0.0001
#
# the problem is once again first/last channel no beam, 
#
test 		 = 'test2-symmetry'
model        = '../models/model12.fits' 
model        = '../models/model11.fits' 
phasecenter  = 'J2000 180.000000deg -30.000000deg'

# pick the piece of the model to image, and at what pixel size
imsize_m     = 192
pixel_m      = 0.5

# pick the sky imaging parameters (for tclean)
imsize_s     = 256
pixel_s      = 0.5

# pick a few niter values for tclean to check flux convergence 
niter        = [0,100,1000]

common       = 1

# -- do not change parameters below this ---
import sys
for arg in qac_argv(sys.argv):
    exec(arg)

ptg = test + '.ptg'              # use a single pointing mosaic for the ptg
if type(niter) != type([]): niter = [niter]

# report
qac_log('TEST: %s' % test)
qac_begin(test)
qac_version()

# create a single pointing mosaic
qac_ptg(phasecenter,ptg)

# make sure we start from a clean directory
os.system('rm -rf %s' % test)

# create some MS
ms1 = qac_alma(test,model,imsize_m,pixel_m,cfg=1,ptg=ptg, phasecenter=phasecenter,times=[4,1])
ms2 = qac_alma(test,model,imsize_m,pixel_m,cfg=2,ptg=ptg, phasecenter=phasecenter,times=[4,1])
mslist   = [ms1, ms2]
skymodel = ms1.replace('.ms','.skymodel')

# clean this interferometric map a bit with clean and tclean
qac_log('CLEAN')
line = {}
# CLEAN
if common == 1:
    line = {'resmooth' : True}
qac_clean1(test+'/clean1', mslist, imsize_s, pixel_s, phasecenter=phasecenter, niter=niter, t=False, **line)
# TCLEAN
if common == 1:
    line = {'restoringbeam' : 'common'}
qac_clean1(test+'/clean2', mslist, imsize_s, pixel_s, phasecenter=phasecenter, niter=niter, t=True,  **line)


# print flux - reverseflux, should be zero!!

flux = imstat(skymodel,axes=[0,1])['sum']
nch  = len(flux)
idx  = range(nch)
idx.reverse()
print skymodel,flux-flux[idx]

for i in range(len(niter)):
    if i==0:
        f1 = test + '/clean1/dirtymap.image'
        f2 = test + '/clean2/dirtymap.image'
    else:
        f1 = test + '/clean1/dirtymap_%d.image' % (i+1)
        f2 = test + '/clean2/dirtymap_%d.image' % (i+1)
    flux1 = imstat(f1,axes=[0,1])['flux']
    flux2 = imstat(f2,axes=[0,1])['flux']
    d1 = (flux1-flux1[idx])
    d2 = (flux2-flux2[idx])
    print f1,d1[1:nch-1]
    print f2,d2[1:nch-1]
    print f1,flux1[1:nch-1]
    print f1,flux2[1:nch-1]


qac_end()

