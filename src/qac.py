#  QAC:  "Quick Array Combinations"
#        These are helper functions for Feather, TP2VIS and other Array Combination techniques.
#        Some are wrappers around CASA, others are also convenient for regression testing.
#
#  There are a series of qac_*() functions, and one static class QAC.* with pure helper functions
#
# See also : https://casaguides.nrao.edu/index.php/Analysis_Utilities
# (we currently don't assume you have installed these 'au' tools, but they are very useful)
#
# 
#
import os, shutil, math, tempfile
import os.path
# from buildmosaic import buildmosaic
from utils import constutils as const
import numpy as np
# import numpy.ma as ma
# import pyfits as fits
import matplotlib.pyplot as plt

# this is dangerous, creating some convenient numbers in global namespace, but here they are...
cqa  = qa.constants('c')                  # (turns out to be in m/s)
cms  = qa.convert(cqa,"m/s")['value']     # speed of light, forced in m/s (299792458.0)
apr  = 180.0 * 3600.0 / np.pi             # arcsec per radian (206264.8)
bof  = np.pi / (4*math.log(2.0))          # beam oversampling factor (1.1331) : NPPB = bof * (Beam/Pixel)**2  [cbm in tp2vis.py]
stof = 2.0*np.sqrt(2.0*np.log(2.0))       # FWHM=stof*sigma  (2.3548)

# nasty globals
#restoringbeam = 'common'                # common beam for all planes
restoringbeam = None                     # given the edge channel issue, a common beam is not a good idea

def qac_version():
    """ qac helper functions """
    print "qac: version 28-feb-2018"
    print "casa:",casa['version']         # there is also:   cu.version_string()
    print "data:",casa['dirs']['data']    

def qac_log(message, verbose=True):
    """ qac banner message; can be turned off
    """
    if verbose:
        print ""
        print "========= QAC: %s " % message
        print ""
        
    #-end of qac_log()

def qac_tmp(prefix, tmpdir='.'):
    """ Create a temporary file in a tmpdir

        Parameters
        ----------
        prefix : str
           starting name of the filename in <tmpdir>/<pattern>

        tmpdir

        Returns
        -------
        Unique filename
    """
    fd = tempfile.NamedTemporaryFile(prefix=prefix,dir=tmpdir,delete='false')
    name = fd.name
    fd.close()
    return name

    #-end of qac_tmp()

def qac_im_ptg(phasecenter, imsize, pixel, grid, im=[], rect=False, outfile=None):
    """
    Generate hex-grid of pointing centers that covers a specified area. 
    Can optionally output in file or as list. Can check for overlap with input image areas
    
    Required Parameters
    -------------------
        phasecenter : str 
            phasecenter of the image/pointings *only in J2000 decimal degrees format* 
            Example: phasecenter = 'J2000 52.26483deg 31.28025deg' 
        imsize : int or list of 2 ints
            Number of pixels 
            Example: imsize = [1400,1800] imsize = 500 is equivalent to [500,500] 
        pixel : float
            Pixel size in arcsecs
            Example: pixel = 0.5
        grid : float
            Separation of pointings in arcsecs (determined from beam size and sampling)
            Example: grid=15.9
                
    Optional Parameters
    -------------------
        im : list of strings @TODO
            Input image file name(s) as a string or list of strings. This determines the area covered by the pointings.
            Example: im=["GBT.im", "VLA.im"]
            Default: empty
        rect : boolean
            Indicates if only pointings within specified rectangular area will be reported
            Example: rect=False
            Default: False
        outfile : str
            If present, used as name of output file 
            Example: outfile="FinalGBT.ptg"
            Default: None (not used, only list returned)
    
    Returns
    -------
        finalPtglist : list of str
            Pointings in CASA J2000 degrees format
    
    
    -- Arnab Dhabal - Feb 14, 2018
    
    """
    def hex(nring,grid):
        coordlist = []
        for row in range(-nring+1,nring,1):
            y = 0.866025403 * grid * row
            lo = 2-2*nring+abs(row)
            hi = 2*nring-abs(row)-1
            for k in range(lo,hi,2):
                x = 0.5*grid*k
                coords = [x,y]
                coordlist.append((coords))
        return coordlist
    
    #check if images is list or single file or none
    if type(im) == type([]):
            im_list = im
    elif im == None:
        im_list = []
    else:
        im_list = [im]

    # convert phasecenter into ra,dec in degree
    phaseCenCoords = phasecenter.split(" ")
    if (phaseCenCoords[1][-3:] == "deg") and (phaseCenCoords[2][-3:] == "deg"):
        raDeg = float(phaseCenCoords[1][:-3])
        decDeg = float(phaseCenCoords[2][:-3])
    #print("RA:",raDeg, "Dec:",decDeg)
    cosdec = math.cos(decDeg*math.pi/180.0)
    
    imsize = QAC.imsize2(imsize)
    xim = imsize[0]
    yim = imsize[1]
        
    if yim/xim > np.sqrt(3):
        maxim = yim/2.0
        nring = int(np.ceil((pixel*maxim+0.5*grid)/(grid)))+1
    else:
        diag = np.sqrt(xim**2+yim**2)/2.0
        maxim = diag*np.cos(np.pi/6.0 - np.arctan(yim/xim))
        nring = int(np.ceil(pixel*maxim/(grid*np.cos(np.pi/6.0))))+1
        
    # print("rings:",nring)

    xylist = hex(nring,grid)
    ptgbool = [True]*len(xylist)
    #pointings only inside rect
    if(rect == True):
        for xyi in np.arange(0,len(xylist),1):
            if (xylist[xyi][0] > xim*pixel/2.0) or (xylist[xyi][0] < -xim*pixel/2.0) or (xylist[xyi][1] > yim*pixel/2.0) or (xylist[xyi][1] < -yim*pixel/2.0):
                ptgbool[xyi] = False
    

    #add phasecenter and generate J2000 deg pointings
    ralist = [0.0]*len(xylist)
    declist = [0.0]*len(xylist)
    for xyi in np.arange(0,len(xylist),1):
        ralist[xyi] = raDeg + xylist[xyi][0]/3600.0/cosdec
        declist[xyi] = decDeg + xylist[xyi][1]/3600.0
    
    #TODO: compare against each input file non-Nans
#    for imi in im_list
#        h0 = imhead(imi,mode='list')
#        ia.open(imi)
#        h1=ia.summary()
#        ia.close()
#        ??? = h0['...']
#        for xyi in np.arange(0,len(xylist),1):
#            if(... == np.nan):
#                ptgbool[xyi]=False
#        
#        
    #generate final J2000 deg pointings
    finalPtglist = []
    if outfile == None:
        for xyi in np.arange(0,len(xylist),1):
            if ptgbool[xyi] == True:
                strTemp = "J2000 " + str(round(ralist[xyi],6)) + "deg " + str(round(declist[xyi],6)) + "deg"
                finalPtglist.append(strTemp)
    else:
        n=0
        f= open(outfile,"w+")
        for xyi in np.arange(0,len(xylist),1):
            if ptgbool[xyi] == True:
                n=n+1
                strTemp = "J2000 " + str(round(ralist[xyi],6)) + "deg " + str(round(declist[xyi],6)) + "deg"
                f.write("%s\n" % strTemp)
                finalPtglist.append(strTemp)
        f.close()
        print "%d fields used in %s" % (n,outfile)
        
    return finalPtglist

    #-end of qac_im_ptg()

