# Benchmark Notes

As it turns out CASA is throwing us some curve balls with benchmarks, we also
add a more classical benchmark. One that combines a very simple

## sky0f0

This is a quick test

      cp Makefile skymodel-b.fits sky0.py /dev/shm

      T480   hdd   28.29user 4.04system 0:25.90elapsed 124%CPU (somewhat busy machine)
             shm   16.94user 4.05system 0:22.07elapsed  95%CPU
      X1Y4   hdd    9.56user 1.25system 0:12.15elapsed  89%CPU
             shm    9.30user 1.12system 0:11.79elapsed  88%CPU
      XPS13  hdd
             shm


## sky4z

This is the medium scale, with the (old) small gmc_2L model

      T480   hdd   7772.26user 273.52system 34:49.61elapsed 385%CPU
             shm   
      X1Y4   hdd   5439.75user 196.41system 20:43.28elapsed 453%CPU 
             shm  10287.44user 364.05system 41:54.90elapsed 423%CPU 
      XPS13  hdd
             shm


## NEMO

A good disk I/O test in NEMO is the mkspiral task, which writes a file just over 2GB. This will
help us getting some insight in balancing CPU and disk I/O, using a "real life" code.

      /usr/bin/time mkspiral s0 nbody=1000000 nmodel=40 seed=123          writes 2GB to disk
      /usr/bin/time mkspiral .  nbody=1000000 nmodel=40 seed=123          no writes to disk
      /usr/bin/time mkspiral .  nbody=1000000 nmodel=40 seed=123 test=1   faster data setting
      /usr/bin/time mkspiral .  nbody=1000000 nmodel=40 seed=123 test=2   simple data setting
      /usr/bin/time mkspiral .  nbody=1000000 nmodel=40 seed=123 test=3   no data setting
      /usr/bin/time mkspiral s0 nbody=1000000 nmodel=40 seed=123 test=3   disk i/o, but no data setting 

We consider the following machines:

      sdp    Xeon(R) X5550  @ 2.67GHz          96GB mem
      dante  i7-3820 CPU @ 3.60GHz [1.2-5.7]   48GB
      T530   i7-3xxxQM                         16GB
      T480   i7-8550U @ 1.80GHz [0.4-4.0]      16GB
      X1Y4   i5-10210U  @ 1.60GHz [0.4-4.2]     8GB
      XPS13  i5-1135G7 @ 2.4GHz [0.4-4.2]      16GB


From "slow" to "fast" we get a picture of the CPU and DISK I/O portions of this program. This program
is a single-core, able to keep the CPU nearly 100% busy.

Also noteworthy is that for laptops they might need to be tuned to use the CPU at max. allowed CPU/freq,
viz.

      sudo tlp ac
      sudo cpupower  frequency-set --governor performance

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
      
      X1Y4
