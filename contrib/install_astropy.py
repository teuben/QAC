#
# See also: http://docs.astropy.org/en/stable/install.html#installing-astropy-into-casa
#
from setuptools.command import easy_install
easy_install.main(['--user', 'pip'])
import pip
pip.main(['install', 'astropy'])

