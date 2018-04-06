#  QAC:  "Quick Array Combinations"
#
#        These are helper functions for various Array Combination techniques, such as
#        Feather, TP2VIS and others.
#        Some are wrappers around CASA, others are also convenient for regression and performance testing.
#
#        The simplicity of these functions is intended to simplify usage of CASA and promote
#        testing your codes.
#

import os, shutil, math, tempfile
import os.path
# from buildmosaic import buildmosaic
from utils import constutils as const
from utils import radialProfile
import numpy as np
# import numpy.ma as ma
# import pyfits as fits
import matplotlib.pyplot as pl

# this is dangerous, creating some convenient numbers in global namespace, but here they are...
# one should definitely avoid using 2 letter variables, as CASA uses these a lot
cqa  = qa.constants('c')                  # (turns out to be in m/s)
cms  = qa.convert(cqa,"m/s")['value']     # speed of light, forced in m/s (299792458.0)
apr  = 180.0 * 3600.0 / np.pi             # arcsec per radian (206264.8)
bof  = np.pi / (4*math.log(2.0))          # beam oversampling factor (1.1331) : NPPB = bof * (Beam/Pixel)**2  [cbm in tp2vis.py]
stof = 2.0*np.sqrt(2.0*np.log(2.0))       # FWHM=stof*sigma  (2.3548)

def qac_version():
    """ qac version reporter """
    print("qac: version 5-apr-2018")
    print("qac_root: %s" % qac_root)
    print("casa:" + casa['version'])        # there is also:   cu.version_string()
    print("data:" + casa['dirs']['data'])
    
    #-end of qac_version()    

def qac_log(message, verbose=True):
    """ qac banner message; can be turned off
    """
    if verbose:
        print("")
        print("========= QAC: %s " % message)
        print("")
        
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

    One can also use simobserve() to generate a pointing file. Note that it has two
    conventions:  maptype = "HEX" or "ALMA". For "HEX" the base of the triangle is horizontal,
    for "ALMA" the base of the triangle is vertical. This is also the shortest distance between
    two pointings.
    Our qac_im_ptg() only has one convention: the "HEX" maptype.
    
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
        print("%d fields used in %s" % (n,outfile))
        
    return finalPtglist

    #-end of qac_im_ptg()

