#
#  this is a piece of code you can place in ~/.casa/init.py
#  to automatically start up QAC in your CASA session 
#

import os

  
try:
    qac_root  = os.environ['HOME'] + '/.casa/QAC'                     # SET THIS TO YOUR LOCATION OF QAC or use a symlink
    py_files  = ['src/qac', 'distribute/tp2vis', 'tp2vis/tp2vis']     # pick which ones you want
    work_dir = os.getcwd()
    sys.path.append(qac_root)
    os.chdir(qac_root)
    print "QAC: Root ",qac_root
    for py in py_files:
        pfile = py + '.py'
        if os.path.exists(pfile):
            print "QAC: Load ",pfile
            execfile(pfile)
        else:
            print "QAC: Skip ",pfile
    os.chdir(work_dir)
    print "QAC: ",qac_version()
except:
    print "QAC not properly loaded, back to",work_dir
    os.chdir(work_dir)
