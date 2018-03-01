# TP2VIS workflow example 1:  cloud197


The accompanying script **workflow1.py** is a regression test version of what is discussed in this document
in a bit more detail. Note were are using the **qac.py** shortcut functions here.

We start off by using some verbiage directly taken from the ALMA archive:

## ALMA archive

### Project title

Revealing Internal Structure of Molecular Clouds in the LMC at Various Evolutionary Stages

### PI name

Sawada, Tsuyoshi

### Proposal abstract

We propose 12CO J=1-0 mosaic observations of five molecular clouds in
the Large Magellanic Cloud (LMC) at a spatial resolution directly
relevant to star formation (~1 pc). The ALMA Cycle 1 with the
capability of ACA permits resolved studies of molecular gas in the
external galaxy for the first time. The present observations provide
the high fidelity, high spatial resolution images of the sample of
five clouds, which covers a wide range of evolutionary stages based on
their associations to recent star formation. We characterize the
spatial structure of the gas (e.g., clumpiness), which was found to be
tightly related to the evolution of the gas in the Milky Way (MW) in
our recent studies, using the new tools we developed. We then examine
the difference of the structure of the gas among the clouds (i.e.,
evolutionary stages and local environments) and between the LMC and
the MW. The study will give us the clue to understand the properties
of interstellar medium and its influence to star formation in the
galaxy where the environment is very different from the MW.


## Nomenclature

We have:

	TP = Total Power (single dish) image cube.
	VI = Virtual Interferometer
	MS = MeasurementSet, representing visibilities from an Interferometer


For our workflow, lets assume we have a single TP cube, and one or
more MS corresponding to one or more ALMA 12m and/or 7m observations,
with of course overlapping frequencies. Typically your TP will be with
frequencies in the LSRK frame (MEAS_FREQ_REF=1), but the visibilities
of ALMA are often still in the TOPO frame (MEAS_FREQ_REF=5). More on that
re-alignment below.

First you should run a **summary** of your data, to help you understand what
overlap there is in the observations. For line data, a frequent
selection will be to set the rest frequency and select a common gridding
for TP and MS before they go into **tclean()**. Normally you would select
a common velocity gridding, to be able to compare difference lines. 


## Inventory 

In this first workflow we present the example of *cloud197* (Sawada et
al., in prep), which we will use as a benchmark and regression
test. These are part of the ALMA Cycle project 2012.1.00641.S
(see also **acknowledgements** at the end of this document)

To size up what we have for our 3 datasets (1 TP and 2 MS):
(in the CASA shell you will need the ! symbol before the command,in the Unix shell you can leave it off)

     !du -s cloud197_casa47.spw17.image/ calib_split_07m.ms/ calib_split_12m.ms/

     6764      cloud197_casa47.spw17.image/
     364428    calib_split_07m.ms/
     2138252   calib_split_12m.ms/

The TP image cube is small (almost 7 MB), and the 12m data (about 2.1GB) dominate the data.

## First summary

You can of course also use standard CASA tasks **imhead()** and **listobs()**, but we have a
short summary of those in **qtp_summary()**.


	 qtp_summary('cloud197_casa47.spw17.image',['calib_split_07m.ms','calib_split_12m.ms'])

	 TP: cloud197_casa47.spw17.image
	 OBJECT:   cloud_197
	 SHAPE:    [150 150   1  43]
	 CRVAL:    J2000 05h39m50.000s -70d07m0.000s
	 RESTFREQ: 115.271202
	 FREQ:     115.188918285 115.172769145
	 VEL:      213.999999525 255.999999524 0.999999999972
	 VELTYPE:  LSRK
	 UNITS:    Jy/beam

	 MS:  calib_split_07m.ms
	 source 0 J0635-7516 CO_v_0_1_0(ID=3768098) (114.91895511714681, 115.41883304683431, 115.271202, 916.10876785511493, -383.95257132452474, -0.31747529650296452, 4096)
	 source 1 J0635-7516 CO_v_0_1_0(ID=3768098) (114.91894229376393, 115.41882022345143, 115.271202, 916.14211836595439, -383.91922081371848, -0.31747529650297263, 4096)
	 source 2 J0635-7516 CO_v_0_1_0(ID=3768098) (114.91908951355599, 115.41896744324349, 115.271202, 915.75923536862661, -384.30210381101296, -0.31747529650296452, 4096)
	 source 3 cloud_197 CO_v_0_1_0(ID=3768098) (114.9202542230336, 115.4201321527211, 115.271202, 912.73010830921282, -387.33123087039354, -0.31747529650295642, 4096)

	 MS:  calib_split_12m.ms
	 source 0 cloud_197 CO_v_0_1_0(ID=3768098) (114.93438144200016, 115.40300937168766, 115.271202, 875.98863580604768, -342.79902746884346, -0.31747529650296724, 3840)


