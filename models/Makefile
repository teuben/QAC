

help:
	@echo skymodel:     get skymodel.fits
	@echo test:         make a few standard galaxy models

skymodel: skymodel.fits


fits:     skymodel.fits field000.fits

skymodel.fits:
	wget http://admit.astro.umd.edu/~teuben/QAC/skymodel.fits

field000.fits:
	wget http://admit.astro.umd.edu/~teuben/QAC/field000.fits

test:
	./mkgalcube run=model0 beam=0
	./mkgalcube run=model1 
	./mkgalcube run=model2 beam=0.5
	./mkgalcube run=model3 beam=0.5 vbeam=10
	./mkgalcube run=model4 beam=0.5 noise=0.001


