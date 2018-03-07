"""
Routines to interface with CASA's coordinate handling routines. Wraps
the coordsys tool into a simple single line call of the sort that I
want for easy access to WCS writing other scripts.
"""

import pylab as pl
import numpy as np

from tasks import *
from taskinit import *
import casac

# -----------------------------------------------------
# GENERATE RA, DEC, AND VELOCITY AXES FROM THE IMAGE
# -----------------------------------------------------

def make_axes(imname, image=True, only_sky=False
              , only_v=False, restfreq=None, freq=False):
    """
    Return RA, Dec, and Velocity axes for the specified file. Requires
    imname.

    OPTIONS:

    image (True) : return 2-d images of RA and DEC, else 1-d axes

    only_sky (False) : work out only the sky coordinates

    only_v (False) : work out only the velocity axis.

    freq (False) : return frequency, else velocity.

    restfreq (None) : force the supplied rest frequency.

    NOTES:

    To get back only RA and DEC just call as 

    ra, dec = make_axes(im)

    HISTORY:

    written - may 11 aleroy@nrao
    hacked to allow stokes/spectral flopping - aug 11
    
    """
    
    # MORE ERROR CHECKING HERE

    # ... TBD: FIX INEFFICIENCY IN "AXIS ONLY" CASE

    # EXTRACT THE SHAPE AND COORDSYS OF THE IMAGE
    ia.open(imname)
    cs = ia.coordsys()
    units = []
    for ctype in cs.axiscoordinatetypes():
        if ctype == "Direction":
            units.append('deg')
        if ctype == "Spectral":
            units.append('Hz')
        if ctype == "Stokes":
            units.append('')
    cs.setunits(units)
    shape = ia.shape()
    ndim = len(shape)

    # TAKE VELOCITY TO BE FIRST SPECTRAL INDEX
    axis_types = cs.axiscoordinatetypes()
    has_vaxis = (axis_types.count("Spectral") > 0)
    if has_vaxis:
        vaxis_num = axis_types.index("Spectral")    
    else:
        only_sky = True

    # ------------------
    # VELOCITY DIMENSION
    # ------------------

    if only_sky == False:

        # ... CHANGE THE REST FREQUENCY (IF DESIRED)
        if restfreq != None:
            cs.setrestfreq(restfreq)
            
        ind = np.indices((shape[vaxis_num],))
        pix = np.zeros((ndim,shape[vaxis_num]))
        pix[vaxis_num,:] = ind.flatten()
        world = cs.toworldmany(pix)['numeric']
        faxis = world[vaxis_num,:].flatten()
        
        if freq == False:
            # ... UGH, SUCH A KLUGE: GO TO LIST THEN BACK TO NP ARRAY
            vaxis = np.array(cs.frequencytovelocity(faxis.tolist()))
        else:
            vaxis = faxis

    # ----------------
    # SKY DIMENSIONS
    # ----------------
    if only_v == False:

        # ... MAKE IMAGES OF INDICES IN THE (X,Y)
        ind = np.indices((shape[0],shape[1]))
        pix = np.zeros((ndim,shape[0]*shape[1]))

        # ... FORM THESE INTO A 4 X N_POINTS ARRAY AND FEED TO THE CS TOOL
        pix[0,:] = (ind[0,:,:]).flatten()
        pix[1,:] = (ind[1,:,:]).flatten()
        world = cs.toworldmany(pix)['numeric']

        # ... REFORM THE OUTPUT INTO RA AND DEC IMAGES
        ra_img = world[0,:].reshape(shape[0], shape[1])
        dec_img = world[1,:].reshape(shape[0], shape[1])


    # CLOSE THE IA TOOL
    ia.close()

    # RETURN VELOCITY ONLY
    if only_v == True:
        return vaxis

    # RETURN SKY ONLY
    if only_sky == True:
        if image == True:
            return ra_img, dec_img
        else:
            # IF THE USER WANTS A 1-D AXIS, TAKE THE MIDDLE COLUMN AND ROW
            ra_axis = ra_image[:,shape[1]/2]
            dec_axis = ra_image[shape[0]/2,:]
            return ra_axis, dec_axis
    
    # RETURN ALL
    if image == True:
        return ra_img, dec_img, vaxis
    else:
        ra_axis = ra_image[:,shape[1]/2]
        dec_axis = ra_image[shape[0]/2,:]
        return ra_axis, dec_axis, vaxis

