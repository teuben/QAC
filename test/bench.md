# Benchmark Notes 

Benchmarks can be tricky, and modern machines with multiple CPUs, cores and multithreads
that are sensitive to heat all result in situations. Not to mention a parallel cluster,
which we will not cover here.

As it turns out CASA is throwing us some tricky curve balls with benchmarks,
we also add a more classical benchmark to confirm the general picture.

1. Programs should avoid using multithreads on a core. Something like this might be useful

       export OMP_NUM_THREADS=$(lscpu | grep core: | awk -F: '{print $2}')
       
1. To use **tmpfs** (e.g. /dev/shm) on linux seems to degrade the CPU in CASA on some machines.
   Not understood.   Laptops bad, but even subaru degraded, but in a subtle different way (R1 vs. R2)
   Xeon may do a better job.

1. To test the I/O portion of **tclean** in major cycles ...  vislab1 with 512GB memory should be
   a good test, assuming we understand the previous item

1. A simple NEMO program has the expected behavior.

1. On many laptops with less than optimal cooling using more than one core can
   result in a lowering of the cpufreq. Due to cpu hopping it might have a sweet
   spot of using half the cores. The **cpufreq** program can manually set some
   performance related parameters.



Useful links in the CASA memo series:

1. https://casa.nrao.edu/casadocs/casa-6.1.0/memo-series/casa-memos/casa_memo4_imagerparallelization_bhatnagar.pdf/view		

1. https://casa.nrao.edu/casadocs/casa-6.1.0/memo-series/casa-memos/casa_memo5_performance_emonts.pdf/view

## Preparation

Based on having QAC (for code) and dc2019 (for data)

      workdir=/dev/shm      # or pick /tmp , or anything
      cd ~/QAC/test
      cp Makefile skymodel-b.fits skymodel-b.py sky0.py sky4.py $workdir
      cd $workdir
      ln -s ~/dc2019/data/gmcSkymodel/gmc_2L


## sky0f0

This is a quick test, but showing that moving to memory it barely has an impact, if
you look at the system time. Presumably because the disk I/O component is too small.
The benchmark can be run with:

      make sky0f0

and here are some results


      T480   hdd   28.29user 4.04system 0:25.90elapsed 124%CPU (somewhat busy machine)
             shm   16.94user 4.05system 0:22.07elapsed  95%CPU
      X1Y4   hdd    9.56user 1.25system 0:12.15elapsed  89%CPU
             shm    9.30user 1.12system 0:11.79elapsed  88%CPU
      XPS13  hdd    4.37user 1.00system 0:11.63elapsed  46%CPU OMP_NUM_THREADS=1
             shm    4.28user 0.91system 0:11.30elapsed  45%CPU
             shm    4.28user 0.91system 0:11.30elapsed  45%CPU 

## sky4z

This is the medium scale, with the (old) small gmc_2L model. This one
is still confusing, on shm it actually runs slower, despite that there is
enough memory.
The benchmark can be run with:

      make sky4z

and here are some results

      T480    hdd   7772.26user  273.52system   34:49.61elapsed 385%CPU
              shm   
      X1Y4    hdd   5439.75user  196.41system   20:43.28elapsed 453%CPU 
              shm  10287.44user  364.05system   41:54.90elapsed 423%CPU 
      XPS13   hdd   4157.42user  207.88system   16:35.48elapsed 438%CPU 
              shm   7519.31user  355.76system   33:36.69elapsed 390%CPU
      subaru  hdd   2940.37user  269.61system   24:43.23elapsed 216%CPU
              shm   3321.94user  272.76system   36:58.58elapsed 162%CPU
      vislab1 hdd
              shm
	      
      QAC_STATS: export/sky_tweak_box1.fits 1.0010571278181761 1.5930145349309555 -0.69122767448425293 8.9708108901977539 6565.3723606948697 0.942194

What is disturbing here that running on **shm** it takes significantly longer. Even in single processor mode. I don't understand this at all.