def qac_ms_ptg(msfile, outfile=None, uniq=True):
    """ get the ptg's from an MS into a list and/or ascii ptg file
    'J2000 19h00m00.00000 -030d00m00.000000',...
    This is a little trickier than it sounds, because the FIELD table has more entries than
    you will find in the FIELD_ID column (often central coordinate may be present as well,
    if it's not part of the observing fields, and locations of the Tsys measurements
    For 7m data there may also be some jitter amongst each "field" (are multiple SB used?)

    Note that the actual POINTING table is empty for the 12m and 7m data

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
    print("%d/%d fields are actually used in %s" % (n2,n1,msfile))
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
    #  we assume RA-DEC-POL-FREQ cubes as are needed for simobserve
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

def qac_fits(image,overwrite=True):
    """ exportfits shortcut, appends the extension ".fits" to a casa image
        also handles a list of images

        image     casa image, or list of images, to be converted to fits
    """
    if type(image) == type([]):
        ii = image
    else:
        ii = [image]
    for i in ii:
        fi = i + '.fits'
        exportfits(i,fi,overwrite=overwrite)
        print("Wrote " + fi)

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
        print("qac: %s %s" % (cur,req))
        if cur[0] >= req[0]: return
        if cur[1] >= req[1]: return
        if cur[2] >= req[2]: return
        print("WARNING: your CASA is outdated %s %s" % (cur,req))
        
    def ms_sign(ms):
        if ms == None:
            return 0
        # if not iscasa(ms): return 0
        tb.open(ms + '/SPECTRAL_WINDOW')
        cw = tb.getcol('CHAN_WIDTH')
        print('CHAN_WIDTH=' + str(cw[0][0]))
        tb.close()
        if cw[0][0] > 0:
            return 1
        elif cw[0][0] < 0:
            return -1
        print("WARNING: unexpected chan_width")
        return 0      # should never happen

    def im_sign(im):
        if not QAC.iscasa(im): return 0
        ia.open(im)
        h0 = ia.summary()
        aname = h0['axisnames']
        incr =  h0['incr']
        print("AXIS NAMES:" + str(aname))
        print("incr      :" + str(incr))
        ia.close()
        #
        df = None
        for i in range(len(aname)):
            if aname[i] == 'Frequency':
                # print "Frequency found along axis ",i
                df = incr[i]
                break
        if df == None:
            print("Warning: no freq axis found")
            return 0
        if df > 0:
            return 1
        elif df < 0:
            return -1
        print("WARNING: unexpected freq incr %f" % df)
        return 0
        
    # create a local copy of the list, so no multiple call side-effects !!!
    if type(casaworkaround) == list:
        cwa = list(casaworkaround)
    else:
        cwa = [casaworkaround]
    print("tp2vischeck: casaworkaround: " + str(cwa))

    casa_version_check('5.0.0')

    # check sign of freq axis
    sign1 = ms_sign(ms)     # 0, 1 or -1
    sign2 = im_sign(tp)     # 0, 1 or -1
    if sign1*sign2 != 0 and sign1 != sign2:
        print("Adding workaround 11 for flip freq axis")
        cwa.append(11)

    # check if we have a fits file
    if not QAC.iscasa(tp) and not 3 in cwa:
        print("Converting fits file to casa image")
        cwa.append(3)
    elif 3 in cwa and QAC.iscasa(tp):
        print("Already have casa image")
        cwa.remove(3)

    if 3 in cwa:
        if tpout != None:
            importfits(tp,tpout,overwrite=True)
            print("Converted fits to casa image " + tpout)
            print("Rerun tp2vischeck() to ensure no more fixed needed")
            return
        else:
            print("No output file given, expect things to fail now")

    if 1 in cwa or 11 in cwa:
        #  1: ensure we have a RA-DEC-POL-FREQ cube
        # 11: reverse the FREQ axis to align with TP image
        ia.open(tp)
        h0 = ia.summary()
        aname = h0['axisnames']
        print("AXIS NAMES:" + str(aname))
        if len(aname) == 3:
            # ia.adddegaxes(stokes='I')
            print("Cannot deal with 3D cubes yet - fix this code")
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
            print("FIX: ia.transpose order=" + order)
                
        if tpout != None:
            if order != None:
                # on older CASA before 5.0 you will loose beam and object name (bugs.txt #017)
                os.system('rm -rf %s' % tpout)
                ia2 = ia.transpose(outfile=tpout,order=order)
                ia.done()
                ia2.done()
                print("Written transposed " + tpout)
                print("Rerun tp2vischeck() to ensure no more fixed needed")
                return
            else:
                ia.done()                
                print("WARNING: No transposed needed")
        else:
            if order != None:
                print("WARNING: axis ordering not correct, please provide output name")
                return

    if 2 in cwa:
        # ensure we have Jy/pixel
        s0 = imstat(tp)
        h0 = imhead(tp)
        if 'unit' in h0:
            print("UNIT: " + h0['unit'])
        if 'flux' in s0:
            bof = s0['sum'][0] / s0['flux'][0]
            print("BOF = %g" % bof)
            if tpout != None:
                os.system('rm -rf %s' % tpout)                
                expr = 'IM0/%g' % bof
                immath(tp,'evalexpr',tpout,expr)
                imhead(tpout,'del','beammajor')
                imhead(tpout,'put','bunit','Jy/pixel')
                print("Written rescaled " + tpout)
                print("Rerun tp2vischeck() to ensure no more fixed needed")
                return
            else:
                print("Warning: %s is not in the correct units for tp2vis. Provide output file name" % tp)
        else:
            print("WARNING: No rescale fix needed")
        return

    # BUG 15
    # if sign of channel width in TP is not the same as that in MS, the TP needs to be
    # ran via imtrans(order='012-3')
    # could this be combined with the transpose() ?

    #-end of qac_ingest()

def qac_stats_grid(images, **kwargs):
    for image in images:
        qac_stats(image, **kwargs)
    
    
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
    
    qac_tag("plot")    
        
    if not QAC.exists(image):
        print("QAC_STATS: missing %s " % image)
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
            print(delta)
            if delta.max() < eps:
                test_out = "OK"
                report = False
            else:
                test_out = "FAILED regression delta=%g > %g" % (delta.max(),eps)
                report = True
    msg1 = "QAC_STATS: %s" % (image)
    print("%s %s %s" % (msg1,test_new,test_out))
    if report:
        fmt1 = '%%-%ds' % (len(msg1))
        msg2 = fmt1 % ' '
        print("%s %s EXPECTED" % (msg2,test))
    
    #-end of qac_stats()
    
def qac_beam(im, normalized=False, chan=-1, plot=None):
    """ show some properties of the PSF

    im:           image representing the beam (usually a .psf file)
    normalized:   if True, axes are arcsec and normalized flux
                  otherwise pixels
    chan:         which channel to use [-1 means halfway cube]
    plot:         if set, this is the plot created, usually a png

    @todo   have an option to just print beam, no volume info
    """
    if not QAC.iscasa(im):
        print("QAC_BEAM: missing %s " % im)
        return

    h0 = imhead(im)
    nx    = h0['shape'][0]
    ny    = h0['shape'][1]
    nz    = max(h0['shape'][2],h0['shape'][3])
    if nz>1 and chan<0:
        chan = nz//2
    pix2 = abs(h0['incr'][0] * h0['incr'][1] * apr * apr)      # pixel**2 (in arcsec)
    if 'perplanebeams' in h0:
        chans = '*%d' % chan
        bmaj = h0['perplanebeams']['beams'][chans]['*0']['major']['value']
        bmin = h0['perplanebeams']['beams'][chans]['*0']['minor']['value']
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

    print("QAC_BEAM: %s  %g %g %g %g %g" % (im,bmaj,bmin,pix,nppb,factor))

    xcen  = h0['refpix'][0]
    ycen  = h0['refpix'][1]
    nx    = h0['shape'][0]
    ny    = h0['shape'][1]
    nz    = max(h0['shape'][2],h0['shape'][3])
    size  = np.arange(nx/2-20)
    flux  = 0.0 * size
    zero  = flux * 0.0
    ones  = zero + 1.0
    chans = str(chan)
    if False:
        for i in size:
            box = '%d,%d,%d,%d' % (xcen-i,ycen-i,xcen+i,ycen+i)
            flux[i] = imstat(im,chans=chans,box=box)['sum'][0]/factor
        print("QAC_BEAM: Max/Last/PeakLoc %g %g %g" % (flux.max(),flux[-1],flux.argmax()*pix))

    tb.open(im)
    d1 = tb.getcol("map").squeeze()
    tb.close()
    p1 = radialProfile.azimuthalAverage(d1)
    r1 = np.arange(len(p1))
    f1 = 2*math.pi*r1*p1
    flux2 = f1.cumsum() / factor
        
    print("QAC_BEAM: Max/Last/PeakLoc %g %g %g" % (flux2.max(),flux2[-1],flux2.argmax()*pix))    
    
    if plot != None:
        pl.figure()
        if normalized:
            pl.title("%s : Normalized cumulative flux" % im)
            pl.xlabel("size/2 (arcsec)")
            pl.ylabel("Flux")
            size = size * pix
            r1   = r1   * pix
            pl.plot(size,ones)
        else:
            pl.title("%s : Cumulative sum" % im)
            pl.xlabel("size/2 (pixels)")
            pl.ylabel("Sum")
        pl.plot(size,flux)
        pl.plot(size,zero)
        pl.plot(r1,flux2)
        pl.savefig(plot)
        pl.show()
    
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

    print("UVW shape %s %s %g" % str(uvw.shape),str(uvw[:,0]),factor)
    u = uvw[0,:] * factor                   # uvw are in m. we want m
    v = uvw[1,:] * factor                   # or klambda
    uvd = np.sqrt(u*u+v*v)
    print("UVD npts,min/max = %d %g %g" % (len(uvd), uvd.min(), uvd.max()))

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
    print("FIELD1" + str(field1))
    print("FIELD2" + str(field2))
    x1 = field1[0][0]
    y1 = field1[1][0]
    x2 = field2[0][0]
    y2 = field2[1][0]

    n1 = len(field1[0][0])
    n2 = len(field2[0][0])
    print("Found %d in MS1, %d in MS2" % (n1,n2))
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
        print("DMIN %d %f %d" % (i1,dmin,int(mask[i1])))

    print("MASK" + str(mask))
    print("SUM: %g" % mask.sum())
    
    #-end of qac_flag1()

def qac_vla(project, skymodel, imsize=512, pixel=0.5, phasecenter=None, cfg=1, niter=-1, ptg = None, times=[1/3.0, 1]):
    """

    NOTE: each cfg will append its data to any existing data for that same cfg
    
    cfg = 0    ngvlaSA_2b_utm or ngvlaSA_2b   (ngVLA design study)
    cfg = 1    SWcore
    cfg = 2    SW214
    cfg = 3    SWVLB

    times      For ngvla we need shorter times, so 1200s and 60s should be fast enough for #vis
    
    
    """
    qac_tag("vla")
    
    cfg_name = ['ngvlaSA_2b_utm', 'SWcore', 'SW214', 'SWVLB']

    cfg_file = qac_root + '/cfg/' + cfg_name[cfg]
    print("@todo %s " % cfg_file)

    outms = qac_generic_int(project, skymodel, imsize, pixel, phasecenter, cfg=cfg_file, niter=niter, ptg = ptg, times=times)
    return outms
    
def qac_alma(project, skymodel, imsize=512, pixel=0.5, phasecenter=None, cycle=5, cfg=0, niter=-1, ptg = None, times=None):
    """
    helper function to create an MS from a skymodel for a given ALMA configuration

    project     - name (one directory deep) to which files are accumulated - will accumulate
    skymodel    - jy/pixel map
    imsize      -
    pixel       -
    phasecenter - where to place the reference pixel
    times       -

    NOTE: each (cycle,cfg) pair will append its data to any existing data for that same pair
    
    See CASA/data/alma/simmos/ for the allowed (cycle,cfg) pairs

    cycle 1:   ALMA cfg = 1..6    ACA ok
    cycle 2:   ALMA cfg = 1..7    ACA bleeh ('i' and 'ns')
    cycle 3:   ALMA cfg = 1..8    ACA ok
    cycle 4:   ALMA cfg = 1..9    ACA ok
    cycle 5:   ALMA cfg = 1..10   ACA ok [same as 4]
    cycle 6:   ALMA cfg = 1..10   ACA ok [same as 5]
    """
    qac_tag("alma")
    
    # since we call it incrementally, make sure directory exists
    os.system('mkdir -p %s' % project)

    if cfg == 0:
        visweightscale = (7.0/12.0)**2
    else:
        visweightscale = 1.0
        
    #                                                  os.getenv("CASAPATH").split()[0]+"/data/alma/simmos/"    
    data_dir = casa['dirs']['data']                  # data_dir + '/alma/simmos' is the default location for simobserve
    if cfg==0:
        cfg = 'aca.cycle%d' % (cycle)                # cfg=0 means ACA (7m)
    else:
        cfg = 'alma.cycle%d.%d' % (cycle,cfg)        # cfg>1 means ALMA (12m)

    print("CFG: " + cfg)

    ms1 = qac_generic_int(project, skymodel, imsize, pixel, phasecenter, cfg=cfg, niter=niter, ptg = ptg, times=times)
    
    if visweightscale != 1.0:
        print "We need to set lower weights since the 7m dishes are smaller than 12m.",visweightscale
        ms2 = ms1 + '.tmp'
        os.system('mv %s %s' % (ms1,ms2))
        concat(ms2, ms1, visweightscale=visweightscale)
        os.system('rm -rf %s' % ms2)

    return ms1

    #-end of qac_alma()
    
def qac_generic_int(project, skymodel, imsize=512, pixel=0.5, phasecenter=None, freq=None, cfg=None, niter=-1, ptg = None, times=None):
    """
    generic interferometer; called by qac_vla() and qac_alma()

    project     - name (one directory deep) to which files are accumulated - will accumulate
    skymodel    - jy/pixel map
    imsize      -
    pixel       -
    phasecenter - where to place the reference pixel
    times       - a list of two numbers: totaltime in hours, integration time in minutes
    
    """

    # for tclean (only used if niter>=0)
    imsize    = QAC.imsize2(imsize)
    cell      = ['%garcsec' % pixel]
    outms     = '%s/%s.%s.ms'  % (project,project,cfg[cfg.rfind('/')+1:]) 
    outms2    = '%s/%s.%s.ms2' % (project,project,cfg[cfg.rfind('/')+1:])
    outim     = '%s/dirtymap'  % (project)

    if ptg != None:
        setpointings = False
        ptgfile      = ptg
    # obsmode     = "int"
    antennalist = "%s.cfg" % cfg     # can this be a list?

    if times == None:
        totaltime   = "28800s"     # 4 hours  (should be multiple of 2400 ?)
        integration = "30s"        # prevent too many samples for MS
    else:
        totaltime   = "%gs" % (times[0]*3600)
        integration = "%gs" % (times[1]*60)
        

    thermalnoise= ""
    verbose     = True
    overwrite   = True
    graphics    = "file"       # "both" would do "screen" as well
    user_pwv    = 0.0

    incell      = "%garcsec" % pixel
    mapsize     = ["%garcsec" % (pixel*imsize[0])  ,"%garcsec"  % (pixel*imsize[1]) ]


    # we allow accumulation now ..
    # ...make sure old directory is gone
    # ...os.system("rm -rf %s" % project)

    if ptg == None:
        simobserve(project, skymodel,
               indirection=phasecenter,
               incell=incell,
               mapsize=mapsize,
               integration=integration,
               totaltime=totaltime,
               antennalist=antennalist,
               verbose=verbose, overwrite=overwrite,
               user_pwv = 0.0, thermalnoise= "")
    else:
        simobserve(project, skymodel,
               setpointings=False, ptgfile=ptgfile,
               indirection=phasecenter,
               incell=incell,
               mapsize=mapsize,
               integration=integration,
               totaltime=totaltime,
               antennalist=antennalist,
               verbose=verbose, overwrite=overwrite,                   
               user_pwv = 0.0, thermalnoise= "")

    if True:
        # there appears to be also something wrong with the POINTING table via simobserve
        print("CONCAT: removing POINTING table into " + outms2)
        concat(outms,outms2,copypointing=False)

    if niter >= 0:
        cmd1 = 'rm -rf %s.*' % outim
        os.system(cmd1)
        tclean(vis=outms,                         # tclean for just qac_alma()
               imagename=outim,
               niter=niter,
               gridder='mosaic',
               deconvolver = 'clark',
               imsize=imsize,
               cell=cell,
               stokes='I',
               pbcor=True,
               phasecenter=phasecenter,
               weighting='natural',
               specmode='cube')
        qac_stats(outim + '.image')

    return outms

    #-end of qac_int_generic()

def qac_tpdish(name, size=None):
    """
    A patch to work with dishes that are not 12m (currently hardcoded in tp2vis.py)

    E.g. for GBT (a 100m dish) you would need to do:

    qac_tpdish('ALMATP',100.0)
    qac_tpdish('VIRTUAL',100.0)
    """
    qac_tag("tpdish")    
    if size == None:
        if name in t2v_arrays.keys():
            print(t2v_arrays[name])
        else:
            print("'%s' not a valid dish name, valid are : %s" % (name,str(t2v_arrays.keys())))
        return
    old_size = t2v_arrays[name]['dish']
    old_fwhm = t2v_arrays[name]['fwhm100']
    r = size/old_size
    t2v_arrays[name]['dish']   = size
    t2v_arrays[name]['fwhm100']= old_fwhm / r
    print("QAC_DISH: %g %g -> %g %g" % (old_size, old_fwhm, size, old_fwhm/r))

def qac_tp_vis(project, imagename, ptg=None, imsize=512, pixel=1.0, niter=-1, phasecenter=None, rms=None, maxuv=10.0, nvgrp=4, fix=1, deconv=True, **line):    
           
    """
      Simple frontend to call tp2vis() and an optional tclean()
    
    
      _required_keywords:
      ===================
      project:       identifying (one level deep directory) name within which all files are places
      imagename:     casa image in RA-DEC-POL-FREQ order
      ptg            1) Filename with pointings (ptg format) to be used
                     2_ List of (string) pointings
                     If none specified, it will currently return, but there may be a
                     plan to allow auto-filling the (valid) map with pointings.
                     A list of J2000/RA/DEC strings can also be given.
    
    
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
                     Within CASA you can use use deconvolve() to construct a Jy/pixel map.

      line           Dictionary of tclean() parameters, usually the line parameters are useful, e.g.
                     line = {"restfreq":"115.271202GHz","start":"1500km/s", "width":"5km/s","nchan":5}
    """
    qac_tag("tp_vis")
    
    # assert input files
    QAC.assertf(imagename)
    
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
        print("MAP REFERENCE: phasecenter = '%s'" % phasecenter0)
        if phasecenter == None:
            phasecenter == phasecenter0

    if ptg == None:
        print("No PTG specified, no auto-regioning yet")
        return None

    # @todo   similar to qac_alma this should be able to override the mapsize and pixelsize
    #         will need to make a shadow copy of the imagename
    #

    outfile = '%s/tp.ms' % project
    tp2vis(imagename,outfile,ptg, maxuv=maxuv, rms=rms, nvgrp=nvgrp, deconv=deconv)

    vptable = outfile + '/TP2VISVP'    
    if QAC.iscasa(vptable):                   # note: current does not have a Type/SubType
        print("Note: using TP2VISVP, and attempting to use vp from " + vptable)
        use_vp = True
        vp.reset()
        vp.loadfromtable(vptable)        # Kumar says this doesn't work, you need the vptable= in tclean()
    else:
        print("Note: did not find TP2VISVP, not using vp")
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
        print("FIX %d with mstransform and concat for CORRECTED_DATA" % fix_mode )
        outfile1 = '%s/tp1.ms' % project    
        mstransform(outfile,outfile1)
        os.system('rm -rf %s' % outfile)
        concat(outfile1,outfile,copypointing=False)
        os.system('rm -rf %s' % outfile1)

    if fix_mode == 2:
        print("FIX %d with mstransform and concat and for CORRECTED_DATA keeping backups" % fix_mode)
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
        # Plot UV - tp2vispl() does this better
        figfile = outfile + ".png"
        print("PLOTUV " + figfile)
        plotuv(outfile,figfile=figfile)

    if niter < 0 or imsize < 0:
        return outfile

    # finalize by making a tclean()

    print("Final test clean around phasecenter = '%s'" % phasecenter)
    dirtymap = '%s/dirtymap' % project
    imsize    = QAC.imsize2(imsize)
    cell      = ['%garcsec' % pixel]
    weighting = 'natural'
    if 'scales' in line.keys():
        deconvolver = 'multiscale'
    else:
        deconvolver = 'hogbom'        
        deconvolver = 'clark'
    
    tclean(vis = outfile,                              # tclean() just for qac_tp_vis()
           imagename      = dirtymap,
           niter          = niter,
           gridder        = 'mosaic',
           deconvolver    = deconvolver,
           imsize         = imsize,
           cell           = cell,
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


# qac_tp_vis(project, imagename, ptg=None, imsize=512, pixel=1.0, niter=-1, phasecenter=None, rms=None, maxuv=10.0, nvgrp=4, fix=1, deconv=True, **line):


def qac_sd_vis(**kwargs):
    """
    SD2vis from the Nordic Tools
    
    SDimage='',        
    SDchannels = -1,
    SDbaseline=7.0,
    nSDvis=1000,
    inputvis='', 
    inputspw=0,
    inputchan = [0,0],
    wgtfac = 1.0,
    over_resolve = 1.0, 
    scale= 1.0,
    outputvis='SD2vis.ms',
    Python_DFT = False): 

    """
    qac_tag("sd_vis")
    print("Here we go directly to SD2VIS")
    sd2vis(**kwargs)

    #-end of qac_sd_vis()
        
def qac_tp_otf(project, skymodel, dish, label="", freq=None, template=None):
    """
    helper function to create on the fly total power map
    
    dish:       dish diameter in meters
    freq:       frequency in GHz, if you want to override the image header value 
    template:   dirty image --> must come from tclean so there is both *.image and *.pb
    
    @todo make use of the template for regrid
    @todo come up with a good way to handle the directory structure for the project input 
    
    E.g. for 45 m single dish configuration:

    qac_tp_otf('test10/clean1', 'skymodel.im', dish=45)
    """
    qac_tag("tp_otf")
    
    # clean up old project
    os.system('rm -rf %s/otf*%s*' % (project,label))

    # projectpath/filename for temporary otf 
    out_tmp   = '%s/temp_otf.image'%project
    # projectpath/filename for otf.image.pbcor
    out_pbcor = '%s/otf%s.image.pbcor'%(project, label)
    # projectpath/filename for otf.image (primary beam applied)
    out_image = '%s/otf%s.image'%(project, label)

    # check if a freq was specificed in the input
    if freq == None:
        # if none, then pull out frequency from skymodel header
        # @todo come up with a way to check if we are actually grabbing the frequency from the header. it's not always crval3
        h0 = imhead(skymodel,mode='list')
        freq = h0['crval4'] # hertz
    else:
        freq = freq * 1.0e9

    # calculate beam size in arcsecs
    # @todo check if alma uses 1.22*lam/D or just 1.0*lam/D
    beam = cms / (freq * dish) * apr

    # convolve skymodel with beam. assumes circular beam
    imsmooth(imagename=skymodel,
             kernel='gauss',
             major='%sarcsec'%beam,
             minor='%sarcsec'%beam,
             pa='0deg',
             outfile=out_tmp,
             overwrite=True)

    # regrid
    if template == None:
        # inherit template from dirty map if template has not be specified in the input
        # @todo need a way to grab the last dirtymap (e.g. dirtymap7.image) or grab a specified dirty map (e.g. dirtymap7 is bad so we want dirtymap6)
        template = '%s/dirtymap.image'%project

    imregrid(imagename=out_tmp,
             template=template,
             output=out_pbcor,
             overwrite=True)

    # immath to create primary beam applied. assumes the template is output from tclean so that you have file.image and file.pb
    immath(imagename=[out_pbcor, '%s.pb'%template[:-6]],
           expr='IM0*IM1',
           outfile=out_image)
    # qac_math(out_image, '%s.pb'%template[:-6]], '*', out_pbcor);

    # remove the temporary OTF image that was created
    os.system('rm -fr %s'%out_tmp)

    return out_image

    #-end of qac_tp_otf()    


def qac_clean1(project, ms, imsize=512, pixel=0.5, niter=0, weighting="natural", startmodel="", phasecenter="",  t=True, **line):
    """
    Simple interface to do a tclean() [or clean()] on an MS (or list of MS)

    Required:
    
    project - new directory for this  (it is removed before starting)
    ms      - a single MS (or a list, but no concat() is done)

    Optional:
    
    imsize       512  (list of 2 is allowed if you need rectangular area)
    pixel        0.5 arcsec
    niter        0 or more, can be a list as well, e.g. [0,1000,3000]
    weighting    "natural"
    startmodel   Jy/pixel starting model [ignored in clean() mode]
    phasecenter  mapping center   (e.g. 'J2000 03h28m58.6s +31d17m05.8s')
    t            True means using tclean. False means try and fallback to old clean() [w/ caveats]
    **line       Dictionary meant for  ["restfreq","start","width","nchan"] but anything (t)clean can be passed here

    Note that clean() uses a different naming convention (e.g. .flux)
    
    """
    qac_tag("clean1")
    
    os.system('rm -rf %s; mkdir -p %s' % (project,project))
    #
    outim1 = '%s/dirtymap' % project
    imsize = QAC.imsize2(imsize)
    cell   = ['%garcsec' % pixel]
    vis1   = ms
    #
    if True:
        try:
            tb.open(ms + '/SPECTRAL_WINDOW')
            chan_freq = tb.getcol('CHAN_FREQ')
            tb.close()
            tb.open(ms + '/SOURCE')
            ref_freq = tb.getcol('REST_FREQUENCY')
            tb.close()
            print('FREQ: %g %g %g' % (chan_freq[0][0]/1e9,chan_freq[-1][0]/1e9,ref_freq[0][0]/1e9))
        except:
            print("Bypassing some error displaying freq ranges")

    print("VIS1=%s" % str(vis1))
    print("niter=%s" % str(niter))
    if type(niter) == type([]):
        niters = niter
    else:
        niters = [niter]
    if 'scales' in line.keys():
        deconvolver = 'multiscale'
    else:
        deconvolver = 'hogbom'
        deconvolver = 'clark'
        
    if type(ms) != type([]):
        vptable = ms + '/TP2VISVP'
        if QAC.iscasa(vptable):                   # note: current does not have a Type/SubType
            print("Note: using TP2VISVP, and attempting to use vp from" + vptable)
            use_vp = True
            vp.reset()
            vp.loadfromtable(vptable)
        else:
            print("Note: did not find TP2VISVP, not using vp")
            use_vp = False
            vptable = None
        vp.summarizevps()
    else:
        use_vp = False        
        vptable = None

    if t == True:
        # tclean() mode
        tclean_args = {}
        tclean_args['gridder']       = 'mosaic'
        tclean_args['deconvolver']   = deconvolver
        tclean_args['imsize']        = imsize
        tclean_args['cell']          = cell
        tclean_args['stokes']        = 'I'
        tclean_args['pbcor']         = True
        tclean_args['phasecenter']   = phasecenter
        tclean_args['vptable']       = vptable
        tclean_args['weighting']     = weighting
        tclean_args['specmode']      = 'cube'
        tclean_args['startmodel']    = startmodel
        tclean_args['restart']       = True
        for k in line.keys():
            tclean_args[k] = line[k]
        
        for niter in niters:
            print("TCLEAN(niter=%d)" % niter)
            tclean_args['niter']      = niter
            tclean(vis = vis1, imagename = outim1, **tclean_args)
            tclean_args['startmodel'] = ""
            tclean_args['restart']    = False
    else:
        # old clean() mode
        clean_args = {}
        clean_args['imagermode']    = 'mosaic'
        clean_args['psfmode']       = deconvolver
        clean_args['imsize']        = imsize
        clean_args['cell']          = cell
        clean_args['stokes']        = 'I'
        clean_args['pbcor']         = True
        clean_args['phasecenter']   = phasecenter
        clean_args['weighting']     = weighting
        clean_args['mode']          = 'velocity'     #   only for cont?
        clean_args['modelimage']    = startmodel        
        for k in line.keys():
            clean_args[k] = line[k]

        i = 0
        for niter in niters:
            print("CLEAN(niter=%d)" % niter)
            clean_args['niter']     = niter
            i = i + 1
            if i == 1:
                outim2 = outim1
            else:
                outim2 = "%s_%d" % (outim1,i)
            clean(vis = vis1, imagename = outim2, **clean_args)
            clean_args['modelimage']    = ""
        # for niter
            
    print("Wrote %s with %s weighting %s deconvolver" % (outim1,weighting,deconvolver))
    
    #-end of qac_clean1()
    
def qac_clean(project, tp, ms, imsize=512, pixel=0.5, weighting="natural", startmodel="", phasecenter="", niter=0, do_concat = False, do_int = False, do_cleanup = True, **line):
    """
    Simple interface to do a tclean() joint deconvolution of one TP and one or more MS
    
    project - new directory for this operation (it is removed before starting)
    tp      - the TP MS (needs to be a single MS)
    ms      - the int array MS (can be a list of MS)
    imsize  - size of the maps (list of 2 is allowed if you need rectangular)
    pixel   - pixelsize in arcsec, pixels are forced square
    niter   - list of niter for (t)clean

    do_concat   - work around a bug in tclean ?  Default is true until this bug is fixed
    do_int      - also make a map from just the INT ms (without tp)
    do_cleanup  - if do_concat was used, this concat ms would be removed again
    """
    qac_tag("clean")
    #
    os.system('rm -rf %s; mkdir -p %s' % (project,project))
    #
    outim1 = '%s/int' % project
    outim2 = '%s/tpint' % project
    outms  = '%s/tpint.ms' % project       # concat MS to bypass tclean() bug
    #
    imsize    = QAC.imsize2(imsize)
    cell      = ['%garcsec' % pixel]
    #
    vis1 = ms
    if type(ms) == type([]):               # force the MS at the end, there is a problem when not !!!!
        vis2 =  ms  + [tp] 
    else:
        vis2 = [ms] + [tp] 
    # @todo    get the weights[0] and print them
    print("niter=" + str(niter))
    print("line: " + str(line))
    #
    if type(niter) == type([]):
        niters = niter
    else:
        niters = [niter]
    #
    if 'scales' in line.keys():
        deconvolver = 'multiscale'
    else:
        deconvolver = 'hogbom'
        deconvolver = 'clark'
    
    if do_int:
        print("Pure interferometer imaging using vis1=%s" % str(vis1))
        # tclean() mode
        tclean_args = {}
        tclean_args['gridder']       = 'mosaic'
        tclean_args['deconvolver']   = deconvolver
        tclean_args['imsize']        = imsize
        tclean_args['cell']          = cell
        tclean_args['stokes']        = 'I'
        tclean_args['pbcor']         = True
        tclean_args['phasecenter']   = phasecenter
        # tclean_args['vptable']       = vptable
        tclean_args['weighting']     = weighting
        tclean_args['specmode']      = 'cube'
        tclean_args['startmodel']    = startmodel
        tclean_args['restart']       = True
        for k in line.keys():        # merge in **line
            tclean_args[k] = line[k]
        
        for niter in niters:
            print("TCLEAN(niter=%d)" % niter)
            tclean_args['niter']      = niter
            tclean(vis = vis1, imagename = outim1, **tclean_args)
            tclean_args['startmodel'] = ""
            tclean_args['restart']    = False
            
        print("Wrote %s with %s weighting %s deconvolver" % (outim1,weighting,deconvolver))        
    else:
        print("Skipping pure interferometer imaging using vis1=%s" % str(vis1))

    print("Creating TP+INT imaging using vis2=%s" % str(vis2))
    if do_concat:
        # first report weight 
        print("Weights in %s" % str(vis2))
        for v in vis2:
            tp2viswt(v)
        # due to a tclean() bug, the vis2 need to be run via concat
        # MS has a pointing table, this often complaints, but in workflow5 it actually crashes concat()
        print("Using concat to bypass tclean bug - also using copypointing=False")
        #concat(vis=vis2,concatvis=outms,copypointing=False,freqtol='10kHz')
        concat(vis=vis2,concatvis=outms,copypointing=False)
        vis2 = outms
        
    # tclean() mode
    tclean_args = {}
    tclean_args['gridder']       = 'mosaic'
    tclean_args['deconvolver']   = deconvolver
    tclean_args['imsize']        = imsize
    tclean_args['cell']          = cell
    tclean_args['stokes']        = 'I'
    tclean_args['pbcor']         = True
    tclean_args['phasecenter']   = phasecenter
    # tclean_args['vptable']       = vptable
    tclean_args['weighting']     = weighting
    tclean_args['specmode']      = 'cube'
    tclean_args['startmodel']    = startmodel
    tclean_args['restart']       = True
    for k in line.keys():
        tclean_args[k] = line[k]
        
    for niter in niters:
        print("TCLEAN(niter=%d)" % niter)
        tclean_args['niter']      = niter
        tclean(vis = vis2, imagename = outim2, **tclean_args)
        tclean_args['startmodel'] = ""
        tclean_args['restart']    = False

    print("Wrote %s with %s weighting %s deconvolver" % (outim1,weighting,deconvolver))    

    if do_concat and do_cleanup:
        print("Removing " + outms)
        shutil.rmtree(outms)
    
    #-end of qac_clean()

def qac_tweak(project, name = "dirtymap", niter = [0], **kwargs):
    """
    call tp2vistweak for a niter-series of images with a commmon basename

    project     project name, e.g. 'sky1/clean2'
    name        basename of images, e.g. 'dirtymap', 'int', 'tpint'
    niter       the corresponding niter list that belongs to how the images were made
                First entry should be 0, correpsonding to the dirty map, the others
                incrementally the niters, e.g. [0,100,1000,10000]
    kwargs      passed to tp2vistweak(), typically just pbcut=0.8 now
    """
    qac_tag("tp_tweak")
    
    dname = "%s/%s" % (project,name)
    for i in range(len(niter)-1):
        cname = "%s/%s_%d" % (project,name,i+2)
        print("tweak %s %s " % (dname,cname))
        tp2vistweak(dname,cname,**kwargs)
    

def qac_feather(project, highres=None, lowres=None, label="", niteridx=0, name="dirtymap"):
    """
    Feather combination of a highres and lowres image

    project    typical  "sky3/clean2", somewhere where tclean has run
    highres    override default, needs full name w/ its project
    lowres     override default, needs full name w/ its project
    
    If the standard workflow is used, project contains the correctly named
    dirtymap.image and otf.image from qac_clean1() and qac_tp_otf() resp.
    @todo figure out if a manual mode will work

    Typical use in a simulation:
    
    qac_vla('sky3','skymodel.fits',4096,0.01,cfg='../SWcore',ptg='vla.ptg',phasecenter=pcvla)
    qac_clean1('sky3/clean3','sky3/sky3.SWcore.ms',  512,0.25,phasecenter=pcvla,niter=[0,500,1000,2000,3000,4000,5000])
    qac_tp_otf('sky3/clean3','skymodel.fits',45.0,label="45")
    qac_feather('sky3/clean3',label="45")

    """
    qac_tag("feather")
    
    # if the niteridx is 0, then the niter label will be an empty string
    if niteridx == 0:
        niter_label = ""
    else:
        # otherwise the niter label reflect the tclean naming convention
        # e.g. tclean used niter = [0, 1000, 2000] and returned dirtymap, dirtymap_2, and dirtymap_3
        # to get the second iteration of tclean (niter=1000), niteridx = 1
        niter_label = "_%s"%(niteridx + 1)


    if highres == None:
        highres = "%s/%s%s.image" % (project,name,niter_label) 
    if lowres  == None:
        lowres  = "%s/otf%s.image"    % (project,label)        # noise flat OTF image
    pb = highres[:highres.rfind('.')] + ".pb"
    QAC.assertf(highres)
    QAC.assertf(lowres)
    QAC.assertf(pb)

    feather1 = "%s/feather%s%s.image"       % (project,label,niter_label)
    feather2 = "%s/feather%s%s.image.pbcor" % (project,label,niter_label)

    print highres,lowres,pb,feather1,feather2

    feather(feather1,highres,lowres)                           # it will happily overwrite
    os.system('rm -rf %s' % feather2)                          # immath does not overwrite
    immath([feather1,pb],'evalexpr',feather2,'IM0/IM1')
    # ng_math(feather2, feather1, "/", pb)

    if True:
        qac_stats(highres)
        qac_stats(lowres)
        qac_stats(feather1)
        qac_stats(feather2)

    #-end of qac_feather()

def qac_smooth(project, skymodel, name="feather", label="", niteridx=0, do_flux = True):
    """
    helper function to smooth skymodel using beam of feathered image
    essentially converts the orginal skymodel from jy/pixel to jy/beam for easy comparison

    project    typical  "sky3/clean2", somewhere where tclean has run
    skymodel   a skymodel
    name       basename, typically feather, or dirtymap, or tpint.   Default is feather
    label      only used with OTF beams
    niteridx   0,1,2,.... if a niter[] was used so it can be inherited in the basename
    do_flux    if True, do the comparison in flux flat (image.pbcor) space, else noise flat (.image)

    """
    qac_tag("smooth")
    
    if niteridx == 0:
        niter_label = ""
    else:
        niter_label = "_%s"%(niteridx + 1)

    # feather image path/filename
    if do_flux:
        feather = '%s/%s%s%s.image.pbcor' % (project, name, label, niter_label)
    else:
        feather = '%s/%s%s%s.image'       % (project, name, label, niter_label)
        pb      = '%s/%s%s.pb'            % (project, name, niter_label)
    # projectpath/filename for a temporary image that will get deleted
    out_tmp = '%s/skymodel_tmp.image' % project
    # projectpath/filename for final regrid jy/beam image
    out_smoo = '%s/skymodel%s%s.smooth.image' % (project, label, niter_label)
    # projectpath/filename for subtracted image
    out_resid= '%s/skymodel%s%s.residual' % (project, label, niter_label)

    # grab beam size and position angle from feather image
    if not QAC.exists(feather):
        print("QAC_SMOOTH: %s does not exist" % feather)
        return None
    
    h0 = imhead(feather, mode='list')
    bmaj = h0['beammajor']['value']
    bmin = h0['beamminor']['value']
    pa   = h0['beampa']['value']
    print("QAC_SMOOTH: using %s with beam %g x %g @ %g" % (feather,bmaj,bmin,pa))
            
    # convolve skymodel with feather beam
    imsmooth(imagename=skymodel,
             kernel='gauss',
             major='%sarcsec' % bmaj,
             minor='%sarcsec' % bmin,
             pa='%sdeg' % pa,
             outfile=out_tmp,
             overwrite=True)

    # need to regrid skymodel using feather image as template
    imregrid(imagename=out_tmp,
             template=feather,
             output=out_smoo,
             overwrite=True)

    # subtract feather from smoothed skymodel to get a residual map
    if do_flux:
        immath(imagename=[out_smoo, feather], 
               expr='IM0-IM1',
               outfile=out_resid)
    else:
        immath(imagename=[out_smoo, feather, pb], 
               expr='IM0*IM2-IM1',
               outfile=out_resid)
        
    # ng_math(out_resid, out_smoo, '-', feather)

    # remove the temporary image that was created
    os.system('rm -fr %s'%out_tmp)

    return out_smoo

    #-end of qac_smooth()

def qac_analyze(project, imagename, niteridx=0):
    """
    helper function for using simanalyze without it running clean

    has a hard time with the skymodel and dirtymaps being in different directories

    project     project name/directory
    imagename   dirty image or feathered image to compare to skymodel. input as a string without '.image'
    niteridx    same convention as qac_smooth routine for grabbing the images from different iterations on tclean

    @todo get this going with it running clean to see how it compares to our manual cleaning (qac_clean1)
    """

    ng_tag('analyze')

    # if the niteridx is 0, then the niter label will be an empty string
    if niteridx == 0:
        niter_label = ""
    else:
        # otherwise the niter label reflect the tclean naming convention
        # e.g. tclean used niter = [0, 1000, 2000] and returned dirtymap, dirtymap_2, and dirtymap_3
        # to get the second iteration of tclean (niter=1000), niteridx = 1
        niter_label = "_%s"%(niteridx + 1)


    imagename = project + '/%s%s.image' %(imagename,niter_label)


    simanalyze(project=project,
               image=False,
               imagename=imagename,
               analyze=True,
               overwrite=True)

    #-end of qac_analyze()


def qac_phasecenter(im):
    """
    return the map reference center as a phasecenter
    """
    qac_tag("phasecenter")
    
    QAC.assertf(im)
    #
    h0=imhead(im,mode='list')
    ra  = h0['crval1'] * 180.0 / math.pi
    dec = h0['crval2'] * 180.0 / math.pi
    phasecenter = 'J2000 %.6fdeg %.6fdeg' % (ra,dec)
    return  phasecenter

    #-end of qac_phasecenter()

def qac_ptg(ptg, ptgfile=None):
    """ write a ptg list (or single) to a ptg file
        Example for format of the ptg's:
            J2000 180.000000deg 40.000000deg
            J2000 12:00:00.000  40.00.00.000

       @todo  absorb into qac_im_ptg()
    """
    qac_tag("ptg")
    
    if ptgfile == None: return
    fp = open(ptgfile,"w")
    if type(ptg) == type([]):
        for p in ptg:
            fp.write("%s" % p)
    else:
        fp.write("%s" % ptg)
    fp.close()

    #-end of qac_ptg()    
    
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

    # print the image info   @todo
    print("QAC_SUMMARY:")
    print("TP:       " + tp)
    print('OBJECT:   ' + h0['object'])
    print('SHAPE:    ' + str(h0['shape']))
    print('CRVAL:    ' + phasecenter)
    print('CRVALd:   ' + phasecenterd)
    print('RESTFREQ: ' + str(restfreq[0]/1e9) + " Ghz")
    print("FREQ:     " + str(freq_values[0]/1e9) + " " + str(freq_values[-1]/1e9))
    print("VEL:      " + str(vmin[0]) + " " + str(vmax[0]) + " " + str(dv))
    print("VELTYPE:  " + rft)
    print("UNITS:    " + h0['bunit'])
    
    # LIST OF MS (can be empty)
    for msi in ms_list:
        print("")
        if QAC.iscasa(msi):
            print("MS: " + msi)
        else:
            print("MS:   -- skipping non-existent " + msi)
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
            print("source %d %s %s" % (i,source[i],str(vrange(chan_freq[spw_id[i]],rest_freq[0][i]))))

        
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

    @todo    add the mom2 by default as well
    
    """
    def lel(name):
        """ convert filename to a safe filename for LEL expressions, e.g. in mask=
        """
        return '\'' + name + '\''
    pbguess = imcube + '.pb'
    if QAC.exists(pbguess) and not pb:
        print("WARNING: there is a pb file, but you are not using it. Assuming flat pb")
    chans1='%d~%d' % (chan_rms[0],chan_rms[1])
    chans2='%d~%d' % (chan_rms[2],chan_rms[3])
    chans3='%d~%d' % (chan_rms[1]+1,chan_rms[2])
    rms  = imstat(imcube,axes=[0,1])['rms']
    print(rms)
    rms1 = imstat(imcube,axes=[0,1],chans=chans1)['rms'].mean()
    rms2 = imstat(imcube,axes=[0,1],chans=chans2)['rms'].mean()
    print(rms1,rms2)
    rms = 0.5*(rms1+rms2)
    print("RMS = ",rms)
    if pb==None:
        mask = None
    else:
        mask = lel(pb) + '> %g' % pbcut
        print("Using mask=",mask)
    mom0 = imcube + '.mom0'
    mom1 = imcube + '.mom1'
    os.system('rm -rf %s %s' % (mom0,mom1))
    immoments(imcube, 0, chans=chans3, includepix=[rms*2.0,9999], mask=mask, outfile=mom0)
    immoments(imcube, 1, chans=chans3, includepix=[rms*5.5,9999], mask=mask, outfile=mom1)

    #-end of qac_mom()

