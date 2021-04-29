#  -*- python -*-

import sys

print("===========================================================")
print("This script does nothing but measure the 'casa -c' overhead")
print("And tests if the execfile hierarchy works")

tp2vis_version()
qac_version()

if dish3 == None:
    print("dish3 not set")
else:
    print("dish3",dish3)

# casa5:  ['casa', '-c', 'zero.py'])
# casa6:  ['zero.py']
print("ARGV:",sys.argv)
print("qac_argv:",qac_argv(sys.argv))