Looking more carefully at the performance as function of the number of processors. This time on a properly cooled desktop, so the cpufreq is not scaled
down as more processors are used. Two time ratio come to mind to measure how well the the script runs in parallel mode, called R1 and R2 here:


      R1 = user(N)/user(1)                 should be 1, more is bad
      R2 = elapsed(N)/(elapsed(1)/N)       should be 1, more is bad

      yorp20 (2 AMD processors, each has 8 cores, each as 2 hyperthreads)
                   N                                                            R1     R2     P
                   1  4226.02user  528.60system 1:27:35elapsed     90%CPU      1.00    1.00   -
		   2  4742.79user  593.14system 1:21:15elapsed    109%CPU      1.12    1.97   0.03
		   4  5263.59user  646.97system 1:16:14elapsed    129%CPU      1.25    3.49   0.17
		   8  6549.89user  868.98system 1:15:46elapsed    163%CPU      1.55    6.91   0.16
		  16  8898.89user 1138.71system 1:13:16elapsed    228%CPU      2.11   13.40   0.17
		  32 42515.81user 2450.67system 1:32:44elapsed    808%CPU     10.1    33.8    <0		  
		   
      QAC_STATS: export/sky_tweak_box1.fits 0.99950875761575164 1.5935251499479519 -0.65302145481109619 9.0135574340820312 6555.21746878248 0.938545
      QAC_STATS: export/sky_tweak_box1.fits 0.99950884279055641 1.5935252376332345 -0.65302163362503052 9.0135564804077148 6555.2180273962631 0.938545
      QAC_STATS: export/sky_tweak_box1.fits 0.99950884116341465 1.5935252456381339 -0.65302175283432007 9.0135564804077148 6555.2180167247525 0.938545 
      QAC_STATS: export/sky_tweak_box1.fits 0.99950886461600275 1.5935252574245784 -0.65302151441574097 9.0135564804077148 6555.2181705371268 0.938545 
      QAC_STATS: export/sky_tweak_box1.fits 0.99950883428423687 1.5935252410596366 -0.65302187204360962 9.0135564804077148 6555.2179716080827 0.938545
      QAC_STATS: export/sky_tweak_box1.fits 0.99950880441636714 1.5935251967772344 -0.65302157402038574 9.0135564804077148 6555.217775721474 0.938545 


As long as R2 < N, you can still believe in Ahmdal's law.  But the fact that R1 > 1 already hints at problems, since Amdahl assumes R1 = 1 for all N.
The (effective) parallel fraction of code (p) is given by:

      P = (N - R2) / (N - 1)

The reasons for R1 > 1 can be two fold:  for laptops the cpufreq goes down as more cores are used and the kernel is not able to use cpu hopping to prevent
overheating. Secondly the penalty for OpenMP to open and close threads can sit in the way. Since yorp20 already shows a growing R1, for this CASA example
there is already an issue with non-optimal OpenMP usage.

## sky4z - tclean only

The sky4z benchmark just described is a mix of a large number of CASA tasks and does not really reflect the core of the cpu task that most
people will use: tclean.   Therefore a spin-off of sky4z can be used to benchmark just tclean where all of the CPU is spent in tclean. It depends
on sky4z having been run at least once, such that the MS data are present.   If not, there is a fast bootstrap method to get it ready for the
benchmark:

      casa --nogui -c sky4.py pdir='"sky4z"' datafile='"skymodel-b.py"' bench=-1

after which the benchmark can be run under a variety of conditions, e.g.

      OMP_NUM_THREADS=4 /usr/bin/time casa --nogui -c sky4.py pdir='"sky4z"' datafile='"skymodel-b.py"' bench=1 niter='[0,1000]'

This allows you to study the dependance on the number of processors and number of major cycles via niter= on the disk I/O, memory etc.