def qac_ms_ptg(msfile, outfile=None, uniq=True):
    """ get the ptg's from an MS into a list and/or ascii ptg file
    'J2000 19h00m00.00000 -030d00m00.000000',...
    This is a little trickier than it sounds, because the FIELD table has more entries than
    you will find in the FIELD_ID column (often central coordinate may be present as well,
    if it's not part of the observing fields, and locatations of the Tsys measurements
    For 7m data there may also be some jitter amongst each "field" (are multiple SB used?)

    Note that the actual POINTING table is empty for the 12m and 7m data

    The following unix pipe from a listobs.log file should also work

    cat ms.listobs | grep " none " | awk '{print $4,$5}' | sed 's/\([0-9]*\)\:\([0-9]*\):\([0-9.]*\) /\1h\2m\3 /' | sed 's/\([0-9][0-9]\)\.\([0-9][0-9]\)\.\([0-9][0-9]\)\./\1d\2m\3\./' | awk '{printf("J2000 %ss %ss\n",$1,$2)}' > ms.ptg

    # @todo: should get the observing frequency and antenna size, so we also know the PB size
    #
    # @todo: what if DELAY_DIR, PHASE_DIR and REFERENCE_DIR are not the same???
    
    """
    if uniq:
        tb.open('%s' % msfile)
        field_id = list(set(tb.getcol("FIELD_ID")))
        tb.close()
    #li = [a[i] for i in b]
    tb.open('%s/FIELD' % msfile)
    #col = 'DELAY_DIR'
    #col = 'PHASE_DIR'
    col = 'REFERENCE_DIR'
    # get all the RA/DEC fields
    ptr0 = tb.getcol(col)[0,0,:]
    ptr1 = tb.getcol(col)[1,0,:]
    n1 = len(ptr0)
    if uniq:
        # narrow this down to those present in the visibility data
        ptr0 = [ptr0[i] for i in field_id]
        ptr1 = [ptr1[i] for i in field_id]
    n2 = len(ptr0)
    print "%d/%d fields are actually used in %s" % (n2,n1,msfile)
    tb.close()
    #
    pointings = []
    for i in range(len(ptr0)):
        ra  = ptr0[i] * 180.0 / math.pi
        dec = ptr1[i] * 180.0 / math.pi
        if ra < 0:   # don't allow negative HMS
            ra = ra + 360.0
        ra_string = const.sixty_string(const.hms(ra),hms=True)
        dec_string = const.sixty_string(const.dms(dec),hms=False)
        pointings.append('J2000 %s %s' % (ra_string, dec_string))
    if outfile != None:
        fp = open(outfile,"w")
        for p in pointings:
            fp.write("%s\n" %p)
        fp.close()
    return pointings

    #-end of qac_ms_ptg()


def qac_line(im):
    """
    return the line parameters for an image in terms of a dictionary for tclean()
    """
    h0 = imhead(im,mode='list')
    ia.open(im)
    h1=ia.summary()
    ia.close()
    #
    crp = h0['crpix4']
    crv = h0['crval4']
    cde = h0['cdelt4']
    ref = h0['restfreq'][0]
    nchan = h0['shape'][3]
    restfreq = str(ref/1e9) + 'GHz'
    width = -cde/ref*cms/1000.0
    width = str(width) + 'km/s'
    start = (1-(crv - crp*cde)/ref)*cms/1000.0
    start = str(start) + 'km/s'
    return {'start' : start, 'width' : width, 'nchan' : nchan, 'restfreq' : restfreq}

def qac_ingest(tp, tpout = None, casaworkaround=[1,3], ms=None, ptg=None):
    """
    Check (and optionally correct) that a TP image is a valid input for TP2VIS.
    This is also meant as a workaround certain CASA features (see bugs.txt)

    Currently you will need CASA 5.0 or above. 

    Inputs:
    tp                Input TP image to check (required)
    tpout             Output TP image (optional)
    casaworkaround    List of issues to work around CASA problems
                       1   ensure we have RA-DEC-POL-FREQ
                       2   ensure we have Jy/pixel, else scale down from
                           Jy/beam (deprecated, now in tp2vis on the fly)
                       3   ensure it is a casa image, not a fits file
                      11   reverse the FREQ axis (needs to be same as MS)
    ms                Input MS to check sign of TP channels
                      This will automatically enable workaround #11 if
                      the signs different.
    ptg               not implemented

    NOTE: some of these options cannot yet be combined in one run of
    tp2vischeck(), you will need to run it multiple times.

    This function was formerly known as tp2vischeck()
    
    If no tpout given, the routine returns True/False if the TP image
    was correct

    TODO:  add gridding options like:  nchan=43,start='214km/s',width='1.0km/s'
           but we also need to understand the rounding issues we have before
           with this in terms of loosing a first or last channel

    """
    def casa_version_check(version='5.0.0'):
        cur = casa['build']['version'].split('.')
        req = version.split('.')
        print "qac:",cur,req
        if cur[0] >= req[0]: return
        if cur[1] >= req[1]: return
        if cur[2] >= req[2]: return
        print "WARNING: your CASA is outdated",cut,req
        
    def ms_sign(ms):
        if ms == None:
            return 0
        # if not iscasa(ms): return 0
        tb.open(ms + '/SPECTRAL_WINDOW')
        cw = tb.getcol('CHAN_WIDTH')
        print 'CHAN_WIDTH=',cw[0][0]
        tb.close()
        if cw[0][0] > 0:
            return 1
        elif cw[0][0] < 0:
            return -1
        print "WARNING: unexpected chan_width"
        return 0      # should never happen

    def im_sign(im):
        if not QAC.iscasa(im): return 0
        ia.open(im)
        h0 = ia.summary()
        aname = h0['axisnames']
        incr =  h0['incr']
        print "AXIS NAMES:",aname
        print "incr      :",incr
        ia.close()
        #
        df = None
        for i in range(len(aname)):
            if aname[i] == 'Frequency':
                # print "Frequency found along axis ",i
                df = incr[i]
                break
        if df == None:
            print "Warning: no freq axis found"
            return 0
        if df > 0:
            return 1
        elif df < 0:
            return -1
        print "WARNING: unexpected freq incr",df
        return 0
        
    # create a local copy of the list, so no multiple call side-effects !!!
    if type(casaworkaround) == list:
        cwa = list(casaworkaround)
    else:
        cwa = [casaworkaround]
    print "tp2vischeck: casaworkaround: ",cwa

    casa_version_check('5.0.0')

    # check sign of freq axis
    sign1 = ms_sign(ms)     # 0, 1 or -1
    sign2 = im_sign(tp)     # 0, 1 or -1
    if sign1*sign2 != 0 and sign1 != sign2:
        print "Adding workaround 11 for flip freq axis"
        cwa.append(11)

    # check if we have a fits file
    if not QAC.iscasa(tp) and not 3 in cwa:
        print "Converting fits file to casa image"
        cwa.append(3)
    elif 3 in cwa and QAC.iscasa(tp):
        print "Already have casa image"
        cwa.remove(3)

    if 3 in cwa:
        if tpout != None:
            importfits(tp,tpout,overwrite=True)
            print "Converted fits to casa image ",tpout
            print "Rerun tp2vischeck() to ensure no more fixed needed"
            return
        else:
            print "No output file given, expect things to fail now"

    if 1 in cwa or 11 in cwa:
        #  1: ensure we have a RA-DEC-POL-FREQ cube
        # 11: reverse the FREQ axis to align with TP image
        ia.open(tp)
        h0 = ia.summary()
        aname = h0['axisnames']
        print "AXIS NAMES:",aname
        if len(aname) == 3:
            # ia.adddegaxes(stokes='I')
            print "Cannot deal with 3D cubes yet - fix this code"
            ia.done()
            return
        order = None
        if aname[2] == 'Frequency':
            if 11 in cwa:
                order = '01-32'
            else:
                order = '0132'
        elif 11 in cwa:
            order = '012-3'
        if order != None:
            print "FIX: ia.transpose order=",order
                
        if tpout != None:
            if order != None:
                # on older CASA before 5.0 you will loose beam and object name (bugs.txt #017)
                os.system('rm -rf %s' % tpout)
                ia2 = ia.transpose(outfile=tpout,order=order)
                ia.done()
                ia2.done()
                print "Written transposed ",tpout
                print "Rerun tp2vischeck() to ensure no more fixed needed"                
                return
            else:
                ia.done()                
                print "WARNING: No transposed needed"
        else:
            if order != None:
                print "WARNING: axis ordering not correct, please provide output name"
                return

    if 2 in cwa:
        # ensure we have Jy/pixel
        s0 = imstat(tp)
        h0 = imhead(tp)
        if 'unit' in h0:
            print "UNIT: ",h0['unit']
        if 'flux' in s0:
            bof = s0['sum'][0] / s0['flux'][0]
            print "BOF = ",bof
            if tpout != None:
                os.system('rm -rf %s' % tpout)                
                expr = 'IM0/%g' % bof
                immath(tp,'evalexpr',tpout,expr)
                imhead(tpout,'del','beammajor')
                imhead(tpout,'put','bunit','Jy/pixel')
                print "Written rescaled ",tpout
                print "Rerun tp2vischeck() to ensure no more fixed needed"                
                return
            else:
                print "Warning: %s is not in the correct units for tp2vis. Provide output file name" % tp
        else:
            print "WARNING: No rescale fix needed"
        return

    # BUG 15
    # if sign of channel width in TP is not the same as that in MS, the TP needs to be
    # ran via imtrans(order='012-3')
    # could this be combined with the transpose() ?

    #-end of qac_ingest()
    
