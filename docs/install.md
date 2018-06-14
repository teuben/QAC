# Installation

Here is another description of installing QAC with CASA, all self-contained.


## QAC

The QAC toolkit can be obtained directly from github:

      git clone https://github.com/teuben/QAC

this will have created the QAC directory.   A few things need to be done to prepare QAC to work with CASA:

      cd QAC
      make install

Ignore the request to run "make install_casa", we will do this manually in the next step.
     

## CASA

Assuming we don't have CASA yet, we will install CASA using a script available in QAC

      cd casa
      ./install_casa https://casa.nrao.edu/download/distro/linux/release/el6/casa-release-5.3.0-143.el6.tar.gz
      source casa_start.sh

now we can ask what version of CASA we have

      casa-config --version

and you should see 5.3.0-rel-143 in this example.

## Example data

For most examples we will use a file **skymodel.fits** from the models directory:

      cd ../models
      make skymodel

And in CASA there is a program **casaviewer** to look at these fits images:

      casaviewer skymodel.fits
