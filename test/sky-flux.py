# -*- python -*-
#
#  Typical usage (see also Makefile)
#      casa -c sky4.py  [optional parameters]
#
#  Reminder: at 115 GHz we have:
#      12m PB is 50" (FWHM)   [FWHM" ~ 600/DishDiam]
#       7m PB is 85"
#
#  Integration times:
#     TP               uses (nvgrp * npnt) seconds
#     INT (per config) uses times[0] hours in total, times[1] minutes per pointing
#                      thus it is useful to make sure that (times[0]*60) / (times[1]*npnt) is integral
#
#
#  - clean0:    mapping the TP.MS: 
#  - clean3:    mapping the 'int' and 'tpint' from tp2vis
#  - clean4:    hybrid :
#                   with or without tp.ms,   with rescaled otf or skymodel (jy/pix)
#               
#
# @todo    set a mask so it only cleans in the original

import glob

pdir         = 'slide30'
image        = 'clean3/int_*.image.pbcor'
box          = '150,150,970,970'

# export smooth in arcsec? 
esmooth      = None
esmooth      = 2.0

# -- do not change parameters below this ---
import sys
for arg in qac_argv(sys.argv):
    exec(arg)


images = glob.glob('%s/%s' % (pdir,image))
images.sort()
print(images)
print("Found %d images" % len(images))

for i in images:
    qac_fits(i, box=box, stats=True, smooth=esmooth)

