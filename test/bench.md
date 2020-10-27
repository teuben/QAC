# Benchmark Notes

As it turns out CASA is throwing us some tricky curve balls with benchmarks,
so we also add a more classical benchmark to confirm the general picture.
One that combines a very simple CPU and DISK I/O component, so they can be
separated.

## Preparation

Based on having QAC (for code) and dc2019 (for data)

      cd ~/QAC/test
      cp Makefile skymodel-b.fits sky0.py sky4.py /dev/shm
      cd /dev/shm
      ln -s ~/dc2019/data/gmcSkymodel/gmc_2L
      make sky0f0 sky4z sky4

## sky0f0

This is a quick test, but showing that moving to memory it barely has an impact, if
you look at the system time.


      T480   hdd   28.29user 4.04system 0:25.90elapsed 124%CPU (somewhat busy machine)
             shm   16.94user 4.05system 0:22.07elapsed  95%CPU
      X1Y4   hdd    9.56user 1.25system 0:12.15elapsed  89%CPU
             shm    9.30user 1.12system 0:11.79elapsed  88%CPU
      XPS13  hdd   11.49user 1.62system 0:12.84elapsed 102%CPU
             shm   11.87user 1.33system 0:12.53elapsed 105%CPU

## sky4z

This is the medium scale, with the (old) small gmc_2L model. This is confusing,
on shm it actually runs slower, despite that there is enough memory.

      T480   hdd   7772.26user 273.52system 34:49.61elapsed 385%CPU
             shm   
      X1Y4   hdd   5439.75user  196.41system   20:43.28elapsed 453%CPU 
             shm  10287.44user  364.05system   41:54.90elapsed 423%CPU 
      XPS13  hdd   4601.71user  199.77system   17:29.57elapsed 457%CPU cpu heavier
                   4055.08user  206.60system   16:18.39elapsed 435%CPU
		   4157.42user  207.88system   16:35.48elapsed 438%CPU drop cache
             shm   7519.31user  355.76system   33:36.69elapsed 390%CPU
                   7549.72user  357.43system   33:42.61elapsed 390%CPU
      subaru hdd   2940.37user  269.61system   24:43.23elapsed 216%CPU		   

      QAC_STATS: export/sky_tweak_box1.fits 1.0010571278181761 1.5930145349309555 -0.69122767448425293 8.9708108901977539 6565.3723606948697 0.942194 

      yorp20 hdd  42515.81user 2450.67system 1:32:44elapsed    808%CPU

      QAC_STATS: export/sky_tweak_box1.fits 0.99950875761575164 1.5935251499479519 -0.65302145481109619 9.0135574340820312 6555.21746878248 0.938545



# sky4

      XPS13  hdd   6637.55user 329.92system 28:51.53elapsed 402%CPU busy>
                   6460.71user 311.96system 27:49.63elapsed 405%CPU
		   6508.26user 310.58system 27:57.96elapsed 406%CPU   uncached
		   6405.97user 310.07system 27:43.83elapsed 403%CPU
             shm   6387.34user 299.42system 27:15.54elapsed 408%CPU 
      

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
      subaru i7-4930K CPU @ 3.40GHz            64GB
      dante  i7-3820 CPU @ 3.60GHz [1.2-5.7]   48GB
      yorp20 AMD 6380 @ 2.50 GHz               64GB
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