def qac_stats(image, test = None, eps=None, box=None, pb=None, pbcut=0.8, edge=False):
    """ summary of some stats in an image or measurement set
        in the latter case the flux is always reported as 0

        This routine can also be used for regression testing (see test=)

        image     image file name (CASA, FITS, MIRIAD)
        test      expected regression string
        eps       if given, it should parse the test string into numbers, each number
                  needs to be within relative error "eps", i.e. abs(v1-v2)/abs(v) < eps
        box       if used, this is the box for imstat()   box='xmin,ymin,xmax,ymax'
        pb        optional pb file, if the .image -> .pb would not work
        pbcut     only used for images, and a .pb should be parallel to the .image file
                  or else it will be skipped
        edge      take off an edge channel from either end (not implemented)

        Output should contain:   mean,rms,min,max,flux
    """
    def text2array(text):
        a = text.split()
        b = np.zeros(len(a))
        for i,ai in zip(range(len(a)),a):
            b[i] = float(ai)
        return b
    def arraydiff(a1,a2):
        delta = abs(a1-a2)
        idx = np.where(delta>0)
        return delta[idx]/a1[idx]
    def lel(name):
        """ convert filename to a safe filename for LEL expressions, e.g. in mask=
        """
        return '\'' + name + '\''
    
        
    if not QAC.iscasa(image):
        print "QAC_STATS: missing %s " % image
        return
    if QAC.iscasa(image + '/ANTENNA'):                      # assume it's a MS
        tb.open(image)
        data  = np.abs(tb.getcol('DATA')[0,:,:])  # first pol ->  data[nchan,nvis]
        mean = data.mean()
        rms  = data.std()
        min  = data.min()
        max  = data.max()
        flux = 0.0
        tb.close()
        del data
    else:                                    # assume it's an IM
        maskarea = None
        if pbcut != None:
            # this requires a .pb file to be parallel to the .image file
            if pb == None:
                pb = image[:image.rindex('.')] + '.pb'
                if QAC.iscasa(pb):
                    maskarea = lel(pb) + '>' + str(pbcut)      # create a LEL for the mask
            else:
                maskarea = lel(pb) + '>' + str(pbcut)
        if edge:
            nchan = imhead(image)['shape'][3]
            s0 = imstat(image,mask=maskarea,chans='1~%d' % (nchan-2),box=box)
        else:
            s0 = imstat(image,box=box,mask=maskarea)
        # mean, rms, min, max, flux
        # @TODO   this often fails
        mean = s0['mean'][0]
        rms  = s0['rms'][0]
        min  = s0['min'][0]
        max  = s0['max'][0]
        if 'flux' in s0:
            flux = s0['flux'][0]
        else:
            flux = s0['sum'][0]
    test_new = "%s %s %s %s %s" % (repr(mean),repr(rms),repr(min),repr(max),repr(flux))
    if test == None:
        test_out = ""
        report = False
    else:
        if eps == None:
            if test_new == test:
                test_out = "OK"
                report = False
            else:
                test_out = "FAILED regression"
                report = True
        else:
            v1 = text2array(test_new)
            v2 = text2array(test)
            delta = arraydiff(v1,v2)
            print delta
            if delta.max() < eps:
                test_out = "OK"
                report = False
            else:
                test_out = "FAILED regression delta=%g > %g" % (delta.max(),eps)
                report = True
    msg1 = "QAC_STATS: %s" % (image)
    print "%s %s %s" % (msg1,test_new,test_out)
    if report:
        fmt1 = '%%-%ds' % (len(msg1))
        msg2 = fmt1 % ' '
        print "%s %s EXPECTED" % (msg2,test)
    
    #-end of qac_stats()
    
def qac_beam(im, normalized=False, plot=None):
    """ some properties of the PSF

    im:           image representing the beam (usually a .psf file)
    normalized:   if True, axes are arcsec and normalized flux
    plot:         if set, this is the plot created, usually a png

    @todo   have an option to just print beam, no volume info
    """
    if not QAC.iscasa(im):
        print "QAC_BEAM: missing %s " % im
        return

    h0 = imhead(im)
    pix2 = abs(h0['incr'][0] * h0['incr'][1] * apr * apr)      # pixel**2 (in arcsec)
    if 'perplanebeams' in h0:
        bmaj = h0['perplanebeams']['beams']['*0']['*0']['major']['value']
        bmin = h0['perplanebeams']['beams']['*0']['*0']['minor']['value']
        pix  = sqrt(pix2)
        nppb =  bof * bmaj*bmin/pix2        
    elif 'restoringbeam' in h0:
        bmaj = h0['restoringbeam']['major']['value']
        bmin = h0['restoringbeam']['minor']['value']
        pix  = sqrt(pix2)        
        nppb =  bof * bmaj*bmin/pix2        
    else:
        bmaj = 1.0
        bmin = 1.0
        pix  = 1.0        
        nppb = 1.0

    if normalized:
        factor = nppb
    else:
        factor = 1.0
        pix    = 1.0

    print "QAC_BEAM: %s  %g %g %g %g %g" % (im,bmaj,bmin,pix,nppb,factor)

    xcen = h0['refpix'][0]
    ycen = h0['refpix'][1]
    nx = h0['shape'][0]
    ny = h0['shape'][1]
    nz = max(h0['shape'][2],h0['shape'][3])
    size = np.arange(nx/2-20)
    flux = 0.0 * size
    zero = flux * 0.0
    for i in size:
        box = '%d,%d,%d,%d' % (xcen-i,ycen-i,xcen+i,ycen+i)
        flux[i] = imstat(im,chans='0',box=box)['sum'][0]/factor
    print "QAC_BEAM: Max/Last/PeakLoc",flux.max(),flux[-1],flux.argmax()*pix
    
    if plot != None:
        plt.figure()
        if normalized:
            plt.title("%s : Normalized cumulative flux" % im)
            plt.xlabel("size/2 (arcsec)")
            plt.ylabel("Flux")
            size = size * sqrt(pix2)
        else:
            plt.title("%s : Cumulative sum" % im)
            plt.xlabel("size/2 (pixels)")
            plt.ylabel("Sum")
        plt.plot(size,flux)
        plt.plot(size,zero)
        plt.savefig(plot)
        plt.show()
    
    #-end of qac_beam()
    
    