def qac_math(outfile, infile1, oper, infile2):
    """  image math; just simpler to read than immath() for a few basic ones
    
         immath([a,b],'evalexpr',c,'IM0+IM1')
    is
         qac_math(c,a,'+',b)
    """
    qac_tag("math")
    if not QAC.exists(infile1) or not QAC.exists(infile2):
        print("QAC_MATH: missing %s and/or %s" % (infile1,infile2))
        return
    
    if oper=='+':  expr = 'IM0+IM1'
    if oper=='-':  expr = 'IM0-IM1'
    if oper=='*':  expr = 'IM0*IM1'
    if oper=='/':  expr = 'IM0/IM1'
    os.system("rm -rf %s" % outfile)
    immath([infile1,infile2],'evalexpr',outfile,expr)

    #-end of qac_math()
    
def qac_plot(image, channel=0, box=None, range=None, mode=0, title="", plot=None):
    """
    mode=0     pick the default
    mode=1     force casa
    mode=2     force numpy/imshow
    """
    qac_tag("plot")
    #
    # zoom={'channel':23,'blc': [200,200], 'trc': [600,600]},
    #'range': [-0.3,25.],'scaling': -1.3,
    if plot==None:
        out = image+'.png'
    else:
        out = plot
        
    if mode == 0: mode=2      # our hardcoded default
        
    if mode == 1:
        if range == None:
            h0 = imstat(image,chans='%d' % channel)
            range = [h0['min'][0],h0['max'][0]]
        raster =[{'file': image,  'colorwedge' : True, 'range' : range}]    # scaling (numeric), colormap (string)
        zoom={'channel' : channel,
              'coord':'pixel'}      # @todo 'blc': [190,150],'trc': [650,610]}
        if box != None:
            zoom['blc'] = box[0:2]
            zoom['trc'] = box[2:4]
            
        print("QAC_PLOT: %s range=%s" % (image,str(range)))
        imview(raster=raster, zoom=zoom, out=out)
    elif mode == 2:
        cmap = 'nipy_spectral'
        
        tb.open(image)
        d1 = tb.getcol("map").squeeze()
        tb.close()
        print("SHAPE from casa: ",d1.shape)
        nx = d1.shape[0]
        ny = d1.shape[1]
        if len(d1.shape) == 2:
            d3 = np.flipud(np.rot90(d1.reshape((nx,ny))))            
        else:
            d2 = d1[:,:,channel]
            d3 = np.flipud(np.rot90(d2.reshape((nx,ny))))            

        if box != None:
            data = d3[box[1]:box[3],box[0]:box[2]]
        else:
            data = d3
        if range == None:
            range = [data.min(), data.max()]

        pl.ioff()    # not interactive
        pl.figure()
        alplot = pl.imshow(data, origin='lower', vmin = range[0], vmax = range[1])
        #alplot = pl.imshow(data, origin='lower')
        #pl.set_cmap(cmap)
        #alplot.set_cmap(cmap)
        pl.colorbar()
        pl.ylabel('X')
        pl.xlabel('Y')
        pl.title('%s chan=%d %s' % (image,channel,title))
        print("QAC_PLOT: %s range=%s   %s" % (image,str(range),out))
        pl.savefig(out)
        if False:
            pl.show()
        else:
            pl.close('all') 
           
        
        
    #-end of qac_plot()

