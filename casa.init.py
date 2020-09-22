#
#  Code snippets to add modules to CASA can be added to the following files
#
#  In CASA5:   init.py   and  prelude.py
#  In CASA6:   config.py and  startup.py
#
#  You can add the following lines
#
#       import os
#       execfile( os.environ['HOME'] + '/.casa/QAC/casa.init.py' , globals())
#
#  to ~/.casa/init.py  (CASA5) or ~/.casa/startup.py (CASA6)
#
#  assuming you have placed QAC (or a symlink) in ~/.casa
#  or alternatively you can copy this file into ~/.casa and hack it.
#
#  A few other common examples of enhancing your CASA have been given
#  here, but except for "au" they are not activated since you will need to
#  install them and put in the correct paths for you.
#
#  Note that another startup file ~/.casa/prelude.py is first read, early
#  in the CASA startup. Most likely you will need to tinker in the init.py
#  since that's being read just before the CASA prompt appears.
#

import os, sys


#          for some large mosaics you will need to modify the max. open files
#          here's a python method to do this. The shell can do this with
#                  ulimit -Sn 8000
if False:
    nofiles = 8000
    import resource
    soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
    resource.setrlimit(resource.RLIMIT_NOFILE, (nofiles, hard))
    print("Changing max open files from %d to %d" % (soft,nofiles))


# https://casaguides.nrao.edu/index.php/Analysis_Utilities
# ftp://ftp.cv.nrao.edu/pub/casaguides/analysis_scripts.tar
if True:
    _au_dir = os.environ['HOME'] + '/.casa/analysis_scripts'
    if os.path.exists(_au_dir):
        print("Adding au")
        sys.path.append(_au_dir)
        import analysisUtils as au
        import analysisUtils as aU

# https://www.oso.nordic-alma.se/software-tools.php
if False:
    print("Adding uvm")
    sys.path.append("/astromake/opt/casa/Nordic_Tools")
    import uvmultifit as uvm

if False:
    print("Adding SD2vis_1.4")
    execfile("/home/teuben/.casa/SD2vis_1.4/mytasks.py",globals())

if False:
    print("Adding casairing_1.1")
    execfile('/astromake/opt/casa/Nordic_Tools/casairing_1.1/mytasks.py',globals())


#   QAC version 22-sep-2020
#
#   To select the version of tp2vis to be activated:
#   - in QAC run "make tp2vis dev" which places two .git repos in QAC
#     (developers release is not public)
#   - manually make a symlink to the name without ".git" if you want to activate it
#     e.g.      ln -s tp2vis.git tp2vis
#               ln -s distribute.git distribute
#   - note that this is the order of searching for tp2vis.py:   contrib, distribute, tpvis
#   - note the CASA6 execfile now has globals() and the order of loading makes a difference
try:
    if sys.path[0] != "":   sys.path.insert(0,'')                  # ipython5 took this out, we put it back
    qac_root  = os.environ['HOME'] + '/.casa/QAC'                  # SET THIS TO YOUR LOCATION OF QAC or use a symlink
    py_files  = ['contrib/tp2vis.py',
                 'distribute/tp2vis.py',
                 'tp2vis/tp2vis.py',
                 'src/qac.py',
                 'src/ssc.py',
                 'src/plot.py',
                 #'contrib/sdint_helper.py',
                 #'contrib/sdint_imager.py',
                 ]
    sys.path.append(qac_root + '/src')
    work_dir = os.getcwd()
    os.chdir(qac_root)
    print("QAC: Root %s" % qac_root)
    for p in py_files:
        if os.path.exists(p):
            print("QAC: Load %s" % p)
            if p.rfind('/') < 0:
                execfile(p,globals())
            else:
                # need to execfile() in the directory in order for local import to work
                os.chdir(p[:p.rfind('/')])
                execfile(p[p.rfind('/')+1:],globals())
                os.chdir(qac_root)
        else:
            print("QAC: Skip %s" % p)
    os.chdir(work_dir)
    print("QAC: ",qac_version())
except:
    print("QAC not properly loaded, back to %s" % work_dir)
    os.chdir(work_dir)
