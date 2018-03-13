#
#  Version:    31-jan-2018
#
#  In this version we use plot= to denote te plotfile name. in the "au" tools the "figfile="
#  keyword is used.  In imview() they use the "out=". Go figure for standardization, but we
#  should probably assume something standard.
#
#  Also:   plot=None could be used to not show a plot?
#
import matplotlib.pyplot as plt

# example figures made:
#   plot1('test1/tp.ms','aver_12.ms', 'aver_07.ms',11.0,plot='figures/plot1.png')
#   plot1('test1/tp.ms','aver_12.ms', 'aver_07.ms',200.0,plot='figures/plot1a.png')


def plot1(ms0=None, ms7=None, ms12=None, uvmax = 5.0, kwave=True, stride=1, plot='plot1.png'):
    """ Plotting several MS in a U-V plot
    ms0:     TP (but could be any)
    ms7:     7m (single MS)
    ms12:    12m (single MS)

    kwave:   True means converted to klambda, False means native (meters)
    stride:  Take every stride'd point to plot

    """
    def get_stride(uv, stride=1):
        if stride == 1:
            return uv
        (u,v) = uv
        idx = range(0,len(u),stride)
        return (u[idx],v[idx])
        
    (w,h) = plt.figaspect(1.0)
    plt.figure(figsize=(w,h))
    plt.xlim(-uvmax, uvmax)
    plt.ylim(-uvmax, uvmax)
    if ms0 != None:
        (u0,v0)  = get_stride(qtp_getuv(ms0,kwave),stride)
        plt.scatter(u0, v0, c='b',s=1)
    if ms7 != None:
        (u7,v7)   = get_stride(qtp_getuv(ms7,kwave),stride)
        plt.scatter(u7, v7, c='g',s=20)
    if ms12 != None:
        (u12,v12) = get_stride(qtp_getuv(ms12,kwave),stride)
        plt.scatter(u12,v12,c='r',s=60)
    if kwave:
        plt.xlabel("u (k$\lambda$)")
        plt.ylabel("v (k$\lambda$)")
    else:
        plt.xlabel("u (meter)")
        plt.ylabel("v (meter)")
    plt.savefig(plot)
    plt.show()

def plot1a(mslist, uvmax = 5.0, kwave=True, stride=1, plot='plot1a.png'):
    """ Plotting several MS as a heat map in a U-V plot
    mslist:  List of MS

    kwave:   True means converted to klambda, False means native (meters)
    stride:  Take every stride'd point to plot

    @todo   CASA's matplotlib doesn't seem to have hist2d()

    """
    def get_stride(uv, stride=1):
        if stride == 1:
            return uv
        (u,v) = uv
        idx = range(0,len(u),stride)
        return (u[idx],v[idx])
    
    from matplotlib.colors import LogNorm
       
    (w,h) = plt.figaspect(1.0)
    plt.figure(figsize=(w,h))
    plt.xlim(-uvmax, uvmax)
    plt.ylim(-uvmax, uvmax)
    u = np.array([])
    v = np.array([])
    for ms in mslist:
        (u0,v0)  = get_stride(qtp_getuv(ms,kwave),stride)
        u = np.append(u, u0)
        v = np.append(v, v0)
    # casa's plt doesn't have hist2d yet
    #plt.hist2d(u,v,bins=300, norm=LogNorm())
    #plt.colorbar()
    if kwave:
        plt.xlabel("u (k$\lambda$)")
        plt.ylabel("v (k$\lambda$)")
    else:
        plt.xlabel("u (meter)")
        plt.ylabel("v (meter)")
    plt.savefig(plot)
    plt.show()
    # since this fails, write the (u,v)'s to a file and use a more modern python
    if True:
        np.savetxt("plot1a.tab",(u,v))
        # (u,v) = np.loadtxt("plot1a.tab")