def qac_getuv(ms, kwave=True):
    """ return the UV coordinates, in m or kilowaves

    ms       MS file, No default
    
    kwave    boolean, if true (u,v) in klambda, else in native meter
             Default:  True

    Usage:   (u,v) = qac_getuv('msfile',True)
    """
    tb.open(ms)
    uvw  = tb.getcol('UVW')
    tb.close()
    if kwave:
        tb.open(ms + '/SPECTRAL_WINDOW')
        chan_freq = tb.getcol('CHAN_FREQ')
        ref_freq = (chan_freq[0] + chan_freq[-1])/2.0
        factor = ref_freq / cms / 1000.0
        factor = factor[0]                  # assume/ignore polarization dependent issues
        tb.close()
    else:
        factor = 1.0

    print "UVW shape",uvw.shape,uvw[:,0],factor
    u = uvw[0,:] * factor                   # uvw are in m. we want m
    v = uvw[1,:] * factor                   # or klambda
    uvd = np.sqrt(u*u+v*v)
    print "UVD npts,min/max = ",len(uvd), uvd.min(), uvd.max()

    return (u,v)

    #-end of qac_getuv()
    
def qac_getamp(ms, record=0):
    """ return the AMP for each channel for the (0,0) spacings.
    It needs to sum for all fields where uv=(0,0)

    ms       MS file, No default
    
    Usage:   amp = qac_getamp('msfile')
    """
    tb.open(ms)
    uvw  = tb.getcol('UVW')[0:2,:]               # uvw[2,nvis]
    idx = np.where( np.abs(uvw).min(axis=0) == 0 )[0]

    data  = tb.getcol('DATA')[0,:,idx]      # getcol() returns  [npol,nchan,nvis]
                                            # but with idx it returns [nvisidx,nchan]
    amp = np.abs(data.max(axis=0))          # strongest field
    amp = np.abs(data.sum(axis=0))/2.0      # sum for all fields (but they overlap, so guess 2.0)
    tb.close()
    return amp

    #-end of qac_getamp()
    
def qac_flag1(ms1, ms2):
    """
    niche flagger:    flag all data in ms2 that have no field in ms1.
    in the end.... useless.

    """
    def dist(x1,y1,x2,y2):
        d = (x1-x2)**2 + (y1-y2)**2
        return np.sqrt(d)
        
    tb.open("%s/FIELD" % ms1)
    field1 = tb.getcol("REFERENCE_DIR")
    tb.close()
    #
    tb.open("%s/FIELD" % ms2)
    field2 = tb.getcol("REFERENCE_DIR")
    tb.close()
    #
    print "FIELD1",field1
    print "FIELD2",field2
    x1 = field1[0][0]
    y1 = field1[1][0]
    x2 = field2[0][0]
    y2 = field2[1][0]

    n1 = len(field1[0][0])
    n2 = len(field2[0][0])
    print "Found %d in MS1, %d in MS2" % (n1,n2)
    # ensure n1 > n2
    mask = np.zeros(n1)
    eps = 0.001
    for i1 in range(n1):
        dmin = 999
        for i2 in range(n2):
            d = dist(x1[i1],y1[i1],x2[i2],y2[i2])
            if d < dmin:
                dmin = d
        if dmin < eps:  mask[i] = 1.0
        print "DMIN %d %f %d" % (i1,dmin,int(mask[i1]))

    print "MASK",mask
    print "SUM:",mask.sum()
    
    #-end of qac_flag1()
    
def qac_alma(project, skymodel, imsize=512, pixel=0.5, phasecenter=None, cycle=5, cfg=0, niter=-1, ptg = None):
    """
    helper function to create an MS from a skymodel for a given ALMA configuration


    project     - name (one directory deep) to which files are accumulated
    
    See CASA/data/alma/simmos/ for the allowed (cycle,cfg) pairs

    cycle 1:   ALMA cfg = 1..6    ACA ok
    cycle 2:   ALMA cfg = 1..7    ACA bleeh ('i' and 'ns')
    cycle 3:   ALMA cfg = 1..8    ACA ok
    cycle 4:   ALMA cfg = 1..9    ACA ok
    cycle 5:   ALMA cfg = 1..10   ACA ok [same as 4]
    """

    # since we call it incrementally, make sure directory exists
    os.system('mkdir -p %s' % project)
    
    
    data_dir = casa['dirs']['data']                  # data_dir + '/alma/simmos' is the default location for simobserve
    if cfg==0:
        cfg = 'aca.cycle%d' % (cycle)                # cfg=0 means ACA (7m)
    else:
        cfg = 'alma.cycle%d.%d' % (cycle,cfg)        # cfg>1 means ALMA (12m)

    print "CFG: ",cfg


    # for tclean (only used if niter>=0)
    imsize    = QAC.imsize2(imsize)
    cell      = ['%garcsec' % pixel]
    outms     = '%s/%s.%s.ms'  % (project,project,cfg)
    outms2    = '%s/%s.%s.ms2' % (project,project,cfg)       # debug
    outim     = '%s/dirtymap' % (project)
    do_fits   = False          # output fits when you clean?


    if ptg != None:
        setpointings = False
        ptgfile      = ptg
    # obsmode     = "int"
    antennalist = "%s.cfg" % cfg     # can this be a list?

    totaltime   = "28800s"     # 4 hours  (should be multiple of 2400 ?)
    integration = "30s"        # prevent too many samples for MS

    thermalnoise= ""
    verbose     = True
    overwrite   = True
    graphics    = "file"       # "both" would do "screen" as well
    user_pwv    = 0.0

    # we allow accumulation now ..
    # ...make sure old directory is gone
    # ...os.system("rm -rf %s" % project)

    if ptg == None:
        simobserve(project, skymodel,
               integration=integration,
               totaltime=totaltime,
               antennalist=antennalist,
               verbose=verbose, overwrite=overwrite,
               user_pwv = 0.0, thermalnoise= "")
    else:
        simobserve(project, skymodel,
               setpointings=False, ptgfile=ptgfile,
               integration=integration,
               totaltime=totaltime,
               antennalist=antennalist,
               verbose=verbose, overwrite=overwrite,                   
               user_pwv = 0.0, thermalnoise= "")

    if True:
        # there appears to be also something wrong with the POINTING table via simobserve
        print "CONCAT: removing POINTING table into ",outms2
        concat(outms,outms2,copypointing=False)

    if niter >= 0:
        cmd1 = 'rm -rf %s.*' % outim
        os.system(cmd1)
        tclean(vis=outms,
               imagename=outim,
               niter=niter,
               gridder='mosaic',
               imsize=imsize,
               cell=cell,
               restoringbeam  = restoringbeam,
               stokes='I',
               pbcor=True,
               phasecenter=phasecenter,
               weighting='natural',
               specmode='cube')
        qac_stats(outim + '.image')
        if do_fits:
            exportfits(outim+'.image',outim+'.fits')

    return outms
    #-end of qac_alma()

