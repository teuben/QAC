# TP2VIS workflow example 3: Combining VLA and GBT data

In this workflow the following peculiarities are discussed:

1) non-ALMA data

2) ...

## Background

We started this VLA (25m) and GBT (100m) combination, at 23 GHz, but have decided to finish this later
due to the enormous size of the MS files and the non-ALMA application which has lower priority. We hope
to come back to this later, as it is a really neat application of TP2VIS.


## Inventory 

Here is the example of *Perseus* (Mundy et al., in prep). It has 100m GBT  single dish
observations, coveraging a larger portion than the VLA interferometric observations. Two
interesting GBT data exist, covering the 1-1 and 2-2 lines of NH3. A third observation does not
cover as much area and is not interesting for our experiment. The GBT data has 913 channels with 
channel width of 5.722kHz.

The VLA observations cover the NH3(1,1) lines in spectral windows 6 and 7 with some overlap between them. 
Each window has 1152 channels of width of 3.9 kHz.
NH3(2,2) is covered in windows 8 and 9. 
There are 91 fields (svs*). 

To size up what we got for our 3 datasets (1 TP and 6 MS):

     du -s NH3_11_cube.fits  ...

     469408	NH3_11_cube.fits


     importfits('NH3_11_cube.fits','NH3_11_cube.im')
     192 x 342 x 915 in 10.61" pixels and 0.0724 km/s channels, 
        covering roughly a 30' by 60' region, and 66 km/s bandwidth.
	
There is no OBJECT name, nor is BUNIT filled in. We assume K
Noise is about 0.09 K. We will need to patch up the header to prepare this for TP2VIS

![plot3a](figures/plot3a.png)

A typical spectrum in the **NH3_11_cube**. Notice a negative line artifact in the first 100 channels.

![plot3b](figures/plot3b.png)

Total emission in the coverage area, including a plotting crop error in top region.

### Conversion from K to Jy/pixel

See also http://www.gb.nrao.edu/~fghigo/gbtdoc/perform.html 

In the FITS header of the (1,1) line the beam is claimed to be 31.8" FWHM. Based on numbers elsewhere on the web,
I would have said 30.6" but lets go with 31.8". The BUNIT is blank, but they are Kelvin.

The conversion from T to Janskys is 1.446 K/Jy per beam at 23.694 GHz 
(after including beam efficiency; calculated using values in the GBT sensitivity calculator).

The (1,1) cube has pixels that are 10.61" in size. For a 31.8" FWHM, there are 8.98*1.133 = 10.2 pixels per beam area. 
If we need to go from Kelvins to Jy per pixel,
the answer is   Jy/pixel = K/(1.5*8.98*1.133) = K/15.26

Here I am assuming that the K in the map are Kelvins under
the same definition as used for calculating the basic
K/Jy above.

##TP data preperation

     # cutting down the cube in size for some experiments, and fixing up missing header items
     # and getting the correct axis order for the simulations
     # This assumes CASA 5.0 and up, as in earlier version some header items were lost

     importfits('NH3_11_cube.fits','NH3_11_cube.im',overwrite=True)

     # flux check, for later. Units in input map are Kelvin
     imstat('NH3_11_cube.im')['sum']
     -> 225009

     # remove stuff we're going to create
     rm -rf NH3_11_cube2.im
     rm -rf NH3_11_cube3.im
     rm -rf NH3_11_cube4.im
     rm -rf NH3_11_cube5.im          

     # get the cube in RA-DEC-POL-FREQ order (input was RA-DEC-FREQ)
     ia.open('NH3_11_cube.im')
     ia2 = ia.adddegaxes(stokes='I')
     ia3 = ia2.transpose('NH3_11_cube2.im',order='0132')
     ia3.close()
     ia2.close()
     ia.close()
     

     # summary what we have now
     qtp_summary('NH3_11_cube2.im')
     # QTP_SUMMARY:
     # TP: NH3_11_cube2.im
     # OBJECT:   
     # SHAPE:    [192 342   1 915]
     # CRVAL:    J2000 03h29m18.458s +31d20m27.678s
     # RESTFREQ: 23.6944955
     # FREQ:     23.6910771092 23.6963070591
     # VEL:      43.250880345 -22.9205876688 -0.0723976674111
     # VELTYPE:  LSRK
     # UNITS:    

     factor = 1/1.446          # K to Jy/GBTbeam
     expr = 'IM0*%f' % factor
     immath('NH3_11_cube2.im','evalexpr','NH3_11_cube3.im',expr=expr)
     imhead('NH3_11_cube3.im','put','bunit','Jy/beam')                 
     imhead('NH3_11_cube3.im','put','object','SVS')
     # now inspect
     imhead('NH3_11_cube3.im')
     

     # flux conservation check:
     imstat('NH3_11_cube3.im')['sum']
     => 155608

     imstat('NH3_11_cube3.im')['flux']
     -> 1104.7 Jy.km/s   ( = 155608 * 0.0724 km/s / 10.2 points-per-beam) 
     (this will fail before CASA 5.0 since beam was forgotten)

     # select central line, bin by 4 channels, cut a square box where the VLA pointings are, plus some
     # channels 415~568 covers the central strongest line
     # box picks a central 128 x 128 pixel area
     imrebin('NH3_11_cube3.im','NH3_11_cube4.im',factor=[1,1,1,4],chans='414~569',box='56,88,183,215',overwrite=True)
     exportfits('NH3_11_cube4.im','NH3_11_cube4.fits',overwrite=True)

     # flux
     qtp_stats('NH3_11_cube4.im')
     # -> 0.021654944995298863 0.12978557652776368 -0.65108144283294678 3.2268295288085938 379.93502913244754

     # just one slice for even faster testing
     imsubimage('NH3_11_cube4.im','NH3_11_cube5.im',chans='22',overwrite=True)


     # Get a decent value for the RMS, which is what tp2vis needs.
     # First, plot min/max/rms for the (binned) cube
     plot5('NH3_11_cube4.im')
     # the rms in the line free channels is about 0.44, but lets do it official 
     # by using the mean of the first 10 and last 10 channels
     rms1 = imstat('NH3_11_cube4.im',axes=[0,1])['rms'][:10].mean()
     # -> 0.0436
     rms2 = imstat('NH3_11_cube4.im',axes=[0,1])['rms'][-10:].mean()
     # -> 0.0435
     rms = 0.5*(rms1+rms2)

     immoments('NH3_11_cube4.im',moments=0,outfile='NH3_11_cube4.mom0')
     viewer('NH3_11_cube4.mom0')
     imview (raster=[{'file': 'NH3_11_cube4.mom0',
                 'range': [-6,44.],'scaling': -1.3,'colorwedge': True}],
             zoom={'blc': [0,0],'trc': [127,127]},
             out='NH3_11_cube4.mom0.png')

