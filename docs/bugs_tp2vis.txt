List of Bugs and Issues and Workarounds for TP2VIS
==================================================

Some bugs reported on JIRA, some on HELPDESK
Some of our bug numbers are resolved in tpvischeck(), for the time being.
Search here for HELPDESK/JIRA tickets:    https://casa.nrao.edu/hdtickets

001. [FIXED] 3d cube output from modeling does not have the correct wcs in freq
     This was fixed by stuffing the proper restfreq in two tables, but this needs
     to be run by Remy to see why he left it out.
     Also the difference between REST_FREQUENCY and REF_FREQUENCY in the
     SOURCE and SPECTRAL_WINDOW table resp.
     We should note that the MSv2 document hasn't been updated since 2000.

002. [NOTED] the simulator tool (sm) must have a cube in RA-DEC-POL-FREQ
     (rdpf) order, else it will not work. This is how cubes come out of
     tclean, however fits files from the archive are delivered in
     RA-DEC-FREQ-POL order
     You'll need to use       ia.transpose(order='0132')      for this.
     This in turn needs CASA 5.0 as before there were header bugs in this
     operation.
     Remy says: the tool (sm) will not change. Live with it.

003. [NOTED] directly using fits files in the simulator does not work, they
     need to be in casa image format (via e.g. importfits()) Our script
     will now convert .fits -> .im if a fits file is seen.

004. [FIXED] 2 (testcube) and 3 (skymodel) work ok.  1 (cloud197) fails, keeps saying
  "all weights zero", even for a single channel however, using
  testcube_a.py (a modified version using the task, not the tool), it
  works for 43 channels, but with erors in the WCS of the FREQ. Possibly
  that's bug001 again.

  => turns out if you fix the header with a DEC -30.0, everything works.

  -> solution was an error in the setting of the antpos in the MS.

005. [N/A] The testcube regression test had a problem with CRPIX3
     We don't use this anymore.

006. [FIXED] listobs('test3d.tp.ms') shows that ANT0 has long/lat of (0,0), the rest is ok.
     This is with 25 ants.
     -> this was related to  004

007.  [submitted] using XX and XX,YY in tclean() is confusing; what is assumed about the missing YY?
      helpdesk ticket #11256    https://help.almascience.org/index.php?/na/Tickets/Ticket/View/11256

008.  related items to be sorted out: (all related to tclean() crashing on mixing tp.ms and vis.ms)
      - mstransform() and tclean() use start=, width=, and nchan= not the same way
        notably mstransform doesn't flip the sign of channel width
	There is an official ticket on this:
	https://open-jira.nrao.edu/browse/CAS-7371      mstransform doesn't revert axes
	=> this seems to have been fixed in casa 5.0
      - concat() does not handle [tp,vis] same as [vis,tp], the latter being the one that works ok
      - See also [011] below.

009.  (solved?) Since we "observe" an LSRK cube, it's going back in TOPO frame , and mapping it in LSRK will
      cause a minor doppler correction that we don't want !!!  This will cause the first or last
      channel in the combination to be blanked/not seen.
      **after setting the correct number of digits for the CO restfreq the rounding is now correct,
      we have channels from 256 to 214, and the bug is now refocussed to [011]

010.  [submitted] vp.setpbgauss() confusing halfwidth setting (or a bug?)
      https://help.almascience.org/index.php?/na/Tickets/Ticket/View/11267
      https://open-jira.nrao.edu/browse/CAS-10384

