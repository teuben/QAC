# QAC tests

Here we cover some QAC testing results, all available to run via the Makefile:

* sky4 :  (uses sky4.py) the ideal/ultimate does everything script for a skymodel
* point : (uses sky1.py) cleaning a point source. sounds simple, right?

## API changes

There were some API changes in October 2020 where, until all is verified and changed, some scripts will now fail:

* no more phasecenter= in qac_tp_vis
* related to this:  need to call qac_image_desc() to get phasecenter,imsize_m,pixel_m
* no more t= to be able to complare clean() and tclean()

## SKY4 todo list

* [DONE] now has an option to re-use from sky4f, which has cfg=[0,1,2,3,4,5,6], 
  see skymodel.py for an example of re-use; "make sky4q" uses it 
  and can be compared to "make sky4"

* [DONE] comparing sky4 and sky4q should be identical now

* sky4o is running sky4 with a perfect OTF
  -> it will be interesting to compare sky4 with sky4o

* sky4z is running sky4 with Toshi's skymodel-b.py re-usable setup
  -> it will even more interesting to compare sky4z with sky4o

* properly add sdintimaging() to qac_sd_int()

* properly add tclean() options to qac_clean()

* what's the deal with different casa versions and the polkadot patterns in the difference maps
  - same version of casa on subaru and T480 give the polkadot difference 
    OMP_NUM_THREADS=1 did not solve the issue, results are within noise the same

* sky4 is now able to compare three different modes they should be "identical":
  - using the Jy/pixel map
  - using the OTF map
  - using the SD map (from simalma) with the unresolved 4% issue

* Cases to study:
  - different weight (or afactor=) for 7m array
    - sky4 has wtACA=0.340278 and wtALMA=1
  - different UV coverage [sky4i, but it uses afactor=2]  ->   sky4i_1 and sky4i_2
  - more cfg  [sky4f:  this doesn't need a new wfactor]

* Toshi's data
  - uses weight=1 for both ACA and ALMA
  - do an experiment with one first day, check the PB is flat


## Comparisons

The QA team is already comparing, and quantitavely measuring how well a combination
measures up to the original.
