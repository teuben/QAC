# TP2VIS workflow examples:  Lupus 3 MMS Outflow


In this workflow the following peculiarities are discussed:

1) ...

2) missing RESTFREQ in one of the MS files


## Inventory 

Here is an example of *an outflow* (Plunkett et al., in prep), from cycle 3 (2015.1.00306.S)

We have the following data for TP and two MS (almost 21GB):

     du -s Lupus_3_MMS.spw15.I.sd.im.fits Lup3mms_12CO_calibrated_12m.ms Lup3mms_12CO_calibrated_7m.ms

     11628      Lupus_3_MMS.spw15.I.sd.im.fits
     17780192   Lup3mms_12CO_calibrated_12m.ms
     2877280    Lup3mms_12CO_calibrated_7m.ms


with the TP being a 64 x 44 x 1024 image cube at 115.27 GHz with 5.61"
pixels, so covering almost 360", or about 6 arcmin, on the sky.  Notice the
RESTFREQ in the FITS header is a bit offset (115.217921276) from the
expected CO, so programs like
ADMIT will not detect the very obvious CO line!

## Import

After the initial import, the axes are not RA-DEC-POL-FREQ, which is fixed by **tp2vischeck()**


     importfits('Lupus_3_MMS.spw15.I.sd.im.fits','tp1.im')
     pjt_summary('tp1.im')

     phasecenter = 'J2000 16h09m18.12s -39d04m41.974s'


## Inventory and Inspection


The CO line is limited between channels 470 and 540, channels are
0.317591 km/s. There is another source in the SW corner coming in at
slightly lower velocity, -17.0 km/s with sigma 0.4 km/s, where Lupus
has signal between about 2 and 8 km/s. Since there is no obvious
connection the the main line (as seen in PV diagrams), we're going to
ignore this.  Glancing through PV diagrams one can see low level
emissions coming off the main line around 10-20 Jy/beam, where the
main line is 500-700 Jy/beam, mostly on the high velocity side.  RMS
in the cube is 0.19 Jy/beam.


        imstat('tp1.im',axes=[0,1])['rms'][0:400].mean()
        -> 0.19

	imsubimage('tp1.im','tp2.im',chans='470~540')
	exportfits('tp2.im','tp2.fits',overwrite=True)
	
Visualizing this cube is difficult due to the strong CO line. Here is
a viewing trick to see large dynamic range images, scaling them as
sigma*log10(1+flux/sigma), i.e. near 0 the signal is linear, and turns
logarithmic beyond. It only works well is there is no bias
(continuum). We assume the sigma is 0.19 Jy/beam:

	s = 0.19
	expr = 'SIGN(IM0)*%f*log10(1+ABS(IM0)/%f)' % (s,s)
	rm -rf tp1s.im
	immath('tp1.im','evalexpr','tp1s.im',expr)
	viewer('tp1s.im')
	exportfits('tp1s.im','tp1s.fits',overwrite=True)


## Summary

	pjt_summary('tp1.im')

	TP: tp2.im
	OBJECT:   Lupus_3_MMS
	SHAPE:    [  66   44    1 1024]
	CRVAL:    J2000 16h09m18.120s -39d04m41.974s
	RESTFREQ: 115.217921276
	FREQ:     115.206829169 115.331695011
	VEL:      28.8612208518 -296.03474256 -0.317591362084
	VELTYPE:  LSRK
	UNITS:    Jy/beam

## Layout

There are 29 pointings in 3 rows. Circles are 20" diameter, but the PB is 56", to avoid crowding the plot. It does however look like the TP map
covered more than the VIS pointings! For example, the SW cloud at -17 km/s is not picked up in the VIS pointings.

![figure1](figures/lupus1.png)

## Initial mapping

A test mapping of the TP data: (cheating to get the ptg from listobs). Need to get the RMS in the cube.

       
       pjt_ms_ptg('aver_12.ms','aver_12.ptg')
       
       pjt_tp('test1','tp2.im','aver_12.ptg',128,4,niter=0,indirection=phasecenter,rms=0.19)
       WEIGHT: Old=1.0 New=0.00669102 Nvis=4140

Problem? beam is not very spherical: 58" x 45" @ 74deg, despite that UV looks ok.

## PJT running

Combining:

       pjt_clean('test2a','test1/tp.ms',['aver_07.ms','aver_12.ms'],400,1.0,niter=0,indirection=phasecenter)

shorter and quicker

	line = {'nchan' : 3 }
	pjt_clean('test2a','test1/tp.ms',['aver_07.ms','aver_12.ms'],400,1.0,niter=0,indirection=phasecenter,do_alma=False,**line)
	Wall time: 2min 50s
	# 6 ok too
	#  3-> 2'24"    100=24min 33s

	pjt_clean('test2a','aver_tp.ms',['aver_07.ms','aver_12.ms'],900,0.4,niter=0,indirection=phasecenter,do_alma=False,**line)
	=>DIES

## ALP running according to README.md

Get pointing (and other) information.

       listobs(vis='../datasym/12m_Lup3mms_12CO_calibrated.ms/',listfile='calibrated_12m.log')

Copy and paste the pointings into a file 12m.ptg, manually adjust the format to look like :

J2000 ##h##m##s ##d##m##s

       execfile('/mnt/sciops/data/aplunket/Combo/tp2vis/tp2vis.py')  # simple install
       tpfitsfile = '../datasym/Lupus_3_MMS.spw15.I.sd.im.fits'
       importfits(tpfitsfile,'tp1.im')

You need the RMS:

       tprms = imstat(tpfitsfile,axes=[0,1,])['rms'][:10].mean() #in this case, tprms=0.19148408057198799

Finally make visibilities:

       tp2vis('tp1.im','tp.ms','12m.ptg',rms=tprms)    # make visibilities 

