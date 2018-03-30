# QAC

The qac_ routines help you writing short python scripts that
orchestrate various array combination simulations and to some degree
real data as well.

In general you would do all the work
within a project directory, similar to how CASA's **simobserve()**,
where the names of files inside the
directory have a fixed meaning, and only the directory name (the 'project')
has a meaning for the observer.

For example, In our test/ directory they are just
called 'test1', 'test1-alma', 'test1-SSA', 'test2', etc.

## Summary

A typical simulation script might ook as follows. Explanations follow
next:

    qac_ptr(phasecenter,"test123.ptg")
    qac_vla("test123","skymodel.fits", 4096, 0.01, ptg="test123.ptg",phasecenter=phasecenter)
    qac_clean1("test123/clean1",phasecenter=phasecenter)

## Logging

Standard CASA logging is using , and you can use the python **print** function
in the usual way.  You can use the function

    qac_log(msg)

to space your output with a header type message.

## Performance

To measure performance, you can of course use the unix "time" prefix to your command,
e.g.

    time casa --nogui -c  sim1.py  a=1 b=10 c=100

but this only gives the final compute times of the script, nothing internal.

Every qac_ command will tag the output with a timestamp, and optionally measure
virtual and real memory. This is added to the standard python **logging** output.
But you must start and end your code as follows:

    qac_begin("test1-alma")
    qac_version()
    ....
    qac_end()

and the output will contain things like


    INFO:root:test1-alma BEGIN [ 0.  0.]
    INFO:root:test1-alma ptg  [  3.44000000e-04   3.42130661e-04   1.13960547e+03   1.90476562e+02]
    INFO:root:test1-alma alma  [  4.00000000e-04   3.99827957e-04   1.13960547e+03   1.90476562e+02]
    INFO:root:test1-alma alma  [  143.253957     331.35863519  6093.55859375  4505.33203125]
    INFO:root:test1-alma alma  [   39.554776      39.0021348   4701.64453125  3106.890625  ]
    INFO:root:test1-alma alma  [   35.794047      35.00777411  4765.64453125  3108.046875  ]
    INFO:root:test1-alma alma  [   41.075288      39.60072398  4765.64453125  3108.12890625]
    INFO:root:test1-alma alma  [   34.188305      32.5692451   4765.64453125  3108.12890625]
    INFO:root:test1-alma clean1  [   34.755774      34.09187388  4765.64453125  3108.12890625]
    INFO:root:test1-alma clean1  [ 1000.589456     309.20978689  4765.66796875  3110.734375  ]
    INFO:root:test1-alma tpdish  [ 1026.255616     315.74331117  4765.66796875  3110.734375  ]
    INFO:root:test1-alma tpdish  [   23.116537      22.50622487  4765.66796875  3111.6015625 ]
    INFO:root:test1-alma feather  [   23.429309      22.71242213  4765.66796875  3111.6015625 ]
    INFO:root:test1-alma stats  [  4.65160000e-01   1.48370099e+00   4.76566797e+03   3.11174219e+03]
    ....
    INFO:root:test1-alma smooth  [  1.16539000e-01   6.64260387e-02   4.76566797e+03   3.11183594e+03]
    INFO:root:test1-alma stats  [    8.981304       6.08805799  4765.66796875  3111.8359375 ]
    INFO:root:test1-alma done  [  2.18567800e+00   6.15752935e-01   4.76566797e+03   3.11183594e+03]
    INFO:root:test1-alma END [ 2483.496519    1244.87865996]

whereas in this case the **time**  command-prefix would have given just the END result:


    2418.71user 68.66system 20:48.26elapsed 199%CPU (0avgtext+0avgdata 7029656maxresident)k
    18162112inputs+36370600outputs (130major+11010875minor)pagefaults 0swaps

Some interestsing observations is the CPU (first number) and WALL (second number) clock, and many
routines will have the WALL less than the CPU time, indication that a good amount of parallelism
was achieved. But not always, and the above listing clearly shows some puzzling behavior why
some do have a good ratio, others are near 1.

## Simulation routines

