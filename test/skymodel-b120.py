#
#  a set of parameters to override sky4.py parameters to work with Toshi's data
#
#  via sky4.py this use about 1GB memory and produce around 2GB in datafiles
#  probably needs ulimit -Sn 4096
#

# root directory (plus slash) where the models are
#  
gdir = 'gmc_120L/'             # old one
gdir = 'skymodel-b_120L/'      # new one (oct 2, 2020)

# TP image
sd0    =  gdir+'skymodel-b_120L.sd.image'

# MS dictionary of cfg's. Each entry can be a list of ms

ms0    = {}
ms0[0] = [gdir+'skymodel-b_120L.aca.cycle6.2018-10-20.ms',
          gdir+'skymodel-b_120L.aca.cycle6.2018-10-21.ms',
          gdir+'skymodel-b_120L.aca.cycle6.2018-10-22.ms',
          gdir+'skymodel-b_120L.aca.cycle6.2018-10-23.ms']
ms0[1] = [gdir+'skymodel-b_120L.alma.cycle6.1.2018-10-02.ms',
          gdir+'skymodel-b_120L.alma.cycle6.1.2018-10-03.ms',
          gdir+'skymodel-b_120L.alma.cycle6.1.2018-10-04.ms',
          gdir+'skymodel-b_120L.alma.cycle6.1.2018-10-05.ms']
ms0[4] = [gdir+'skymodel-b_120L.alma.cycle6.4.2018-10-02.ms',
          gdir+'skymodel-b_120L.alma.cycle6.4.2018-10-03.ms',
          gdir+'skymodel-b_120L.alma.cycle6.4.2018-10-04.ms',
          gdir+'skymodel-b_120L.alma.cycle6.4.2018-10-05.ms']

# SM startmodel, can be used for a cheat

sm0    =  gdir + 'skymodel-b_120L.aca.cycle6.2018-10-20.skymodel'


wfactor = 0.03   # beam is ..
wfactor = 0.3    # beam is ..

#
Qgmc   = True     # this is required to use sd0/ms0/sm0

# something odd about the TPINT beam, it's bigger than 2.0" !!!
# the INT beam is 1.99

# esmooth = 2.5

