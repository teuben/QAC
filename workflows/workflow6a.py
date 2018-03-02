#  casaguide "M100 Band3 Combine" - slightly modified version for TP2VIS and CASA 5
#
#  For more background, see also:
#
#        https://casaguides.nrao.edu/index.php/M100_Band3
#        https://casaguides.nrao.edu/index.php/M100_Band3_Combine_4.3
#
#  In these scripts huge MS files are used, but here we are using the processed
#  "aver" MS files created in TP2VIS' workflow6.
#  Those data are in http://admit.astro.umd.edu/~teuben/TP2VIS/workflow6_data.tar.gz
#
#  The resulting final fluxes will be a little different, also because of newer CASA ?
#
#  TODO:    option to use tclean instead of clean
#
#  TIMING:  this script takes about 81' (39' CPU) on nemo2, and about 29' (58' CPU) on dante
#           and with do_automask=False it will take  11' (24' CPU) on nemo2.
#
#  WARNING: this script needs a lot of memory (~13g)
#
#  NOTE:    info on generating scripts from casaguide wiki's:
#           https://casaguides.nrao.edu/index.php?title=Extracting_scripts_from_these_tutorials
#           https://github.com/jaredcrossley/CASA-Guides-Script-Extractor
#           ./extractCASAscript.py https://casaguides.nrao.edu/index.php/M100_Band3_Combine_4.3
#
#  fixes needed from the casaguide for CASA 5.1.1 (EKeller should know about this?)
#         T -> True   (8 times  in imview)
#         imstat()['flux']*5.0     the *5.0 is not needed, it (now?) properly does Jy.km/s units
#         amp vs. velocity plot ?  M100_combine_vel.png
#         needed an extra:   os.system('rm -rf M100_Feather_CO.image.pbcor')
#         no need for os.system('rm  ...png'), before each imview, it will overwrite (now)
#         
#
# For original data you need:
#      M100_Band3_12m_CalibratedData.ms     spw 0
#      M100_Band3_7m_CalibratedData.ms      spw 3,5
#      M100_TP_CO_cube.bl.image             -                 [why are there no 5.1 reference images available now]
#
# For the SD gridded MS files you need:
#      M100_aver_12.ms                      spw 0
#      M100_aver_7.ms                       spw 0,1
#      M100_TP_CO_cube.bl.image             (no change)



do_plotting = False        # MS plots
do_fits     = False        # FITS output
do_automask = True         # automasking iteration


sel0 = {'spw' : '0~2',  'vis' : ['M100_12m_CO.ms',  'M100_7m_CO.ms']  }   # original big and narrow channel data   (4.1G and 1.6G resp.)
sel1 = {'spw' : '0',    'vis' : ['M100_aver_12.ms', 'M100_aver_7.ms'] }   # 5 km/s data from workflow6.py          (89M  and 25M resp.)        

# pick sel0 or sel1 (ahum, sel0 may still not work)
sel = sel1         
# then derive the parameters we decided to make it depend on sel{}
vis = sel['vis']
spw = sel['spw']

print "CONCAT"
os.system('rm -rf M100_combine_CO.ms')
concat(vis=vis, concatvis='M100_combine_CO.ms')


if do_plotting:
    os.system('rm -rf *m_mosaic.png')
    au.plotmosaic(vis[0],sourceid='0',figfile='12m_mosaic.png')
    au.plotmosaic(vis[1],sourceid='0',figfile='7m_mosaic.png')

    os.system('rm -rf 7m_WT.png 12m_WT.png')
    plotms(vis=vis[0],yaxis='wt',xaxis='uvdist',spw='0:200',
       coloraxis='spw',plotfile='12m_WT.png')
    #
    plotms(vis=vis[1],yaxis='wt',xaxis='uvdist',spw='0~1:200',
       coloraxis='spw',plotfile='7m_WT.png')

    # In CASA  ? spw='0~2:200',
    os.system('rm -rf combine_CO_WT.png')
    plotms(vis='M100_combine_CO.ms',yaxis='wt',xaxis='uvdist',
       coloraxis='spw',plotfile='combine_CO_WT.png')


    os.system('rm -rf M100_combine_uvdist.png')
    plotms(vis='M100_combine_CO.ms',yaxis='amp',xaxis='uvdist',spw='', avgscan=True,
       avgchannel='5000', coloraxis='spw',plotfile='M100_combine_uvdist.png')

    os.system('rm -rf M100_combine_vel.png')
    plotms(vis='M100_combine_CO.ms',yaxis='amp',xaxis='velocity',spw='', avgtime='1e8',avgscan=True,coloraxis='spw',avgchannel='5',
       transform=True,freqframe='LSRK',restfreq='115.271201800GHz', plotfile='M100_combine_vel.png')