As mentioned before,the project directory is within which all the work occurs. Some routines will accumulate
(e.g. qac_vla()), others will remove that project directory and rebuild that directory (e.g. qac_clean1). The
user will remember to orchestrate them inside each where needed, e.g.

    qac_vla("test1", cfg=0, ...
    qac_clean1("test1/clean0", ...
    
    qac_vla("test1", cfg=1, ...
    qac_clean1("test1/clean1", ...

    mslist = glob.glob("test1/*.ms")
    qac_clean1("test1/clean2", mslist, ...)


### qac_vla(project, skymodel, imsize, pixel, phasecenter, freq, cfg, niter, ptg)

This is usually how you start a simulation, from a skymodel you create a measurement set reprenting a configuration.
Since the ngVLA can have multiple configurations, you would need call this routine multiple times, e.g.

    qac_vla("test1", cfg=0, ...)
    qac_vla("test2", cfg=0, ...)

Setting different  weights based on dish sizes will need to be implemented. See also qac_alma(). See also
[**simobserve()**](https://casa.nrao.edu/casadocs/latest/global-task-list/task_simobserve/about)

### qac_alma(project, skymodel, imsize, pixel, phasecenter, freq, cycle, cfg, niter, ptg)

Just for kicks, we have way to create ALMA observations from diffent cycle's and cfg's. We automatically add
a visweightscale to the WEIGHT column to properly account for the dish size if you do a combination tclean.

### qac_clean1(project, ms, imsize, pixel, niter, weighting, startmodel, phasecenter, **line)

This is simply a front end to CASA's **tclean()**. Interesting note is that **niter** can be a list here,
e.g. niter=[0,1000,2000], thus creating a series of dirtymaps.

[**tclean()**](https://casa.nrao.edu/casadocs/latest/global-task-list/task_tclean/about)

### qac_clean()

Unclear if we keep this routine. Don't use for now.

### qac_tp_otf(project, skymodel, dish, label, freq, template)

Create the OTF map via a simple smooth.

NOTE: **simobserve** also has an **obsmode=sd** keyword, which creates
a Measurement Set representing the autocorrelations of a TP (sd) map. After this you would need to map
this MS into a casa image, using the
[**sdimaging()**](https://casa.nrao.edu/casadocs/latest/global-task-list/task_sdimaging/about)
task.

See Mangum et al.'s (2007) paper : https://www.aanda.org/articles/aa/pdf/2007/41/aa7811-07.pdf

### qac_tp_vis(project, imagename, ptg, imsize, pixel, niter, phasecenter, rms, maxuv, nvgrp, fix, deconv, **line)

TP2VIS method. Not covering here yet.


### qac_feather(project, highres, lowres, label, niteridx)

Feather two maps that were created from qac_clean1 and qac_tp_otf

### qac_ssc(project, highres, lowres)



### qac_smooth(project, skymodel, label, niteridx)

Smooth a skymodel so it can be compared to a (feathered for now) map.

### qac_combine

Futuristic routine that automatically detects (via the argumnent list) what the intent is,
and then combines MS/IM things into a map.

## Helper routines

### qac_stats

### qac_beam

### qac_tpdish

### qac_phasecenter

### qac_ptg

We should re-import the qac_im_ptg routine from qtp. See below.

### qtp_im_ptg(phasecenter, imsize, pixel, grid, im=[], rect=False, outfile=None)

this should possibly become an qac_im_ptg 

### qac_summary

### qac_math

Just a super simple front-end to immath, so we can wrote code such as

    qac_math(out, in1, '+', in2)

it only allows the four basic operators combining two maps. Partially driven because immath
does not have the overwrite=True option.
[**immath()**](https://casa.nrao.edu/casadocs/latest/global-task-list/task_immath/about)

### qac_mom

Compute moments 0,1 (and soon 2) in some standard way, so we can compare simulations and skymodels.

[**immoments()**](https://casa.nrao.edu/casadocs/latest/global-task-list/task_immoments)

### qac_plot(image, box, plot)

Create a simple colorimage from a casa imasge. By default it appends "png" to the current name.

[**imview()**](https://casa.nrao.edu/casadocs/latest/global-task-list/task_imview)  but seems
to have some hysteresis problem with plot size.

### qac_flux(image, box, dv, plot)

Create a plot showing flux as function of channel. Good to compare flux comparisons
between various simulations and skymodels.