011.  [submitted] mstransform() can create an MS where the last channel is blanked after tclean()
      https://help.almascience.org/index.php?/na/Tickets/Ticket/View/11270
      We decided this needs to be transferred to CAS-10340
      
      Added note: when qtp_clean() is called with uniform weighting,the problem went away [one case observed,
      need to verify if this is a general statement.

      Q:  where did we log the aliasing effect of the blanking.

012.  ???  In early casa 5.1 mysterious "file exists" and "no memory" issues were occuring. Perhaps new casa,
      perhaps tp2vis not freeing enough memory?   This bug hasn't re-appeared recently.

013.  In the standard cloud197 tests the first channel (V=256) seems to be blanked????
      This seems a recurring problem due to roundoff from the "214 + 43 * 1" km/s channels in the TP and MS.
      Perhaps we need to use the "regrid with template image option". In that sense this bug is related to 014.
      See also 011.

014.  Regridding image cube is hard: we need a simple interface. Helpdesk ticket is
      https://help.almascience.org/index.php?/na/Tickets/Ticket/View/11273

015.  [NOTED] Currently the sign of the channel width in TP and MS needs to be the same.
      tp2vischeck() can work on that. The fix is the use imtrans('cloud197_casa47.spw17.image','cloud197_imtransimage','012-3')

016.  [NOTED] No pointing table aver_07 and aver_12   concat complains about it. In a later case (workflow6) it crashed,
      so we added copypointing=False

017.  [FIXED] ia.transpose() blanks (and looses) header items:      OBJECT:         UNITS:
      41 header items went to 38          ['beamminor', 'beampa', 'beammajor']
      https://open-jira.nrao.edu/browse/CAS-10441
      fixed in 5.0 (was broken in 4.7.2)

018.  [FIXED] need good example of making 4D testimage  (e.g. to test #017)
      https://open-jira.nrao.edu/browse/CAS-10442

019.  [resolved]  use of shared casa/data if you run many casa's
      https://help.almascience.org/index.php?/na/Tickets/Ticket/View/11273

020.  [unresolved] vpmanager: not understanding how it works?  Despite save and load (astable), tclean still seems to use ALMA,
      not our GAUS12M.
      It should be noted that the field "pbdescription" (a record?) in the VP table has an access error in casabrowser.
      although the record in vp.getvp('GAUS12M') looks clean.
      email from Kumar:  only vptable= to sm.predict() and tclean() can be used now.
      Finally resolved 18-oct-2017 when we figured out obs_obsname needs to be "ALMA" first, and then "VIRTUAL"
      28-nov: Nope, false alarm:  now the code is looking for a VIRTUAL site on the planet, and there's a subsequent warning that
      frequency conversion is not working. Very alarming, back to use_vp=False

021.  [FIXED] If an input map is Jy/beam, the modeling software will take a flux larger by a factor or the number of points per beam.
      Solution is to tp2vischeck() that file and make sure it is Jy/pixel and the numbers scaled down.
      However, finding the correct RMS for tp2vis(rms=) is now down by number of points per beam!!
      Use on the fly correction?

022.  [SUBMITTED] tclean will crash if TP.MS is included in the VIS chane, but via concat it's ok. This is a longstanding
      issue we work around in qtp_clean() using do_concat=True
      https://open-jira.nrao.edu/browse/CAS-10519
      -> DATA vs. DATA_CORRECTED : can't mix?

023.  [CAUTION] imregrid has warnings about flux conservation. We need to check code examples if that's done correctly.
      In particular spectral regridding.

024.  [submitted] phasecenter in tclean() does not describe the default value (a very generic CASA problem)	 
      https://help.almascience.org/index.php?/na/Tickets/Ticket/View/12225

025.  [noted]  we needed concat(copypointing=False) to skip the pointing table. It used to just complain, but for workflow5
      it caused concat() to die. The POINTING table is not essential, it's the FIELD table that contains where the phase center
      is. That's what counts. In theory an antenna can point away from the phase center (e.g. on-the-fly), but this is not
      important here. We should have data where the ant's point at the field center

      BUT: In workflow1 we get a different flux if the pointing table is not copied.....  workflow1-test3

      In workflow4 finding out that we need tp with fix=0 and ??

026.  [noted]  related to contact with spectral axes of different sign
      WARN	MSConcat::copySpwAndPol	Negative or zero total bandwidth in SPW 0 of MS to be appended.

027.  [fixed] imcontsub can't run 2nd time in the same casa session, has a lockfile?
      https://help.almascience.org/index.php?/na/Tickets/Ticket/View/12286
      Only important in our workflow2.
      Fixed in a JIRA ticket 10752


Questions regarding MS compliance:

- do we really need a pointing table. it's in the field table.  ALMA ms don't have them. Simulator adds it.
  Also to note: copypointing=False in concat didn't resolve the crash issue 

- REST_FREQ vs REF_FREQ. 


Our Major issues with CASA

- tclean() crashes if MS is a list
  -> we use concat() with no POINTINGS copied as well
- rounding (?) in combining results in seemingly random bad first or last channel
  -> we make sure no edge channels
- if casa tools (e.g. mstransform() are not used to bring interferometry data into LSRK frame,
  instead of TOPO frame, array combination could be suspect?

Our own issues:

- why does flux vary so much as function of weight (e.g. workflow1)
  -> known "issue" with complex beams.  [in progress]
- why is the beam not round anymore after qtp_tp ?    59x56"   [increasing nvgrp does not work]
  -> looks like the ALMA beam, VIRTUAL is better
  -> not been able to reproduce that in the new branch
- why is the recovered flux in e.g. workflow4 five (5.1) times higher from the deconvolved tp2vis.
  TODO
- deal with WEIGHT_SPECTRUM and/or SIGMA_SPECTRUM when present (since it's preferred to WEIGHT/SIGMA)
  see tp2vis.ms_update_weight() [fixed]

- various @todo's in tp2vis: They used to be in @todo comments, but they've been removed [sic] for sake of clarity [sic] of the code 
  - variables (cms, etc.) are defined multiple times; one variable has different name in qtp and tp2vis
  - temp files don't always have unique names and could prevent parallel runs (the 'dd' solution is 99% ok)
    Fixed names that could use improvements:
         tmp_imagedec.im
  - some code duplication present which could be improved by defining functions (e.g. getting lel(), get_beam())
  - code is written for execfile() style, and not easily converted to "import tp2vis"
  - sigma = 1/np.sqrt(weight)   is now done inline; no protection for weight=0 anymore. This was defined via tp2vis.ms_update_weight()
  - An ALMA MS can now be heterogeneous i.e. 7m and 12m in one MS are correllated.

https://github.com/kodajn/tp2vis/issues/7     beam from TP vis itself it not round and size depends on mosaic
https://github.com/kodajn/tp2vis/issues/8     POINTING table issue
