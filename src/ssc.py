#
#  taken from snippet.txt
#

"""
Last Update: 2017.09.30
- Fill free to use and modify this pipeline.
- Please consider citing the following publications
    1) https://arxiv.org/abs/1709.09365
    2) http://adsabs.harvard.edu/abs/2014A%26A...563A..99F
- Or contact Shahram Faridani (shahram.faridani@gmail.com)
**********************************
"""
import math
import os
import sys
import datetime

testMode = False

# Procedures
# Check if d exists, if not it will be created
def ensure_dir(d):
    if os.path.exists(d):
        print 'Target directory already exists!'
        print 'If you continue all the files in the existing directory will be removed permanently'
        key_strike = raw_input(
            'Press C if you want to continue for aborting press X: ')
        if key_strike.upper() == 'C':
            os.system('rm -rf ' + str(d) + '/*.*')
        if key_strike.upper() == 'X':
            print 'Aborting the script immediately'
            sys.exit()
    if not os.path.exists(d):
        os.makedirs(d)

# BUNIT from the header
def getBunit(imName):
    ia.open(str(imName))
    summary = ia.summary()
    return summary['unit']

# BMAJ beam major axis in units of arcseconds
def getBmaj(imName):
    ia.open(str(imName))
    summary = ia.summary()
    major = summary['restoringbeam']['major']
    unit = summary['restoringbeam']['major']['unit']
    major_value = summary['restoringbeam']['major']['value']
    if unit == 'deg':
        major_value = major_value * 3600
    return major_value

# BMIN beam minor axis in units of arcseconds
def getBmin(imName):
    ia.open(str(imName))
    summary = ia.summary()
    minor = summary['restoringbeam']['minor']
    unit = summary['restoringbeam']['minor']['unit']
    minor_value = summary['restoringbeam']['minor']['value']
    if unit == 'deg':
        minor_value = minor_value * 3600
    return minor_value

# Position angle of the interferometeric data
def getPA(imName):
    ia.open(str(imName))
    summary = ia.summary()
    pa_value = summary['restoringbeam']['positionangle']['value']
    pa_unit  = summary['restoringbeam']['positionangle']['unit']
    return pa_value, pa_unit