A few notes: 

1) We always need a CASA image for the TP. The CASA simulation tools we use cannot deal
with FITS files (yet).  You can use **importfits()** to get a CASA image. For example

       importfits('cloud197_casa47.spw17.fits','cloud197.im')

but in our case we already have a CASA image.

2) the TP cube needs to be 4D, and must be ordered as RA-DEC-POL-FREQ, again because of the
simulation tools we are using. If you have a RA-DEC-FREQ or RA-DEC-FREQ-POL
cube, there is a tool to fix your cube, e.g.

       qac_ingest('cloud197_casa47.spw17.fits','cloud197.im')

and continue with this good image cube.  In our current example the input CASA
image was actually correct, the shape is [150 150 1 43] and the spectral
axis is the last axis. As long as the input image is a CASA image, **tp2vis()** is
able to handle this, and you don't need this separate ingestion step.

3) The TP seems to have a deceptive roundoff error if you look at the velocity ranges,
but if you would take gridding that starts at 214 and ends at 256 km/s in steps of 1 km/s,
you will actually run into loosing a channel here and there. This could be a python rounding,
as no other combination of numbers would give a consistent value for C or the RESTFREQ.

This problem of rounding or gridding has plagued us all the way through this project,
and the safest thing seems to be to always ignore the first and last channel when going
into **tclean()**. More on that later.

4) the TP map needs be in Jy/beam units. Although the simulation software needs Jy/pixel, 
   we do this on the fly inside of **tp2vis()** since we know the beam size.  However,
   we do have an option to deal with Jy/pixel maps.


5) Both MS have ~4k channels, covering a much wider range than the TP,
and their channels are also ~3 narrower than the TP cube. In addition, the 7m 
contains sources and spw's we don't need. So we will use **mstransform()** to cut them down
in size and also bring them to the same velocity frame as the TP, to ease importing them into **tclean()**.
This is probably strictly not needed, but since more than likely will you re-run **tclean** a number
of times, this can be a huge time saving step.


       line = {'restfreq':'115.271202GHz', 'start':'214km/s', 'width':'1km/s', 'nchan':43}

       rm -rf aver_07.ms
       mstransform('calib_split_07m.ms','aver_07.ms',spw='3',
	     datacolumn='DATA',outframe='LSRK',mode='velocity',regridms=True,nspw=1,keepflags=False,
	     **line)

       rm -rf aver_12.ms
       mstransform('calib_split_12m.ms','aver_12.ms',spw='0',
             datacolumn='DATA',outframe='LSRK',mode='velocity',regridms=True,nspw=1,keepflags=False,
	     **line)


If you want to inspect a quick resulting map from **tclean**, using just the 7m or 12m visibilities, use
one of the functions from **qtp.py**:

       qtp_clean1('test7','aver_07.ms')
       qtp_clean1('test12','aver_12.ms')

and view your results using one of:

       viewer('test7/dirtymap.image')
       !casaviewer test7/dirtymap.image
       !ds9 test7/dirtymap.fits

Just is just to ensure that gridding worked. if you inspect these images, you will notice the phasecenter was
not placed well for either image, because it took the first field it encountered in the MS. Often you can use
the CRVAL (reference pixel) from the TP map as the phase center. We will come back to this later.


6) It probably is wise to first check a single (or small number)
channel(s) with a fair amount of emission to study the correct settings
of your workflow in tp2vis. We are currently still suffering from a first and/or last channel
mis-alignment/rounding/.... so 3 channels would be the minimum, as neither edge channel can
be trusted.


## Some initial plots

Spectrum in  **cloud197** through the brightest point in the cube:

![plot1b](figures/plot1b.png)

Total emission in the coverage area:

![plot1c](figures/plot1c.png)






## Second summary