## sky4

      XPS13  hdd   6637.55user 329.92system 28:51.53elapsed 402%CPU busy>
                   6460.71user 311.96system 27:49.63elapsed 405%CPU
		   6508.26user 310.58system 27:57.96elapsed 406%CPU   uncached
		   6405.97user 310.07system 27:43.83elapsed 403%CPU
             shm   6387.34user 299.42system 27:15.54elapsed 408%CPU

Very odd, here we have an example where the CPU is not larger on **shm**.

## M100

Although the full benchmark still suffers from a CASA edge-channel bug, it maps 5 out of
the 70 channels of the standard M100 casaguide feather benchmark.  The data must have been prepared via
http://admit.astro.umd.edu/~teuben/QAC/qac_bench5.tar.gz, which creates three files:

      make M100data

which creates

      M100_TP_CO_cube.bl.image
      M100_aver_12.ms
      M100_aver_7.ms

the benchmark (which creates a new directory M100qac) can be run via

      make M100feather

On a desktop (with 6 cores)

      N                                                       R1    R2    P
      1   1873.99user 217.05system 44:31.13elapsed  78%CPU   1.00  1.00  -
      2   2003.04user 227.69system 38:24.37elapsed  96%CPU   1.07  1.72  0.28
      4   2286.83user 233.42system 35:07.95elapsed 119%CPU   1.21  3.15  0.28
      6   2826.72user 316.75system 34:18.85elapsed 152%CPU   1.50  4.61  0.28
     12   4840.44user 704.36system 36:43.21elapsed 251%CPU   2.58  9.90  0.19

      make M100data
      make M100feather


Although the amount to CPU time is increasing (R1 > 1), it is comforting to see that
P is amazingly constant for N=2,4,6. Once we hit multiple hyperthreads for N>6 we
can see P drop.

On a laptop with 4 cores (and 2 hyperthreads per core) we get the following result:

      N                     R1     R2    p
      1  1260 + 130  24:14  1.00  1.00   -
      2  1670 + 142  20:23  1.32  1.68  0.32
      4  2566 + 168  19:19  2.04  3.19  0.27
      8  5872 + 244  23:07  4.66  7.63  0.05

not too different from the desktop, despite that the laptop will need to scale back
cpufreq for N>1 to it's basefeq (4.2 -> 2.8 GHz for this laptop).   It seems clear
that the number of processors used should not be surpassing the number of cores.
By default it does not do that, so a better strategy is

   	   export OMP_NUM_THREADS=$(lscpu | grep core: | awk -F: '{print $2}')

for such systems, i.e. avoid using the multithreads.

## NEMO

A good disk I/O test in NEMO is the mkspiral task, which does some (configurable) computations
and then writes a file just over 2GB. This will
help us getting some insight in balancing CPU and disk I/O, using a "real life" code.
The code is single processor, no OpenMP.

      /usr/bin/time mkspiral s0 nbody=1000000 nmodel=40 seed=123          writes 2GB to disk
      /usr/bin/time mkspiral .  nbody=1000000 nmodel=40 seed=123          no writes to disk
      /usr/bin/time mkspiral .  nbody=1000000 nmodel=40 seed=123 test=1   faster data setting
      /usr/bin/time mkspiral .  nbody=1000000 nmodel=40 seed=123 test=2   simple data setting
      /usr/bin/time mkspiral .  nbody=1000000 nmodel=40 seed=123 test=3   no data setting
      /usr/bin/time mkspiral s0 nbody=1000000 nmodel=40 seed=123 test=3   disk i/o, but no data setting 

We consider the following machines, listing the CPU base frequency and the range

      mach    nc  cpu                              mem
      ------- --  -------------------------------- -----
      sdp      4  Xeon X5550  @ 2.67GHz             96GB
      subaru   6  i7-4930K CPU @ 3.40GHz [1.2-4.2]  64GB
      dante    4  i7-3820 CPU @ 3.60GHz [1.2-5.7]   48GB
      yorp20  16  AMD 6380 @ 2.50 GHz               64GB
      vislab1  4  Xeon E5-2609 v2 @ 2.50GHz        512GB
      T530     4  i7-3630QM  @ 2.40GHz [1.2-3.4]    16GB
      T480     4  i7-8550U @ 1.80GHz [0.4-4.0]      16GB
      X1Y4     4  i5-10210U  @ 1.60GHz [0.4-4.2]     8GB
      XPS13    4  i5-1135G7 @ 2.4GHz [0.4-4.2]      16GB


