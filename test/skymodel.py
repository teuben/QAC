#
#  a set of parameters to override sky4.py parameters, see e.g. sky4q
#

# root name of already existing skymodel models
mdir = 'sky4f'

# TP image  - two options:   the OTF or the original skymodel (model)
sd0    =  '%s/skymodel.otf' % mdir
sd0    =  model

# MS dictionary of cfg's. Each entry can be a list of ms

ms0    = {}
ms0[0] = ['%s/%s.aca.cycle6.ms'    % (mdir,mdir)]
ms0[1] = ['%s/%s.alma.cycle6.1.ms' % (mdir,mdir)]
ms0[2] = ['%s/%s.alma.cycle6.2.ms' % (mdir,mdir)]
ms0[3] = ['%s/%s.alma.cycle6.3.ms' % (mdir,mdir)]
ms0[4] = ['%s/%s.alma.cycle6.4.ms' % (mdir,mdir)]
ms0[5] = ['%s/%s.alma.cycle6.5.ms' % (mdir,mdir)]
ms0[6] = ['%s/%s.alma.cycle6.6.ms' % (mdir,mdir)]

# SM startmodel, can be used for a cheat. Any of the ms0's can be used
sm0    =   ms0[0].replace('.ms','.skymodel')

#
Qgmc   = True     # this is required to use sd0/ms0/sm0

# esmooth = 2.1       #   2 should be ok now

