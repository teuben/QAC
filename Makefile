#  
#    some easy targets for install and guidance to operations
#    including a CASA install if it's not present yet
#

.PHONY:  tp2vis.git distribute.git install test casa


# should just be an ID, e.g. 0.5 or 0.5a, or 0.5.1, in one single line.
VERSION = `cat VERSION`

# the master git repo
URL1     = https://github.com/kodajn/tp2vis.git

# the distribute git repo
URL2     = https://github.com/tp2vis/distribute.git

# data url
URL3     = http://admit.astro.umd.edu/~teuben/QAC/

CASA     = `which casa`

help:
	@echo QAC VERSION=`cat VERSION`
	@echo ""
	@echo "The following targets are available for make:"
	@echo ""
	@echo "  install         add QAC execfile to ~/.casa/init.py for CASA to recognize QAC"
	@echo "  install_casa    install this if you don't have casa yet"
	@echo "  test            confirm all components are working"
	@echo "  clean           remove the 'distribute' version"
	@echo "  tp2vis          install the public version of tp2vis (recommended)"
	@echo "  dev             install the developers version of tp2vis"
	@echo ""
	@echo "There are a few more targets for experts as reminders to mundane tasks we may need"
	@echo "See the Makefile for comments"

install:
	-@mkdir -p ~/.casa; touch ~/.casa/init.py
	@echo Patching your ~/.casa/init.py
	@echo "   (You might want to check on multiple installs, this code does not check for that)"
	@echo "execfile(os.environ['HOME'] + '/.casa/QAC/casa.init.py')"  >> ~/.casa/init.py
	@if [ ! -e ~/.casa/QAC ]; then \
	   echo No QAC in .casa, creating link to $(PWD);\
	   echo ln -s $(PWD) ~/.casa/QAC ;\
	   ln -s $(PWD) ~/.casa/QAC ;\
	else \
	   echo Symlink ~/.casa/QAC to $(PWD) already exists, LG;\
	fi
	@if [ -z $(CASA) ]; then \
	  echo 'No casa, suggest you type "make install_casa"' ;\
	else \
	  echo casa=$(CASA);\
	fi


install_casa:
	@(cd casa; ./install_casa)
	@echo Also make sure that casa is now in your PATH, e.g.
	@tail -1 $(PWD)/casa/casa_start.sh
	@echo "  OR for csh shell"
	@tail -1 $(PWD)/casa/casa_start.csh
	@echo "Add one of those lines to your .bashrc or .cshrc file or cut-and-paste it into your current shell"

install_astropy:
	@casa -c contrib/install_astropy.py



test:
	@echo Simple test, needs no data, test if your installation is good.
	$(CASA) --no-gui -c test0.py n=1

pjt:

data:
	mkdir -p data
	(cd data; wget $(URL3)/skymodel.fits)
	(cd data; wget $(URL3)/skymodel.ptg)
	(cd data; wget $(URL3)/qac_bench.tar.gz -O - | tar zxf -)

# the public release is in a directory 'distribute', or 'distribute.git'
# do not modify this, it gets updated from the developers release 
tp2vis: distribute.git

distribute.git:
	if [ ! -d distribute.git ]; then \
	  git clone $(URL2) ;\
	else \
	  (cd distribute.git; git status; git pull)\
	fi
	@echo Done with the public release distribute.git

# private developers version is in a directory 'tp2vis', or 'tp2vis.git'
dev: tp2vis.git
	if [ ! -d tp2vis.git ]; then \
	  git clone $(URL1) ;\
	else \
	  (cd tp2vis.git; git status; git pull)\
	fi
	@echo Done with the developer release tp2vis.git

clean:
	rm -rf distribute tp2vis



### below are reminders how to do some mundane things #########################################



#  example how to make the pdf from md files
pdf:
	pandoc workflow1.md -o workflow1.pdf

#  example how to make the html from md files
html:
	pandoc example1.md -o example1.html

#  example how to present md in a browser and view it while editing occurs
#  browser typically is pointed to http://localhost:6419
#  or use:    grip example1.md 6419
#  if you want to use a specific port
live:
	grip example1.md