## Pointings

Since the GBT is a 100m dish, the mosaic pointings from the VLA (25m) array are no good, and we have to generate
a new pointing file with a finer sampling. Thus ...  

    phasecenter = 'J2000 52.26483deg 31.28025deg'        # note the decimal notation for now
    imsize=[1400,1800]
    pixel=0.5
    ptgfile='GBT.ptg'
    ptg = qtp_im_ptg(phasecenter=phasecenter, imsize=imsize, pixel=pixel, grid=15.9, rect=True, outfile=ptgfile)           # ARNAB's new routine

which will generate a hex grid of pointings, centered on the given phasecenter, in a map of size 600 x 800 with 0.5arcsec pixels and a
15.9 arcsec (nyquist) sampling of the 31.8 arcsec GBT beam. [FIX NUMBERS]

## tp2vis
     
     # first we need to cheat and patch the dish size in tp2vis' secret data structure.....
     qtp_tpdish('ALMATP',100.0)
     qtp_tpdish('VIRTUAL',100.0)

     # then run tp2vis
     qtp_tp('test1','NH3_11_cube4.im',ptg=ptgfile,mapsize=128,pixel=8,niter=0,phasecenter=phasecenter,maxuv=100,rms=rms)

     # flux as function of channel plot
     f0 = imstat('NH3_11_cube4.im',      axes=[0,1])['flux']   # 13382 ok
     f1 = imstat('test1/dirtymap.image', axes=[0,1])['flux']   # 107   bad
     plot2a([f0,f1])


## Visibilities: preparation

Now we need to cut down the measurement sets into more manageable pieces.  This is what we have:

    du -sh WorkingDir[1,2,4,5,6,7]/13*.ms
    496G    WorkingDir1/13A-309.sb14963534.eb19404889.56365.98588047454.ms
    307G    WorkingDir2/13A-309.sb15360625.eb21297547.56417.86466341435.ms
    202G    WorkingDir4/13A-309.sb19258101.eb20686427.56395.74123677083.ms
    164G    WorkingDir5/13A-309.sb19263801.eb19401463.56365.008171608795.ms
    201G    WorkingDir6/13A-309.sb19410810.eb19419470.56367.00304743055.ms
    332G    WorkingDir7/13A-309.sb19419907.eb19739205.56389.92033303241.ms


It will also be good to bring all datasets into the same frame of reference, an LSRK doppler velocity cube.

    line1 = {'start' : '5.0km/s' , 'width' : '0.2km/s' , 'nchan' : 31 , 'restfreq' : '23.6944955GHz'}

or consider inheriting **line1** from the image cube, since we can't seem to regrid images easily

    line1 = qtp_line('NH3_11_cube4.im')

Here are some suggestions how we could cut down the data to just what we need for tclean():
    
    mstransform('../WorkingDir2/13A-309.sb15360625.eb21297547.56417.86466341435.ms','ms2a.ms', datacolumn='corrected', outframe='LSRK', regridms=True,spw='6,7',nspw=1,field='svs*',keepflags=False,**line1)

This reduces the filesizes to about 40 GB.

    


## Imaging

An example how to map:

    qtp_clean('test2','test1/tp.ms',['ms1a.ms','ms5a.ms'],mapsize, pixel, 0, phasecenter=phasecenter, **line1)

After this step there is a discussion on setting weights in the TP file, as well as the tweak option. For this it will be easier
to allow qtp_clean() to have a list of niter's.
    
