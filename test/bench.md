# Benchmark Notes


## Preparation

Based on having QAC and dc2019.

      cd ~/QAC/test
      cp Makefile skymodel-b.fits sky0.py sky4.py /dev/shm
      cd /dev/shm
      ln -s ~/dc2019/data/gmcSkymodel/gmc_2L
      make sky0f0 sky4z sky4


## sky0f0

This is a quick test


      T480   hdd   28.29user 4.04system 0:25.90elapsed 124%CPU (somewhat busy machine)
             shm   16.94user 4.05system 0:22.07elapsed  95%CPU
      X1Y4   hdd
             shm
      XPS13  hdd
             shm


## sky4z

This is the medium scale, with the (old) small gmc_2L model

      T480   hdd   7772.26user 273.52system 34:49.61elapsed 385%CPU
             shm   
      X1Y4   hdd
             shm
      XPS13  hdd
             shm