def qac_tpdish(name, size):
    """
    A patch to work with dishes that are not 12m (currently hardcoded in tp2vis.py)

    E.g. for GBT (a 100m dish) you would need to do:

    qac_tpdish('ALMATP',100.0)
    qac_tpdish('VIRTUAL',100.0)
    """
    old_size = t2v_arrays[name]['dish']
    old_fwhm = t2v_arrays[name]['fwhm100']
    r = size/old_size
    t2v_arrays[name]['dish']   = size
    t2v_arrays[name]['fwhm100']= old_fwhm / r
    print "QAC_DISH: ",old_size, old_fwhm, ' -> ', size, old_fwhm/r
    
 
def qac_tp(project, imagename, ptg=None, imsize=512, pixel=1.0, niter=-1, phasecenter=None, rms=None, maxuv=10.0, nvgrp=4, fix=1, deconv=True, **line):
           
    """
      Simple frontend to call tp2vis() and an optional tclean()
    
    
      _required_keywords:
      ===================
      project:       identifying (one level deep directory) name within which all files are places
      imagename:     casa image in RA-DEC-POL-FREQ order
      ptg            Filename with pointings (ptg format) to be used
                     If none specified, it will currently return, but there may be a
                     plan to allow auto-filling the (valid) map with pointings.
    
    
      _optional_keywords:
      ===================
      imsize:        if maps are made, this is mapsize (list of 2 is allowed if you need rectangular)
      pixel:         pixel size, in arcsec
      niter:         -1 if no maps needed, 0 if just fft, no cleaning cycles
    
      phasecenter    Defaults to mapcenter (note special format)
                     e.g. 'J2000 00h48m15.849s -73d05m0.158s'
      rms            if set, this is the TP cube noise to be used to set the weights
      maxuv          maximum uv distance of TP vis distribution (in m)  [10m] 
      nvgrp          Number of visibility group (nvis = 1035*nvgrp)
      fix            Various fixes such that tclean() can handle a list of ms.
                     ** this parameter will disappear or should have default 1
                     0   no fix, you need to run mstransform()/concat() on the tp.ms
                     1   output only the CORRECTED_DATA column, remove other *DATA*
                     2   debug mode, keep all intermediate MS files
                     @todo   there is a flux difference between fix=0 and fix=1 in dirtymap
      deconv         Use the deconvolved map as model for the simulator

      line           Dictionary of tclean() parameters
    """
    # assert input files
    QAC.assertf(imagename)
    QAC.assertf(ptg)    
    
    # clean up old project
    os.system('rm -rf %s ; mkdir -p %s' % (project,project))

    # report phasecenter in a proper phasecenter format (tp2vis used to do that)
    if True:
        h0=imhead(imagename,mode='list')
        ra  = h0['crval1'] * 180.0 / math.pi
        dec = h0['crval2'] * 180.0 / math.pi
        ra_string  = const.sixty_string(const.hms(ra),hms=True)
        dec_string = const.sixty_string(const.dms(dec),hms=False)
        phasecenter0 = 'J2000 %s %s' % (ra_string, dec_string)
        print "MAP REFERENCE: phasecenter = '%s'" % phasecenter0
        if phasecenter == None:
            phasecenter == phasecenter0

    if ptg == None:
        print "No PTG specified, no auto-regioning yet"
        return None

    outfile = '%s/tp.ms' % project
    tp2vis(imagename,outfile,ptg, maxuv=maxuv, rms=rms, nvgrp=nvgrp, deconv=deconv)

    vptable = outfile + '/TP2VISVP'    
    if QAC.iscasa(vptable):                   # note: current does not have a Type/SubType
        print "Note: using TP2VISVP, and attempting to use vp from ",vptable
        use_vp = True
        vp.reset()
        vp.loadfromtable(vptable)        # Kumar says this doesn't work, you need the vptable= in tclean()
    else:
        print "Note: did not find TP2VISVP, not using vp"
        use_vp = False
        vptable = None
    vp.summarizevps()

    # remove DATA_* columns to prevent tclean with mslist crash
    # for more stability (some combinations caused tclean() to fail) use concat(copypointing=False)
    # with fix_mode
    #          0 = do nothing (will need do_concat=True)
    #          1 = one fixed tp.ms file
    #          2 = tp.mp, tp1.ms and tp2.ms for experimenting
    fix_mode = fix
    
    if fix_mode == 1:    # should be the default
        print "FIX with mstransform and concat for CORRECTED_DATA" 
        outfile1 = '%s/tp1.ms' % project    
        mstransform(outfile,outfile1)
        os.system('rm -rf %s' % outfile)
        concat(outfile1,outfile,copypointing=False)
        os.system('rm -rf %s' % outfile1)

    if fix_mode == 2:
        print "FIX with mstransform and concat and for CORRECTED_DATA keeping backups"
        outfile1 = '%s/tp1.ms' % project    
        outfile2 = '%s/tp2.ms' % project
        outfile3 = '%s/tp3.ms' % project    
        mstransform(outfile,outfile1)
        concat(outfile1,outfile2,copypointing=False)
        concat(outfile1,outfile3)
        #   @todo  so far, simple removal of the POINTING table is not working right:
        if False:
            # this remove the POINTING file, tclean() cannot handle it 
            tb.open(outfile3,nomodify=False)
            tb.removekeyword('POINTING')
            tb.flush()
            tb.close()
        if False:
            # this seems to remove columns, but table still thinks it has entries, and thus tclean() fails again
            tb.open(outfile3 + '/POINTING',nomodify=False)
            tb.removecols(tb.colnames())    # @todo    CASA documentation is not giving the right example
            tb.flush()
            tb.close()
        # removecols removekeyword removecolkeyword

    if False:
        # Plot UV
        figfile = outfile + ".png"
        print "PLOTUV ",figfile                                                            
        plotuv(outfile,figfile=figfile)

    if niter < 0 or imsize < 0:
        return outfile

    # finalize by making a tclean()

    print "Final test clean around phasecenter = '%s'" % phasecenter
    dirtymap = '%s/dirtymap' % project
    imsize    = QAC.imsize2(imsize)
    cell      = ['%garcsec' % pixel]
    weighting = 'natural'

    tclean(vis = outfile,
           imagename      = dirtymap,
           niter          = niter,
           gridder        = 'mosaic',
           imsize         = imsize,
           cell           = cell,
           restoringbeam  = restoringbeam,           
           stokes         = 'I',
           pbcor          = True,
           phasecenter    = phasecenter,
           vptable        = vptable,
           weighting      = weighting,
           specmode       = 'cube',
           **line)
    
    exportfits(dirtymap + ".image", dirtymap + ".fits")

    return outfile

    #-end of qac_tp()