### Initialize 
import scipy.ndimage 

### Define clean parameters
vis        = 'M100_combine_CO.ms'
prename    = 'M100_combine_CO_cube'
myimage    = prename+'.image'
myflux     = prename+'.flux'
mymask     = prename+'.mask'
myresidual = prename+'.residual'
imsize     = 800
cell       = '0.5arcsec'
minpb      = 0.2
restfreq   = '115.271201800GHz'
outframe   = 'LSRK'
# spw='0~2'
spw        = '0'
width      = '5km/s'
start      = '1400km/s'
nchan      = 70
robust     = 0.5
phasecenter= 'J2000 12h22m54.9 +15d49m15.0'
scales     = [0]
ssbias     = 0.6
box1       = '219,148,612,579'       # regrid box, so feather overlaps and is not close to where PB is low
box2       = [190, 150, 650, 610]    # orig box for plotting
box2       = [219, 148, 612, 579]    # regrid box, match box1 for better figure comparison

### Setup stopping criteria with multiplier for rms.
stop       = 3. 

### Minimum size multiplier for beam area for removing very small mask regions. 
pixelmin   = 0.5

### If not automasking, try some niter's. Else do them in the automasking loop
if do_automask:
    niter0 = 0
else:
    niter0 = 10000

## Make Initial Dirty Image and Determine Synthesized Beam area
print "CLEAN-0"
### Make initial dirty image
os.system('rm -rf ' + prename + '.* ' + prename + '_*')
clean(vis=vis,imagename=prename,
      imagermode='mosaic',ftmachine='mosaic',minpb=minpb,
      imsize=imsize,cell=cell,spw=spw,
      weighting='briggs',robust=robust,phasecenter=phasecenter,
      mode='velocity',width=width,start=start,nchan=nchan,      
      restfreq=restfreq,outframe=outframe,veltype='radio',
      mask='',
      niter=niter0,interactive=False)

# Determine the beam area in pixels for later removal of very small mask regions
major=imhead(imagename=myimage,mode='get',hdkey='beammajor')['value']
minor=imhead(imagename=myimage,mode='get',hdkey='beamminor')['value']
pixelsize=float(cell.split('arcsec')[0])
beamarea=(major*minor*pi/(4*log(2)))/(pixelsize**2)
print 'beamarea in pixels =', beamarea

## Find properties of the dirty image

### Find the peak in the dirty cube.
myimage=prename+'.image'
bigstat=imstat(imagename=myimage)
peak= bigstat['max'][0]
print 'peak (Jy/beam) in cube = '+str(peak)
### Sets threshold of first loop, try 2-4. Subsequent loops are set thresh/2.
if do_automask:
    thresh = peak / 4.
else:
    thresh = 0.0

### If True: find the rms in two line-free channels; If False:  Set rms by hand in else statement.
if True:  
    chanstat = imstat(imagename=myimage,chans='4')
    rms1     = chanstat['rms'][0]
    chanstat = imstat(imagename=myimage,chans='66')
    rms2     = chanstat['rms'][0]
    rms      = 0.5*(rms1+rms2)        
else:
    rms      = 0.011


print 'rms (Jy/beam) in a channel = '+str(rms)


## Automasking Loop

if do_automask:
    os.system('rm -rf ' + prename +'_threshmask*')
    os.system('rm -rf ' + prename +'_fullmask*')
    os.system('rm -rf ' + prename +'.image*')