def plot1b(tab, uvmax = 5.0, bins=256, kwave=True, plot='plot1b.png'):
    """ Plotting several MS as a heat map in a U-V plot
    tab:     ascii table from loadtxt/savetxt via plot1a()

    kwave:   True means converted to klambda, False means native (meters)

    @todo   CASA's matplotlib doesn't seem to have hist2d()

    """
    (u,v) = np.loadtxt(tab)
    print u.min(),v.min(),u.max(),v.max()
    u = np.append(u,-u)
    v = np.append(v,-v)

    from matplotlib.colors import LogNorm
       
    (w,h) = plt.figaspect(1.0)
    plt.figure(figsize=(w,h))
    plt.hist2d(u,v,bins=bins, norm=LogNorm())
    # plt.colorbar()
    plt.xlim(-uvmax, uvmax)
    plt.ylim(-uvmax, uvmax)
    if kwave:
        plt.xlabel("u (k$\lambda$)")
        plt.ylabel("v (k$\lambda$)")
    else:
        plt.xlabel("u (meter)")
        plt.ylabel("v (meter)")
    plt.savefig(plot)
    plt.show()
    
def plot2(plot2file, f1=None, f2=None, plot='plot2.png'):
    """ Plotting flux as function of channel for various situations
        This is normally used to build up composite plots
    """
    plt.figure()
    _tmp = imstat(plot2file,axes=[0,1])
    if 'flux' in _tmp:
        flux = _tmp['flux']/1000.0
        totalflux = imstat(plot2file)['flux'][0]/1000.0
    else:
        flux = _tmp['sum']/1000.0
        totalflux = imstat(plot2file)['sum'][0]/1000.0
    rms = _tmp['rms']/1000.0
    chan = np.arange(len(flux))
    plt.plot(chan,flux,c='r',label='TP image')
    if f1 != None:
        plt.plot(chan,f1,c='g')
    if f2 != None:
        plt.plot(chan,f2,c='b')
    zero = 0.0 * flux
    plt.plot(chan,zero,c='black')
    plt.ylabel('Flux/1000')
    plt.xlabel('Channel')
    plt.title('%s  Total flux/1000: %f' % (plot2file,totalflux))
    plt.legend()
    plt.savefig(plot)
    plt.show()
    return flux

def plot2a(f, title='Flux Comparison', plot='plot2a.png'):
    """ Plotting flux as function of channel for various situations
        f = list of equal sized arrays of fluxes
        Also prints out the flux sums (sans the km/s factor we don't know)
    """
    plt.figure()
    chan = np.arange(len(f[0]))
    for (fi,n) in zip(f,range(len(f))):
        plt.plot(chan,fi,label='%d' % (n+1))
        print "Sum[%d]: %g Jy (* unknown km/s)" % (n+1,fi.sum())
    zero = 0.0 * f[0]
    plt.plot(chan,zero,c='black')
    plt.ylabel('Flux')
    plt.xlabel('Channel')
    plt.title(title)
    plt.legend()
    plt.savefig(plot)
    plt.show()
    return 


def plot3(mslist, log=True, kwave=True, plot='plot3.png'):
    """ Plotting several MS in a UVD - AMP plot

    mlist:   list of MS
    log:     logaritmic scale for AMP's
    kwave:   True means converted to klambda, False means native (meters)    

    This routine will probably run out of memory for large files, it needs to stream and collect
    due to keeping nchan 
    
    """
    def my_getamp(ms, log=True):
        tb.open(ms)
        data  = np.abs(tb.getcol('DATA')[0,:,:])     # -> data[nchan,nvis]
        amp = data.max(axis=0)
        tb.close()
        if log:  amp = np.log10(amp)
        print "AMP min/max = ",amp.min(),amp.max()
        return amp

    colors = ['r', 'g', 'b']
   
    plt.figure()
    if type(mslist) == str:
        mslist = [mslist]
    for (ms,c) in zip(mslist,colors):
        if iscasa(ms):
            print "Processing ",ms
            (u0,v0)  = qtp_getuv(ms,kwave)
            uvd = np.sqrt(u0*u0+v0*v0)
            amp = my_getamp(ms,log)
            plt.scatter(uvd,amp,c=c,label=ms)
        else:
            print "Skipping ",ms
    if kwave:
        plt.xlabel("uvdistance (k$\lambda$)")
    else:
        plt.xlabel("uvdistance (meter)")
    if log:
        plt.ylabel("log(amp[channel_max])")
    else:
        plt.ylabel("amp[channel_max]")
    plt.legend()
    plt.savefig(plot)
    plt.show()


