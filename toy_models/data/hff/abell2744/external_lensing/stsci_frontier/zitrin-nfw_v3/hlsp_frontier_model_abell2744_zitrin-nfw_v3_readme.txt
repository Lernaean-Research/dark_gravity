# Lens model ReadMe file for the cluster: a2744
# Constructed and supplied by Irene Sendra on behalf of the Zitrin & Merten map making group.
#Last updated ReadMe file on 24-September-2015

------------------------------------------------------------------------------
------------------------------------------------------------------------------

# The current ReadMe file contains the following sections:
  [A] Description of files submitted
  [B] Description of the method(s) incorporated
  [C] Specific information regarding the model of the cluster
  [D] Comments
  [E] Acknowledgments
 ------------------------------------------------------------------------------
------------------------------------------------------------------------------

 [A] Description of the files submitted
 # Our submission includes models from two different mass modeling methods (or parametrizations;
 # see below section [B] for more details).
 # We supply:
  - Cluster members list used (_cluster_members.txt)
    This file contains the list of cluster members adopted in our model, along with their data
    extracted using SExtractor [Bertin & Arnout, 1996, A&AS, 117, 393] and divided in 10 columns:
          #   1 NUMBER          Running object number
          #   2 X_IMAGE         Object position along x                         [pixel]
          #   3 Y_IMAGE         Object position along y                         [pixel]
          #   4 FLUX_AUTO       Flux within a Kron-like elliptical aperture     [count]
          #                     Note however that in a few cases the flux has been manually modified by us,
          #                     especially, to down weight the lensing contribution from galaxies which were not
          #                     obvious cluster members
          #   5 RA              Right ascension of barycenter (J2000)           [deg]
          #   6 DEC             Declination of barycenter (J2000)               [deg]
          #   7 A_IMAGE         Profile RMS along major axis                    [pixel]
          #   8 B_IMAGE         Profile RMS along minor axis                    [pixel]
          #   9 THETA_IMAGE     Position angle (CCW/x)                          [deg]
          #   10 ELLIPTICITY    1 - B_IMAGE/A_IMAGE

 - List of systems of multiple images adopted (_images.txt)
    This file contains the list of multiple images used as constraints in our model, along with their data in
    8 different columns:      #   1 ID              Image number
       #   2 RA              Right ascension of barycenter (J2000)           [deg]
       #   3 DEC             Declination of barycenter (J2000)               [deg]
       #   4 Z_SPEC          Spectroscopic Redshift
       #   5 REDSFHIT_REF    Redshift reference
       #   6 Z_ADOPT         Initially Adopted Redshift (E.g., following previous works or photometric redshift)
                             Most of the redshifts in the z_adopt column were taken from Merten et al. 2011 and Jauzac et al. 2014.
       #   7 F?              Redshift considered as free parameter in our model [Y for YES or N for NO]
       #   8 ID_REFERENCE    Reference of First Identification of the system/image
 
 # And produce the following model OUTPUT files (_products/):
  - best-fit gamma map, scaled to DLS/DS=1 (_gamma.fits)
  - best-fit gamma maps (two components; gamma 1 and gamma 2), scaled to DLS/DS=1 (_gamma1.fits and _gamma2.fits)
  - best-fit kappa map, scaled to DLS/DS=1 (_kappa.fits)
  - best-fit magnification map, scaled to DLS/DS=1 (_magnif.fits)
  - best-fit potential map, scaled to DLS/DS=1 (_psi.fits)
    Notice this is the first time the psi is realized with this model and there might be some....)
  - best-fit deflection angle maps (x and y components), scaled DLS/DS=1, in units of pixels (with 0.060"/pix) (_x-pixels-deflect.fits and _y-pixels-deflect.fits)
 - best-fit deflection angle maps (x and y components), scaled DLS/DS=1, in arcsec (_x-arcsec-deflect.fits and _y-arcsec-deflect.fits)
 - best-fit magnification map, scaled to redshift 1, 2, 4 and 9 (_z01-magnif.fits, _z02-magnif.fits, _z04-magnif.fits and _z09-magnif.fits)
  - a subdirectory (named "range") with 30 random models from the MC chain for error calculation. 
(Note: small, sub-arcsec, few-ACS-pixel offsets in the model files may occur due to internal interpolations in the modeling).

 ------------------------------------------------------------------------------

 [B] Description of the method(s) incorporated
 # The two methods we apply here are:
 (i) the [revised, improved version of] Zitrin et al. 2009 (MNRAS, 396, 1985) light-traces-mass method (LTM)
     with a Gaussian smoothing instead of a 2D Spline interpolation (also see below further details)
 (ii) a PIEMD+eNFW parametrization (e.g. Zitrin et al. 2013, ApJ, 762L, 30). 
  We refer the reader to these papers for additional information. We also ask that when using these models, please cite the two above papers upon relevance. Also, user should acknowledge in the following manner, 
  or similar: "The mass models were constructed by Irene Sendra with the method of A. Zitrin et al. (2009,2013), and obtained through the Hubble Space Telescope Archive as Frontier Fields products form the Zitrin & Merten map making group.
  # General, brief review of the modeling methods in use:

 LTM: The light-traces-mass method used here was first sketched by Broadhurst et al. 
  2005 (ApJ, 621, 53), and later revised and simplified by Zitrin et al. 2009 (MNRAS, 396, 
  1985), where full details can be found. This method adopts the LTM assumption for 
  *both* the galaxies and DM, which are the two main components of the mass model. We  
  start by choosing cluster members following an identified red-sequence. Each cluster 
  member is then assigned with a power-law mass density profile scaled by the galaxy  
  luminosity, so that the superposition of all galaxy contributions constitutes the first  
  component for the model. This mass map is then smoothed with either a 2D Spline  
  interpolation, or a Gaussian kernel (here we supply models with the two options), to 
  obtain a smooth component representing the DM mass density distribution. The two mass  
  components are then added with a relative weight, and supplemented by a 2-component  
  external shear to allow for additional flexibility and higher ellipticity of the critical  
  curves. The method thus includes six basic free parameters: the exponent of the power- 
  law (q); the smoothing degree (s) - either the polynomial degree of the spline fit or the  
  Gaussian width; the relative of weight of the galaxies component with the DM (k_gal); the  
  overall normalization (k); and the strength and angle of the external shear (gamma, phi).  
  Additionally, we add a core to the BCG(s); the core radius (r_c) is a free parameter(s) as  
  well.  
  The best fit solution and accompanying errors are estimated via a long MCMC. Also,  
  specific bright galaxies can be left to be freely optimized by the minimization procedure,  
  as well as the redshift of multiple-image systems which do not have accurate source  
  redshifts. 

  The LTM method has the unique advantage of being initially well enough constrained to readily help find,  
  physically, multiple images across the cluster field, which can be then used to iteratively  
  improve the model. The final fit, though, is still relatively strongly coupled to the light  
  and thus may be somewhat less  flexible than other common parameterizations. 

  PIEMD+eNFW: To supply an additional model which has inherently a higher spatial  
  flexibility (and thus usually a somewhat better fit to the data), we also supply a model  
  consisting of Pseudo Isothermal Elliptical Mass Distributions for the galaxies, whose  
  superposition constitutes the lumpy, galaxies component for the model. The DM halo(s)  
  is(are) then simply constructed using an analytical elliptical-NFW form, centered  
  primarily on the BCG(s). This method includes two free parameters for the PIEMDs: the  
  central velocity dispersion simga_0, and cut-off radius r_cut, of a reference (usually L*)  
  galaxy, where all other galaxies are scaled relative to it by their luminosity. For each dark   
  eNFW halo incorporated, four additional free parameters are added: the concentration   
  c_200, scale radius r_s, ellipticity e, and angle phi. At times it is also useful leaving the   
  DM center free to be optimized by the model, as well as specific bright galaxies, and   
  redshift of multiple-image systems which do not have accurate source redshifts. Lastly, 
there exists also the option to add an external shear although we generally do not use this feature here. More   
  details on our implementation of this method are given in (e.g. Zitrin et   
  al. 2013, ApJ, 762L, 30). 

# Note also that additional, complete details of the lensing models will be given shortly in related works; or could be
# obtained directly (also for reporting problems, queries etc.) by 
# contacting Irene at isendra@caltech.edu or Adi at adizitrin@gmail.com .

 ------------------------------------------------------------------------------

 [C] Specific information regarding the model of the cluster
 # Specific details for the model for a2744

  - Cluster redshift used 0.3080

  - The cluster was modeled here using PIEMD+eNFWs: on top of the PIEMD galaxies, two eNFW halos are used, whose centers we fix on the centers of the BCGs. 
   - We leave 2 bright galaxies to be freely weighted by the MCMC, as well as 24 free source redshifts.   
  - The resulting multiple image reproduction rms is 2.0" (using the average source position).  

   - The best-fit model and error are obtained using a positional error of sigma_pos=0.5 arcsecond.
     We use this value since it is the most common is strong-lensing analyses, especially if combined
     with weak-lensing constraints, but note - it was found that this value probably strongly (about an order
     of magnitude) underestimates the underlying errors, and to reflect the true error it is generally
     preferable to use a position uncertainty of 1.66", at least to contribute to effect of large scale struture
     along the line of sight.
------------------------------------------------------------------------------

 [D] Comments

 -There may be some periodic artifacts especially in the LTM models, and mainly towards the edges of the frame from Fourier Transforms used in the procedure.
  However, these are typically of order ~0.02 in kappa and are thus negligible compared with the noise/statistical errors. 
 -small, sub-arcsec, few-ACS-pixel offsets may occur due to internal interpolations in the modeling
  ------------------------------------------------------------------------------

 [E] Acknowledgments

 The different Frontier Fields Map Making groups have all contributed significantly to the identification and measurement
 of multiple images and cluster members. Correspondingly it was not always clear who was the first reference for each image and we tried 
 following the literature as closely as possible, and apologize for any mis-referencing. Nonetheless the contribution of 
 all Map Making groups as well as other individusls who contributed, is greatly appreciated, and products agreed upon internally within the Map Making groups have been used here as well. 
 