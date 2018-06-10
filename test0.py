#  -*- python -*-
#

#   parameters that can be changed via the command line
n = 0


#-- do not change parameters below this ---
import sys
for arg in qac_argv(sys.argv):
    exec(arg)

#   report
qac_log("TEST0: n=%d" % n)
qac_version()
tp2vis_version()
qac_log("END OF TEST")
print("If you see this line, it looks like everything is in the right place. ")
print("Carefully look at the CASA, QAC and TP2VIS versions")