# -----------------------------------------------------
# CONVERT A VECTOR OF RA AND DEC COORDINATES TO PIXELS
# -----------------------------------------------------
    
def adv_to_xyz(imname, ra=None, dec=None, v=None
               , restfreq=None, freq=False):
    """ 
    Accept {RA, Dec, velocity} for a given image and return the
    corresponding {X, Y, Z} pixel coordinates.

    OPTIONS:

    If you leave v unset it works only on the sky coordinates and
    returns only x, y. Similarly, if you leave ra or dec unset, it
    works only on the spectral coordinate.

    restfreq (None) : force a particular resfreq

    freq (False) : the "v" axis is already in frequency units

    """
    
    # INSERT ERROR-CHECKING HERE

    # CHECK IF THIS IS A SKY ONLY OR VELOCITY ONLY CALL
    if v==None and ra != None and dec != None:
        sky_only = True
    else:
        sky_only = False

    if v != None and (ra == None or dec == None):
        v_only = True
    else:
        v_only = False
    
    # FORCE INTO NUMPY ARRAYS IF NOT ALREADY THERE
    if v_only == False:
        if type(ra) != type(np.array([0])):
            use_ra = np.array(ra)
            use_dec = np.array(dec)
        else:
            # ... SHOULD CREATE A VIEW, NOT COPY THE DATA
            use_ra = ra
            use_dec = dec
    
    if sky_only == False:
        if type(v) != type(np.array([0])):
            use_v = np.array(v)
        else:
            use_v = v

    # NOTE NUMBER OF DATA POINTS
    if sky_only == True:
        npts = use_ra.size
    else:
        npts = use_v.size

    # EXTRACT THE SHAPE AND COORDSYS OF THE IMAGE
    ia.open(imname)
    cs = ia.coordsys()
    units = []
    for ctype in cs.axiscoordinatetypes():
        if ctype == "Direction":
            units.append('deg')
        if ctype == "Spectral":
            units.append('Hz')
        if ctype == "Stokes":
            units.append('')
    cs.setunits(units)
    shape = ia.shape()
    ndim = len(shape)

    # TAKE VELOCITY TO BE FIRST SPECTRAL INDEX
    axis_types = cs.axiscoordinatetypes()
    has_vaxis = (axis_types.count("Spectral") > 0)
    if has_vaxis:
        vaxis_num = axis_types.index("Spectral")    
    else:
        sky_only = True

    # DEAL WITH DOPPLER SHIFTS IF NEEDED

    # ... CASE WHERE THE USER SUPPLIED FREQUENCY
    if freq == True and sky_only == False:
        use_f = use_v

    # ... CASE WHERE THE USER SUPPLIED VELOCITY
    if freq == False and sky_only == False:
        
        # ... IMPOSE THE USER-SPECIFIED REST FREQUENCY
        if restfreq != None:
            cs.setrestfreq(restfreq)
        
        # ... CONVERT FROM VELOCITY TO FREQUENCY
        use_f = np.array(cs.velocitytofrequency(use_v.tolist()))        
        

    # MAKE IMAGES OF INDICES IN THE (X,Y)    
    world = np.zeros((ndim,npts))
    
    if v_only == False:
        world[0,:] = use_ra
        world[1,:] = use_dec

    if sky_only == False:
        world[vaxis_num,:] = use_f

    # CONVERT VIA THE COORDSYS TOOL
    pix = cs.topixelmany(world)['numeric']
    x = pix[0,:]
    y = pix[1,:]
    if sky_only == False:
        z = pix[vaxis_num,:]

    # RETURN IN THE ORIGINAL SHAPE ACCORDING TO INPUT
    if v_only == True:
        z.reshape(use_v.shape)
        return z
    
    if sky_only == True:
        x.reshape(use_ra.shape)
        y.reshape(use_dec.shape)
        return x, y

    x.reshape(use_ra.shape)
    y.reshape(use_dec.shape)
    z.reshape(use_v.shape)
    return x, y, z

