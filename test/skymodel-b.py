#
#  a set of parameters to override sky4.py parameters to work with Toshi's data
#

# root directory (plus slash) where the models are
gdir = 'gmc_2L/'

# TP image
sd0    =  gdir+'gmc_2L.sd.image'

# MS dictionary of cfg's. Each entry can be a list of ms

ms0    = {}
ms0[0] = [gdir+'gmc_2L.aca.cycle6.2018-10-06.ms',
          gdir+'gmc_2L.aca.cycle6.2018-10-07.ms']
ms0[1] = [gdir+'gmc_2L.alma.cycle6.1.2018-10-02.ms',
          gdir+'gmc_2L.alma.cycle6.1.2018-10-03.ms']
ms0[4] = [gdir+'gmc_2L.alma.cycle6.4.2018-10-02.ms',
          gdir+'gmc_2L.alma.cycle6.4.2018-10-03.ms']

# SM startmodel, can be used for a cheat

sm0    =  gdir + 'gmc_2L.aca.cycle6.2018-10-06.skymodel'


wfactor = 0.03

#
Qgmc   = True     # this is required to use sd0/ms0/sm0

# something odd about the TPINT beam, it's bigger than 2.0" !!!
# the INT beam is 1.99

esmooth = 2.1

