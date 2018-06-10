# Workflows

During the TP2VIS development workflow's 1-6 were used to test the code.
See the respective workflow scripts (.py and/or .md) for details which
data were used.  Some workflows use PI data which may not be available
yet, however workflow 4 and 6 are freely available.

WARNINGS:
 1)  workflow md files are badly out of sync with their py countersparts
     (regresssion was deemed more important for now)
 2)  workflow 4 and 6 are the prime working one, and 1 is in pretty good 
     shape too



## Example Workflows

In addition to TP2VIS' standard 
[M100 example](https://github.com/tp2vis/distribute/blob/master/example1.md)
we have several workflows, some of which also served as regressions tests during the TP2VIS development. We keep those
here for reference, although most need to be updated for QAC and need updated graphics. (soon, i promise)

* [workflow1:](workflows/workflow1.md) ALMA **cloud197** (LMC)  [our standard regression test]
* [workflow2:](workflows/workflow2.md) ALMA **SWBarN** (SMC)  [private data]
* [workflow3:](workflows/workflow3.md) Combining VLA with GBT [under development]
* [workflow4:](workflows/workflow4.md) Synthetic SkyModel Simulations (see also [MAP4SIM](map4sim.md) how to create models) 
* [workflow5:](workflows/workflow5.md) ALMA **Lupus 3 MMS** [private data]
* [workflow6:](workflows/workflow6.md) ALMA **M100** science verification (this should follow [example1](example1.md)) [example demo, including regression]

Example public datasets for some of these workflows can be found in http://admit.astro.umd.edu/~teuben/QAC (currently 4 and 6). For
other workflows, contact us if the PI has released the data.

### Benchmarks

A better supported show of QAC functionality is currently in the **test/bench.py, bench0.py** and **sky1.py** routines [March 2018] as those were used in the
[SD2018](https://github.com/teuben/sd2018) workshop. Please note the software in that repo is not maintained anymore, and updated versions can be found
within QAC.
