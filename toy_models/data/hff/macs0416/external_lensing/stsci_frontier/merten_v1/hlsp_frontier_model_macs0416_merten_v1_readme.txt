Cluster: MACS J0416
Method: SaWLens 
Author: Julian Merten

Description: The "map" file contains a single reconstruction of the cluster field and shows as a FITS image the convergence, both components of the shear, the determinant of the lens mapping Jacobian and the magnification. All FITS images contain a WCS. Several versions for different redshifts are provided and the FITS headers contain the lens redshifts under the keyword "Z_L" and the source redshift under "Z_S".  The file is a multi-extension FITS file with the following image content:

primary: convergence
ext.: shear1
ext.: shear2
ext.: jacdet
ext.: magnification

Map details:
Centre: 64.034684; -24.071618 [RA/DEC/in deg]
x-dim [pixels]: 180
y-dim [pixels]: 180
Field size x [arcsec]: 1500 
Field size y [arcsec]: 1500
pixel scale [arcsec]: 8.33

Input data WL:
-Subaru Rc-band shear catalogue, 21241 sources at an effective lensing redshift of z_s = 1.24, background selected with a colour-colour method. This catalogue cover the full 1500 arcsec field. Source: CLASH team 
-HST/ACS multi-band shear catalogue,  551 sources at an effective lensing redshift of z_s = 1.16, background selected by photo-zs. This catalogue covers the inner ~300 arcsec of the field. Source: CLASH team

Input data SL:
-The following multiple image system following the nomenclature of the Frontier Field arcs Google spreadsheet used by the map makers. Source: CLASH team, J. Merten and the ST FF map makers:

ID   RA	       DEC	z     delta_z

  1.1  64.04075 -24.06159     1.896	0.01     
  1.2  64.04348 -24.06354
  1.3  64.04735 -24.06867
  2.1  64.04118 -24.06188     1.8925	0.01
  2.2  64.043   -24.06304
  2.3  64.04748 -24.06885
  3.1  64.03078 -24.06712     1.9893	0.01
  3.2  64.03525 -24.07098
  3.3  64.04182 -24.07571
  4.1  64.03083 -24.06723     2.25	0.3
  4.2  64.03515 -24.07098
  4.3  64.04188 -24.07586
  5.1  64.03239 -24.0684      2.45	0.3	
  5.2  64.03266 -24.06867
  5.3  64.03351 -24.06945
  8.1  64.0366  -24.06613     2.4	0.25
  8.2  64.03683 -24.06634
  9.1  64.02703 -24.07858     2.35	0.5
  9.2  64.02752 -24.07911
  9.3  64.03812 -24.08368
  10.1 64.02602 -24.07716     2.2997	0.01
  10.2 64.02847 -24.07976
  12.1 64.03846 -24.07382     1.7	0.3
  12.2 64.03755 -24.07326
  13.1 64.02758 -24.07279     3.2226	0.01
  13.2 64.03213 -24.07517
  13.3 64.04034 -24.08154
  14.1 64.02623 -24.07434     2.0554	0.01
  14.2 64.03104 -24.07896
  14.3 64.03583 -24.08133
  16.1 64.02406 -24.08089     1.9644	0.01	
  16.2 64.02833 -24.08454
  16.3 64.0316  -24.08577

Map production details:
The SaWLens method (Merten et al. 2009, 2011) was used to produce these maps with a three-level adaptive mesh scheme. The first level is a full-field run using all WL and SL data on relatively low resolution, which then serves as a template for the run on the med-resolution regimes focussing on the area which is covered by the VLT and HST WL catalogue. This reconstruction is then again used as a template for the final reconstruction of the cluster core on high resolution and which is mostly dominated by the CL constraints.

lowres:
-750.0 -- 750.0; -750.0 -- 750.0  [x/y/in arcsec] around centre 
60x60 [pixels] with 25 arcsec resolution per pixel
medres:
-75.0 -- 75.0; -75.0 -- 75.0  [x/y/in arcsec] around centre
14x14 pixels with 10.71 arcsec resolution per pixel
highres:
-66.66 -- 50.00; -66.66 -- 50.0  [x/y/in arcsec] around centre
14x14 pixel with 8.33 arcsec resolution per pixel

Error maps info:
Also attached are error maps for convergence, shear and magnification, following the same FITS extension scheme as for the actual maps. All error maps contain the a WCS and are available for the same redshifts as the actual maps.

Map details:
Centre: 64.034684; -24.071618  [RA/DEC/in deg]  
x-dim [pixels]: 360
y-dim [pixels]: 360
Field size x [arcsec]: 1500 
Field size y [arcsec]: 1500
pixel scale [arcsec]: 4.17


Error maps production:
All errors are derived from bootstraps realisations of the three different regimes highlighted above. The maps show a simple 1 SD error in each pixel, as they are derived from the bootstraps using the full sample and not only certain quartiles, as discussed within the map maker teams. The bootstraps of the different regimes are presented in a separate readme file.  
    
Bootstraps:

Description: Because of the way how SaWLens works and to keep runtime at acceptable levels, we produce bootstrap realisations for three different regimes of the cluster field separately. Each bootstrap realisation is a multi-extension FITS file with the following images

primary: convergence
1.ext.: shear1
2.ext.: shear2 
3.ext.: jacdet
4.ext.: magnification
5.ext.: field mask

The last extension shows masked pixels in the reconstructed field by a pixel value of "not 0" instead of 0 for unmasked pixels. All FITS images contain in their header the redshift of the lens under the keyword "Z_L" and the source redshift the map is scaled to under keyword "Z_S".

The bootstraps were derived by bootstrap-resampling the input WL catalogues and by randomly sampling the allowed redshift range of SL features.  

Bootstrap regimes:

lowres
Filename: */rec1_BS<N>.fits
Number of bootstraps: 250/250/250/250/250 [z=1/2/4/9/20000]
Field size: -750.0 -- 750.0; -750.0 -- 750.0  [x;y in arcsec]
Field centre: 64.034684; -24.071618 [RA/DEC/in deg]  
Map size: 30x30 [pixel]

medres
Filename: */rec2_BS<N>.fits
Number of bootstraps: 250/250/250/250/250 [z=1/2/4/9/20000]
Field size: -75.0 -- 75.0; -75.0 -- 75.0   [x;y in arcsec]
Field centre: 64.034684; -24.071618 [RA/DEC/in deg]   
Map size: 12x12 [pixel]

highres
Filename: */rec3_BS<N>.fits
Number of bootstraps: 901/845/765/735/670   [z=1/2/4/9/20000]
Field size: -75.0 -- 75.0; -75.0 -- 75.0   [x;y in arcsec]
Field centre: 64.034684; -24.071618 [RA/DEC/in deg]  
Map size: 18x18 [pixel]
    
