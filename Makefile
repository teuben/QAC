#  
#

.PHONY:  tp2vis distribute


# should just be an ID, e.g. 0.5 or 0.5a, or 0.5.1, in one single line.
VERSION = `cat VERSION`

# the master git repo
URL1     = https://github.com/kodajn/tp2vis

# the distribute git repo
URL2     = https://github.com/tp2vis/distribute

help:
	@echo QAC VERSION=`cat VERSION`
	@echo ""
	@echo "The following targets are available for make:"
	@echo ""
	@echo "  install    add QAC execfile to ~/.casa/init.py"
	@echo "  clean      remove the 'distribute' version"
	@echo "  tp2vis     install the public version of tp2vis (recommended)"
	@echo "  dev        install the developers version of tp2vis"
	@echo ""
	@echo "There are a few more targets for experts as reminders to mundane tasks we may need"
	@echo "See the Makefile for comments"

install:
	@echo Creating a blank ~/.casa/init.py just in case it does not exist
	-@mkdir -p ~/.casa; touch ~/.casa/init.py
	echo "execfile(os.environ['HOME'] + '/.casa/QAC/casa.init.py')"  >> ~/.casa/init.py
	@echo Obviously this example assumes QAC was located in ~/.casa.
	@echo Modify as needed.

# public release is in a directory 'distribute', go figure
tp2vis:
	if [ ! -d distribute ]; then \
	  git clone $(URL2) ;\
	else \
	  (cd distribute; git status; git pull)\
	fi

# private developers version is in a directory 'tp2vis'
dev:
	if [ ! -d tp2vis ]; then \
	  git clone $(URL1) ;\
	else \
	  (cd tp2vis; git status; git pull)\
	fi



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