Now we can run the summary again, and observe we have a much smaller amount of data to deal with

    !du -s cloud197_casa47.spw17.image/ aver_07.ms/ aver_12.ms/
    6764	cloud197_casa47.spw17.image/
    6488	aver_07.ms/
    26560	aver_12.ms/

which is a significant savings from the nearly 2.5 GB we had before.  And here is our new summary:

    qtp_summary('cloud197_casa47.spw17.image',['aver_07.ms','aver_12.ms'])

    TP: cloud197_casa47.spw17.image
    OBJECT:   cloud_197
    SHAPE:    [150 150   1  43]
    CRVAL:    J2000 05h39m50.000s -70d07m0.000s
    RESTFREQ: 115.271202
    FREQ:     115.188918285 115.172769145
    VEL:      213.999999525 255.999999524 0.999999999972
    VELTYPE:  LSRK
    UNITS:    Jy/beam
    
    MS:  aver_07.ms
    source 0 cloud_197 CO_v_0_1_0(ID=3768098) (115.17276914463741, 115.18891828499991, 115.271202, 255.9999995237942, 213.99999952500579, -0.99999999997115263, 43)

    MS:  aver_12.ms
    source 0 cloud_197 CO_v_0_1_0(ID=3768098) (115.17276914463741, 115.18891828499991, 115.271202, 255.9999995237942, 213.99999952500579, -0.99999999997115263, 43)



## Some Inspection

Inspect the TP cube, in particular if the velocity resolution cannot
be binned up a bit to speed up the workflow. In our case of 43 channels
no more binning is needed. Also check if the
baselines look flat enough (wavy or negative emission will throw off
the joint deconvolution). Sometimes you will find that your spectral
lines are oversampled, by binning you will also gain some signal to
noise and less work to do. Also, to compare multiple spectral lines,
it will be useful to grid them to the same velocity scale.


## Creating TP VIS data.

The final step before the joint deconvolution is to create the virtual interferometer
MS from the TP data, but before this
we need to select the pointings for the mosaic.
We can create pointing files from the 7m and 12m data first:

       qtp_ms_ptg('aver_12.ms', 'aver_12.ptg')
       qtp_ms_ptg('aver_07.ms', 'aver_07.ptg')

For example, the **aver_07.ptg** file has 11 pointings and looks as follows:

	J2000 05h39m45.660s -70d07m57.524s
	J2000 05h39m54.340s -70d07m57.524s
	J2000 05h39m41.320s -70d07m19.175s
	J2000 05h39m50.000s -70d07m19.175s
	J2000 05h39m58.680s -70d07m19.175s
	J2000 05h39m45.660s -70d06m40.825s
	J2000 05h39m54.340s -70d06m40.825s
	J2000 05h39m41.320s -70d06m2.476s
	J2000 05h39m50.000s -70d06m2.476s
	J2000 05h39m58.680s -70d06m2.476s

With some creative **grep** and **awk** you can also turn the output of **listobs()** into such
a **ptg** file, but obviously **qtp_ms_ptg()** is easier to use. We have an example in our
[M100 example1:](example1.md) 

Now we create an MS, and  use a 12m dish (the default) and the 12m pointings. The simplified shortcut
to **tp2vis()** and **tclean()** is:

    phasecenter = 'J2000 05h39m50.000s -70d07m0.000s'
    qtp_tp('test1','cloud197.im','aver_12.ptg',512,0.5,niter=0,phasecenter=phasecenter)


The 3 arguments "*512,0.5,niter=0*" will cause it to create an image cube for inspection, derived purely from
the simulated visibilities. You can inspect the **test1/dirtymap.image** with casaviewer, or the corresponding
fits file with for example ds9. Our shortcut functions also create a FITS file for convenience.


We can now run the joint deconvolution via **tclean()**. Our shortcut could be:

    qtp_clean('test2','test1/tp.ms',['aver_07.ms','aver_12.ms'],512,0.5,niter=0,phasecenter=phasecenter)

There are some more idiosyncrasies we need to take care of before this is mature:

1) the phasecenter (is ok in TP, but not in MS), it needs to be set here. You saw that before already.
2) visibility weights (see below)
3) various parameters controlling how the TP visibilities are choosen (nchan, nvgrp, uvmax, rms, ...)

These are all hidden in parameters for which reasonable defaults exist. 


