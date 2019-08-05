#
# See also: http://docs.astropy.org/en/stable/install.html#installing-astropy-into-casa
#
# but withouth the --user, so it installs for all users in the current python that casa used
#
# Note with casa6 may not be needed anymore.
#
from setuptools.command import easy_install
easy_install.main(['pip'])
import pip
pip.main(['install', 'astropy'])