def qac_plot_grid(images, channel=0, box=None, minmax=None, ncol=2, diff=0, xgrid=[], ygrid=[], plot=None):
    """
    Same as qac_plot() except it can plot a nrow x ncol grid of images and optionally add
    a column of difference images

    images  list of images. Needs to fit in nrow x ncol, where nrow is computed from ncol
            order of images is row by row
    channel which channel, in case images are cubes
            @todo   if channel is a list, these are the channels on one image
    box     [xmin,ymin,xmax,ymax]   defaults to whole image
    minmax  [dmin,dmax]  defaults to minmax of all images
    ncol    number of columns to be used. rows follow from #images
    diff    if non-zero, in pairs of two, a new difference image is computed and plotted
            this will increase ncol from 2 to 3 (diff != 0 needs ncol=2)
            diff is the factor by which the difference image is scaled
            Note that diff can be positive or negative. 
    xgrid   List of strings for the X panels in the grid
    ygrid   List of strings for the Y panels in the grid
    plot    if given, plotfile name

    0,0 is top left in row,col notation

    WARNINGS:
    - Since there is no WCS on the images, it is the responsibility of the caller to make sure each
    image has the same physical scale, although the pixel scale does not matter.
    - box is applied to all images in the same way. This makes the previous item even more dangerous.
    
    

    @todo   we need a colorbar (or nrows's) somewhere on the right?

    @todo   allow for a single image, to set a list of channels
    """
    qac_tag("plot_grid")
    #
    # zoom={'channel':23,'blc': [200,200], 'trc': [600,600]},
    #'range': [-0.3,25.],'scaling': -1.3,
    #
    print("QAC_PLOT_GRID",images)
    n = len(images)
    dim = range(n)
    for i in range(n):
        tb.open(images[i])
        d1 = tb.getcol("map").squeeze()
        tb.close()
        nx = d1.shape[0]
        ny = d1.shape[1]
        if len(d1.shape) == 2:
            d3 = np.flipud(np.rot90(d1.reshape((nx,ny))))            
        else:
            d2 = d1[:,:,channel]
            d3 = np.flipud(np.rot90(d2.reshape((nx,ny))))            
        if box != None:
            data = d3[box[1]:box[3],box[0]:box[2]]
        else:
            data = d3
        if i==0:
            dmin = data.min()
            dmax = data.max()
        else:
            dmin = min(data.min(),dmin)
            dmax = max(data.max(),dmax)
        dim[i] = np.copy(data)
    print("Data min/max",dmin,dmax)
    if minmax != None:
        dmin = minmax[0]
        dmax = minmax[1]
    #
    nrow = n // ncol
    if diff != 0:
        if ncol != 2:
            print("Cannot compute diff with ncol=",ncol)
            return
        ncol = ncol + 1
    print("Nrow/col = ",nrow,ncol)
    # @todo check if enough xgrid[] and ygrid[]
    #
    # placeholders for the data
    d = range(nrow)
    i = 0
    for row in range(nrow):
        d[row] = range(ncol)
        for col in range(ncol):
            if diff != 0:
                if col < 2:
                    d[row][col] = dim[i]
                    i=i+1
                else:
                    d[row][col] = d[row][col-1] - d[row][col-2]
                    print("Difference map minmax",d[row][col].min(),d[row][col].max())
                    d[row][col]  *= diff
            else:
                d[row][col] = dim[i]
                i=i+1

    fig = pl.figure()
    # pl.title(title)     # @todo global title needs work
    # fig.tight_layout()   # @todo this didn't work
    i = 0
    # @todo need less whitespace between boxes
    pl.subplots_adjust(hspace=0.1)
    for row in range(nrow):
        for col in range(ncol):
            f1 = fig.add_subplot(nrow,ncol,i+1)
            p1 = f1.imshow(d[row][col], origin='lower', vmin = dmin, vmax = dmax)
            #f1.set_title("im %d" % i)     # makes plot too busy
            f1.set_xticklabels([])
            f1.set_yticklabels([])
            if col==0 and len(ygrid) > 0:
                f1.set_ylabel(ygrid[row])
            if row==nrow-1 and len(xgrid) > 0:    # @todo should auto-create "diff" if diff != 0
                f1.set_xlabel(xgrid[col])
            i = i + 1
    if plot != None:
        pl.savefig(plot)
    pl.show()

    #-end of qac_plot_grid()
    

