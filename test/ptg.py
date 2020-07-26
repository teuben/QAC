# -*- python -*-
#
#  find pointings


test         = 'test'
phasecenter  = 'J2000 180.0deg -30.0deg'

imsize_m     = 4096                 # pixels
pixel_m      = 0.05                 # arcsec
grid         = 30.0                 # arcsec   
dish         = 12.0                 # m

fwhm12       = 57.0                 # at 115 GHz for 12m dish; should not change this

ms = None
im = None


# -- do not change parameters below this ---
import sys
for arg in qac_argv(sys.argv):
    exec(arg)

# derived parameters
ptg      = test + '.ptg'            # pointing mosaic for the ptg

fwhm = fwhm12 * (12.0/dish)

if ms != None:
    p = qac_ms_ptg(ms)
    print("Found %d pointings in %s from ms=%s" % (len(p),ms))
else:
    # create a mosaic of pointings for 12m
    p = qac_im_ptg(phasecenter, imsize_m, pixel_m, grid, rect=True, outfile=ptg)

    print("Found %d pointings in %s for grid=%g on FOV = %d * %g = %g" % (len(p),ptg,grid,imsize_m,pixel_m,imsize_m*pixel_m))
    print("dish=%gm gives FWHM=%g   sampling FWHM/grid=%g and should be around 2" % (dish,fwhm,fwhm/grid))
