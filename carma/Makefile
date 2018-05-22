#

TESTS = carma1

#  example on Mac:
CASA  = /Applications/CASA.app/Contents/MacOS/casa
#  example on Linux if you used the install_casa script
CASA  = ../casa/casa-release-5.1.2-4.el7/bin/casa
#  example on Linux: (assuming it's in your $PATH - the portable solution)
CASA  = casa

help:
	@echo tests = $(TESTS)

.PHONY: $(TESTS)

carma1:
	@echo running carma.py ...
	time $(CASA) --nogui -c carma.py > carma.log 2>&1
