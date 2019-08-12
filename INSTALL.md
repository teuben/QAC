# Installation instructions for QAC and related functions

## 0) Executive Summary

On a linux machine with "nothing" installed, the following commands should get you to be able
to run the benchmark  Explanations and alternate ways to install are detailed below. This benchmark
should take around 2 minutes to run.

    cd ~
    git clone https://github.com/teuben/QAC
    
    # phase 1: install CASA (skip this if "casa" is already in your path)
    cd QAC/casa
    ./install_casa
    source casa_start.sh
    cd ..
    
    # phase 2: prepare install and run benchmark
    make data
    make install
    cd ~/.casa
    ln -s ~/QAC
    cd ~/QAC/test
    ln -s ../data/M100_TP_CO_cube.bl.image
    ln -s ../data/M100_aver_12.ms
    ln -s ../data/M100_aver_7.ms
    make bench

## 1) CASA:

You will need to install CASA before you can use QAC.
See https://casa.nrao.edu/casa_obtaining.shtml

An example is in the [casa/install_casa](casa/install_casa) shell script.

## 2) QAC and TP2VIS

Although you can manually execfile() the appropriate python file(s),
this can become cumbersome, and we now encourage you to use CASA's
~/.casa/init.py method. With this you will automatically have anything
personal available within CASA each time you use CASA.

Within QAC we have made this one step easier, by creating a
casa.init.py file that you can directly load.

For example, the following shell commands would grab QAC from github, and
add an execfile() command to your ~/.casa/init.py so this is loaded
into CASA each time you start CASA. 

    mkdir -p  ~/.casa
    cd  ~/.casa
    git clone https://github.com/teuben/QAC
    cd QAC
    make install
    make tp2vis

The next time CASA starts, you will see the QAC routines are loaded,
as well have access to the tp2vis routines.

You can look at QAC's casa.init.py file and steal some ideas how
to load other interesting CASA add-ons.


## 3) TP2VIS:

An alternative to loading TP2VIS via QAC is loading it manually:

    execfile("tp2vis.py")

this is the recommending procedure in the public release of
[tp2vis](https://github.com/tp2vis/distribute).



## FUTURE:

In the current CASA environment there are two other ways QAC could be
installed:
 
- the "buildmytasks" method (supposedly deprecated?)
- python's "setup.py" method (e.g. ADMIT uses this)

but none are supported in this development version of QAC. They might
be in some future release, depending on further development of CASA.
As it stands now, using the execfile() style to load the correct files
is the more pragmatic approach, well realizing this will have to be
replaced when CASA switches to Python 3.