def qac_flux(image, box=None, dv = 1.0, plot='qac_flux.png'):
    """ Plotting min,max,rms as function of channel
    
        box     xmin,ymin,xmax,ymax       defaults to whole area

        A useful way to check the the mean RMS at the first
        or last 10 channels is:

        imstat(image,axes=[0,1])['rms'][:10].mean()
        imstat(image,axes=[0,1])['rms'][-10:].mean()
    
    """
    qac_tag("flux")
    
    pl.figure()
    _tmp = imstat(image,axes=[0,1],box=box)
    fmin = _tmp['min']
    fmax = _tmp['max']
    frms = _tmp['rms']
    chan = np.arange(len(fmin))
    f = 0.5 * (fmax - fmin) / frms
    pl.plot(chan,fmin,c='r',label='min')
    pl.plot(chan,fmax,c='g',label='max')
    pl.plot(chan,frms,c='b',label='rms')
    # pl.plot(chan,f,   c='black', label='<peak>/rms')
    zero = 0.0 * frms
    pl.plot(chan,zero,c='black')
    pl.ylabel('Flux')
    pl.xlabel('Channel')
    pl.title('%s  Min/Max/RMS' % (image))
    pl.legend()
    pl.savefig(plot)
    pl.show()
    print("Sum: %g Jy km/s (%g km/s)" % (fmax.sum() * dv, dv))

    #-end of qac_flux()

