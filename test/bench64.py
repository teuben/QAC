#  -*- python -*-
#
#  QAC benchmark for tclean with 64 channels 
#
#  Based on:           https://casaguides.nrao.edu/index.php/M100_Band3_Combine_5.4
#
#  Grab data from:     http://admit.astro.umd.edu/~teuben/QAC/qac_bench.tar.gz
#                      but this benchmark only used 'M100_aver_12.ms'
#
#  Benchmark run:      time casa --nogui -c bench64.py
#             or:      %time execfile('bench64.py')
#
#  Space needs:        200MB
#  Memory needed:      ~3.1GB
#
#  Timing examples:
#
#  niter
#      0    8   558.98user 24.00system 2:18.50elapsed 420%CPU  XPS i5-1135G7
#      0    1   110.07user 19.94system 2:13.06elapsed  97%CPU
#   1000    8   805.84user 30.75system 3:06.98elapsed 447%CPU
#   1000    4   355.97user 27.25system 2:36.79elapsed 244%CPU
#   1000    2   237.11user 25.86system 2:50.75elapsed 154%CPU
#   1000    1   172.46user 25.15system 3:22.33elapsed  97%CPU
#  10000    1   354.79user 28.39system 6:26.30elapsed  99%CPU
#
#
#
#
#------------------------------------------------------------------------------------------------------------------------------

# parameters in this benchmark workflow
test        = 'bench64' 
phasecenter = 'J2000 12h22m54.900s +15d49m15.000s'
line        = {"restfreq":"115.271202GHz","start":"1410km/s", "width":"5km/s","nchan":64}
ms12        = 'M100_aver_12.ms'
nsize       = 800
pixel       = 0.5
niter       = 1000

plot        = 0             # make some extra plots

#-- do not change parameters below this ---
import sys
for arg in qac_argv(sys.argv):
    exec(arg)

#   report
qac_log("TEST: %s" % test)
qac_begin(test)
qac_version()

qac_project(test)

#   make sure all the files we need are here
QAC.assertf(ms12)

qac_clean1(test+'/clean',ms12,nsize,pixel,niter=niter,phasecenter=phasecenter,**line)

    
qac_stats(ms12,i3)
qac_stats(test+'/clean/dirtymap.image')

# done
qac_end()
