General notes on methodology.

We build parametric models that treat the cluster as a collection of galaxies and large-scale halos, and also include foreground and background galaxies within the strong lensing region.  We focus on gold samples of sources because of the importance of spectroscopic redshifts for both image matching and lens modeling.

Galaxy selection: 
We combine public datasets (listed below) to assemble a catalog of redshifts and photometry for galaxies in the field.  We focus on the region within 2¿ of the field center, and on magnitudes brighter than F814W = 23.5.  For galaxies with spectroscopic redshifts, we use 3-sigma clipping to identify cluster members, and also to identify galaxies that are are known to lie in the foreground or background.  We use the confirmed members to identify a color-magnitude relation using F606W and F814W.  (For galaxies that lack photometry in one or both bands, we interpolate from nearby filters in other datasets such as Subaru or SDSS.)  Among galaxies without spectroscopic redshifts, we identify those within 1-sigma of the color-magnitude relation to be included as photometrically selected members.  (This sigma refers to the width of the color distribution.)

Model components:
- The large-scale halos are treated as softened isothermal ellipsoids, and the number of components varies from field to field.  The combination of components allows a lot of freedom to reproduce the mass distribution in the strong lensing region, but the isothermal profile is not likely to be accurate at large radii and so our models are probably not reliable far outside the strong lensing region (where they are not well constrained anyway). 
- Member galaxies are treated with spherical pseudo-Jaffe models characterized by Einstein radius and truncation radius.  In the fiducial model, the radii are locked via scaling relations from Brimioulle et al. (2013, MNRAS, 432, 1046):  sigma ~ L^0.25 so Rein ~ L^0.50, and r200 ~ L^0.40, where L is obtained from the F814W magnitude.  We fit for the normalization of scaling relation.  In the range models, we account for intrinsic scatter of 0.05 dex in sigma and 0.03 dex in r200 (see below).
- Line of sight (LOS) galaxies are also treated with spherical pseudo-Jaffe models.  We impose priors on their Einstein radii using scaling relations that evolve as L ~ (1+z) from Brimioulle et al., and we recognize that red and blue galaxies follow scaling relations that are parallel but have different normalizations.  In the models presented here, LOS galaxies are scaled to the lens plane using a factor Dps/Dls where ¿p¿ denotes perturber, assuming a fiducial source redshift of 2.  (We separately present models with LOS galaxies treated in their own lens planes.)  We allow an uncertainty of 0.3 dex on these Einstein radii to account for the fact that the scaling relation has intrinsic scatter, it may evolve differently than (1+z), and scaling to the lens plane should actually vary with source redshift.  We do not expect their truncation radii to be well constrained, so we fix them to log(r200/¿) = 2.
- We allow external shear in the lens plane to account for asymmetries in the distribution of galaxies outside the region we model.

Parameter search:
- When searching parameter space, we use a chi^2 goodness of fit that is evaluated in the source plane but includes magnification factors to produce a good approximation to a chi^2 evaluated in the image plane (see Keeton 2010, GRG, 42, 2151).  When reporting residuals, we work explicitly in the image plane.
- For the fiducial model, we lock the member galaxies to each other through the scaling relations, and fit for the scaling relation normalizations.  We allow the LOS galaxies to vary with priors from the scaling relations.
- To sample the range of models, we perturb all of the input data and refit.  This procedure lets us include three sources of uncertainty simultaneously:
  * Image positions: we adopt fiducial uncertainties of 0.5¿, comparable to typical residuals
  * Scatter in scaling relations: 0.1 dex for Einstein radius, and 0.03 dex for r200 (see above)
  * Uncertainties in photometric redshifts for LOS galaxies

We assume a cosmology with Omega = 0.3, Lambda = 0.7, and h = 0.7.



------------------------------------------------------------
Specific notes for MACSJ0416.1-2403

LENS DATA

We use 95 images from 35 gold systems (following the ¿New Arc ID¿ labeling in the Frontier Fields 2016 spreadsheet):
1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 30, 31, 32, 33, 34, 35, 36, 37
Among systems classified as gold, we omit #5 because one image is blended with a galaxy so that galaxy does not appear in catalogs, and #29 because it is a triplet around a galaxy so it mainly constrains that galaxy.

GALAXY DATA

We use the following data to construct the galaxy catalog from which we select members and important line-of-sight galaxies.

Spectroscopic redshifts:
* Balestra et al. -- https://sites.google.com/site/vltclashpublic/data-release
* Ebeling et al. -- http://www.ifa.hawaii.edu/~ebeling/FF-spectroscopy/
* GLASS -- https://archive.stsci.edu/prepds/glass/
* ASTRODEEP -- http://astrodeep.u-strasbg.fr/ff/?ffid=FF_M0416CL
Photometry:
* ASTRODEEP
* CLASH -- https://archive.stsci.edu/missions/hlsp/clash/macs0416/catalogs/hst/
* Coe catalog -- https://stsci.app.box.com/v/Coe-FF-catalogs
* Subaru -- https://archive.stsci.edu/missions/hlsp/frontier/macs0416/catalogs/subaru/

Our member selection yields:
* 146 spectroscopically confirmed members
* 61 photometrically selected members

We add 19 line of sight galaxies:

  RA           Dec       type    z    color   notes
--------------------------------------------------------------------------
64.028443  -24.085679   spec-z 0.114   red    large galaxy in south
64.032326  -24.08539    spec-z 0.113   red    just east of that, near 11.3
64.032099  -24.075641   spec-z 0.500   blue   edge-on spiral
64.032333  -24.074734   spec-z 0.469   blue   north of the spiral
64.028885  -24.07506    spec-z 0.459   red    west of the spiral
64.047287  -24.074467   spec-z 0.468   blue   spirals in the core or east
64.044109  -24.074422   spec-z 0.710   blue   "
64.041309  -24.071337   spec-z 0.94    blue   "
64.037033  -24.073761   spec-z 0.154   blue   "
64.041862  -24.076536   spec-z 0.424   red    near 3.3 and 4.3
64.023308  -24.071419   spec-z 0.736   blue   spirals in the west
64.023575  -24.068653   spec-z 0.734   blue   "
64.026558  -24.070131   spec-z 0.268   red    near 25.3
64.03717   -24.063656   spec-z 0.537   blue   spirals in the north, on
64.033279  -24.062946   spec-z 0.485   blue     either side of 13.3
64.047256  -24.063246   spec-z 0.528   blue   spiral in northeast
64.037941  -24.083113   spec-z 0.711   blue   near 19.1
64.032499  -24.078486   spec-z 0.400   red    right beside 34.2
64.037773  -24.066149   spec-z 0.520   blue   near 26.2

(The color determines which scaling relation is used, as described in the general notes.)

MODEL NOTES

Two halos are required to produce the proper morphology, and a third halo in the northeast significantly improves the fit.  We let the two main halos be free and place mild priors on the ellipticity of the third halo.  In initial modeling, it was difficult to get the parameter search to find models that run the critical curve between the close fold pair images 14.1 and 14.2.  We reduced the error bars on those two images to 0.1¿ as a way to encourage the model to put the critical curve in the right place.  Galaxy catalogs do not have good photometry for the background edge-on spiral at (64.032099, -24.075641), so we do not place priors on its Einstein radius.

Image plane RMS = 0.52".

