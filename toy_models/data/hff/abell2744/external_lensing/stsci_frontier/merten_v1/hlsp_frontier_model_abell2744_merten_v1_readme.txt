Cluster: Abell 2744
Method: SaWLens 
Author: Julian Merten

Description: The "map" file contains a single reconstruction of the cluster field and shows as a FITS image the convergence, both components of the shear, the determinant of the lens mapping Jacobian and the magnification. All FITS images contain a WCS. Several versions for different redshifts are provided and the FITS headers contain the lens redshifts under the keyword "Z_L" and the source redshift under "Z_S".  The file is a multi-extension FITS file with the following image content:

primary: convergence
ext.: shear1
ext.: shear2
ext.: jacdet
ext.: magnification

Map details:
Centre: 3.58611; -30.40024 [RA/DEC/in deg]  
x-dim [pixels]: 180
y-dim [pixels]: 180
Field size x [arcsec]: 1500 
Field size y [arcsec]: 1500
pixel scale [arcsec]: 8.33

Input data WL:
-Subaru i-band shear catalogue, 16121 sources at an effective lensing redshift of z_s~1.0, background selected with a simple magnitude and size cut. The seeing of this image was bad: > 1.0 arcsec. This catalogue cover the full 1500 arcsec field. Source: N. Okabe and Merten et al. 2011
-VLT multi-band shear catalogue, 912 sources at an effective lensing redshift of z_s = 1.01, background selected by photo-zs. This catalogue covers the inner ~400 arcsec of the total field. Souce: E. Cypriano and Merten et al. 2011  
-HST/ACS F814W shear catalogue, 1205 sources at an effective lensing redshift of z_s = 1.18, background selected by photo-zs. This catalogue covers the inner ~300 arcsec of the field. Source: Merten et al. 2011

Input data SL:
-The following multiple image system following the nomenclature of the Frontier Field arcs Google spreadsheet used by the map makers. Source: J. Merten and the ST FF map makers:

ID   RA	       DEC	z     delta_z

  1.1  3.5975477 -30.403918   2.0	0.3	     
  1.2  3.5959456 -30.406822
  1.3  3.5862071 -30.409985
  1.11 3.5970573 -30.404752
  1.21 3.5964031 -30.406125
  1.31 3.5857328 -30.410122
  2.1  3.5832588 -30.403351   2.0	0.3				
  2.2  3.5972752 -30.396724
  2.3  3.5854036 -30.399898
  2.4  3.5864275 -30.402128
  2.11 3.5825314 -30.402272
  2.21 3.5967382 -30.3963  
  2.31 3.5844847 -30.399286
  2.41 3.586237  -30.40085 
  3.1  3.5893808 -30.393875   4.0	0.3
  3.2  3.5888033 -30.393803
  3.3  3.5774802 -30.399566
  4.1  3.5921145 -30.402634   3.58	0.01
  4.2  3.5956434 -30.401623
  4.3  3.5804331 -30.408926
  4.4  3.5931933 -30.404915
  4.5  3.5935934 -30.405106
  5.1  3.5834304 -30.39207    4.0	0.5	 
  5.2  3.5849816 -30.391374
  5.3  3.5799722 -30.394762
  6.1  3.598534  -30.4018     2.019	0.01
  6.2  3.5940518 -30.408011
  6.3  3.5864225 -30.409371
  7.1  3.598259  -30.402319   3.7	0.5
  7.2  3.5952206 -30.407424
  7.3  3.5845994 -30.409814
  8.1  3.5896976 -30.394339   4.0	0.2
  8.2  3.588815  -30.394223
  9.1  3.5883815 -30.405271   3.0	0.5
  9.2  3.5871202 -30.406241
  9.3  3.6001472 -30.397154
  10.1 3.5883976 -30.405879   3.0	0.5	
  10.2 3.5873815 -30.406481
  10.3 3.6007164 -30.397099
  11.1 3.591379  -30.403857   3.0	0.5
  11.2 3.5972615 -30.401452
  11.3 3.5827795 -30.408913
  11.4 3.5945353 -30.406543
  12.1 3.5936083 -30.404469   2.8	0.8
  12.2 3.5932458 -30.403256  
  12.3 3.5945667 -30.402989
  13.1 3.5923625 -30.402558   1.3	0.9	   	
  13.2 3.5938042 -30.402164
  13.3 3.582775  -30.408044
  14.1 3.5897542 -30.394636   3.0	0.8	
  14.2 3.5884458 -30.394436
  16.1 3.5565333 -30.375808   3.1	0.5
  16.2 3.5563714 -30.376767
  16.3 3.5545667 -30.379308
  18.1 3.5907423 -30.395561   2.8	1.5	
  18.2 3.5883946 -30.395636     


Map production details:
The SaWLens method (Merten et al. 2009, 2011) was used to produce these maps with a three-level adaptive mesh scheme. The first level is a full-field run using all WL and SL data on relatively low resolution, which then serves as a template for the run on the med-resolution regimes focussing on the area which is covered by the VLT and HST WL catalogue. This reconstruction is then again used as a template for the final reconstruction of the cluster core on high resolution and which is mostly dominated by the CL constraints.

lowres:
-750.0 -- 750.0; -750.0 -- 750.0  [x/y/in arcsec] around centre 
60x60 [pixels] with 25 arcsec resolution per pixel
medres:
-50.0 -- 150.0; -50.0 -- 150.0  [x/y/in arcsec] around centre
16x16 pixels with 12.5 arcsec resolution per pixel
highres:
-50.0 -- 115.2; -50.0 -- 115.2  [x/y/in arcsec] around centre
20x20 pixel with 8.3 arcsec resolution per pixel

Error maps info:
Also attached are error maps for convergence, shear and magnification, following the same FITS extension scheme as for the actual maps. All error maps contain the a WCS and are available for the same redshifts as the actual maps.

Map details:
Centre: 3.58611; -30.40024 [RA/DEC/in deg]  
x-dim [pixels]: 180
y-dim [pixels]: 180
Field size x [arcsec]: 1500 
Field size y [arcsec]: 1500
pixel scale [arcsec]: 8.33


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
Field centre: 3.58611; -30.40024 [RA/DEC/in deg]
Map size: 30x30 [pixel]

medres
Filename: */rec2_BS<N>.fits
Number of bootstraps: 250/250/250/250/250 [z=1/2/4/9/20000]
Field size: -50.0 -- 150.0; -50.0 -- 150.0  [x;y in arcsec]
Field centre: 3.58611; -30.40024 [RA/DEC/in deg]
Map size: 12x12 [pixel]

highres
Filename: */rec3_BS<N>.fits
Number of bootstraps: 682/638/617/609/601 [z=1/2/4/9/20000]
Field size: -50.0 -- 150.0; -50.0 -- 150.0  [x;y in arcsec]
Field centre: 3.58611; -30.40024 [RA/DEC/in deg]
Map size: 24x24 [pixel]
    
