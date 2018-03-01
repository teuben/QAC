#
# execfile this in CASA, it should mirror example1.md
# make sure files beyond the "cmds" don't exist
#
# workflow6 is the regression test version of this, except it only deals with 5 km/s channel data
#
# this example needs about 32GB in its full glory and takes about 90 mins to completion.
# It also produced Figure 3 from the paper as plot_tp2viswt_rms.png

import os, sys

cmds = [
    'wget -c https://bulk.cv.nrao.edu/almadata/sciver/M100Band3_12m/M100_Band3_12m_CalibratedData.tgz',
    'wget -c https://bulk.cv.nrao.edu/almadata/sciver/M100Band3ACA/M100_Band3_7m_CalibratedData.tgz',
    'wget -c https://bulk.cv.nrao.edu/almadata/sciver/M100Band3ACA/M100_Band3_ACA_ReferenceImages.tgz',
    'tar xfz M100_Band3_12m_CalibratedData.tgz',
    'tar xfz M100_Band3_7m_CalibratedData.tgz',
    'tar xfz M100_Band3_ACA_ReferenceImages.tgz',
    'mv -i M100_Band3_12m_CalibratedData/M100_Band3_12m_CalibratedData.ms .',
    'mv -i M100_Band3_7m_CalibratedData/M100_Band3_7m_CalibratedData.ms .',
    'mv -i M100_Band3_ACA_ReferenceImages/M100_TP_CO_cube.bl.image .',
]


if False:
    for cmd in cmds:
        print "CMD:",cmd
        os.system(cmd)
    sys.exit(0)
else:
    import os.path
    if not os.path.exists('M100_12m.ptg'):
        print "Assuming you have your 5 files and nothing else; e.g."
        print "ln -s ...somewhere.../data"
        print "ln -s data/M100_Band3_12m_CalibratedData.ms"
        print "ln -s data/M100_Band3_7m_CalibratedData.ms"
        print "ln -s data/M100_TP_CO_cube.bl.image"
        print "ln -s data/M100_12m.ptg"
        sys.exit(1)

#   execfile('tp2vis.py')           # Assume this was done and it's in the environment now


#   the two split() steps take a lot of time and diskspace, so are protected to run again
#   M100_Band3_12m_CalibratedData.ms     16.7 GB
#   M100_Band3_7m_CalibratedData.ms       5.5 GB
#   M100_12m_CO.ms                        4.2 GB
#   M100_7m_CO.ms                         1.6 GB
if not os.path.exists('M100_12m_CO.ms'):   
    split(vis='M100_Band3_12m_CalibratedData.ms',outputvis='M100_12m_CO.ms',spw='0',field='M100',datacolumn='data',keepflags=False)
if not os.path.exists('M100_7m_CO.ms'):
    split(vis='M100_Band3_7m_CalibratedData.ms',outputvis='M100_7m_CO.ms',spw='3,5',field='M100',datacolumn='data',keepflags=False)

# none of the code below deals very well with files that exist, so don't even think about re-running this.


os.system('rm -rf M100_07m12m_CO_dirty.* M100_07m12m_CO_clean.*')

tclean(vis=['M100_12m_CO.ms','M100_7m_CO.ms'],imagename='M100_07m12m_CO_dirty', niter=0,    gridder='mosaic',imsize=800,cell='0.5arcsec',phasecenter='J2000 12h22m54.9 +15d49m15',weighting='natural',threshold='0mJy',specmode='cube',outframe='LSRK',restfreq='115.271201800GHz',nchan=70,start='1400km/s',width='5km/s')
tclean(vis=['M100_12m_CO.ms','M100_7m_CO.ms'],imagename='M100_07m12m_CO_clean', niter=10000,gridder='mosaic',imsize=800,cell='0.5arcsec',phasecenter='J2000 12h22m54.9 +15d49m15',weighting='natural',threshold='0mJy',specmode='cube',outframe='LSRK',restfreq='115.271201800GHz',nchan=70,start='1400km/s',width='5km/s')

#

#imview(raster=[{'file': 'M100_07m12m_CO_dirty.image'}],zoom={'channel':23,'blc': [200,200], 'trc': [600,600]},out='M100_07m12m_CO_dirty.23.png')
#imview(raster=[{'file': 'M100_07m12m_CO_dirty.image'}],zoom={'channel':47,'blc': [200,200], 'trc': [600,600]},out='M100_07m12m_CO_dirty.47.png')


rms =  imstat('M100_TP_CO_cube.bl.image',axes=[0,1])['rms'][:6].mean()

