# Quick Array Combinations

There are a number of techniques around to combine interferometric
array data, in particular adding short spacings information.  The
"QAC" functions (they are not formally CASA tasks)

In addition to **tp2vis.py** there are some functions for testing,
regressions and a few other helper functions that make life easier for
developers, but otherwise don't add any real tp2vis core functionality.


Loading QTP ("Quick TP") and TP2VISPLOT in the usual way we also do this
for TPVIS:

         execfile('qtp.py')
         execfile('tp2visplot.py')

after which a few new functions are available.  We show some examples
here, but detailed examples can be found in the the individual
workflow's listed below 

## 1. Making a pointing (**ptg**) file: qtp_ms_ptg()

The base [README](README.md) describes a standard Unix, but pretty
horrific, procedure that requires you to run **listobs()** and parse
the output using standard unix tools grep and awk. You can find the
example for M100 in [example1](example1.md), but be aware that this example
could easily fail for different sources or new versions of listobs.

In the QTP tools you would simply use

         qtp_ms_ptg('aver_12.ms', 'aver_12.ptg')

where from an MS file it produces a PTG file. Note that we expect also to be
able to produce PTG files that just cover where emission is given a sampling
frequency (e.g. nyquist) and dish size.

## 2. Find a reasonable RMS in a TP cube:   plot5()

We need to know the RMS in the TP cube from some line free channels. We showed an example how to judge that from
the first few or last channels. A better way is to plot the MIN,MAX,RMS so it is more obvious which
channels are line free.  This function is still in tp2visplot.py:


         plot5('M100_TP_CO_cube.bl.image')

Using matplotlib's pan and zoom it is now easy to identify the line free channels and, for example

	imstat('M100_TP_CO_cube.bl.image',axes=[0,1])['rms'][:6].mean()
	imstat('M100_TP_CO_cube.bl.image',axes=[0,1])['rms'][-6:].mean()

would give you a numeric value for average RMS at the two ends of the spectral range in this example.
See also example1 or workflow6.

## 3. Regression testing: qtp_stats()


As the result of a computation, some statistical properties of an
image (or measurement set) can be used to check if the results agree with a baseline
result. We call this a regression (or baseline) test. It can be
used in two ways. Either a text string has to exactly match, or
the individual floating point values need to agree within a certain
margin. Let's assume an image **test123.im*** would have been
produced, the two ways to test these would be

	t123 = '11.163420726184935 24.116404990046043 -5.2444772720336914 171.04049682617188 8296.5438525100362'

	qtp_stats('test123.im', t123)
or
	qtp_stats('test123.im', t123, 0.00001)

the output would be something like

	QTP_STATS: test123.im  11.163420726184935 24.116404990046043 -5.2444772720336914 171.04049682617188 8296.5438525100362 OK

or a **FAILED regression** message with the **EXPECTED** output to compare to. In logfiles this can then be easily checked for.

### Example regression tests

For TP2VIS we employ the following regression tests (note you will need to get appropriate data sets)

	execfile('workflow1.py')

## Installation

The current public distribution does not go beyond telling you to copy
tp2vis.py in your working directory, so you must

    	execfile('tp2vis.py')

The file INSTALL in the full distribution explains a few other ways how you can , or might, install TP2VIS.
Short end of the story: no more execfile, and no more need to copy tp2vis.py files around.

## Example Workflows

In addition to the standard M100 [example1:](example1.md)  we have several workflows that also serve as
regressions tests in development.

* [workflow1:](workflows/workflow1.md) ALMA **cloud197** (LMC)  [our standard regression test]
* [workflow2:](workflows/workflow2.md) ALMA **SWBarN** (SMC)  [private data]
* [workflow3:](workflows/workflow3.md) Combining VLA with GBT [under development]
* [workflow4:](workflows/workflow4.md) Synthetic SkyModel Simulations (see also [MAP4SIM](map4sim.md) how to create models) 
* [workflow5:](workflows/workflow5.md) ALMA **Lupus 3 MMS** [private data]
* [workflow6:](workflows/workflow6.md) ALMA **M100** science verification (this should follow [example1](example1.md)) [example demo, including regression]

Example datasets for some of these workflows can be found in http://admit.astro.umd.edu/~teuben/TP2VIS (currently 4 and 6)


## References

* CASA reference manual and cookbook : http://casa.nrao.edu/docs/cookbook/
   * Measurement Set: https://casa.nrao.edu/casadocs/latest/reference-material/measurement-set
   * MS V2 document: [MS v2 memo](https://casa.nrao.edu/casadocs/latest/reference-material/229-1.ps/@@download/file/229.ps)
* CASA simulations: https://casa.nrao.edu/casadocs/latest/simulation
  * Simulations (in 4.4) https://casaguides.nrao.edu/index.php/Simulating_Observations_in_CASA_4.4
  * See also our [workflow4](workflow4.md)
* CASA single dish imaging:  https://casa.nrao.edu/casadocs/latest/single-dish-imaging
* CASA feather: https://casa.nrao.edu/casadocs/latest/image-combination/feather
* CASA data weights and combination:  https://casaguides.nrao.edu/index.php/DataWeightsAndCombination
* Nordic Tools SD2VIS: https://www.oso.nordic-alma.se/software-tools.php
* Kauffman's *Adding Zero-Spacing* workflow: https://sites.google.com/site/jenskauffmann/research-notes/adding-zero-spa
* Papers of interest:
  * [Ekers and Rots]()
  * [Jorsater and van Moorsel 1995](http://adsabs.harvard.edu/abs/1995AJ....110.2037J)
  * [Kurono, Morita, Kamazaki 2009](http://adsabs.harvard.edu/abs/2009PASJ...61..873K)
  * [Koda et al. 2011](http://adsabs.harvard.edu/abs/2011ApJS..193...19K)