def qac_clean1(project, ms, imsize=512, pixel=0.5, niter=0, weighting="natural", phasecenter="",  **line):
    """
    Simple interface to do a tclean() on one MS
    
    project - new directory for this  (it is removed before starting)
    ms      - a single MS (or a list, but no concat() is done)

    imsize       512  (list of 2 is allowed if you need rectangular)
    pixel        0.5
    niter        0 or more ; @todo   can also be a list, in which case tclean() will be returning results for each niter
    weighting    "natural"
    phasecenter  ""     (e.g. 'J2000 03h28m58.6s +31d17m05.8s')
    **line
    """
    os.system('rm -rf %s; mkdir -p %s' % (project,project))
    #
    outim1 = '%s/dirtymap' % project
    #
    imsize    = QAC.imsize2(imsize)
    cell      = ['%garcsec' % pixel]
    # weighting = 'natural'
    # weighting = 'uniform'
    #
    vis1 = ms
    #
    if True:
        try:
            tb.open(ms + '/SPECTRAL_WINDOW')
            chan_freq = tb.getcol('CHAN_FREQ')
            tb.close()
            tb.open(ms + '/SOURCE')
            ref_freq = tb.getcol('REST_FREQUENCY')
            tb.close()
            print 'FREQ:',chan_freq[0][0]/1e9,chan_freq[-1][0]/1e9,ref_freq[0][0]/1e9
        except:
            print "Bypassing some error displaying freq ranges"

    print "VIS1",vis1
    print "niter=",niter
    if type(niter) == type([]):
        niters = niter
    else:
        niters = [niter]

    if type(ms) != type([]):
        vptable = ms + '/TP2VISVP'
        if QAC.iscasa(vptable):                   # note: current does not have a Type/SubType
            print "Note: using TP2VISVP, and attempting to use vp from",vptable
            use_vp = True
            vp.reset()
            vp.loadfromtable(vptable)
        else:
            print "Note: did not find TP2VISVP, not using vp"
            use_vp = False
            vptable = None
        vp.summarizevps()
    else:
        use_vp = False        
        vptable = None

    restart = True
    for niter in niters:
        print "TCLEAN(niter=%d)" % niter
        tclean(vis             = vis1,
               imagename       = outim1,
               niter           = niter,
               gridder         = 'mosaic',
               imsize          = imsize,
               cell            = cell,
               restoringbeam   = restoringbeam,           
               stokes          = 'I',
               pbcor           = True,
               phasecenter     = phasecenter,
               vptable         = vptable,
               weighting       = weighting,
               specmode        = 'cube',
               restart         = restart,
               **line)
        restart = False
    
    print "Wrote %s with %s weighting" % (outim1,weighting)

    if len(niters) == 1:
        exportfits(outim1+'.image',outim1+'.fits')
    
    #-end of qac_clean1()
    
def qac_clean(project, tp, ms, imsize=512, pixel=0.5, weighting="natural", phasecenter="", niter=0, do_concat = False, do_alma = False, do_cleanup = True, **line):
    """
    Simple interface to do a tclean() joint deconvolution of one TP and one or more MS
    
    project - new directory for this operation (it is removed before starting)
    tp      - the TP MS (needs to be a single MS)
    ms      - the array MS (can be a list of MS)
    imsize  - (square) size of the maps (list of 2 is allowed if you need rectangular)
    pixel   - pixelsize in arcsec
    niter   - 0 or more interactions for tclean

    do_concat   - work around a bug in tclean ?  Default is true until this bug is fixed
    do_alma     - also make a map from just the ms (without tp)
    """
    os.system('rm -rf %s; mkdir -p %s' % (project,project))
    #
    outim1 = '%s/alma' % project
    outim2 = '%s/tpalma' % project
    outms  = '%s/tpalma.ms' % project       # concat MS to bypass tclean() bug
    #
    imsize    = QAC.imsize2(imsize)
    cell      = ['%garcsec' % pixel]
    # weighting = 'natural'
    # weighting = 'uniform'    
    #
    vis1 = ms
    if type(ms) == type([]):
        vis2 =  ms  + [tp] 
    else:
        vis2 = [ms] + [tp] 
    # @todo    get the weights[0] and print them
    # vis2.reverse()         # for debugging; in 5.0 it seems to be sort of ok,but small diffs can still be seen
    print "niter=",niter
    print "line: ",line
    #
    if type(niter) == type([]):
        niters = niter
    else:
        niters = [niter]
    #
    if do_alma:
        print "Creating ALMA using vis1=",vis1
        tclean(vis = vis1,
               imagename      = outim1,
               niter          = niters[0],
               gridder        = 'mosaic',
               imsize         = imsize,
               cell           = cell,
               restoringbeam  = restoringbeam,               
               stokes         = 'I',
               pbcor          = True,
               phasecenter    = phasecenter,
               vptable        = None,
               weighting      = weighting,
               specmode       = 'cube',
               **line)
        print "Wrote %s with %s weighting" % (outim1,weighting)        
    else:
        print "Skipping pure ALMA using vis1=",vis1        

    print "Creating TPALMA using vis2=",vis2
    if do_concat:
        # first report weight 
        print "Weights in ",vis2
        for v in vis2:
            tp2viswt(v)
        # due to a tclean() bug, the vis2 need to be run via concat
        # MS has a pointing table, this often complaints, but in workflow5 it actually crashes concat()
        print "Using concat to bypass tclean bug - also using copypointing=False, freqtol='10kHz'"
        #concat(vis=vis2,concatvis=outms,copypointing=False,freqtol='10kHz')
        concat(vis=vis2,concatvis=outms,copypointing=False)
        vis2 = outms

    restart = True
    for niter in niters:
        print "TCLEAN(niter=%d)" % niter        
        tclean(vis=vis2,
               imagename      = outim2,
               niter          = niter,
               gridder        = 'mosaic',
               imsize         = imsize,
               cell           = cell,
               restoringbeam  = restoringbeam,           
               stokes         = 'I',
               pbcor          = True,
               phasecenter    = phasecenter,
               vptable        = None,
               weighting      = weighting,
               specmode       = 'cube',
               restart        = restart,
               **line)
        restart = False

#          phasecenter=phasecenter,weighting='briggs',robust=-2.0,threshold='0mJy',specmode='cube')

    print "Wrote %s with %s weighting" % (outim2,weighting)

    if do_alma:
        exportfits(outim1+'.image',outim1+'.fits')
    if len(niters) == 1:
        exportfits(outim2+'.image',outim2+'.fits')

    if do_concat and do_cleanup:
        print "Removing ",outms
        shutil.rmtree(outms)
    
    #-end of qac_clean()
    
