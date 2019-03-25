# Installation

Here is a description of installing QAC with CASA, all self-contained.
The more complicated one is [here](../INSTALL.md). This description is also meant
for those not so familiar with the Unix shell.


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
      ./install_casa https://casa.nrao.edu/download/distro/linux/release/el7/casa-release-5.4.1-32.el7.tar.gz
      echo $SHELL

if you see the bash shell being reported, use
      
      source casa_start.sh

and if you see the csh or tcsh shell being reported, use

      source casa_start.csh

now we can ask what version of CASA we have

      casa-config --version

and you should see 5.3.0-rel-143 in this example.

## Test

To test if CASA and QAC were installed properly, from the QAC directory type

      cd ..
      make test

and it should some sensible things, no errors.

## Example model data

For most examples we will use a file **skymodel.fits** from the models directory:

      cd models
      make skymodel

And in CASA there is a program **casaviewer** to look at these fits images. You can run that from
the unix command line in the terminal:

      casaviewer skymodel.fits

Now you have called the viewer from the unix command line. A more natural way perhaps is
to do this from within CASA:

      casa
      imview('skymodel.fits')
      exit

for unix the **casa** program is just another unix program, in fact, it's an ipython shell in disguise. You
are just issuing interactive python commands. so for example, from the CASA prompt, you can do
things like

      help(imview)
      print(math.pi)

There is a lot of  documention on casa. The **help()** function is useful (but brief reminder if you need
it right in the screen). Online you can see this expanded on
https://casa.nrao.edu/casadocs-devel/stable/global-task-list/task_imview/about

## Installing it in your Unix shell

This session made the **casa** command available to you in the terminal, but the next time you login, it will
be gone.  To make this permanent add the following line to your ~/.cshrc or ~/.bashrc file, which ever the appropriate
one to which shell you use:

   	 echo $SHELL

	 # if bash:
	 source /somewhere/QAC/casa/casa_start.sh

	 # if (t)csh
	 source /somewhere/QAC/casa/casa_start.csh

where you will of course need to fill in the **/somewhere/** part.
	 
      