Note: including the rms at this stage results in weights being set for TP map, so you will see this part of the output:

      Adjusting the weights using rms = 0.191484  nvis=4140
      WEIGHT: Old=1.0 New=0.00658771 Nvis=4140

Setup the tclean of the dirty TP cube:

	imagename='tp_dirt'
	visname='tp.ms'
	
	phasecenter='J2000 16h09m18.12s -39d04m41.974s'
	mapsize_inx = 900
	mapsize_iny = 480
	pixelsize='0.4arcsec'
	niter=0
	imsize=[mapsize_inx,mapsize_iny]
	weighting = 'natural'
	tclean(vis=visname,imagename=imagename,niter=niter,gridder='mosaic',
               imsize=imsize, cell=pixelsize,                          
               phasecenter=phasecenter,
               weighting=weighting,specmode='cube',
               nchan=70,start=470)

(I only choose the channels 470-540 to make the cube smaller, other channels were noise.
Notice velocities are still strange until you set rest frequency in the mstransform step.)

![figure2](figures/lupusTPdirtymap.png)

Now for mstransform:

	restfreq='115.27120GHz' 
	start='-30km/s' # start velocity. See science goals for appropriate value.
	width='0.318km/s' # velocity width. See science goals.
	nchan = 200  # number of channels. See science goals for appropriate value.

	sevenmms = 'Lup3mms_12CO_calibrated_7m.ms'
	twelvemms = 'Lup3mms_12CO_calibrated_12m.ms'

	tpms      = 'tp.ms'

	#7M array
	!rm -rf aver_07.ms
	mstransform(sevenmms,'aver_07.ms',
	  start=start,nchan=nchan,width=width,restfreq=restfreq,
	  datacolumn='DATA',outframe='LSRK',mode='velocity',regridms=True,keepflags=False)
	#12M array
	!rm -rf aver_12.ms
	mstransform(twelvemms,'aver_12.ms',
	  start=start,nchan=nchan,width=width,restfreq=restfreq,
	  datacolumn='DATA',outframe='LSRK',mode='velocity',regridms=True,keepflags=False)
	#TOTAL POWER array
	## FOR NOW THIS aver_tp.ms file will not work in the final concat (below)
	!rm -rf aver_tp.ms
	mstransform(visname,'aver_tp.ms',
	  start=start,nchan=nchan,width=width,restfreq=restfreq,
	  datacolumn='DATA',outframe='LSRK',mode='velocity',regridms=True,keepflags=False)

It's possible to make a map for each array individually (dirty map with niter=0).  This is a good time to choose map size and pixel size.

	vis7='aver_07.ms'
	outim7='test7'
	vis12='aver_12.ms'
	outim12='test12'
	vistp='aver_tp.ms'
	outimtp='testtp2'
	phasecenter='J2000 242.3255deg -39.0783261111deg'
	mapsize_inx = 900
	mapsize_iny = 600
	pixelsize='0.4arcsec'
	niter=0
	imsize=[mapsize_inx,mapsize_iny]
	weighting = 'natural'
	tclean(vis=vis7,imagename=outim7,niter=niter,gridder='mosaic',
               imsize=imsize, cell=pixelsize,                          
               phasecenter=phasecenter,
               weighting=weighting,specmode='cube')
	tclean(vis=vis12,imagename=outim12,niter=niter,gridder='mosaic',
               imsize=imsize, cell=pixelsize,                          
               phasecenter=phasecenter,
               weighting=weighting,specmode='cube')
	tclean(vis=vistp,imagename=outimtp,niter=niter,gridder='mosaic',
               imsize=imsize, cell=pixelsize,                          
               phasecenter=phasecenter,
               weighting=weighting,specmode='cube',restfreq=restfreq)

![figure3](figures/Lup3mms_red.png)
![figure4](figures/Lup3mms_cloud.png)
![figure5](figures/Lup3mms_blu.png)

Before proceeding, you need to concat each .ms file into a single .ms :

	concat(vis=['aver_12.ms','aver_07.ms','tp.ms'], concatvis='all3.ms',copypointing=False)
	
(The copypointing part is important!)

Note, this way (using the mstransform version of tp.ms) will not work!

	concat(vis=['aver_12.ms','aver_07.ms','aver_tp.ms'], concatvis='all3.ms',copypointing=False)

Finally, the "tclean" step.

	visname='all3.ms'
	imagename='alldirt4'
	phasecenter='J2000 242.3255deg -39.0783261111deg'
	mapsize_inx = 1800
	mapsize_iny = 1200
	pixelsize='0.2arcsec'
	#previously I tried with these parameters
	#mapsize_inx = 900
	#mapsize_iny = 600
	#pixelsize='0.4arcsec'
	niter=0
	imsize=[mapsize_inx,mapsize_iny]
	weighting = 'natural'

	tclean(vis=visname,imagename=imagename,niter=niter,gridder='mosaic',
	  imsize=imsize, cell=pixelsize,
	  phasecenter=phasecenter,
	  weighting=weighting,specmode='cube')

## PJT

   pjt_clean('junk1','aver_tp.ms', ['aver_12.ms','aver_07.ms'],512,1,niter=0,do_alma=False)

Notice this full data takes about 8GB of memory, and takes a few hours to complete.


## Other data?


Cycle2 data exist.   See https://arxiv.org/abs/1611.08416

**ALP:** Yes, and he is involved in our Cycle 5 proposal for Band 6 mapping observations of the same source, so we could potentially share data.


## Troubleshooting

**ALP** "Issues": 
* How to see phase center: https://github.com/kodajn/tp2vis/issues/1
* Remember to use CASA 5.0: https://github.com/kodajn/tp2vis/issues/2

<