def qac_psd(image, plot='qac_psd.png'):
    """ compute the PSD of a map

    image:     casa image (fits file not allowed here)
    
    see also: radio_astro_tools et al. (sd2018)
    """

    tb.open(image)
    d1 = tb.getcol("map").squeeze()
    if len(d1.shape) != 2:
        print("Shape not supported for %s: %s" % (image,d1.shape))
        return
    nx = d1.shape[0]
    ny = d1.shape[1]
    tb.close()
    d2 = np.flipud(np.rot90(d1.reshape((nx,ny))))
    data = d2.squeeze()
    #
    f1 = np.fft.fft2(data)
    f2 = np.fft.fftshift(f1)
    p2 = np.abs(f2)**2
    p1 = radialProfile.azimuthalAverage(p2)    # now in util
    #p1 = azimuthalAverage(p2)     # if in contrib/radialProfile.py
    r1 = np.arange(1.0,len(p1)+1)
    
    pl.figure()
    pl.loglog(r1,p1)
    pl.xlabel('Spatial Frequency')
    pl.ylabel('Power Spectrum')
    pl.xlabel('Channel')
    pl.title('%s' % (image))
    pl.savefig(plot)
    pl.show()
    
    return p1
    
        
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

    print("you just wished this would work already eh....")

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



