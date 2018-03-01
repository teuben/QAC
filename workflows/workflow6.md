# TP2VIS workflow examples:  M100 Band3

In this workflow the following things are discussed:

1) benchmark comparing tp2vis with a published feather solution for ALMA Science Verification data

2) ...


## History

This Science Verification dataset is described at length in the
[casaguide "M100 Band3 Combine 4.3"](https://casaguides.nrao.edu/index.php/M100_Band3_Combine_4.3), where also
the CASA task **feather()** was used to combine 12m, 7m and TP data. The code is currently valid for CASA 4.3.0,
but in our workflow6a.py we have an expanded version that also works for CASA 5.1.1

Here we will show how to do this with tp2vis.

NOTE: this workflow uses the "QTP" routines. A CASA-only version is available in
[example1](example1.md). A executable regression version is available in workflow6.py

## Organizing the data

If you have not organized the calibrated data, here's a quick reminder.

You can also use our prepared 5 km/s datasets, this will only take about 120 MB. If you have
those data, you can skip to **Summary-2** below. The data for
this shortcut are available in http://admit.astro.umd.edu/~teuben/TP2VIS/

In the full version you will need close to 50GB of disk space to get you
started, but if you narrow this down using the **mstransform()** based
procedure we used in earlier examples, this will get you down to a
little over 100 MB to go through the examples. We have the smaller
files available elsewhere, so there is no real need to go through this procedure.

     # grab calibrated data as adertised in the CasaGuide
     wget -c https://bulk.cv.nrao.edu/almadata/sciver/M100Band3_12m/M100_Band3_12m_CalibratedData.tgz
     wget -c https://bulk.cv.nrao.edu/almadata/sciver/M100Band3ACA/M100_Band3_7m_CalibratedData.tgz
     wget -c https://bulk.cv.nrao.edu/almadata/sciver/M100Band3ACA/M100_Band3_ACA_ReferenceImages.tgz

     # checksum
     md5sum *.tgz

     7f0fe8a0cc4aeaf99cecfe97462f6768  M100_Band3_12m_CalibratedData.tgz
     eb37923d702d810a9ea1824f82228b94  M100_Band3_7m_CalibratedData.tgz
     12eb6b6dc1846095d006f10122fa4a00  M100_Band3_ACA_ReferenceImages.tgz


     # 12m
     tar zxf M100_Band3_12m_CalibratedData.tgz
     mv M100_Band3_12m_CalibratedData/M100_Band3_12m_CalibratedData.ms .

     # 7m
     tar zxf M100_Band3_7m_CalibratedData.tgz
     mv M100_Band3_7m_CalibratedData/M100_Band3_7m_CalibratedData.ms .

     # TP
     tar zxf M100_Band3_ACA_ReferenceImages.tgz
     mv M100_Band3_ACA_ReferenceImages/M100_TP_CO_cube.bl.image .

     # cleanup
     rm -rf *.tgz

     # you could keep these if you want to keep the the masks
     rm -rf M100_Band3_12m_CalibratedData M100_Band3_7m_CalibratedData M100_Band3_ACA_ReferenceImages 
     
## Inventory

You will now have the following data, two MS and one TP, about 21 GB in total:

     du -s M100_Band3_12m_CalibratedData.ms M100_Band3_7m_CalibratedData.ms M100_TP_CO_cube.bl.image

     16728112   M100_Band3_12m_CalibratedData.ms
     5525476    M100_Band3_7m_CalibratedData.ms
     3516       M100_TP_CO_cube.bl.image


The TP cube is already a CASA image, and is a
110 x 110 x 70 image cube
at 115 GHz with 5.64" pixels, so covering 616", or about 10 arcmin, on the sky.
However, only the central quarter of the image is filled, just under 300" in size.
It is already in the LSRK frame (see below).


## Summary-1

	qtp_summary('M100_TP_CO_cube.bl.image',['M100_Band3_7m_CalibratedData.ms'])
	TP: M100_TP_CO_cube.bl.image
	OBJECT:   M100
	SHAPE:    [110 110   1  70]
	CRVAL:    J2000 12h22m54.900s +15d49m15.000s
	RESTFREQ: 115.2712018
	FREQ:     114.732897122 114.600243469
	VEL:      1400.00000044 1745.00000044 5.00000000001
	VELTYPE:  LSRK
	UNITS:    Jy/beam
	
	MS:  M100_Band3_7m_CalibratedData.ms
	source 0 M100 (101.94584960927499, 99.954150390524987, 100.95, -2957.3868465863115, 2957.3868471803253, 1.4500548403448486, 4080)
	source 1 M100 (103.76099960937501, 101.76930039062501, 102.7941, -2819.9012446606944, 2988.7629139412702, 1.4240412254478954, 4080)
	source 2 M100 (111.81130039062499, 113.80299960937499, 112.7941, 2612.1571129693139, -2681.5276133216748, -1.2977898323831794, 4080)
	source 3 M100 (113.68630039062499, 115.67799960937499, 114.6691, 2569.4446944815313, -2637.6808902290977, -1.276569155359311, 4080)
	source 4 M100 (111.798250390625, 113.789949609375, 100.95, -32216.182759830859, -38130.95645359753, -1.4500548403448568, 4080)
	source 5 M100 (113.673250390625, 115.664949609375, 102.7941, -31728.35052359162, -37537.014682193556, -1.4240412254478882, 4080) 

NOTE: *There is a missing restfreq issue in the 12m data (qtp_summary can't deal with it yet). It is a little hard to decipher, because the
restfreq in spw 3 and 5 (hidden in source 3 and 5) are not that of CO(1-0).*

Comparing the spectral coverage of the TP with that of the MS data, this is a prime candidate to narrow down the MS data size.

We'll need to set the phase center (from CRPIX) to set the map center for the combination later on

     phasecenter = 'J2000 12h22m54.900s +15d49m15.000s'

According to [http://ned.ipac.caltech.edu](NED) the center of the galaxy is at   **12h22m54.8s +15d49m19s**   but this does appear a little bit off
from the center of the CO distribution.

## CO line

The CO line is in spw=0 for the 12m data, and spw=3,5 for the 7m data. Following the *casaguide*  we would do:

       split(vis='M100_Band3_12m_CalibratedData.ms',outputvis='M100_12m_CO.ms',spw='0',field='M100',datacolumn='data',keepflags=False)
       split(vis='M100_Band3_7m_CalibratedData.ms',outputvis='M100_7m_CO.ms',spw='3,5',field='M100',datacolumn='data',keepflags=False)

however, this still results in a 4.1 and 1.6 GB MS file for the 12m and 7m resp,
because is has all the 4080 narrow channels in a TOPO frame, and also
in rather narrow channels compared to those in the TP cube.  Better is
to transform them to the LSRK frame that the TP is already using, as
well as use the wider 5 km/s channels.  Following earlier workflow example we
arrive at:


       line = {"restfreq":'115.271202GHz','start':'1400km/s', 'width':'5km/s','nchan':70}

       rm -rf aver_12.ms
       mstransform('M100_Band3_12m_CalibratedData.ms','aver_12.ms',
		datacolumn='DATA',outframe='LSRK',mode='velocity',regridms=True,nspw=1,spw='0',field='M100',keepflags=False,
		**line)

       rm -rf aver_7.ms
       mstransform('M100_Band3_7m_CalibratedData.ms','aver_7.ms',
		datacolumn='DATA',outframe='LSRK',mode='velocity',regridms=True,nspw=1,spw='3,5',field='M100',keepflags=False,
		**line)

This resulted in a huge savings, down to 91MB and 35MB for the 12m and 7m data resp. This will also cut down the time
it needs to combine the data in tclean.

There is still a missing RESTFREQ in the header, but we will pass this directly into **tclean()** using the
**line argument.

       
## Summary-2

A final summary: (still missing the 12m for this)

       qtp_summary('M100_TP_CO_cube.bl.image',['aver_7.ms','aver_12.ms'])
       TP: M100_TP_CO_cube.bl.image       
       OBJECT:   M100
       SHAPE:    [110 110   1  70]
       CRVAL:    J2000 12h22m54.900s +15d49m15.000s
       RESTFREQ: 115.2712018
       FREQ:     114.732897122 114.600243469
       VEL:      1400.00000044 1745.00000044 5.00000000001
       VELTYPE:  LSRK
       UNITS:    Jy/beam

       MS:  aver_7.ms
       source 0 M100 (114.60024366825306, 114.73289732123453, 115.271202, 1744.9999999999588, 1399.9999999999975, -4.9999999999994396, 70)
       source 1 M100 (114.60024366825306, 114.73289732123453, 115.271202, 1744.9999999999588, 1399.9999999999975, -4.9999999999994396, 70)

       MS:  aver_12.ms
       source 0 M100 (114.60024366825306, 114.73289732123453, 0.0, 0.0, 0.0, 0.0, 70)


## RMS in TP

For a first estimate of the weights, we need the RMS in the line free channels. We use **imstat()** to get the RMS in each channel:

       imstat('M100_TP_CO_cube.bl.image',axes=[0,1])['rms']
       array([ 0.14337216,  0.15416368,  0.1538811 ,  0.1637802 ,  0.15695214,
        0.15064906,  0.19009656,  0.13240274,  0.22253673,  0.29421415,
        0.54377563,  0.99837328,  1.44225686,  1.66375035,  1.83363971,
        1.70566721,  1.52608863,  1.42842863,  1.46339637,  1.46338736,
        1.49941495,  1.53423894,  1.6788115 ,  1.69735124,  1.66694226,
        1.65208956,  1.63182044,  1.50324131,  1.33159866,  1.26049209,
        1.27482774,  1.30224403,  1.3155383 ,  1.35278868,  1.38103872,
        1.38343852,  1.33440951,  1.2350521 ,  1.26101556,  1.32380901,
        1.36983004,  1.48570868,  1.54116441,  1.61903414,  1.64715744,
        1.68984851,  1.80783974,  1.919558  ,  1.92914851,  1.91434157,
        1.83122544,  1.71110827,  1.63323534,  1.64795756,  1.77503358,
        1.81684968,  1.55364226,  1.23536157,  0.94053626,  0.62474876,
        0.36526463,  0.22212504,  0.15871309,  0.16036025,  0.15752548,
        0.13215077,  0.15331902,  0.13407601,  0.16014362,  0.17119723])

Which looks like the first few and last few channels are line free:

	imstat('M100_TP_CO_cube.bl.image',axes=[0,1])['rms'][:6].mean()
	-> 0.154  (0.125 in the inner box)

	imstat('M100_TP_CO_cube.bl.image',axes=[0,1])['rms'][-6:].mean()
	-> 0.151  (0.114 in the inner box)

If you want to see a plot of Min/Max/RMS, use one of the plot helper functions:

	plot5('M100_TP_CO_cube.bl.image')

![plot5](figures/m100_plot5.png)

If you get the interactive matplotlib on the screen, you will be able to zoom into the two shoulders
and inspect the best ranges for the channels to estimate a good value for the RMS.


## Initial mapping

We need to get the 12m pointings for mapping the TP

       qtp_ms_ptg('aver_12.ms','aver_12.ptg')


Compute visibilities from the TP and re-mapping these (notice large pixels)

       qtp_tp('test1','M100_TP_CO_cube.bl.image','aver_12.ptg',128,5,niter=0,rms=0.15,phasecenter=phasecenter)
       WEIGHT: Old=1.0 New=0.0107354 Nvis=4140

Comparing fluxes: (mean, rms, min, max, flux)

       qtp_stats('M100_TP_CO_cube.bl.image')
       STATS: 0.54682752152594571, 1.2847112260328186, -0.89499807357788086, 8.8632850646972656, 4001.315200610718)
       
       qtp_stats('test1/dirtymap.image')
       STATS:  0.91702267288437445, 1.2589038325185919, 0.072469912469387054, 6.873809814453125, 4737.5539535223179

Although the TP data claims the total flux is about 4000 Jy.km/s, inspection of the maps will show this is an overestimate due to
TP artifacts in the edge regions. Generally we will need to do a flux comparison in a better defined region.  From the M100 casaguide
we pick

	box1 = '39,33,74,71'
       
Then we continue and map various combinations of 12m, 7m and TP, but in order to avoid edge channel problems, take off one channel of either end:

       line = {"restfreq":'115.271202GHz','start':'1405km/s', 'width':'5km/s','nchan':68}

       # just 7m
       qtp_clean1('test2a','aver_7.ms',512,1.5,niter=0,phasecenter=phasecenter,**line)
       -> 13.9 x 10.8 @ -88deg
       qtp_stats('test2a/dirtymap.image')
       STATS:  0.00010608723994142315, 0.08997501585030572, -0.68462353944778442, 2.4904146194458008, 15.856599635733675)

       # just 12m
       qtp_clean1('test2b','aver_12.ms',512,1.5,niter=0,phasecenter=phasecenter,**line)
       qtp_stats('test2b/dirtymap.image')
       STATS:  -1.8733255271132615e-06, 0.016066182823863462, -0.15252432227134705, 0.55621969699859619, -3.0518904661967525

       # TP + 7m
       qtp_clean('test2c','test1/tp.ms','aver_7.ms',512,1.5,niter=0,phasecenter=phasecenter,**line)
       WEIGHT min/max:  0.0610964559019 0.290469944477
       WEIGHT min/max:  0.0107353730127 0.0107353730127
       -> 13.9" x 10.8" @ -88deg
       qtp_stats('test2c/tpalma.image')
       STATS:  0.05594231838218594, 0.12513078349605897, -0.35609498620033264, 2.7943828105926514, 7019.5587377738921

       # TP + 12m
       qtp_clean('test2d','test1/tp.ms','aver_12.ms',512,1.5,niter=0,phasecenter=phasecenter,**line)
       WEIGHT min/max:  0.473205626011 1.79564714432
       WEIGHT min/max:  0.0107353730127 0.0107353730127
       -> 4.3" x 2.5" @ 70deg
       qtp_stats('test2d/tpalma.image')
       STATS: 0.019088903248514841, 0.058592089079343941, -0.088251858949661255, 0.71008288860321045, 20712.214140501328

       # TP + 12m + 7m
       qtp_clean('test2e','test1/tp.ms',['aver_12.ms','aver_7.ms'],800,0.5,niter=0,phasecenter=phasecenter,**line)
       WEIGHT min/max:  0.473205626011 1.79564714432
       WEIGHT min/max:  0.0610964559019 0.290469944477
       WEIGHT min/max:  0.0107353730127 0.0107353730127
       -> 4.6" x 3.0" @ -89
       qtp_stats('test2e/tpalma.image')       
       STATS:  0.016501103732203416, 0.059258307847094231, -0.12162975966930389, 0.88630974292755127, 14098.603744797363

       tp2viswt('test1/tp.ms',mode=2,factor=10)
       qtp_clean('test2f','test1/tp.ms',['aver_12.ms','aver_7.ms'],512,1.5,niter=0,phasecenter=phasecenter,do_alma=False,**line)
       WEIGHT min/max:  0.10735373199 0.10735373199
       -> 4.3" x 3.0" @ 89deg
       qtp_stats('test2f/tpalma.image')              
       STATS:  0.10279768542478428, 0.1450867078647059, -0.039790254086256027, 1.3810303211212158, 109731.4920369356

       # weights based on theoretical Cij's
       tp2viswt('test1/tp.ms',rms=41.9,mode=5)
       # wt -> 0.000569602588274
       qtp_clean('test2g','test1/tp.ms',[ms12,ms07],512,1.5,niter=0,phasecenter=phasecenter,do_alma=False,**line)

       # beam size weights 
       tp2viswt('test1/tp.ms',[ms07,ms12],'test1/dirtymap.psf',4.0,mode=4)
       # wt -> 0.0044103029511 -> 0.00433382295945
       qtp_clean('test2h','test1/tp.ms',[ms12,ms07],512,1.5,niter=0,phasecenter=phasecenter,do_alma=False,**line)

       

## Automasking

In the casaguide a whole section is spent on automasking. This would be useful to consider for a tp2vis approach as well.

box='219,148,612,579'

## Acknowledgements and Data Usage

This paper makes use of the following ALMA data: ADS/JAO.ALMA#2011.0.00004.SV.
ALMA is a partnership of ESO (representing its member states), NSF (USA)
and NINS (Japan), together with NRC (Canada) and NSC and ASIAA (Taiwan),
and KASI (Republic of Korea), in cooperation with the Republic of Chile.
The Joint ALMA Observatory is operated by ESO, AUI/NRAO and NAOJ.

We thank the following people for suggesting M100 for ALMA Science Verification:
Preben Grosbol and Catherine Vlahakis.