def qac_summary(tp, ms=None, source=None, line=False):
    """
    Summarize what could be useful to understand how to combine a TP map with one or more MS files
    and how to call mstransform()

    tp      - one image cube (casa image, or fits file)
    ms      - MS, or a list of MS
    source  - if given, it needs to match this source name in the MS
    """

    def vrange(f,rf):
        nf = len(f)
        if rf > 0:
            v0 = (1-f[0]/rf)*cms/1000.0
            v1 = (1-f[-1]/rf)*cms/1000.0
            dv = (v1-v0)/(nf-1.0)
        else:
            v0 = 0.0
            v1 = 0.0
            dv = 0.0
        return f[0],f[-1],rf,v0,v1,dv,nf

    if type(ms) == type([]):
        ms_list = ms
    elif ms == None:
        ms_list = []
    else:
        ms_list = [ms]

    # ONE IMAGE
    h0=imhead(tp,mode='list')
    ia.open(tp)
    shape = ia.shape()
    h1 = ia.summary()
    iz = h1['axisnames'].tolist().index('Frequency')     # axis # for freq
    ia.close()
    #
    restfreq = h0['restfreq']    
    ra  = h0['crval1'] * 180.0 / math.pi
    dec = h0['crval2'] * 180.0 / math.pi
    phasecenterd = 'J2000 %.6fdeg %.6fdeg' % (ra,dec)
    ra_string  = const.sixty_string(const.hms(ra),hms=True)
    dec_string = const.sixty_string(const.dms(dec),hms=False)
    phasecenter = 'J2000 %s %s' % (ra_string, dec_string)
    nx = h0['shape'][0]
    ny = h0['shape'][1]
    nz = h0['shape'][iz]
    dx = np.abs(h0['cdelt1']) # in radians!
    dy = np.abs(h0['cdelt2'])
    du = 1.0/(nx*dx)
    dv = 1.0/(ny*dy)
    # freq_values = h0['crval4'] + (np.arange(nz) - h0['crpix4']) * h0['cdelt4']
    # freq_values.reshape(1,1,1,nz)
    freq_values = h1['refval'][iz] + (np.arange(nz) - h1['refpix'][iz]) * h1['incr'][iz]
    vmin = (1-freq_values[0]/restfreq)*cms/1000.0
    vmax = (1-freq_values[-1]/restfreq)*cms/1000.0
    dv   = (vmax[0]-vmin[0])/(nz-1)
    rft = h0['reffreqtype']

    if line:
        _line = {}
        _line['restfreq'] = '%sGHz'  % repr(restfreq[0]/1e9)
        _line['nchan']    =  nz
        _line['start']    = '%skm/s' % repr(vmin[0])
        _line['width']    = '%skm/s' % repr(dv)
        return _line

    # print the image info
    print "QAC_SUMMARY:"
    print "TP:",tp
    print 'OBJECT:  ',h0['object']
    print 'SHAPE:   ',h0['shape']
    print 'CRVAL:   ',phasecenter
    print 'CRVALd:  ',phasecenterd
    print 'RESTFREQ:',restfreq[0]/1e9
    print "FREQ:    ",freq_values[0]/1e9,freq_values[-1]/1e9
    print "VEL:     ",vmin[0],vmax[0],dv
    print "VELTYPE: ",rft
    print "UNITS:   ",h0['bunit']
    
    # LIST OF MS (can be empty)
    for msi in ms_list:
        print ""
        if QAC.iscasa(msi):
            print "MS: ",msi
        else:
            print "MS:   -- skipping non-existent ",msi
            continue

        # first get the rest_freq per source (it may be missing)
        tb.open(msi + '/SOURCE')
        source  = tb.getcol('NAME')
        nsource = len(source)
        try:
            rest_freq = tb.getcol('REST_FREQUENCY')/1e9
        except:
            rest_freq = np.array([[0.0]])
        spw_id    = tb.getcol('SPECTRAL_WINDOW_ID')
        tb.close()
        # print "rest_freq",rest_freq.shape,rest_freq
        
        # special treatment for spw, since each spw can have a different # channels (CHAN_FREQ)
        tb.open(msi + '/SPECTRAL_WINDOW')
        ref_freq = tb.getcol('REF_FREQUENCY')/1e9
        # print "ref_freq",ref_freq.shape,ref_freq

        chan_freq = []
        nspw = len(ref_freq)
        for i in range(nspw):
            chan_freq_i = tb.getcell('CHAN_FREQ',i)/1e9
            # print "spw",i,vrange(chan_freq_i,ref_freq[i])
            chan_freq.append(chan_freq_i)
        tb.close()
        #
        for i in range(nsource):
            # print "source",i,source[i],spw_id[i],rest_freq[0][i]
            # print "source",i,source[i],trans[0][i],vrange(chan_freq[spw_id[i]],rest_freq[0][i])
            print "source",i,source[i],vrange(chan_freq[spw_id[i]],rest_freq[0][i])            

        
        #print "chan_freq",chan_freq.shape,chan_freq
        # print 'FREQ:',chan_freq[0][0]/1e9,chan_freq[-1][0]/1e9,ref_freq[0][0]/1e9

    #-end of qac_summary()

def qac_mom(imcube, chan_rms, pb=None, pbcut=0.3):
    """
    Take mom0 and mom1 of an image cube, in the style of the M100 casaguide.
    
    imcube:      image cube (flux flat, i.e. the .image file)
    chan_rms:    list of 4 integers, which denote the low and high channel range where RMS should be measured
    pb:          primary beam. If given, it can do a final pb corrected version and use it for masking
    pbcut:       if PB is used, this is the cutoff above which mask is used
    
    """
    def lel(name):
        """ convert filename to a safe filename for LEL expressions, e.g. in mask=
        """
        return '\'' + name + '\''
    chans1='%d~%d' % (chan_rms[0],chan_rms[1])
    chans2='%d~%d' % (chan_rms[2],chan_rms[3])
    chans3='%d~%d' % (chan_rms[1]+1,chan_rms[2])
    rms  = imstat(imcube,axes=[0,1])['rms']
    print rms
    rms1 = imstat(imcube,axes=[0,1],chans=chans1)['rms'].mean()
    rms2 = imstat(imcube,axes=[0,1],chans=chans2)['rms'].mean()
    print rms1,rms2
    rms = 0.5*(rms1+rms2)
    print "RMS = ",rms
    if pb==None:
        mask = None
    else:
        mask = lel(pb) + '> %g' % pbcut
        print "Using mask=",mask
    mom0 = imcube + '.mom0'
    mom1 = imcube + '.mom1'
    os.system('rm -rf %s %s' % (mom0,mom1))
    immoments(imcube, 0, chans=chans3, includepix=[rms*2.0,9999], mask=mask, outfile=mom0)
    immoments(imcube, 1, chans=chans3, includepix=[rms*5.5,9999], mask=mask, outfile=mom1)

def qac_math(outfile, infile1, oper, infile2):
    """  just simpler to read....
    """
    qac_tag("math")
    if not QAC.exists(infile1) or not QAC.exists(infile2):
        print "QAC_MATH: missing %s and/or %s" % (infile1,infile2)
        return
    
    if oper=='+':  expr = 'IM0+IM1'
    if oper=='-':  expr = 'IM0-IM1'
    if oper=='*':  expr = 'IM0*IM1'
    if oper=='/':  expr = 'IM0/IM1'
    os.system("rm -rf %s" % outfile)
    immath([infile1,infile2],'evalexpr',outfile,expr)

    #-end of qac_math()
    
def qac_plot(image, channel=0, box=None, range=None, plot=None):
    #
    # zoom={'channel':23,'blc': [200,200], 'trc': [600,600]},
    #'range': [-0.3,25.],'scaling': -1.3,
    if plot==None:
        out = image+'.png'
    else:
        out = plot
    raster =[{'file': image,  'colorwedge' : True}]    # scaling (numeric), colormap (string)
    if range != None:
        raster[0]['range'] = range
    else:
        h0 = imstat(image,chans='%d' % channel)
        print "%s: data range=[%g,%g]" % (image,h0['min'][0],h0['max'][0])
    zoom={'channel' : channel,
          'coord':'pixel'}      # @todo 'blc': [190,150],'trc': [650,610]}
    if box != None:
        zoom['blc'] = box[0:2]
        zoom['trc'] = box[2:4]

    imview(raster=raster, zoom=zoom, out=out)

    #-end of qac_plot()
    
def qac_mom(imcube, chan_rms, pb=None, pbcut=0.3):
    """
    Take mom0 and mom1 of an image cube, in the style of the M100 casaguide.
    
    imcube:      image cube (flux flat, i.e. the .image file)
    chan_rms:    list of 4 integers, which denote the low and high channel range where RMS should be measured
    pb:          primary beam. If given, it can do a final pb corrected version and use it for masking
    pbcut:       if PB is used, this is the cutoff above which mask is used
    
    """
    qac_tag("mom")
    
    def lel(name):
        """ convert filename to a safe filename for LEL expressions, e.g. in mask=
        """
        return '\'' + name + '\''
    chans1='%d~%d' % (chan_rms[0],chan_rms[1])
    chans2='%d~%d' % (chan_rms[2],chan_rms[3])
    chans3='%d~%d' % (chan_rms[1]+1,chan_rms[2])
    rms  = imstat(imcube,axes=[0,1])['rms']
    print rms
    rms1 = imstat(imcube,axes=[0,1],chans=chans1)['rms'].mean()
    rms2 = imstat(imcube,axes=[0,1],chans=chans2)['rms'].mean()
    print rms1,rms2
    rms = 0.5*(rms1+rms2)
    print "RMS = ",rms
    if pb==None:
        mask = None
    else:
        mask = lel(pb) + '> %g' % pbcut
        print "Using mask=",mask
    mom0 = imcube + '.mom0'
    mom1 = imcube + '.mom1'
    os.system('rm -rf %s %s' % (mom0,mom1))
    immoments(imcube, 0, chans=chans3, includepix=[rms*2.0,9999], mask=mask, outfile=mom0)
    immoments(imcube, 1, chans=chans3, includepix=[rms*5.5,9999], mask=mask, outfile=mom1)

    #-end of qac_mom()