# our Main, QAC style
def qac_ssc(project_dir, highres, lowres, sdTel = None):
    """
        project_dir       (new) directory in which all work will be performed
        highres           high res (interferometer) image
        lowres            low res (SD/TP) image
        sdTEL             if not provided, sdFITS must contain the telescope
    """
    print 'The presented pipeline performs short-spacing correction (SSC) in the image domain'
    print '   Project directory :', project_dir
    print '   Single-dish Telescope: ',sdTel
    print 'Single-dish and interferometric fits files'
    print '   Single-dish: ',lowres
    print '   Interferometer: ',highres

    ensure_dir(project_dir)    

    # Getting the current time
    nowStr = datetime.datetime.now()
    dateStr = str(nowStr.year) + str(nowStr.month) + str(nowStr.day)
    print 'Current Date: ' + str(dateStr) + '\n'
    # Determining the current path
    currentPath = str(os.getcwd())
    print 'currentPath: ' + str(currentPath) + '\n'

    # this will be our prefix/directory in which all work occurs
    source = project_dir

    # Creating a temporary directory for partial results
    # it will be deleted at the end of script while the "scriptMode" is True.
    #dirName = str(source) + '_' + str(dateStr) + '_casaIms'
    
    # Path of temp directory for the partial results
    #casaImages = currentPath + '/' + str(dirName)
    casaImages = project_dir
    casaImPath = casaImages + '/'
    print 'CASA-images will be stored in: ' + str(casaImPath) + '\n'


    # Check if the temporary directory exists if not it creates one
    # ensure_dir(casaImages)

    # yuck, this could damage other work unless you work in a project_dir
    
    #print 'Cleaning the previous log files ...' + '\n'
    #os.system('rm -rf *.last')
    #os.system('rm -rf *.log')

    # Creating the prefix for all the CASA-images
    #prefix = str(source) + '_'
    prefix = project_dir + '/'

    # Defining some useful variables
    # lr = str(prefix) + 'LR.im'                 # imported low resolution cube
    # hr = str(prefix) + 'HR.im'                 # imported high resolution cube
    lr = lowres                                
    hr = highres

    lr_reg = str(prefix) + 'LR_reg.im'         # regridded low resolution cube
    hr_conv = str(prefix) + 'HR_conv.im'       # convolved high resolution cube
    sub = str(prefix) + 'sub.im'               # observed flux only by single-dish
    sub_bc = str(prefix) + 'sub_bc.im'         # Corrected flux by the ratio of beam sizes
    combined = str(prefix) + 'combined.im'     # restored missing flux
    comb_fits = str(prefix) + 'combined.fits'  # final fits

    print 'Importing FITS files ...'

    # single-dish re-gridded
    # default(importfits)
    # fitsimage = str(sdFITS)
    # imagename = str(lr)
    # importfits()
    #     importfits(sdFITS,lr)

    # interferometer
    #default(importfits)
    #fitsimage = str(intFITS)
    #imagename = str(hr)
    #importfits()
    # importfits(intFITS,hr)
    # print 'Low and high resolution cubes are imported' + '\n'

    # Re-gridding the Single-dish cube
    print 'Begin regridding ...'
    print 'The default interpolation scheme is linear'
    ia.open(str(lr))
    mycs = ia.coordsys()
    mycs.telescope
    mycs.settelescope(str(sdTel))
    ia.setcoordsys(csys=mycs.torecord())
    ia.done()
    # 
    ia.open(str(hr))
    cs1 = ia.coordsys()
    s1 = ia.shape()
    ia.close()
    ia.open(str(lr))
    ia.regrid(outfile=str(lr_reg), method='linear',
              shape=s1, csys=cs1.torecord(), overwrite=True)
    ia.close()
    print 'End of re-griding' + '\n'


    # Check if both data sets are in the same units
    if str(getBunit(lr_reg)) != str(getBunit(hr)):
        print 'Bunits of low- and high-resolution data cubes are not identical!'
        return


    print ''
    print 'LR_Bmin: ' + str(getBmin(lr_reg))
    print 'LR_Bmaj: ' + str(getBmaj(lr_reg))
    print ''
    print 'HR_Bmin: ' + str(getBmin(hr))
    print 'HR_Bmaj: ' + str(getBmaj(hr))
    print ''

    kernel1 = math.sqrt(float(getBmaj(lr_reg))**2 - float(getBmaj(hr))**2)
    kernel2 = math.sqrt(float(getBmin(lr_reg))**2 - float(getBmin(hr))**2)

    print 'Kernel1: ' + str(kernel1)
    print 'Kernel2: ' + str(kernel2)
    print ''

    # Convolve the interferometer with the appropriate beam
    print 'Convolving high resolution cube ...'
    default(imsmooth)
    imagename = str(hr)
    kernel = 'gauss'
    major = str(getBmaj(lr_reg)) + 'arcsec'
    minor = str(getBmin(lr_reg)) + 'arcsec'
    targetres = True
    pa = str(getPA(hr)[0]) + str(getPA(hr)[1])
    outfile = str(hr_conv)
    imsmooth()
    print 'End of convolution' + '\n'

    # Missing flux
    default(immath)
    print 'Computing the obtained flux only by single-dish ...'
    imagename = [str(lr_reg), str(hr_conv)]
    mode = 'evalexpr'
    expr = 'IM0 - IM1'
    outfile = str(sub)
    immath()
    print 'Flux difference has been determined' + '\n'

    if getBunit(lr_reg) == 'Jy/beam':
        print 'Computing the weighting factor according to the surface of the beam ...'
        weightingfac = (float(getBmaj(str(hr))) * float(getBmin(str(hr)))
                        ) / (float(getBmaj(str(lr_reg))) * float(getBmin(str(lr_reg))))
        print 'Weighting factor: ' + str(weightingfac) + '\n'

        print 'Considering the different beam sizes ...'
        default(immath)
        imagename = str(sub)
        mode = 'evalexpr'
        expr = 'IM0 *' + str(weightingfac)
        outfile = str(sub_bc)
        immath()
        print 'Fixed for the beam size' + '\n'

        print 'Combinig the single-dish and interferometer cube'
        default(immath)
        imagename = [str(hr), str(sub_bc)]
        mode = 'evalexpr'
        expr = 'IM0 + IM1'
        outfile = str(combined)
        immath()
        print 'The missing flux has been restored' + '\n'

    if getBunit(lr_reg) == 'Kelvin':
        print 'Combinig the single-dish and interferometer cube'
        default(immath)
        imagename = [str(hr), str(sub)]
        mode = 'evalexpr'
        expr = 'IM0 + IM1'
        outfile = str(combined)
        immath()
        print 'The missing flux has been restored' + '\n'

    # Export the combined FITS
    print 'Exporting the combined FITS ...'
    print 'The existing FITS-file will be overwritten'
    default(exportfits)
    imagename = str(combined)
    fitsimage = str(comb_fits)
    overwrite = True
    exportfits()
    print ''

    print 'Moving all CASA Images to :' + '\n' + str(casaImages)
    os.system('mv *.im ' + str(casaImages))
    os.system('rm -rf *.last')
    os.system('rm -rf *.log')
    print 'Short-spacing-correction has been performed'