def plot4(mslist, bin=None, kwave=True, plot='plot4.png'):
    """ Plotting several MS in a UVD - WEIGHT plot

    mslist:  list of MS
    bin:     if given, this is the binsize in kLambda for ring weight density
    kwave:   True in kLambda, False in native meters

    """
    def my_getwt(ms):
        tb.open(ms)
        data  = tb.getcol('WEIGHT')[:,:]         # -> data[npol,nvis]
        tb.close()
        return data

    colors = ['r', 'g', 'b']
   
    plt.figure()
    if type(mslist) == str:
        mslist = [mslist]
    for (ms,c) in zip(mslist,colors):
        if iscasa(ms):
            print "Processing ",ms
            (u0,v0)  = qtp_getuv(ms,kwave)
            uvd = np.sqrt(u0*u0+v0*v0)     # in kLambda (or meters)
            wt  = my_getwt(ms)
            print "PJT",wt.shape
            if bin == None:
                # only do the first pol
                plt.scatter(uvd,wt[0,:],c=c,label=ms)
                # plt.scatter(uvd,wt[1,:],c=c,label=ms)
            else:
                uvbins = np.arange(0.0,uvd.max() + bin, bin)
                #uvbins = np.arange(2.0,6.0,1.0)
                print uvbins
                print "UVD max",uvd.max()
                wt = wt[0,:]
                digit = np.digitize(uvd,uvbins)
                if True:
                    # weight density
                    wt_bin = [wt[digit == i].sum() for i in range(1,len(uvbins))]
                    print wt_bin
                    print len(uvbins),len(digit),len(wt_bin)
                    # @todo  check if i'm not off by 1/2 bin
                    uvarea = np.diff(uvbins*uvbins)
                    wt_bin = wt_bin / uvarea
                else:
                    # mean weight per uvbin
                    wt_bin = [wt[digit == i].mean() for i in range(1,len(uvbins))]
                    print wt_bin
                    print len(uvbins),len(digit),len(wt_bin)
                wt_bin = np.log10(wt_bin)
                plt.plot(uvbins[1:],wt_bin,drawstyle='steps-mid')
        else:
            print "Skipping ",ms
    if kwave:
        plt.xlabel("uvdistance (k$\lambda$)")
    else:
        plt.xlabel("uvdistance (meter)")
    if bin == None:
        plt.ylabel("weight[channel_max]")
    else:
        plt.ylabel("weight density")
    plt.legend()
    plt.savefig(plot)
    plt.show()

def plot5(image, box=None, plot='plot5.png'):
    """ Plotting min,max,rms as function of channel
    
        box     xmin,ymin,xmax,ymax       defaults to whole area

        A useful way to check the the mean RMS at the first
        or last 10 channels is:

        imstat(image,axes=[0,1])['rms'][:10].mean()
        imstat(image,axes=[0,1])['rms'][-10:].mean()
    
    """
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
    plt.plot(chan,f,   c='black', label='<peak>/rms')
    zero = 0.0 * frms
    plt.plot(chan,zero,c='black')
    plt.ylabel('Flux')
    plt.xlabel('Channel')
    plt.title('%s  Min/Max/RMS' % (image))
    plt.legend()
    plt.savefig(plot)
    plt.show()

def plot6(imlist, bins=50, range=None, log=False, alpha=[1, 0.3, 0.1], box=None, plot='plot6.png'):
    """ Plotting histograms on top of each other, nice for comparison

    imlist                            list of images
    box='xmin,ymin,xmax,ymax'         is the only syntax allowed here
    """
    def mybox(box):
        a = box.split(',')
        if len(a) != 4:
            return (0,0,0,0)
        xmin = int(a[0])
        ymin = int(a[1])
        xmax = int(a[2])
        ymax = int(a[3])
        return (xmin,ymin,xmax,ymax)
    
    plt.figure()
    for (i,a) in zip(imlist,alpha):
        data = ia.open(i)
        if box == None:
            data = ia.getchunk().ravel()
        else:
            (xmin,ymin,xmax,ymax) = mybox(box)
            if xmin==0 and xmax==0:
                print "Warning: bad box ",box
                data = ia.getchunk().ravel()
            else:
                data = ia.getchunk([xmin,ymin],[xmax,ymax]).ravel()
        ia.close()
        plt.hist(data,bins=bins,range=range,log=log,alpha=a)
    plt.savefig(plot)
    plt.show()
    