## Creating TP VIS data, part 2, and setting weights

Get an idea what the noise per channel is, where the edges should be signal free

    imstat('cloud197_casa47.spw17.image',axes=[0,1])['rms']
    array([  0.81444146,   0.93346004,   1.04999339,   1.68540715,
         2.41114383,   3.65666558,   5.34560999,   6.44932718,
         7.18137358,   8.58450582,  10.61939395,  14.35698732,
        20.80798914,  29.79471169,  39.83081052,  49.58010498,
        55.9672849 ,  55.24956448,  48.64794787,  39.17294081,
        30.71854896,  26.39480093,  23.96687086,  23.04788678,
        26.81045278,  32.10158818,  36.40725613,  37.3763145 ,
        33.47390816,  22.30660695,  10.88637817,   5.44328965,
         2.7655302 ,   1.64343255,   1.2276188 ,   1.07932003,
         0.84567861,   0.77672803,   0.92992875,   0.73599365,
         0.85368232,   0.7129901 ,   0.78708032])
    imstat('cloud197_casa47.spw17.image',axes=[0,1])['rms'][-7:].mean()
    -> 0.8 

![plot1d](figures/plot1d.png)

Generate visibilities, setting sigma=0.8 which we got from averaging the rms in the
last 7 channels using imstat

    qtp_tp('test1','cloud197_casa47.spw17.image','aver_12.ptg',512,0.5,niter=0,rms=0.8,phasecenter=phasecenter)
    WEIGHT: Old=1.0 New=0.000377415 Nvis=4140
    qtp_stats('test1/dirtymap.image')
    STATS: 11.707418158560197, 19.590387396407348, 0.45887401700019836, 118.52285003662109, 3439.5379741983957

Based on sigma, the WEIGHT was set at 0.000377415, but we can also use the theoretically expected weights, based on
a TSYS:

First checking what we have:

    tp2viswt('aver_07.ms')
    WEIGHT min/max:  0.0093015069142 0.0589787997305

    tp2viswt('aver_12.ms')
    WEIGHT min/max:  0.268536657095 0.505275905132

But these are from cycle-1 and not to be trusted. So we need to     


    tp2viswt('aver_07.ms',rms=77.4,mode=5)
    WEIGHT min/max:  0.00168259119043 0.00168259119043

    tp2viswt('aver_12.ms',rms=24.2,mode=5)
    WEIGHT min/max:  0.0103271634451 0.0103271634451

    tp2viswt('test1/tp.ms',rms=41.9,mode=5)
    WEIGHT min/max:  0.000569602588274 0.000569602588274

and notice the 0.00057 is only slightly more than the value we had before, 0.00038, based on cube rms. Also consult
https://casaguides.nrao.edu/index.php/DataWeightsAndCombination for a discussion how to set weights for various
ALMA cycles.

Now we are ready for JD again:

    qtp_clean('test2','test1/tp.ms',['aver_07.ms','aver_12.ms'],512,0.5,niter=0,phasecenter=phasecenter)

notice during the output it will remind you to the weights:

       Weights in  ['aver_07.ms', 'aver_12.ms', 'test1/tp.ms']
       WEIGHT min/max:  0.0016825911589 0.0016825911589
       WEIGHT min/max:  0.0103271631524 0.0103271631524
       WEIGHT min/max:  0.000569602590986 0.000569602590986


### Beam Size Based Weights

This is still unchecked....

    tp2viswt('test1/tp.ms',['aver_07.ms','aver_12.ms'],'test1/dirtymap.psf',2.0)

## Creating TP VIS data, part 3

Now trying this for using 7m dishes, using the 7m pointings:


Generate visibilities, setting rms=0.7 which we got from **imstat()** before

	 qtp_tp('test3','cloud197_imtransimage','aver_07.ptg',512,0.5,niter=0,rms=0.7,dish=7.0,phasecenter=phasecenter)

and JD

	qtp_clean('test4','test3/tp.ms', ['aver_07.ms','aver_12.ms'],512,0.5,phasecenter=phasecenter)


## Some plotting

We have some simple matplotlib based plotting functions in **tp2visplot.py**

   	execfile("tp2visplot.py")