# -----------------------------------------------------
# CONVERT A VECTOR OF PIXEL COORDINATES INTO RA AND DEC
# -----------------------------------------------------

def xyz_to_adv(imname, x=None, y=None, z=None
               , restfreq=None, freq=False):
    
    """
    Accept {X, Y, Z} for a given image and return the
    corresponding {RA, Dec, Velocity}.

    OPTIONS:

    If you leave z unset it works only on the sky coordinates and
    returns only {RA, Dec}. Similarly, if you leave x or y unset,
    it works only on the spectral coordinate.

    restfreq (None) : force a particular resfreq

    freq (False) : return the "v" axis in frequency units

    """

    # PLACE ERROR CHECKING HERE

    # CHECK IF THIS IS A SKY ONLY OR VELOCITY ONLY CALL
    if z==None and x != None and y != None:
        sky_only = True
    else:
        sky_only = False

    if z != None and (x == None or y == None):
        v_only = True
    else:
        v_only = False

    # FORCE INTO NUMPY ARRAYS IF NOT ALREADY THERE
    if v_only == False:
        if type(x) != type(np.array([0])):
            use_x = np.array(x)
            use_y = np.array(y)
        else:
            # ... SHOULD CREATE A VIEW
            use_x = x
            use_y = y

    if sky_only == False:
        if type(z) != type(np.array([0])):
            use_z = np.array(z)
        else:
            use_z = z

    # NOTE NUMBER OF DATA POINTS
    if sky_only == True:
        npts = use_x.size
    else:
        npts = use_z.size
    
    # EXTRACT THE SHAPE AND COORDSYS OF THE IMAGE
    ia.open(imname)
    cs = ia.coordsys()
    units = []
    for ctype in cs.axiscoordinatetypes():
        if ctype == "Direction":
            units.append('deg')
        if ctype == "Spectral":
            units.append('Hz')
        if ctype == "Stokes":
            units.append('')
    cs.setunits(units)
    shape = ia.shape()
    ndim = len(shape)

    # TAKE VELOCITY TO BE FIRST SPECTRAL INDEX
    axis_types = cs.axiscoordinatetypes()
    has_vaxis = (axis_types.count("Spectral") > 0)
    if has_vaxis:
        vaxis_num = axis_types.index("Spectral")    
    else:
        sky_only = True

    # MAKE IMAGES OF INDICES IN THE (X,Y)    
    pix = np.zeros((4,npts))

    if v_only == False:
        pix[0,:] = use_x
        pix[1,:] = use_y

    if sky_only == False:
        pix[vaxis_num,:] = use_z

    # CONVERT VIA THE COORDSYS TOOL
    world = cs.toworldmany(pix)['numeric']

    ra = world[0,:]
    dec = world[1,:]
    fr = world[vaxis_num,:]
    
    # APPLY DOPPLER SHIFT
    if freq == False:

        # ... IMPOSE THE USER-SPECIFIED REST FREQUENCY
        if restfreq != None:
            cs.setrestfreq(restfreq)

        # USE THE COORDSYS TOOL TO CALCULATE THE DOPPLER SHIFT
        spec = np.array(cs.frequencytovelocity(fr.tolist()))
    else:
        spec = fr
        
    # RETURN IN THE ORIGINAL SHAPE ACCORDING TO INPUT
    if v_only == True:
        spec.reshape(use_z.shape)
        return spec
    
    if sky_only == True:
        ra.reshape(use_x.shape)
        dec.reshape(use_y.shape)
        return ra, dec

    ra.reshape(use_x.shape)
    dec.reshape(use_y.shape)
    spec.reshape(use_z.shape)
    return ra, dec, spec

