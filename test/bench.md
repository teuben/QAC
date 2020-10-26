# Benchmark Notes

## sky0f0

This is a quick test

      cp Makefile skymodel-b.fits sky0.py /dev/shm

      T480   hdd   28.29user 4.04system 0:25.90elapsed 124%CPU (somewhat busy machine)
             shm   16.94user 4.05system 0:22.07elapsed  95%CPU
      X1Y4   hdd
             shm
      XPS13  hdd   11.49user 1.62system 0:12.84elapsed 102%CPU
             shm   11.87user 1.33system 0:12.53elapsed 105%CPU

## sky4z

This is the medium scale, with the (old) small gmc_2L model

      T480   hdd   7772.26user 273.52system 34:49.61elapsed 385%CPU
             shm   
      X1Y4   hdd
             shm
      XPS13  hdd   4601.71user 199.77system 17:29.57elapsed 457%CPU cpu heavier
                   4055.08user 206.60system 16:18.39elapsed 435%CPU
		   4157.42user 207.88system 16:35.48elapsed 438%CPU drop cache
             shm   7519.31user 355.76system 33:36.69elapsed 390%CPU
                   7549.72user 357.43system 33:42.61elapsed 390%CPU


# sky4

      XPS13  hdd   6637.55user 329.92system 28:51.53elapsed 402%CPU busy>
                   6460.71user 311.96system 27:49.63elapsed 405%CPU
		   6508.26user 310.58system 27:57.96elapsed 406%CPU   uncached
		   6405.97user 310.07system 27:43.83elapsed 403%CPU
             shm   6387.34user 299.42system 27:15.54elapsed 408%CPU 
      