def qac_flux(image, box=None, dv = 1.0, plot='qac_flux.png'):
    """ Plotting min,max,rms as function of channel
    
        box     xmin,ymin,xmax,ymax       defaults to whole area

        A useful way to check the the mean RMS at the first
        or last 10 channels is:

        imstat(image,axes=[0,1])['rms'][:10].mean()
        imstat(image,axes=[0,1])['rms'][-10:].mean()
    
    """
    qac_tag("flux")
    
    plt.figure()
    _tmp = imstat(image,axes=[0,1],box=box)
    fmin = _tmp['min']
    fmax = _tmp['max']
    frms = _tmp['rms']
    chan = np.arange(len(fmin))
    f = 0.5 * (fmax - fmin) / frms
    plt.plot(chan,fmin,c='r',label='min')
    plt.plot(chan,fmax,c='g',label='max')
    plt.plot(chan,frms,c='b',label='rms')
    # plt.plot(chan,f,   c='black', label='<peak>/rms')
    zero = 0.0 * frms
    plt.plot(chan,zero,c='black')
    plt.ylabel('Flux')
    plt.xlabel('Channel')
    plt.title('%s  Min/Max/RMS' % (image))
    plt.legend()
    plt.savefig(plot)
    plt.show()
    print "Sum: %g Jy km/s (%g km/s)" % (fmax.sum() * dv, dv)

    #-end of qac_flux()

def qac_psd(image, plot='qac_psd.png'):
    """ compute the PSD of a map
    """
    fd = fits.getdata(image).squeeze()     # this has to be a 2D image
    f1 = np.fft.fft2(fd)
    f2 = np.np.fftshift(f2)
    psd2 = np.abs(f2)**2
    psd1 = radialProfile.azimuthalAverage(psd2)
    rad1 = np.arange(1.0,len(psd1)+1)
    
    plt.figure()
    plt.loglog(rad1,psd1)
    plt.xlabel('Spatial Frequency')
    plt.ylabel('Power Spectrum')
    plt.xlabel('Channel')
    plt.title('%s' % (image))
    plt.savefig(plot)
    plt.show()
    
    return psd1
    
        
def qac_combine(project, TPdata, INTdata, **kwargs):
    """
    Wishful Function to combine total power and interferometry data.

    The current implementation requires you to use the same gridding for likewise axes.

    project : project directory within which all work will be done. See below for a
              description of names of datasets.

    TPdata :  input one (or list) of datasets representing TP data.
              These will be (CASA or FITS) images.

    INTdata : input one (or list) of datasets represenring interferometry data.
              These can either be (FITS or CASA) images, or measurement sets (but no mix).
              Depending on which type, different methods can be exposed.

    mode :    non-zero if you want to try to enforce mode of combining data.   0 = automated.
    

    **kwargs : python dictionary of {key:value} pairs which depends on the method choosen.

    If INTdata is an image, the following modes are available:
        11. CASA's feather() tool will be used. [default for mode=0]
        12. Faridani's SSC will be used.
    If INTdata is a measurement set, imaging parameters for tclean() will be needed.
        21. TP2VIS will be used. [default for mode=0]
        22. SD2VIS will be used.



    """

    print "you just wished this would work...."

    if False:
        os.system('rm -rf %s; mkdir -p %s' % (project,project))    
    
    if type(TPdata) == type([]):
        _TP_data = TPdata
    else:
        _TP_data = [TPdata]        

    if type(INTdata) == type([]):
        _INT_data = INTdata
    else:
        _INT_data = [INTdata]        
        
def qac_argv(sysargv):
    """
    safe argument parser from CASA, removing the CASA dependant ones, including the script name
    
    Typical usage:

         import sys

         for arg in qac_argv(sys.argv):
         exec(arg)

    """
    return sysargv[3:]

def qac_initkeys(keys, argv=[]):
    QAC.keys = {}
    for k in keys.keys():
        QAC.keys[k] = keys[k]
    for kv in argv[3:]:
        i = kv.find('=')
        if i > 0:
            # @todo isn't there a better pythonic way to do this?
            cmd='QAC.keys["%s"]=%s' % (kv[:i], kv[i+1:])
            exec(cmd)
        
def qac_getkey(key):
    return QAC.keys[key]



def qac_begin(label="ngvla"):
    """
    Every script should start with qac_begin() if you want to use the logger
    and/or Dtime output for performance testing

    See also qac_tag() and qac_end()
    """
    if False:
        # @todo until the logging + print problem solved, this is disabled
        logging.basicConfig(level = logging.INFO)
        root_logger = logging.getLogger()
        print 'root_logger =', root_logger
        print 'handlers:', root_logger.handlers
        handler = root_logger.handlers[0]
        print 'handler stream:', handler.stream
        import sys
        print 'sys.stderr:', sys.stderr
        NG.dt = Dtime(label)

def qac_tag(label):
    """
    Dtime.tag()
    
    See also qac_begin()
    """
    if QAC.hasdt(): 
        QAC.dt.tag(label)

def qac_end():
    """
    Dtime.end()
    
    See also qac_begin()
    """
    if QAC.hasdt(): 
        QAC.dt.tag("done")
        QAC.dt.end()
        
    

class QAC(object):
    """ Static class to hide some local helper functions

        rmcasa
        iscasa
        casa2np
        imsize2
        assertf
    
    """
    @staticmethod
    def hasdt():
        if dir(QAC).count('dt') == 0: return False
        return True
        
    @staticmethod
    def exists(filename):
        return os.path.exists(filename)
    
    @staticmethod
    def rmcasa(filename):
        if QAC.iscasa(filename):
            os.system('rm -rf %s' % filename)
        else:
            print "Warning: %s is not a CASA dataset" % filename

    @staticmethod
    def iscasa(filename, casatype=None):
        """is a file a casa image
        
        casatype not implemented yet
        (why) isn't there a CASA function for this?
        
        Returns
        -------
        boolean
        """
        isdir = os.path.isdir(filename)
        if casatype == None:
            return isdir
        if not isdir:
            return False
        # ms + '/table.info' is an ascii file , first line should be
        # Type = Image
        # Type = Measurement Set

        # @todo for now
        return False

    @staticmethod    
    def casa2np(image, z=None):
        """
        convert a casa[x][y] to a numpy[y][x] such that fits writers
        will produce a fits file that looks like an RA-DEC image
        and also native matplotlib routines, such that imshow(origin='lower')
        will give the correct orientation.

        z      which plane to pick in case it's a cube (not implemented)
        """
        return np.flipud(np.rot90(image))

    @staticmethod    
    def imsize2(imsize):
        """ if scalar, convert to list, else just return the list
        """
        if type(imsize) == type([]):
            return imsize
        return [imsize,imsize]

    @staticmethod
    def iarray(array):
        """
        """
        return map(int,array.split(','))

    @staticmethod
    def farray(array):
        """
        """
        return map(float,array.split(','))
    
    @staticmethod
    def assertf(filename = None):
        """ ensure a file or directory exists, else report and and fail
        """
        if filename == None: return
        assert os.path.exists(filename),  "QAC.assertf: %s does not exist" % filename
        return
        
    
#- end of qac.py
