# TP2VIS workflow example 2: SMC

## ALMA data

### Proposal title (2013.1.00652.S)

Spying on our Neighbor: Peering into Low Metallicity Molecular Clouds in the Small Magellanic Cloud

### PI name

Jameson, Katherine

### Proposal abstract

A dominant reservoir of H2 gas faint in CO emerges as metallicity
decreases, which alters the structure of molecular clouds and perhaps
the sites of star formation. With ALMA, we can reach the resolution
necessary to see the structure of photodissociation regions and the
transition from *CO-bright* to *CO-faint* molecular gas for the
first time at 1/5 Solar metallicity in the Small Magellanic Cloud. We
propose to map four regions in the Southwest Bar of the SMC at high
spatial and spectral resolution (1.6" or 0.5 pc scales and ~0.1 km/s)
in 12CO, 13CO, and C18O (2-1). We will determine the mass, structure,
and kinematics of molecular clouds across a range of environments. We
will explore the structure of CO gas, the transition to CO-faint
molecular gas, and the effect of the CO-faint molecular gas on low
metallicity star formation. With the slew of ancillary data in hand
(much collected by the Co-Is in this proposal), including PAHs, [CII],
[CI], [NII], [OI], dust continuum, and dust-based H2 maps, we can
fully exploit the ALMA observations and answer key questions needed to
inform ISM and star formation models used in galaxy simulations.


## Data Inventory

The TP data is 122 x 122 x 351, at CO(2-1) [ALMA band 6] with 0.16
km/s channels and 2.8" pixels, covering about 5' and 56 km/s.  In the
Alladin sky view below *SWBarN* is the northern most source.


Here is the example of *SWBarN* (Jameson et al., in prep), a star forming region in the SMC.

These are part of the ALMA Cycle 1 project 2013.1.00652.S. There are 4
sources observed in the central part of the SMC, and  we focus on the northern most
one, *SWBarN*, for this workflow example.

Sizing up what we got in our 3 datasets (1 TP and 2 MS):

     du -s SWBarN_CO21_ALMA_TP_Jybeam.fits calibrated_7m.ms/ calibrated_final_12m.ms/

     166476     SWBarN_CO21_ALMA_TP_Jybeam.fits
     8686288    calibrated_7m.ms        
     53543216   calibrated_final_12m.ms



![plot1](figures/smc-overview.png)


And two plots from ADMIT: a spectrum through the peak in the cube, and the sum of (what it thinks is) all
emission:

![plot2a](figures/plot2a.png)

A typical spectrum in the **SWBarN**. There are still issues in this cube with negative baselines. RMS is about 1.2 

![plot2b](figures/plot2b.png)

Total emission in the coverage area. We are looking at a complex molecular structure in the SMC, where along the line
of sight several clouds at different velocities seen. Typical line widths are around 2 km/s.



After an inspection via listobs, cut down the VIS data to only keep the unflagged SWBarN source data, but keep the original spectral resolution:

       listobs('calibrated_7m.ms',        listfile='calibrated_7m.log')
       listobs('calibrated_final_12m.ms', listfile='calibrated_final_12m.log')
       

       rm -rf aver_07.ms
       mstransform('calibrated_7m.ms','aver_07.ms',
         restfreq='230.538GHz',
	 datacolumn='DATA',outframe='LSRK',mode='velocity',regridms=True,nspw=1,spw='0,4',field='SWBarN',keepflags=False)

       rm -rf aver_12.ms
       mstransform('calibrated_final_12m.ms','aver_12.ms',
         restfreq='230.538GHz',
	 datacolumn='DATA',outframe='LSRK',mode='velocity',regridms=True,nspw=1,spw='0,4',field='SWBarN',keepflags=False)

        du -s aver_07.ms aver_12.ms
	254072	aver_07.ms
	5793672	aver_12.ms

	pjt_ms_ptg('aver_12.ms', 'aver_12.ptg')
	pjt_ms_ptg('aver_07.ms', 'aver_07.ptg')


The 7m data were taken 18-Jul-2014, but the 12m had to be redone and were finally taken 15-Jan-2016, the TP data were taken 4-Sep-2015.


### Import TP image


	importfits('SWBarN_CO21_ALMA_TP_Jybeam.fits','SWBarN_CO21_ALMA_TP_Jybeam.image',overwrite=True)
	tp2vischeck('SWBarN_CO21_ALMA_TP_Jybeam.image','SWBarN_CO21_TP.image',ms='aver_07.ms')

	pjt_summary('SWBarN_CO21_TP.image',['aver_07.ms','aver_12.ms'])

	
	TP: SWBarN_CO21_TP.image
	OBJECT:   SWBarN
	SHAPE:    [ 204  204    1 1024]
	RESTFREQ: 230.538
	FREQ:     230.383313197 230.508198259
	VEL:      201.155283605 38.7542932009 -0.15874974624
	VELTYPE:  LSRK
	UNITS:    Jy/beam

	MS:  aver_07.ms
	source 0 SWBarN (230.38327870590174, 230.50815957337377, 230.53800000000001, 201.20013647492874, 38.804599875281554, -0.15874441505341855, 1024)
	source 1 SWBarN (230.38324460603869, 230.50812547351074, 230.53800000000001, 201.24448006151567, 38.848943461835205, -0.1587444150534511, 1024)

	MS:  aver_12.ms
	source 0 SWBarN (230.38717451714001, 230.50424552192223, 230.53800000000001, 196.13400929840049, 43.894446691861546, -0.15874824046562974, 960)
	source 1 SWBarN (230.39940424128832, 230.51647524609984, 230.53800000000001, 180.23043130656015, 27.990868661911438, -0.15874824050536884, 960)


You can see that the MS have two sources with the same name, based on
a different SPW (0 and 4) [* i don't understant why, I would have
expected nspw=1 in mstransform to merge them ? *]

Here's a typical spectrum through the CO21 fits cube:

![plotsp0](figures/smc-sp0.png)

An obvious problem with this cube are the non-flat baselines.  A 2nd
image (provenance unknown, Katie?), called **smc1.image**, does have flat
baselines, but they are negative where there are strong lines (hinting
at bad cont subtraction). The first and last 50 channels are
free of emission, so these could be used for an image based continuum
correction using **imcontsub()**. More on that later.

This image needs a tpvischeck() correction first, since the axes are not in the correct order.

	tp2vischeck('smc1.image','smc2.im')
	exportfits('smc2.im','smc2.fits',overwrite=True)
	
	pjt_summary('smc2.im')
	
	TP: smc2.im
	OBJECT:   SWBarN
	SHAPE:    [122 122   1 351]
	RESTFREQ: 230.538
	FREQ:     230.426040247 230.468767296
	VEL:      145.59287242 90.0304612364 -0.15874974624
	VELTYPE:  LSRK
	UNITS:    Jy/beam


### Continuum Subtraction

The continuum subtraction is not done correctly in TP, as if the lines were part of it. But
some locations (e.g. 49,40) in the earlier example plot, looks pretty decent. But two
locations at (49,49) and (62,62) look quite bad, as shown in the following figure:

![plotsp1](figures/smc-sp1.png)

        imcontsub('smc2.im','smc3.im','smc2-cont.im',fitorder=0,chans='0~50,300~350')
        exportfits('smc3.im','smc3.fits',overwrite=True)

resulting the folllowing spectrum:

![plotsp2](figures/smc-sp2.png)

We will continue with this cube as **the** TP cube

### Weights

	 tp2viswt('aver_07.ms')
	 TP2VISWT: Statistics
	 WEIGHT min/max:  0.00500088511035 0.0703270733356


	 tp2viswt('aver_12.ms')
	 TP2VISWT: Statistics
	 WEIGHT min/max:  0.0117608001456 0.0983374714851


### Flux check

    	 imstat('SWBarN_CO21_TP.image')
	 -> flux = 4255.34677633 Jy.km/s
	 -> sum = 3078278.62035798  Jy/beam 
	 -> nppb = sum * dv / flux = 114.838

	 imstat('smc2.im')
	 -> flux = 4253.12429015 Jy.km/s

	 imstat('smc3.im')
	 -> flux = 5206.06154692 Jy.km/s

	 imhead('smc3.im')
	 -> beam = 28.26 " (circular)

### Summary

A final summery now we have all data lined up:

         pjt_summary('smc3.im',['aver_12.ms','aver_07.ms'])

	 TP: smc3.im
	 OBJECT:   SWBarN
	 SHAPE:    [122 122   1 351]
	 RESTFREQ: 230.538
	 FREQ:     230.426040247 230.468767296
	 VEL:      145.59287242 90.0304612364 -0.15874974624
	 VELTYPE:  LSRK
	 UNITS:    Jy/beam

	 MS:  aver_12.ms
	 source 0 SWBarN (230.38717451714001, 230.50424552192223, 230.53800000000001, 196.13400929840049, 43.894446691861546, -0.15874824046562974, 960)
	 source 1 SWBarN (230.39940424128832, 230.51647524609984, 230.53800000000001, 180.23043130656015, 27.990868661911438, -0.15874824050536884, 960)

	 MS:  aver_07.ms
	 source 0 SWBarN (230.38327870590174, 230.50815957337377, 230.53800000000001, 201.20013647492874, 38.804599875281554, -0.15874441505341855, 1024)
	 source 1 SWBarN (230.38324460603869, 230.50812547351074, 230.53800000000001, 201.24448006151567, 38.848943461835205, -0.1587444150534511, 1024)


### Downsizing

To get your workflow optimed quickly, it's best to select a channel,
or small range of channels with sufficient emission to check fluxes,
amplitudes etc.


	phasecenter = 'J2000 0h48m15.852 -73d04m55.883'
	
	# 115.50979557339004    -1.5874974624171756   2

	# a few options to pick a line setting
	# 3 is probably the mininum nchan,
	#   since the first and/or last channel could become masked (CASA BUG)
	line1 = {"restfreq":'230.538GHz','start':'145km/s', 'width':'-1km/s','nchan':55}
	line2 = {"restfreq":'230.538GHz','start':'120km/s', 'width':'-5km/s','nchan':4}

	line = line2

	rm -rf aver_07a.ms
	mstransform('aver_07.ms', 'aver_07a.ms',
	datacolumn='DATA',outframe='LSRK',mode='velocity',regridms=True,nspw=1,
	**line)

	rm -rf aver_12a.ms
	mstransform('aver_12.ms', 'aver_12a.ms',
	datacolumn='DATA',outframe='LSRK',mode='velocity',regridms=True,nspw=1,
	**line)

	# get a quick cube with a good spectral axis to inherit
	pjt_clean1('test7','aver_07a.ms',128,4,niter=0,indirection=phasecenter)
	imregrid('smc3.im','test7/dirtymap.image','smc4.im',overwrite=True, axes=[3])

	# @todo regrid vs. imbin

	# summary on the smaller datasets
        pjt_summary('smc4.im',['aver_12a.ms','aver_07a.ms'])
	 
	# create TP.MS from this new regridded image
	pjt_tp('test1','smc4.im','aver_12.ptg',512,1,niter=0,indirection=phasecenter,rms=1.1)
	# for line2: this is odd, the resulting cube has 1 masking plane (last plane) 
	# PSF is blank for[C3:P0] despite that the correct gridding used -> float roundoff?
	-> WEIGHT: Old=1.0 New=0.000199625 Nvis=4140 
	# took about 20' on dante on full cube
	#  
	# TP with 7m (7m itself has 7.7 x 5.8" beam) gives 9.8 x 7.7 beam
	pjt_clean('test2a','test1/tp.ms','aver_07a.ms',512,1,niter=0,indirection=phasecenter,do_alma=False)
	tp2viswt('test1/tp.ms')
	# no masked channels now!!!
	#  W7m    0.00500091863796  0.0703282207251
	#  Wtp    0.000199624701054 0.000199624701054
	

	# TP with 12m (12m itself has 2.5 x 1.25" beam) gives --
	pjt_clean('test2b','test1/tp.ms','aver_12a.ms',512,1,niter=0,indirection=phasecenter,do_alma=False)
	### SEVERE	ms::concatenate	Exception Reported: TableRow::put; names not conforming
	# -> looks like the 12m only
	# W12m    0.0117607656866   0.0983376130462
	#  Wtp    0.000199624701054 0.000199624701054	

	# TP with 7m+12m (7+12 has a .. beam)
	pjt_clean('test2c','test1/tp.ms',['aver_07a.ms','aver_12a.ms'],512,1,niter=0,indirection=phasecenter)
	-> WEIGHT min/max:  0.00500091863796 0.0703282207251
	-> WEIGHT min/max:  0.0117607656866 0.0983376130462
	-> WEIGHT min/max:  0.000199624701054 0.000199624701054

	tp2viswt('test1/tp.ms',mode=2,factor=10)
	-> TP2VISWT: multiply the weights by 10
	-> WEIGHT: Old=0.000199624701054 New=0.00199625 Nvis=616860

	pjt_clean('test2d','test1/tp.ms',['aver_07a.ms','aver_12a.ms'],512,1,niter=0,indirection=phasecenter,do_alma=False)

	tp2viswt('test1/tp.ms',mode=2,factor=10)
	-> WEIGHT: Old=0.00199624709785 New=0.0199625 Nvis=616860

	pjt_clean('test2e','test1/tp.ms',['aver_07a.ms','aver_12a.ms'],512,1,niter=0,indirection=phasecenter,do_alma=False)

From these it is clear that the weights for the TP seem to be generally too low to make a good image.

        line={'robust' : +2.0, 'weighting' : 'briggs'}
	pjt_clean('test2e_r','test1/tp.ms',['aver_07a.ms','aver_12a.ms'],512,1,niter=0,indirection=phasecenter,do_alma=False,line)

### Summary Plot

Here is a panel with the 12m pointings overlayed on the TP map (top row), and
the 12+7m and 12+7+TP map (no cleaning).

![plotds9](figures/smc2.png)


## Plotting

The full files will crash CASA. Downsized versions:


    	 plot3(['aver_12a.ms','aver_07a.ms','test1/tp.ms'])

and this results in:
![plot3a](figures/smc3a.png)
![plot3b](figures/smc3b.png)

Weights:

**test2c**

![plot4c](figures/smc4c1.png)

**test2d**

![plot4d](figures/smc4d1.png)

**test2e**

![plot4e](figures/smc4e1.png)



## Acknowledgements

This paper makes use of the following ALMA data: ADS/JAO.ALMA#2013.1.00652.S.
ALMA is a partnership of ESO (representing its member states), NSF (USA) and
NINS (Japan), together with NRC (Canada) and NSC and ASIAA (Taiwan) and
KASI (Republic of Korea), in cooperation with the Republic of Chile.
The Joint ALMA Observatory is operated by ESO, AUI/NRAO and NAOJ."