def qac_begin(label="QAC", log=True):
    """
    Every script should start with qac_begin() if you want to use the logger
    and/or Dtime output for performance testing. You can safely leave this
    call out, or set log=False

    See also qac_tag() and qac_end()
    """
    if log:
        from utils import Dtime
        import logging
        # @todo until the logging + print problem solved, this is disabled
        logging.basicConfig(level = logging.INFO)
        root_logger = logging.getLogger()
        print('root_logger =', root_logger)
        print('handlers:', root_logger.handlers)
        handler = root_logger.handlers[0]
        print('handler stream:', handler.stream)
        import sys
        print('sys.stderr:', sys.stderr)
        QAC.dt = Dtime.Dtime(label)

def qac_tag(label):
    """
    Create a time/memory tag for the logger using  Dtime.tag()
    
    See also qac_begin()
    """
    if QAC.hasdt(): 
        QAC.dt.tag(label)

def qac_end():
    """
    Stop logging. Calls    Dtime.end()
    
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
            print("Warning: %s is not a CASA dataset" % filename)

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
    def casa2np(image, box=None, z=None):
        """
        convert a casa[x][y] to a numpy[y][x] such that fits writers
        will produce a fits file that looks like an RA-DEC image
        and also native matplotlib routines, such that imshow(origin='lower')
        will give the correct orientation.

        if image is a string, it's assumed to be the casa image name

        box    pixel list of [xmin,ymin, xmax, ymax]
        z      which plane to pick in case it's a cube (not implemented)
        """
        if type(image)==type(""):
            tb.open(image)
            d1 = tb.getcol("map").squeeze()            
            tb.close()
            return np.flipud(np.rot90(d1))
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
