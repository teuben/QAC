
===================================================================
 24  April 2018:   ngVLA Configuration Material 
===================================================================

Update from 9 Dec. 2017:
       - We have introduced a new configuration that deviates from the classical VLA on ~35km scales and have introduced both a short baseline array (SBA) along with a VLBA stations located in Green Bank.
       

Summary:
--------------------------------
We include a finite set of notional configurations for the ngVLA that span a limited range of phase space.  This information is provided as a simple resource to help the community carry out imaging simulations/investigations that critically explore the science capabilities of the proposed array.  We expect that such investigations will lead to suggested modifications to these notional configurations for specific science cases, and hope the community will report on such findings via ngVLA memos and/or refereed publications.  



--------------------------------
Included in this tarball:
--------------------------------
Configuration files (described in more detail below):
	      - ngvla-revB.cfg
	      - ngvla-core-revB.cfg
	      - ngvla-plains-revB.cfg
	      - ngvla-sba-revB.cfg
	      - ngvla-gb-vlba-revB.cfg

Supporting Documents:
	   - CONFIG.CASA.pdf: Instructions on how to use configuration files to generate mock observations using CASA.  

--------------------------------
Brief Description of Configuration Files:
--------------------------------

ngvla-revB.cfg
--------------------------------
The reference configuration of the main array.   This array includes 214 antennas of 18m diameter, to baselines up to 1000 km. The array will not be reconfigurable, hence we have designed a configuration that performs well on a range of angular scales, from 0.01" to 1" at 30GHz.  The Spiral214 array can be characterized by three scales, starting from the core with 94 antennas in a semi-random distrbution within a region of 1km diameter. Extending from the core are 74 antennas in a five armed spiral pattern out to 30km baselines (the "plains" array).  The remaining 46 antennas are then distributed mostly to the south, in a rough three arm spiral pattern, out to a maximum baseline of 1000km, into Texas, Arizona, and
Mexico.  The array configuration is practical, accounting for logistical limitations such as topography and utility availability. Investigations are underway to improve the imaging sensitivity and fidelity while accounting for additional limitations such as local RFI sources and land management and availability.

Numerous memos and science studies have been published that address the imaging parameters for optimal performance (sensitivity, PSF).  We refer interested parties to the ngVLA memo series, and in particular, memos: 16, 30, 35, 41.


ngvla-core-revB.cfg
--------------------------------
This configuration is just 94 core stations from the full 214 antenna array above. This configuration is suitable for imaging lower surface brightness regions, and provides a resolution of about 2" at 30GHz.

ngvla-plains-revB.cfg
--------------------------------
This configuration is just the 168 antennas (94 core stations + 74 antennas included in the 5 spiral arm pattern) located on the plains of San Agustin.  This configuration is suitable for imaging with similar spatial scale capabilities of the existing VLA.  


ngvla-sba-revB.cfg
--------------------------------
A small array of 19 close-packed antennas of 6m diameter to complement array core for very low surface brightness imaging.  The use of 4 18 m antennas in total power mode to fill in the uv-hole left by the SBA is being investigated.


ngvla-gb-vlba-revB.cfg
--------------------------------
Includes the full 214 antenna configuration above, with an additional 10 continential-scale antennas: 5 18m antennas randomly placed at the Green Bank site  and individual 18m antennas located at the existing Saint Croix, Hancock, North Liberty, Brewster, Owens Valley, Mauna Kea VLBA sites.  