From "slow" to "fast" we get a picture of the CPU and DISK I/O portions of this program. This program
is a single-core, able to keep the CPU nearly 100% busy.

Also noteworthy is that for laptops they might need to be tuned to use the CPU at max. allowed CPU/freq,
viz.

      sudo tlp ac
      sudo cpupower  frequency-set --governor performance --max 4200MHz


Here are results on an old Xeon:

      sdp    hdd  12.779u 2.367s 0:15.15 99.8%
      sdp    raid 12.767u 2.354s 0:15.14 99.8% 
      sdp    shm  12.833u 1.137s 0:13.98 99.8%
      sdp    .    12.658u 1.043s 0:13.71 99.8%
      sdp    .     5.887u 1.048s 0:06.95 99.5%   test=1
      sdp    .     2.532u 0.993s 0:03.53 99.7%   test=2
      sdp    .     0.808u 1.064s 0:01.88 98.9%   test=3
      sdp    hdd   0.856u 2.193s 0:03.06 99.3%   test=0

      dante  shm   8.442u 1.326s 0:09.85 99.0%
      dante  .     8.481u 0.679s 0:09.16 99.8%
      dante  .     0.707u 0.669s 0:01.38 98.5%
      dante  shm   0.681u 1.408s 0:02.09 99.5%   test=3
      

      x1y4   hdd   3.87u 1.38s 0:05.25
      x1y4         3.83u 0.47s 0:04.31
      x1y4         1.98u 0.48s 0:02.47
      x1y4         0.95u 0.45s 0:01.41
      x1y4         0.12u 0.46s 0:00.59
      x1y4         0.14u 1.44s 0:01.58

            shm    3.85u 0.95s 0:04.81
		   3.92u 0.48s 0:04.40
		   1.96u 0.49s 0:02.46
		   0.97u 0.46s 0:01.43
		   0.16u 0.43s 0:00.59
		   0.14u 0.98s 0:01.13


## OpenMP vs. OpenMPI

OpenMP is an implementation of using the multiple cores within a single
machine. They normally require few, if any, changes to the code. But
depending on that code, the performance may deteriote as the number of
cores increase.

Here is an example of a simple loop adding up numbers on a machine
with 16 cores, with 2 multithreads per core

      N                                                     R1     R2     P
      1   69.21user 0.00system 1:09.22elapsed  99%CPU      1.00   1.00    -
      2   69.25user 0.00system 0:34.64elapsed  199%CPU     1.00   1.00   1.00
      4   69.27user 0.00system 0:17.32elapsed  399%CPU     1.00   1.00   1.00
      8   69.60user 0.00system 0:08.70elapsed  799%CPU     1.01   1.01   1.00
      16  69.47user 0.01system 0:04.34elapsed 1597%CPU     1.00   1.00   1.00
      32 141.11user 0.01system 0:04.43elapsed 3182%CPU     2.03   2.05   0.97

The same code on a laptop

      N                                                     R1     R2     P
      1   19.22user 0.00system 0:19.23elapsed   99%CPU     1.00   1.00    -
      2   19.30user 0.00system 0:09.66elapsed  199%CPU     1.00   1.00   1.00
      4   21.13user 0.00system 0:05.28elapsed  400%CPU     1.10   1.10   0.97
      8   41.79user 0.01system 0:05.28elapsed  791%CPU     2.17   2.20   0.83
      
shows that for N=4 performance was dropping a little bit. Manual inspection showed
the cpufreq was droppng a bit, which will be more if the run would take longer.
