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
Specific notes for Abell 2744

LENS DATA

We use 71 images from 24 gold systems:
1, 3, 4, 6, 8, 10, 18, 22, 24, 26, 30, 31, 33, 34, 37, 39, 40, 41, 42, 61, 62, 63, 47, 147
Among systems classified as gold, we omit #5, #105, and #64 because it is not clear how to match counter-images.

GALAXY DATA

We use the following data to construct the galaxy catalog from which we select members and important line-of-sight galaxies.

Spectroscopic redshifts:
* Owers et al. -- http://iopscience.iop.org/0004-637X/728/1/27/fulltext/apj377497t5_mrt.txt
* GLASS -- https://archive.stsci.edu/prepds/glass
* ASTRODEEP -- http://astrodeep.u-strasbg.fr/ff/
Photometry:
* ASTRODEEP
* Coe catalog -- https://stsci.app.box.com/v/Coe-FF-catalogs
* Subaru -- https://archive.stsci.edu/missions/hlsp/frontier/abell2744/catalogs/subaru/

Our member selection yields:
* 92 spectroscopically confirmed members
* 163 photometrically selected members

We add seven line of sight galaxies:

  RA           Dec       type    z           color   notes
------------------------------------------------------------------------------
3.58741033 -30.39330259 spec-z 0.499          blue   spiral in lensing region
3.59032801 -30.40038939 spec-z 0.498          blue   spiral in lensing region
3.589198   -30.393581   phot-z 0.43 +/- 0.06  blue   just north of 3.1 and 3.2
3.60005    -30.389715   spec-z 0.063          blue   spiral in east
3.584968   -30.383724   spec-z 0.239          blue   spiral in north
3.574393   -30.383654   spec-z 0.255          blue   spiral in northwest
3.593273   -30.384378   spec-z 0.296          blue   spiral in northeast

(The color determines which scaling relation is used, as described in the general notes.)

MODEL NOTES

Our model prefers three halos: two in the cluster core and one to the west.  The neighbor component could represent a physical object, or it could be working with the shear to reflect complexity in the large-scale distribution of matter.  Its position is well constrained in our models, but its core properties vary quite substantially in the range models.  We place mild priors on the ellipticity of this third halo.

Image plane RMS = 0.41".

We did not use the magnification for SN Tom as a constraint on the models because we wanted to use it as a posterior check.  Our models predict a magnification of 2.40+/-0.10, which (like many previous models that did not use the constraint) is biased high but consistent with the observed value given uncertainties (qv. Rodney et al. 2015, ApJ, 811, 70).