n=-1
while thresh >= stop*rms:   
    n=n+1
    print 'clean threshold this loop is', thresh
    threshmask = prename+'_threshmask' +str(n)
    maskim = prename+'_fullmask' +str(n)
    immath(imagename = [myresidual],
           outfile = threshmask,
           expr = 'iif(IM0 > '+str(thresh) +',1.0,0.0)',
           mask=myflux+'>'+str(minpb))
    if n==0:
        os.system('cp -r '+threshmask+' '+maskim+'.pb')
        print 'This is the first loop'
    else:
        makemask(mode='copy',inpimage=myimage,
                 inpmask=[threshmask,mymask],
                 output=maskim)
        imsubimage(imagename=maskim, mask=myflux+'>'+str(minpb),
                   outfile=maskim+'.pb')     
    print 'Combined mask ' +maskim+' generated.'

    # Remove small masks
    os.system('cp -r '+maskim+'.pb ' +maskim+'.pb.min')
    maskfile=maskim+'.pb.min'
    ia.open(maskfile)
    mask = ia.getchunk()
    labeled,j = scipy.ndimage.label(mask)                     
    myhistogram = scipy.ndimage.measurements.histogram(labeled,0,j+1,j+1)
    object_slices = scipy.ndimage.find_objects(labeled)
    threshold = beamarea*pixelmin
    for i in range(j):
        if myhistogram[i+1]<threshold:
            mask[object_slices[i]] = 0

    ia.putchunk(mask)
    ia.done()
    print 'Small masks removed and ' +maskim +'.pb.min generated.'

    os.system('rm -rf '+mymask+'')
    clean(vis=vis,imagename=prename,
          imagermode='mosaic',ftmachine='mosaic',minpb=minpb,
          imsize=imsize,cell=cell,spw=spw,
          weighting='briggs',robust=robust,phasecenter=phasecenter,
          mode='velocity',width=width,start=start,nchan=nchan,      
          restfreq=restfreq,outframe=outframe,veltype='radio',
          mask = maskim+'.pb.min',
          multiscale=scales,smallscalebias=ssbias,
          interactive = False,
          niter = 10000,
          threshold = str(thresh) +'Jy/beam')

    if thresh==stop*rms: break
    thresh = thresh/2.
    # Run a final time with stop*rms if more than a little above
    # stop*rms. Also make a back-up of next to last image
    if thresh < stop*rms and thresh*2.>1.05*stop*rms:
        thresh=stop*rms  
        os.system('cp -r '+myimage+' '+myimage+str(n))

if do_plotting:        
    viewer('M100_combine_CO_cube.image')

myimage  = 'M100_combine_CO_cube.image'
chanstat = imstat(imagename=myimage,chans='4')
rms1     = chanstat['rms'][0]
chanstat = imstat(imagename=myimage,chans='66')
rms2     = chanstat['rms'][0]
rms      = 0.5*(rms1+rms2)
print 'rms in a channel = '+str(rms)


## Make moment maps

os.system('rm -rf M100_combine_CO_cube.image.mom0')
immoments(imagename = 'M100_combine_CO_cube.image',
         moments = [0],
         axis = 'spectral',chans = '9~61',
         mask='M100_combine_CO_cube.flux>0.3',
         includepix = [rms*2,100.],
         outfile = 'M100_combine_CO_cube.image.mom0')

os.system('rm -rf M100_combine_CO_cube.image.mom1')
immoments(imagename = 'M100_combine_CO_cube.image',
         moments = [1],
         axis = 'spectral',chans = '9~61',
         mask='M100_combine_CO_cube.flux>0.3',
         includepix = [rms*5.5,100.],
         outfile = 'M100_combine_CO_cube.image.mom1')


# and figures
imview (raster=[{'file': 'M100_combine_CO_cube.image.mom0',
                 'range': [-0.3,25.],'scaling': -1.3,'colorwedge': True}],
         zoom={'blc': box2[0:2],'trc': box2[2:4]},  
         out='M100_combine_CO_cube.image.mom0.png')

imview (raster=[{'file': 'M100_combine_CO_cube.image.mom1',
                 'range': [1440,1695],'colorwedge': True}],
         zoom={'blc': box2[0:2],'trc': box2[2:4]}, 
         out='M100_combine_CO_cube.image.mom1.png')


os.system('rm -rf M100_combine_CO_cube.flux.1ch')
imsubimage(imagename='M100_combine_CO_cube.flux',
           outfile='M100_combine_CO_cube.flux.1ch',
           chans='35')

