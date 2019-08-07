#
#  This is a snippet of python code you can place in ~/.casa/init.py
#  to automatically start up QAC in your CASA session. For example
#  the first time you can do:
#       cat casa.init.py >> ~/.casa/init.py
#
#  Even better, you can directly execfile this
#       execfile(os.environ['HOME'] + '/.casa/QAC/casa.init.py')
#  assuming you have placed QAC (or a symlink) in ~/.casa
#
#  A few other common examples of enhancing your CASA have been given
#  but not activated since you will need to install them and put in
#  the correct paths for you.
#

import os, sys

# https://casaguides.nrao.edu/index.php/Analysis_Utilities
# ftp://ftp.cv.nrao.edu/pub/casaguides/analysis_scripts.tar
if False:
    print "Adding au"
    sys.path.append("/astromake/opt/casa/analysis_scripts")
    import analysisUtils as au

# https://www.oso.nordic-alma.se/software-tools.php
if False:
    print "Adding uvm"
    sys.path.append("/astromake/opt/casa/Nordic_Tools")
    import uvmultifit as uvm

if False:
    print "Adding SD2vis_1.4"
    execfile("/home/teuben/.casa/SD2vis_1.4/mytasks.py")

if False:
    print "Adding casairing_1.1"
    execfile('/astromake/opt/casa/Nordic_Tools/casairing_1.1/mytasks.py')


#   QAC version 6-aug-2019
#
#   To select the version of tp2vis to be activated:
#   - in QAC run "make tp2vis dev" which places two .git repos in QAC
#     (developers release is not public)
#   - manually make a symlink to the name without ".git" if you want to activate it
#     e.g.      ln -s tp2vis.git tp2vis
#               ln -s distribute.git distribute
#   - note that this is the order of searching for tp2vis.py:   contrib, distribute, tpvis
try:
    if sys.path[0] != "":   sys.path.insert(0,'')                  # ipython5 took this out, we put it back
    qac_root  = os.environ['HOME'] + '/.casa/QAC'                  # SET THIS TO YOUR LOCATION OF QAC or use a symlink
    py_files  = ['src/qac',
                 'src/ssc',
                 'src/plot',
                 'contrib/tp2vis',
                 'distribute/tp2vis',
                 'tp2vis/tp2vis']
    sys.path.append(qac_root + '/src')
    work_dir = os.getcwd()
    os.chdir(qac_root)
    print "QAC: Root ",qac_root
    for py in py_files:
        p = py + '.py'
        if os.path.exists(p):
            print "QAC: Load ",p
            if p.rfind('/') < 0:
                execfile(p)
            else:
                # need to execfile() in the directory in order for local import to work
                os.chdir(p[:p.rfind('/')])
                execfile(p[p.rfind('/')+1:])
                os.chdir(qac_root)
        else:
            print "QAC: Skip ",p
    os.chdir(work_dir)
    print "QAC: ",qac_version()
except:
    print "QAC not properly loaded, back to",work_dir
    os.chdir(work_dir)
