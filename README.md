# Quick Array Combinations

There are a number of techniques around to combine interferometric
array data, in particular adding short spacings information.  The
"QAC" functions (they are not formally CASA tasks) hide some of
the complexity of writing CASA scripts and provide a simple
interface to array combinations.

The project was born out of the TP2VIS project, and was used to
provide a number of examples, and regression tests.

See the [INSTALL](install) file for ways how to use these functions
in your CASA shell.



## Example Workflows

In addition to the standard M100 [example1:](example1.md)  we have several workflows that also serve as
regressions tests in development.

* [workflow1:](workflows/workflow1.md) ALMA **cloud197** (LMC)  [our standard regression test]
* [workflow2:](workflows/workflow2.md) ALMA **SWBarN** (SMC)  [private data]
* [workflow3:](workflows/workflow3.md) Combining VLA with GBT [under development]
* [workflow4:](workflows/workflow4.md) Synthetic SkyModel Simulations (see also [MAP4SIM](map4sim.md) how to create models) 
* [workflow5:](workflows/workflow5.md) ALMA **Lupus 3 MMS** [private data]
* [workflow6:](workflows/workflow6.md) ALMA **M100** science verification (this should follow [example1](example1.md)) [example demo, including regression]

Example public datasets for some of these workflows can be found in http://admit.astro.umd.edu/~teuben/TP2VIS (currently 4 and 6). For
other workflows, contact us if the PI has released the data.


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
  * Braun and Walterbos  197x?
  * Vogel et al.   1984?
  * [Jorsater and van Moorsel 1995](http://adsabs.harvard.edu/abs/1995AJ....110.2037J)
  * [Kurono, Morita, Kamazaki 2009](http://adsabs.harvard.edu/abs/2009PASJ...61..873K)
  * [Koda et al. 2011](http://adsabs.harvard.edu/abs/2011ApJS..193...19K)