os.system('rm -rf M100_combine_CO_cube.image.mom0.pbcor')
immath(imagename=['M100_combine_CO_cube.image.mom0', \
                       'M100_combine_CO_cube.flux.1ch'],
        expr='IM0/IM1',
        outfile='M100_combine_CO_cube.image.mom0.pbcor')

imview (raster=[{'file': 'M100_combine_CO_cube.image.mom0.pbcor',
                 'range': [-0.3,25.],'scaling': -1.3,'colorwedge': True}],
         zoom={'blc':box2[0:2],'trc': box2[2:4]},
         out='M100_combine_CO_cube.image.mom0.pbcor.png')


## Convert 7m+12m Images to Fits Format

if do_fits:
    os.system('rm -rf *.fits')
    exportfits(imagename='M100_combine_CO_cube.image',            fitsimage='M100_combine_CO_cube.image.fits',            overwrite=True)
    exportfits(imagename='M100_combine_CO_cube.flux',             fitsimage='M100_combine_CO_cube.flux.fits',             overwrite=True)
    exportfits(imagename='M100_combine_CO_cube.image.mom0',       fitsimage='M100_combine_CO_cube.image.mom0.fits',       overwrite=True)
    exportfits(imagename='M100_combine_CO_cube.image.mom0.pbcor', fitsimage='M100_combine_CO_cube.image.mom0.pbcor.fits', overwrite=True)
    exportfits(imagename='M100_combine_CO_cube.image.mom1',       fitsimage='M100_combine_CO_cube.image.mom1.fits',       overwrite=True)


## Prepare Images for Feathering
imregrid(imagename='M100_TP_CO_cube.bl.image',
         template='M100_combine_CO_cube.image',
         axes=[0, 1],
         output='M100_TP_CO_cube.regrid',
         overwrite=True)

# trim

imsubimage(imagename='M100_TP_CO_cube.regrid',
           outfile='M100_TP_CO_cube.regrid.subim', 
           box=box1,
           overwrite=True)

imsubimage(imagename='M100_combine_CO_cube.image',
           outfile='M100_combine_CO_cube.image.subim',
           overwrite=True,
           box=box1)

# fix the TP response
imsubimage(imagename='M100_combine_CO_cube.flux',
           outfile='M100_combine_CO_cube.flux.subim',
           box=box1,
           overwrite=True)           

os.system('rm -rf M100_TP_CO_cube.regrid.subim.depb')
immath(imagename=['M100_TP_CO_cube.regrid.subim',
                  'M100_combine_CO_cube.flux.subim'],
       expr='IM0*IM1',
       outfile='M100_TP_CO_cube.regrid.subim.depb')

# now feather!
os.system('rm -rf M100_Feather_CO.image')
feather(imagename='M100_Feather_CO.image',
        highres='M100_combine_CO_cube.image.subim',
        lowres='M100_TP_CO_cube.regrid.subim.depb')


## Make Moment Maps of the Feathered Images

# First (but optionally; this is solely for comparison to the feathered images and not needed to create the final feathered images),
# make moment maps for the (regridded) TP image.

myimage  = 'M100_TP_CO_cube.regrid.subim'
chanstat = imstat(imagename=myimage,chans='4')
rms1     = chanstat['rms'][0]
chanstat = imstat(imagename=myimage,chans='66')
rms2     = chanstat['rms'][0]
rms      = 0.5*(rms1+rms2)  
 
os.system('rm -rf M100_TP_CO_cube.regrid.subim.mom0')
immoments(imagename='M100_TP_CO_cube.regrid.subim',
         moments=[0],
         axis='spectral',
         chans='10~61',
         includepix=[rms*2., 50],
         outfile='M100_TP_CO_cube.regrid.subim.mom0')
 
os.system('rm -rf M100_TP_CO_cube.regrid.subim.mom1')
immoments(imagename='M100_TP_CO_cube.regrid.subim',
         moments=[1],
         axis='spectral',
         chans='10~61',
         includepix=[rms*5.5, 50],
         outfile='M100_TP_CO_cube.regrid.subim.mom1')

imview(raster=[{'file': 'M100_TP_CO_cube.regrid.subim.mom0',
                'range': [0., 1080.],
                'scaling': -1.3,
                'colorwedge': True}],
       out='M100_TP_CO_cube.regrid.subim.mom0.png')
 
