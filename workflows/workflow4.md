# TP2VIS workflow examples:  skymodel

In this workflow the following is discussed:

1) simulation data, where both TP and MS are derived from a sky model, with a known flux

2) test deconvolution in tp2vis

3) continuum data



# TP data

## Model

We have separate tools to create skymodels with varying parameters. You can read about these in our
[map4sim](map4sim.md) document. Another example of creating synthetic images can be found in
the [image registration](https://image-registration.readthedocs.io/en/latest/) package.

## Inventory 

We use the example of *skymodel* (Koda et al., in prep), which we will use as a benchmark. It represents
large scale emission, with some power on each scale. We have prepared a single high resolution model:

     du -s skymodel.fits

     65548	skymodel.fits

which is a 4096 x 4096 continuum image at exactly 115.0 GHz with 0.05" pixels, so covering 204", or about 3.4 arcmin, on the sky.
The units are *Jy/pixel*.
We also created a pointing file, **skymodel.ptg**, which covers this area with 12m dishes in a hexagonal Nyquist sampled grid.
Below is a figure depicting the emission (grey-scale) and pointing centers (green circles). Some circles are plotted small
to show the hex grid more clearly. Others have the correct 56" PB.

![plot1](figures/skymodel4p.png)

### Resizing

For some systems this 4k image might be too big. You can either take a subset or average pixels to obtain a smaller more
manageable map. For example, in the popular [**montage**](https://ascl.net/1010.036) package this would be:

     mShrink skymodel.fits skymodel4.fits 4

to obtain a 1k image. Or use CASA's **imrebin(...,factor=[4,4])**, which we use below in this workflow example. Luckily both
conversions will preserve the sky coverage.


## Import

The skymodel needs to be imported, and properly ingested with the correct RA-DEC-POL-FREQ axis ordering for TP2VIS.  The
input fits file is RA-DEC-FREQ-POL (this 3rd/4th axis is a frequent issue in CASA).  Currently this means:

     importfits('skymodel.fits','skymodel.im',overwrite=True)
     qtp_ingest('skymodel.im','skymodel2.im')

and for subsequent processing we will also need to set the following phasecenter (essentially the map center):

     phasecenter = 'J2000 12h00m0.000s -30d00m00.000s'

## 4k image

First compute the total flux in the original *Jy/pixel* image, and for a slightly smoothed image:

      qtp_stats('skymodel2.im')
      -> 0.0067413167369069988 0.010552344105427183 0.0 0.10000000149011612 113100.52701950389

      imsmooth('skymodel2.im','gaussian','1arcsec','1arcsec',pa='0deg',outfile='skymodel2s.im',overwrite=True)
      qtp_stats('skymodel2s.im')
      -> 3.0488979247311159 4.7227571346415482 -4.2469496293051634e-06 33.681392669677734 112859.56421051793

pretty good flux conservation, 99.8%, as we expect. Some small amount of spillover is unavoidable.

Now running TP2VIS:
     
     %time qtp_tp('test70','skymodel2.im','skymodel.ptg',256,1.0,niter=0,phasecenter=phasecenter, deconv=False)
     CPU times: user 9min 40s, sys: 7min 15s, total: 16min 56s
     Wall time: 16min 33s

     qtp_stats('test70/dirtymap.image/')
     -> 3444.4730793234357 4772.160281800443 15.113117218017578 14918.203125 55541.694563002682     (ALMA PB)
     -> 4840.4272901256827 6940.3858015801288 -7.1141228675842285 21629.15625 81392.511099505777    (VIRTUAL PB)

these take a long time, and consume a fair amount of memory, since they are 4k images.
Notice, since the images are still *Jy/pixel*, we need to use the **deconv=False**
flag in *qtp_tp()* to conserve flux.


## 1k image

Let us thus resample to a smaller 1k, image, with now 0.2 arcsec pixels, so we keep the same sky coverage.

     imrebin('skymodel2.im','skymodel3.im',factor=[4,4],overwrite=True)

     qtp_stats('skymodel3.im')
     -> 0.0067413167365710279 0.010538542688954752 0.0 0.093201473355293274 7068.7829383667022
     
the sum (flux) is now about 16 times smaller, as imrebin takes an average of the binned pixels.

## TP map

Now smooth it with the large TP beam, so simulate this data was taken with as 12m dish at 115 GHz. We assume that
at 115.2 GHz the beam is 56.6":

     imsmooth('skymodel3.im','gaussian','56.7arcsec','56.7arcsec',pa='0deg',outfile='skymodel3s.im',overwrite=True)

     qtp_stats('skymodel3s.im')
     -> 533.1086583491433 639.15179922881021 17.688047409057617 1509.5882568359375 6138.2574919211502 

     # loose some flux due to edge effects, this is a pretty big beam. Only saw 87% of the flux.
     box = '128,128,895,895'
     qtp_stats('skymodel3.im',box=box)
     -> 0.0079393093557200544 0.012162735513638461 0.0 0.093201473355293274 4682.7952014282255
     qtp_stats('skymodel3s.im',box=box)
     -> 708.82964513885474 792.04254937608221 127.77438354492188 1509.5882568359375 4590.8570073671781
     # here we see 98% of the flux. Much better

Now run TP2VIS for this "TP" map:

     %time qtp_tp('test73s','skymodel3s.im','skymodel.ptg',1024,0.5,niter=0,phasecenter=phasecenter)
     CPU times: user 59 s, sys: 3.97 s, total: 1min 2s
     Wall time: 43 s

     qtp_stats('test73s/dirtymap.image',box=box)
     -> 498.13568240143888 577.9993760289758 94.203758239746094 1324.4320068359375 4814.915858248748

     qtp_stats('test73s/dirtymap.image.pbcor',box=box)
     -> 373.24462107677442 467.97077594625631 34.893051147460938 1342.643798828125 6051.4658773813298
     
there is considerable flux loss due to the edge, compared to taking a slightly larger field.

     %time qtp_tp('test73si','skymodel3s.im','skymodel.ptg',1024,0.5,niter=10000,phasecenter=phasecenter)
     qtp_stats('test73si/dirtymap.image',box=box)
     -> 856.92758386071046 989.69206942780863 146.81253051757812 2806.91259765625 8282.9525341583922 

     qtp_stats('test73si/dirtymap.image.pbcor')
     -> 653.65071754486894 805.90377482397446 19.468864440917969 2825.068359375 10596.842922478017
     NEW:
     -> 654.1575587738572 806.46994935261694 20.061256408691406 2825.67529296875 10605.945596565753 

     Flux in image is 89% of the pbcor image.
     Flux increase for niter=10000 is also 1.75.

Lets check on the deconvolution model

     %time qtp_tp('test72','skymodel3.im','skymodel.ptg',256,1.0,niter=0,phasecenter=phasecenter,deconv=False)

     qtp_stats('test72/dirtymap.image/')     
     -> 215.27963445868534 298.25989890656939 0.94464284181594849 932.38531494140625 3471.3569905698796 

     qtp_stats('test72/dirtymap.image.pbcor/')           
     -> 243.04016308504634 315.86565923889344 4.6677556037902832 964.96905517578125 3918.9920181531666
     

now this is closer, but only 49% of the flux seen. So add a bit of cleaning:

     qtp_tp('test72a','skymodel3.im','skymodel.ptg',256,1.0,niter=1,phasecenter=phasecenter,deconv=False)
     qtp_tp('test72b','skymodel3.im','skymodel.ptg',256,1.0,niter=10,phasecenter=phasecenter,deconv=False)
     qtp_tp('test72c','skymodel3.im','skymodel.ptg',256,1.0,niter=100,phasecenter=phasecenter,deconv=False)
     qtp_tp('test72d','skymodel3.im','skymodel.ptg',256,1.0,niter=1000,phasecenter=phasecenter,deconv=False)
     qtp_tp('test72e','skymodel3.im','skymodel.ptg',256,1.0,niter=10000,phasecenter=phasecenter,deconv=False)

     qtp_stats('test72a/dirtymap.image.pbcor/')
     -> 248.20878395943552 324.8916231523325 4.7178406715393066 975.71966552734375 4002.3353787503324
     qtp_stats('test72b/dirtymap.image.pbcor/')
     -> 264.78369012846184 353.61949168703052 4.7522697448730469 1078.679931640625 4269.6036530697575 
     qtp_stats('test72c/dirtymap.image.pbcor/')
     -> 322.32566862926029 420.03989764510862 8.1520462036132812 1224.415771484375 5197.4608088208388 
     qtp_stats('test72d/dirtymap.image.pbcor/')
     -> 397.04768187685039 499.77795638408207 15.814658164978027 1421.6407470703125 6402.3438609901623 
     qtp_stats('test72e/dirtymap.image.pbcor/')
     -> 432.26931350464508 537.0437639317048 23.463403701782227 1454.3140869140625 6970.2882347246259

so indeed, in the right direction. Now we've recovered 80% of the flux. But this was based on an unsmoothed input model.
the image file only has about 87% of the flux in the pbcor image.


# Summary


       # sky model
       qtp_stats('skymodel3.im')
       -> 0.0067413167365710279 0.010538542688954752 0.0 0.093201473355293274 7068.7829383667022

       # TP map
       qtp_stats('skymodel3s.im')
       -> 533.1086583491433 639.15179922881021 17.688047409057617 1509.5882568359375 6138.2574919211502

The TP map itself has only 86% of the flux of the sky model, due to edge-smooth spillover.

       niter = 10000
     
       qtp_tp('test71', 'skymodel3.im', ptg,mapsize,pixel,niter=0,     phasecenter=phasecenter,deconv=False)
       qtp_tp('test71a','skymodel3.im', ptg,mapsize,pixel,niter=niter, phasecenter=phasecenter,deconv=False)
       qtp_tp('test72', 'skymodel3s.im',ptg,mapsize,pixel,niter=0,     phasecenter=phasecenter)
       qtp_tp('test72a','skymodel3s.im',ptg,mapsize,pixel,niter=niter, phasecenter=phasecenter)

       QTP_STATS: test71/dirtymap.image  217.37447144687164 306.91034329628434 0.68886858224868774 976.6187744140625 3540.1415919987789 
       QTP_STATS: test71/dirtymap.image.pbcor/  246.02748213489227 320.42113111269316 3.4375145435333252 984.8890380859375 4006.7820130081027        88.4%
       QTP_STATS: test71a/dirtymap.image  358.14772008953167 491.15392317318714 -0.51811563968658447 1776.7994384765625 5832.7623824878301 
       QTP_STATS: test71a/dirtymap.image.pbcor/  411.28572649311241 518.17416722314238 -2.5894403457641602 1797.631103515625 6698.1632979361329      87.1

       QTP_STATS: test72/dirtymap.image  338.45580544797741 459.2284881777199 8.1547584533691406 1348.173583984375 5512.0615863702214 
       QTP_STATS: test72/dirtymap.image.pbcor/  380.07102980336424 476.96230594554856 40.579982757568359 1366.2178955078125 6189.8034832004241       89.0
       QTP_STATS: test72a/dirtymap.image  579.28727626987927 780.34442690800699 21.09892463684082 3003.82470703125 9434.2218144963335                
       QTP_STATS: test72a/dirtymap.image.pbcor/  661.02707715757344 817.26894900727882 101.13004302978516 3025.701171875 10765.429048345548          87.6

  

With our given skymodel pointing file, a tight map that covers the same as the skymodel, recovers about 83% of the pbcor flux.
Adding a little more space, this will increase to about 88%.

However, you will get more flux with some cleaning (of course).  There is also a difference if the pure skymodel is used, versus
a TP version of the skymodel.  Taking an extra little space around the edge in the cleaning grid. For both inputs,
the flux increase is about 1.77 for niter=10000. But for the pure skymodel (jy/pixel) we get about ...

# Simulation a 12m and 7m observation (qtp_alma())

Here we make a few configurations, simulating the way ALMA does observing

      # clean project directory that will accumulate the array configurations
      rm -rf map123

      # 7m data
      qtp_alma('map123','skymodel4.im', cfg=0, phasecenter=phasecenter,niter=0)
      qtp_stats('map123/dirtymap.image')
      # -0.022147989751717667 7.5062574618550402 -31.970539093017578 47.941951751708984 -8.2030883304928963
      ->  0.34001287352879528 9.4421584563476948 -31.970539093017578 47.941951751708984 74.99254777433751 

      # 12m data
      qtp_alma('map123','skymodel4.im', cfg=1, phasecenter=phasecenter,niter=0)
      qtp_stats('map123/dirtymap.image')
      # -0.00067117748887026698 0.79881291547218114 -3.3830177783966064 7.2705092430114746 -2.819783624967263
      ->   0.045472048909040642 0.99214617420591744 -3.3830177783966064 7.2705092430114746 113.40940432109203 

      qtp_alma('map123','skymodel4.im', cfg=2, phasecenter=phasecenter,niter=0)
      qtp_stats('map123/dirtymap.image')
      # -0.00040181912455326547 0.51110836834571505 -2.0784823894500732 4.9631514549255371 -2.9753583915594133
      ->   0.028397479823833002 0.63520862623528784 -2.0784823894500732 4.9631514549255371 124.37045653343189 

      qtp_alma('map123','skymodel4.im', cfg=3, phasecenter=phasecenter,niter=0)
      qtp_stats('map123/dirtymap.image')
      # -0.00028889088372208708 0.28135631957154145 -1.1350692510604858 2.7200651168823242 -5.1347200746613106
      ->   0.014195939503561211 0.34916105663293423 -1.1350692510604858 2.7200651168823242 149.17523488731428

      qtp_alma('map123','skymodel4.im', cfg=4, phasecenter=phasecenter,niter=0)
      qtp_stats('map123/dirtymap.image')
      # -0.00035501345573539235 0.14907231740846974 -0.70929414033889771 1.4412457942962646 -14.184133346067188
      ->   0.0082387849982799247 0.1826411793103821 -0.70929414033889771 1.4412457942962646 194.53429984408035 

      !cp map123/map123.alma.cycle5.1.ptg.txt .

      qtp_stats('skymodel4.im')
      # 0.006741305343066069 0.01053853930338459 0.0 0.093201480805873871 7068.7709914108464 

      qtp_tp('map123a','skymodel4.im','map123.alma.cycle5.1.ptg.txt',512,0.5,niter=0,phasecenter=phasecenter, deconv=False)
      qtp_stats('map123a/dirtymap.image')
      # 215.32609922632432 298.29780423985375 0.93181943893432617 932.4154052734375 3469.9342756210644
      -> 314.01041050607228 379.40586907034282 14.516051292419434 932.38623046875 3021.6648276810956 

      import glob
      ms0 = 'map123a/tp.ms'
      ms1 = glob.glob('map123/*alma*.ms')
      ms2 = glob.glob('map123/*aca*.ms')

      # the ugly bug in tclean() is creeping up again, for *all* sim data we need do_concat=False

      qtp_clean('map123b', ms0,ms1+ms2, 512,0.5,niter=0,    phasecenter=phasecenter,do_concat=False)
      qtp_clean('map123b1',ms0,ms1+ms2, 512,0.5,niter=10000,phasecenter=phasecenter,do_concat=False)      
      
      qtp_stats('map123b/alma.image')
      -> 0.041449847856698301 0.74274466762890645 -2.1117897033691406 5.1547932624816895 270.64620087856031 

      qtp_stats('map123b/tpalma.image')
      -> 13.631941391489706 16.437671252277045 0.81794089078903198 42.461055755615234 82803.776240093226 

      tp2vistweak('map123b/tpalma','map123b1/tpalma')
      -> Stat:     Bmaj     Bmin Sum(dirty) Sum(clean) dirty/clean
      	          2.674    1.971 71837.9729  5182.1958    13.8625
      qtp_stats('map123b1/tpalma.tweak.image')
      -> 20.106741642861792 21.873343025273808 -0.65520060062408447 37.914833068847656 207175.87287308357

      qtp_stats('map123b1/tpalma.jvm')
      -> 0.96280296482464456 1.4322078257765019 -9.968995300368988e-07 7.3863706588745117 5848.3028185852536

      qtp_beam('map123b/tpalma.psf',plot='map123b/qtp_beam.png',normalized=True)
      -> QTP_BEAM: map123b/tpalma.psf  2.67405 1.97091 0.5 23.8869 23.8869
         QTP_BEAM: Max/Last/PeakLoc 26.749388042 26.3613088036 78.0



# Notes

tclean() uses:
            imager.initializeDeconvolvers()
	urvashi
	better than dc / deconvolve()