os.system('rm -rf M100_TP_CO.ms')
tp2vis('M100_TP_CO_cube.bl.image','M100_TP_CO.ms','M100_12m.ptg',nvgrp=20,rms=0.15379972353470259)

os.system('rm -rf M100_TP07m12m_CO.ms')
concat(vis=['M100_TP_CO.ms','M100_7m_CO.ms','M100_12m_CO.ms'],concatvis='M100_TP07m12m_CO.ms',copypointing=False)


os.system('rm -rf M100_TP07m12m_CO_dirty.* M100_TP07m12m_CO_clean.*')
tclean(vis='M100_TP07m12m_CO.ms',imagename='M100_TP07m12m_CO_dirty', niter=0,    gridder='mosaic',imsize=800,cell='0.5arcsec',phasecenter='J2000 12h22m54.9 +15d49m15',weighting='natural',threshold='0mJy',specmode='cube',outframe='LSRK',restfreq='115.271201800GHz',nchan=70,start='1400km/s',width='5km/s')
tclean(vis='M100_TP07m12m_CO.ms',imagename='M100_TP07m12m_CO_clean', niter=10000,gridder='mosaic',imsize=800,cell='0.5arcsec',phasecenter='J2000 12h22m54.9 +15d49m15',weighting='natural',threshold='0mJy',specmode='cube',outframe='LSRK',restfreq='115.271201800GHz',nchan=70,start='1400km/s',width='5km/s')

os.system('rm -rf difference.im')
immath(imagename=['M100_TP07m12m_CO_dirty.image','M100_07m12m_CO_dirty.image'],expr='IM0-IM1',outfile='difference.im')


#imview(raster=[{'file': 'M100_TP07m12m_CO_dirty.image'}],zoom={'channel':23,'blc': [200,200], 'trc': [600,600]},out='M100_TP07m12m_CO_dirty.23.png')
#imview(raster=[{'file': 'M100_TP07m12m_CO_dirty.image'}],zoom={'channel':47,'blc': [200,200], 'trc': [600,600]},out='M100_TP07m12m_CO_dirty.47.png')

tp2viswt('M100_TP_CO.ms',mode='stat')

tp2viswt(['M100_7m_CO.ms','M100_12m_CO.ms'],mode='stat')


tp2vispl(['M100_TP_CO.ms','M100_7m_CO.ms','M100_12m_CO.ms'],outfig="plot_tp2viswt_rms.png")

tp2viswt("M100_TP_CO.ms",mode='const',value=0.015)

tp2viswt("M100_TP_CO.ms",mode='multiply',value=10.0)

tp2viswt("M100_TP_CO.ms",mode='rms',value=0.15379972353470259)


tp2viswt(['M100_TP_CO.ms','M100_7m_CO.ms','M100_12m_CO.ms'],mode='beam',makepsf=True)      # this takes time

os.system('rm -rf M100_TP07m12m_CO.ms')
concat(vis=['M100_TP_CO.ms','M100_7m_CO.ms','M100_12m_CO.ms'],concatvis='M100_TP07m12m_CO.ms',copypointing=False)

os.system('rm -rf M100_TP07m12m_CO_dirty.*  M100_TP07m12m_CO_clean.*')
tclean(vis='M100_TP07m12m_CO.ms',imagename='M100_TP07m12m_CO_dirty',niter=0,    gridder='mosaic',imsize=800,cell='0.5arcsec',phasecenter='J2000 12h22m54.9 +15d49m15',weighting='natural',threshold='0mJy',specmode='cube',outframe='LSRK',restfreq='115.271201800GHz',nchan=70,start='1400km/s',width='5km/s')
tclean(vis='M100_TP07m12m_CO.ms',imagename='M100_TP07m12m_CO_clean',niter=10000,gridder='mosaic',imsize=800,cell='0.5arcsec',phasecenter='J2000 12h22m54.9 +15d49m15',weighting='natural',threshold='0mJy',specmode='cube',outframe='LSRK',restfreq='115.271201800GHz',nchan=70,start='1400km/s',width='5km/s')


# outside scope, but useful

tp2vistweak('M100_TP07m12m_CO_dirty','M100_TP07m12m_CO_clean')         # need both dirty and clean image sets


# imview (raster=[{'file': 'M100_TP07m12m_WT_CO_dirty.image'}],zoom={'channel':23,'blc': [200,200], 'trc': [600,600]},out='M100_TP07m12m_WT_CO_dirty.23.png')
# imview (raster=[{'file': 'M100_TP07m12m_WT_CO_dirty.image'}],zoom={'channel':47,'blc': [200,200], 'trc': [600,600]},out='M100_TP07m12m_WT_CO_dirty.47.png')