imview(raster=[{'file': 'M100_TP_CO_cube.regrid.subim.mom1',
                'range': [1440, 1695],
                'colorwedge': True}], 
       out='M100_TP_CO_cube.regrid.subim.mom1.png')

## Then make moment maps for the feathered image.
myimage  = 'M100_Feather_CO.image'
chanstat = imstat(imagename=myimage,chans='4')
rms1     = chanstat['rms'][0]
chanstat = imstat(imagename=myimage,chans='66')
rms2     = chanstat['rms'][0]
rms      = 0.5*(rms1+rms2)  
 
os.system('rm -rf M100_Feather_CO.image.mom0')
immoments(imagename='M100_Feather_CO.image',
         moments=[0],
         axis='spectral',
         chans='10~61',
         includepix=[rms*2., 50],
         outfile='M100_Feather_CO.image.mom0')
 
os.system('rm -rf M100_Feather_CO.image.mom1')
immoments(imagename='M100_Feather_CO.image',
         moments=[1],
         axis='spectral',
         chans='10~61',
         includepix=[rms*5.5, 50],
         outfile='M100_Feather_CO.image.mom1')

imview(raster=[{'file': 'M100_Feather_CO.image.mom0',
                'range': [-0.3, 25.],
                'scaling': -1.3,
                'colorwedge': True}],
       out='M100_Feather_CO.image.mom0.png')
 
imview(raster=[{'file': 'M100_Feather_CO.image.mom1',
                'range': [1440, 1695],
                'colorwedge': True}], 
       out='M100_Feather_CO.image.mom1.png')

## Correct the Primary Beam Response

os.system('rm -rf M100_Feather_CO.image.pbcor')
immath(imagename=['M100_Feather_CO.image',
                  'M100_combine_CO_cube.flux.subim'],
       expr='IM0/IM1',
       outfile='M100_Feather_CO.image.pbcor')

imsubimage(imagename='M100_combine_CO_cube.flux.subim',
           outfile='M100_combine_CO_cube.flux.1ch.subim',
           chans='35',
           overwrite=True)

os.system('rm -rf M100_Feather_CO.image.mom0.pbcor')
immath(imagename=['M100_Feather_CO.image.mom0',
                  'M100_combine_CO_cube.flux.1ch.subim'],
        expr='IM0/IM1',
        outfile='M100_Feather_CO.image.mom0.pbcor')

imview(raster=[{'file': 'M100_Feather_CO.image.mom0.pbcor',
                'range': [-0.3, 25.],
                'scaling': -1.3,
                'colorwedge': True}],
       out='M100_Feather_CO.image.mom0.pbcor.png')

##

imstat('M100_combine_CO_cube.image.subim')

print imstat('M100_combine_CO_cube.image.subim')['flux'][0]
### 1415.87469578
# ->1325.97830921

print imstat('M100_TP_CO_cube.regrid.subim.depb')['flux'][0]
### 2776.12281313
# ->2779.3571811973284
print imstat('M100_Feather_CO.image')['flux'][0]
### 2776.12277509
# ->2779.3573693608228
print imstat('M100_Feather_CO.image.pbcor')['flux'][0]
### 3055.34553736
# ->3062.6710650359505

#  (2972 +/- 319 Jy km/s from the BIMA SONG; Helfer et al. 2003).


### now compare the flux recovery per 5 km/s channel

f0  =  imstat('M100_TP_CO_cube.bl.image',axes=[0,1])['flux']
f0a =  imstat('M100_TP_CO_cube.regrid.subim',axes=[0,1])['flux']

f1  =  imstat('M100_combine_CO_cube.image',axes=[0,1])['flux']
f1a =  imstat('M100_combine_CO_cube.image.subim',axes=[0,1])['flux']

f2  =  imstat('M100_Feather_CO.image',axes=[0,1])['flux']
f2a =  imstat('M100_Feather_CO.image.pbcor',axes=[0,1])['flux']


plot2a([f0,f1,f2],   'plot2a1.png')    
plot2a([f0a,f1a,f2a],'plot2a2.png')    
plot2a([f0,f0a],     'plot2a3.png')    
plot2a([f1,f1a],     'plot2a4.png')    
plot2a([f2,f2a],     'plot2a5.png')    
