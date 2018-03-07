"""
Grab bag of routines for astronomical geometry calculations. Goddard
IDL libraries plundered liberally. Will gleefull replace once someone
puts out a general replacement.
"""

import math
import numpy as np

# ------------------------------------------------------------
# CALCULATE ANGULAR DISTANCE
# ------------------------------------------------------------

def ang_dist(lon1, lat1, lon2, lat2, degrees=False):
    """
    Calculates angular (great circle) distance between points. Follows
    Goddard IDL sphdist. It wants either matched array lengths or for
    one of the two coordinate pairs to be scalars.
    """

    # ACCOUNT FOR DEGREES/RADIANS
    if degrees == True:
        ang_fac = math.pi/180.0
    else:
        ang_fac = 1.0

    # CONVERT TO RECTANGULAR COORDINATES
    rxy = 1.0*np.cos(lat1*ang_fac)
    z1 = 1.0*np.sin(lat1*ang_fac)
    x1 = rxy*np.cos(lon1*ang_fac)
    y1 = rxy*np.sin(lon1*ang_fac)

    rxy = 1.0*np.cos(lat2*ang_fac)
    z2 = 1.0*np.sin(lat2*ang_fac)
    x2 = rxy*np.cos(lon2*ang_fac)
    y2 = rxy*np.sin(lon2*ang_fac)
    
    # VECTOR DOT PRODUCT
    cs = x1*x2 + y1*y2 + z1*z2
    
    # VECTOR CROSS PRODUCT
    xc = y1*z2 - z1*y2
    yc = z1*x2 - x1*z2
    zc = x1*y2 - y1*x2
    sn = np.sqrt(xc*xc + yc*yc + zc*zc)
    
    # BACK TO ANGLE (NOTE Y, X)
    return np.arctan2(sn, cs)*1.0/ang_fac

# ------------------------------------------------------------
# GENERATE A HEXAGONAL GRID
# ------------------------------------------------------------

def hex_grid(ctr_x=0.0, 
             ctr_y=0.0, 
             spacing=1.0,
             radec=False, 
             radius=1.001,
             posang=0.0):   
    """Generate an array of hexagonally spaced points with a specified
    center and spacing. There should always be a point at the
    center. Returns x, y. Optionally treat x as an 'RA-like'
    coordinate and scale the spacings by cosine(y).

    Documented : June '11 aleroy@nrao.edu
    """

    import math    
    import numpy

    # Y-SPACING OF THE GRID
    y_spacing = spacing*math.sin(math.radians(60.0))
    
    # X-SPACING OF THE GRID
    x_spacing = spacing

    # ESTIMATE THE X- AND Y-EXTENT
    scale = radius
    
    half_ny = math.ceil(scale / y_spacing)
    half_nx = math.ceil(scale / x_spacing) + 1
    
    # MAKE THE GRID
    x = numpy.outer(numpy.arange(0, 2*half_nx+1), numpy.ones(2*half_ny+1))
    y = numpy.outer(numpy.ones(2*half_nx+1), numpy.arange(0,2*half_ny+1))
    x -= half_nx
    y -= half_ny

    # IMPLEMENT THE X-SPACING
    x *= x_spacing

    # OFFSET THE ODD-NUMBERED X-ROWS
    x += 0.5 * x_spacing * ((y % 2) == 1)

    # IMPLEMENT THE Y-SPACING
    y *= y_spacing

    # APPLY THE ROTATION MATRIX IF REQUESTED    
    pa_rad = -1.0*math.pi/180.0*posang
    print pa_rad/math.pi
    rot_x = x * math.cos(pa_rad) - y * math.sin(pa_rad)
    rot_y = x * math.sin(pa_rad) + y * math.cos(pa_rad)
    x = rot_x
    y = rot_y

    # KEEP THE SUBSET THAT MATCHES THE REQUESTED CONDITION
    r = (x**2 + y**2)**0.5
    keep = numpy.where(r <= radius)
    x = x[keep]
    y = y[keep]
    
    # CREATE THE OUTPUT ARRAYS
    y += ctr_y

    # (OPTIONALLY) TREAT AS DECIMINAL RA AND DEC DEGREES
    if radec == True:
        x = x / numpy.cos(y*math.pi/180.) + ctr_x
    else:
        x += ctr_x

    return x, y
