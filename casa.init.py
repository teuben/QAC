#
#  this is a piece of code you can place in ~/.casa/init.py
#  to automatically start up QAC in your CASA session
#  Check future versions of the QAC/casa.init.py code if
#  their procedure has not changed
#  The first time you can do:
#       cat casa.init.py >> ~/.casa/init.py
#
#  A few other common examples of enhancing your CASA have been given
#  but not activated since you will need to install them and put in
#  the correct path
#

import os, sys

if False:
    print "Adding au"
    sys.path.append("/astromake/opt/casa/analysis_scripts")
    import analysisUtils as au

if False:
    print "Adding uvm"
    sys.path.append("/astromake/opt/casa/Nordic_Tools")
    import uvmultifit as uvm

if False:
    print "Adding SD2vis"
    execfile("/astromake/opt/casa/Nordic_Tools/SD2vis_1.3/mytasks.py")

if False:
    print "Adding casairing"
    execfile('/astromake/opt/casa/Nordic_Tools/casairing_1.1/mytasks.py')

    

   

#   QAC version 13-mar-2018  
try:
    if sys.path[0] != "":   sys.path.insert(0,'')                  # ipython5 took this out, we put it back
    qac_root  = os.environ['HOME'] + '/.casa/QAC'                  # SET THIS TO YOUR LOCATION OF QAC or use a symlink
    py_files  = ['src/qac', 'src/ssc', 'src/plot', 'distribute/tp2vis', 'tp2vis/tp2vis']
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
