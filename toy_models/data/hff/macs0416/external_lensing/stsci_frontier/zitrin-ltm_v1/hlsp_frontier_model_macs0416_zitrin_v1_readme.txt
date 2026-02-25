# Readme file for the Frontier Fields models, by the Zitrin & Merten map-making group
# Constructed and supplied by Adi Zitrin
# Library and details for cluster: MACS 0416
# Modeled June 29-31 2013; last update August 30 2013

# The current ReadMe file contains:
 -General brief information of the methods incorporated
 -Specific information regarding the model of the said cluster of interest
 -Comments

# Library includes 3 model and error subdirectories, each corresponding to a different mass modeling method (or parametrization; see below for more details).
  Each of the 3 subdirectories/models contains 14 files. For each of the methods we use to model the clusters, we supply here:
 - best-fit deflection angle maps (x and y components), scaled to a source redshift specified therein, in units of pixels (with 0.065"/pix)
 - 1-sigma error maps for the above deflection fields
 - a best-fit kappa map, scaled to the same source redshift
 - 1-sigma error map for the above kappa map
 - a best-fit magnification map, scaled to the same source redshift
 - 1-sigma error map for the above magnification map
 - best-fit gamma maps (two components; gamma 1 and gamma 2), scaled to the same source redshift
 - 1-sigma error maps for the above gamma maps
 - an error file containing the best fit and 1-sigma errors for the parameter values
 - an image of the cluster used to register the wcs coordinates (Note: small, sub-arcsec, few-ACS-pixel offsets may occur due to internal interpolations in the modeling).

 - In addition, each subdirectory contains a zipped folder with 100 arbitrary models from the MC chain, calibrated to the same redshift as above, so that errors could be calculated for each desired redshift. The format of each such file in the zipped folder is a table, containing 100 models, where each model is given as a vector of length of the number of pixels in the FOV, divided by 16, and should be reshaped accordingly. The 101st model given therein is the best-fit model, for consistency check.

# The three methods applied are (i) the [revised, improved version of] Zitrin et al. 2009 (MNRAS, 396, 1985) light-traces-mass method (LTM), (ii) the same as (i) but with a Gaussian smoothing instead of a 2D Spline interpolation (also see below further details), and (iii) a PIEMD+eNFW parametrization (e.g. Zitrin et al. 2013, ApJ, 762L, 30). We refer the reader to these papers for additional information. We also ask that when when these models, please cite the two above papers as relevant. Also, user should acknowledge in the following manner, or similar: "The mass models were constructed by A. Zitrin et al. (2009,2013), and obtained through the Hubble Space Telescope Archive, as a high-end science product of the Frontier Fields initiative from the Zitrin & Merten map making group."

# Note also that additional, complete details of the lensing models will be given shortly in related works; or could be obtained directly (also for reporting problems, queries etc.) by contacting Adi at adizitrin@gmail.com .

# General, brief review of the modeling methods in use:

LTM: The light-traces-mass method used here was first sketched by Broadhurst et al. 2005 (ApJ, 621, 53), and later revised and simplified by Zitrin et al. 2009 (MNRAS, 396, 1985), where full details can be found. This method adopts the LTM assumption for *both* the galaxies and DM, which are the two main components of the mass model. We start by choosing cluster members following an identified red-sequence. Each cluster member is then assigned with a power-law mass density profile scaled by the galaxy's luminosity, so that the superposition of all galaxy contributions constitutes the first component for the model. This mass map is then smoothed with either a 2D Spline interpolation, or a Gaussian kernel (here we supply models with the two options), to obtain a smooth component representing the DM mass density distribution. The two mass components are then added with a relative weight, and supplemented by a 2-component external shear to allow for additional flexibility and higher ellipticity of the critical curves. The method thus includes six basic free parameters: the exponent of the power-law (q); the smoothing degree (s) - either the polynomial degree of the spline fit or the Gaussian width; the relative of weight of the galaxies component wrt the DM (k_gal); the overall normalization (k); and the strength and angle of the external shear (gamma, phi). Additionally, we add a core to the BCG(s); the core radius (r_c) is a free parameter(s) as well.
The best fit solution and accompanying errors are estimated via a long MCMC. Also, specific bright galaxies can be left to be freely optimized by the minimization procedure, as well as the redshift of multiple-image systems which do not have accurate source redshifts.

The LTM method has the unique advantage of aiding to find, physically by the initial model, multiple images across the cluster field, which can be then used to iteratively improve the model. The final fit, though, is still relatively strongly coupled to the light and thus may be somewhat less
flexible than other common parameterizations.

PIEMD+eNFW: To supply a second model which has inherently a higher spatial flexibility (and thus usually a somewhat better fit to the data), we also supply a model consisting of Pseudo Isothermal Elliptical Mass Distributions for the galaxies, whose superposition constitutes the lumpy, galaxies component for the model. The DM halo(s) is(are) then simply constructed using an analytical elliptical-NFW form, centered primarily on the BCG(s). This method includes two free parameters for the PIEMDs: the central velocity dispersion simga_0, and cut-off radius r_cut, of a reference (usually L*) galaxy, where all other galaxies are scaled relative to it by their luminosity. For each dark eNFW halo incorporated, four additional free parameters are added: the concentration c_200, scale radius r_s, ellipticity e, and angle phi. At times it is also useful leaving the DM center free to be optimized by the model, as well as specific bright galaxies, and redshift of multiple-image systems which do not have accurate source redshifts. More details on our implementation of this method are given in (e.g. Zitrin et al. 2013, ApJ, 762L, 30).


#Specific details for the models for MACS 0416

LTM_Spline: here we use a 2D polynomial Spline interpolation smoothing. We leave the three brightest galaxies to be freely weighted. As constraints we use the multiple images we have found as listed in Zitrin et al. 2013 (ApJ, 762L, 30) where we published the first model of this cluster. We use here systems 1-9, 13,14,16,17 of Zitrin et al. 2013. We also acknowledge input from Johan Richard et al. for spectroscopic redshifts and their input for the revision of multiple images in the framework of the Frontier Field map making discussions, and are most grateful for the CLASH/VLT spectroscopic effort supplying many redshifts for the multiple images used here (PI: Rosati, P.). We note that the redshifts of the 4 remaining systems were left to be optimized by the model (namely those that had no spectroscopic redshifts to date): systems number 5,6,8,9 (Zitrin+ 2013). The best-fit model, resulting multiple image reproduction rms, is 2.05" (using the average source position), and the chi^2 is 76.79 using a positional error of sigma_pos=1.4". The number of constraints we use is n_c=44, the number of free parameters is n_p=14, so that the number of DOF=30. This results in a reduced chi^2 of chi^2/DOF=2.55.

LTM_Gaussian: here we repeat the above model, but using a 2D Gaussian smoothing instead of the 2D polynomial Spline interpolation. The best-fit model, resulting multiple image reproduction rms, is 1.93" (using the average source position), and the chi^2 is 118.63 using a positional error of sigma_pos=1.4". The number of constraints we use is n_c=44, the number of free parameters is n_p=14, so that the number of DOF=30. This results in a reduced chi^2 of chi^2/DOF=3.95.

PIEMD+eNFW: on top of the PIEMD galaxies, two eNFW halos are used whose centers we fix on the centers of the two BCGs. Five bright galaxies as are left to be freely weighted by the MCMC, and the same set of constraints as above is used. The best-fit model, resulting multiple image reproduction rms is 1.5" (using the average source position), and the chi^2 is 41.51 using a positional error of sigma_pos=1.4". The number of constraints we use is n_c=44, the number of free parameters is n_p=18, so that the number of DOF=26. This results in a reduced chi^2 of chi^2/DOF=2.3.

# The resulting best-fit parameter values and errors are given in the designated attached file.

# Multiple images and red-sequence selected galaxies, as mentioned, are attached as a ds9 region file or table (multiple images can be obtained directly from Zitrin et al. 2013 (ApJ, 762L, 30).


#Comments:

-There may be some periodic artifacts especially towards the edges of the frame from the spline fitting; these are typically of order ~0.02 in kappa and are thus negligible compared with the noise/statistical errors.
-small, sub-arcsec, few-ACS-pixel offsets may occur due to internal interpolations in the modeling 