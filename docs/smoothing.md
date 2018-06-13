# Intro

Here we assume you have installed the CASA package, and from within the terminal the **casa** command
has now started up casa shell, which is just an ipython terminal in disguise. So all your commands
are now python commands, but within CASA some commands (they call them tasks and tools) have new
meaning.

In this section we are viewing a model with an an ideal (radio) telescope in different ways.

## Skymodel

We have a file **skymodel.fits**, which is a model of a "random", but complex organized structure,
in the sky, matching more or less what we see in the galaxy.

In CASA the command

    imview('skymodel.fits')

will show an image of this sky in a much detail as possible. Learn how to zoom into
sections by left-mouse-button selecting a region. This region will show up as green, which
you can drag around by left-mouse selection it within that region (practice that!). You can
also left-mouse select a corner, and resize the rectangle.  Now double click on it, and watch
how it adjusts to the new viewport.

## Resolution

The CASA command

    imhead('skymodel.fits')

will report some header variable of this image. For example where in the sky it was looking, how
large the pixels are, what units the measurements are in etc.etc. Look in the logger window, but can
you find how large the pixels are.  Do you see 0.05 arcsec ?  Can you see how many pixels the size of
this image is?   Do you see 4096 by 4096 along axis 0 and 1. What about axis 2 and 3. Do you see what
meaning they have?

Once you zoom in too much, you want to zoom out of course. That's a little odd, you again select
a small area, but now don't click inside, but outside the rectangle. You may need to repeat this procedure
a few times, depending how much you zoomed in.

Now go and hunt for the pixel with the largest intensity. Did you find one with a brightness of 0.1 ? Which
pixel was that?  Did you find (3038,2245) ?

## Smoothing

A typical optical telescope on earth would probably have a resolution of 1-2 arcsec. So let's use a program
in CASA to simulate the effects of the atmosphere and blurr the image to a resolution of 2 arcsec.

    imsmooth('skymodel.fits','gauss',outfile='smooth2.im',major='2arcsec',minor='2arcsec',pa='0deg')

and now look at this image

    imview('smooth2.im')

Zoom in and out again, and find the largest pixel value. Is it at the same pixel as the original image?
Also notice that in that image a white circle is drawn in the lower left corner. Any guess what that might
be?   As you zoom in you will the size of that circle also change.


## Comparing images

To answer the previous question if the peak is on/near the same pixel, perhaps comparing two images will
be better. The viewer has this option under the "Data" tab , see top left.  Use Data->Open to select the other image,
skymodel.fits in this case. But don't click on Update, instead click on Rasterimage and then close this window. The
panel on the right should now show a movie like interface, where you can step through images, or play a movie, or pause
the movie. Also a frame rate, the default is 10 Hz. Play with all of those while you zoom into the regionwhere the peak is
and see if you now can see if the peak in the two images is on the same pixel or not.


## smoothing

In radio astronomy the smoothing beam is not always round. Play with the following image and see if you get a feeling
what this means:

    imsmooth('skymodel.fits','gauss',outfile='smooth4.im',major='4arcsec',minor='2arcsec',pa='30deg')

Now load all three images, smooth4.im, smooth2.im and skymodel.fits in your viewer and cycle through them.


## Real beam

The formula to compute the beam (resolution) is

   theta = 1.13 lambda / D

where *lambda* is the wavelength of the signal, and *D* the diameter of the dish. You can also write this in terms
of the frequency, which if you look at the header of the image again, is 115 GHz.

   theta = 1.13 c / (f D)

where *c* is the speed of light.

Compute what the beam should be for a 6m dish, for an 18m dish, and finally a 45m dish.