For example a UV plot like CASA's **plotuv()** can be done:

    	    plot1('test1/tp.ms','aver_07.ms', 'aver_12.ms')
	    UVW shape (3, 111780) [ 0.  0.  0.]
	    UVD npts,min/max =  111780 0.0 5.98536377874
	    UVW shape (3, 840) [  7.79989497   8.57464177 -17.24275976]
	    UVD npts,min/max =  840 2.88143915951 13.2053309321
	    UVW shape (3, 24840) [  57.81642033 -162.35654714  180.89298071]
	    UVD npts,min/max =  24840 5.10844543931 173.206946572

Here are two figures showing the distribution of UV of the 12m (green) and 7m (red) ,
![plot1a](figures/plot1a.png)

and in the zoomed version you can see the TP (small black dots) as well.
![plot1](figures/plot1.png)

Or to plot the total flux per channel, comparing three results:


      	   f2 = qtp_getamp('test1/tp.ms')/1000.0          # (0,0) amps from TP MS
	   f1 = plot2('test1/dirtymap.image',f2)       # flux from Jy/beam map
	   f0 = plot2('cloud197.im',f1)         # sum from Jy/pixel map
	   _ = plot2('cloud197.im',f1, f2, plot='plot2_flux.png')
		 

And this results in:
![plot2](figures/plot2_flux.png)

Here the Red is the TP map, Green the dirty image from tclean(), and Blue the amp at (u,v) = (0,0) which is still at odds. Also disturbing still are
the non-zero flux toward the edges of this spectral window.

To plot a special AMP vs. UVDISTANCE, use plot3:

   	  plot3(['aver_12.ms','aver_07.ms','test1/tp.ms'])
	  
and this results in:
![plot3](figures/plot1_amp.png)
![plot3a](figures/plot1a_amp.png)

To plot WEIGHT vs. UVDISTANCE, use plot4:

   	  plot4(['aver_12.ms','aver_07.ms','test1/tp.ms'])


## TP2VISPL

The official tp2vis plotting interface is currently through the tp2vispl() plot, which produces
a 4-panel plot with the UV distribution of visibilities for each MS, and the
amplitude and weight densities as function of UV distance:

	  tp2vispl('test1/tp.ms','aver_07.ms','aver_12.ms', show=True)


## Rebinning ?  (skip for now)

* will come back to this later *

TODO:  regridding images to a given (nchan,start,width) seems to be painful in CASA.

First use **imrebin()**, or **imsubimage()**, depending if you need to preserve all channels
or just cut channels off the edge, or bin them up in pairs or triples, as in the
following two examples:

      imrebin('cloud197_imtransimage','cloud197a.im',[1,1,1,2],chans='10~21')
      qtp_summary('cloud197a.im')
      SHAPE:    [150 150   1   6]
      VEL:      245.499999524 235.499999524 -1.99999999994

      imrebin('cloud197_imtransimage','cloud197b.im',[1,1,1,3])
      qtp_summary('cloud197b.im')
      SHAPE:    [150 150   1  14]
      VEL:      254.999999524 215.999999525 -2.99999999992

Again note that we need a 4D cube with the spectral axis the last axis. After this you can
rerun **mstransform()** with 2km/s or 3km/s channels (note that the sign of the channel width is preserved
in mstransform, this is confusing, since **tclean()** will honor that request)

	rm -rf aver_07b.ms
	mstransform('calib_split_07m.ms','aver_07b.ms',
	     start='216km/s',width='3km/s',nchan=14,restfreq='115.271202GHz',
	     datacolumn='DATA',outframe='LSRK',mode='velocity',regridms=True,nspw=1,spw='3')

	rm -rf aver_12b.ms
	mstransform('calib_split_12m.ms','aver_12b.ms',
	     start='216km/s',width='3km/s',nchan=14,restfreq='115.271202GHz',
	     datacolumn='DATA',outframe='LSRK',mode='velocity',regridms=True,nspw=1)


NOTE: imregrid has potentially issues with flux conservation!

## Acknowledgements

This paper makes use of the following ALMA data: ADS/JAO.ALMA#2012.1.00641.S.
ALMA is a partnership of ESO (representing its member states), NSF (USA) and
NINS (Japan), together with NRC (Canada) and NSC and ASIAA (Taiwan) and
KASI (Republic of Korea), in cooperation with the Republic of Chile.
The Joint ALMA Observatory is operated by ESO, AUI/NRAO and NAOJ.

