
=================================================
ABELL 2744 HFFv4 reconstruction by the GRALE team
=================================================

Authors: Liliya Williams, Kevin Sebesta, Jori Liesenborgs

BRIEF DESCRIPTION OF THE METHOD: GRALE

The method used to do the lensing reconstruction is GRALE, a free-form, adaptive grid method  that uses a genetic algorithm to iteratively refine the mass map solution. 

An initial course grid is populated with a basis set, such as a projected Plummer density profiles. A uniform mass sheet covering the whole modeling region can also be added to supplement the basis set.  As the code runs the more dense regions are resolved with a finer grid, with each cell given a Plummer with a proportionate width. The code is started with an initial set of trial solutions. These solutions, as well as all the later evolved ones are evaluated for genetic fitness, and the fit ones are cloned, combined and mutated. The procedure is run until a satisfactory degree of mass resolution is achieved.  The final map consists of a superposition of a mass sheet and many Plummers, typically several 100 to 1-2 thousand, each with its own size and weight, determined by the genetic algorithm. In this release we present 40 independent realizations of the reconstruction for each cluster.

Note that GRALE does not use any cluster galaxies to do the mass reconstruction; the only observational input are the lensed image positions, their redshifts (listed above), the redshift of the lensing cluster, and the parameters of the standard Lambda CDM.

For more detailed description of the method see

Priewe, J., Williams, L.L.R., Liesenborgs, J., Coe, D. & Rodney, S. A.	2017, MNRAS, 465, 1030
"Lens Models Under the Microscope: Comparison of Hubble Frontier Field Cluster Magnification Maps"

M. Meneghetti et al. 
"The Frontier Fields Lens Modeling Comparison Project"
	
Sebesta, K., Williams, L.L.R., Mohammed, I., Saha, P. & Liesenborgs, J.
"Testing light-traces-mass in Hubble Frontier Fields Cluster MACS-J0416.1-2403"

Liesenborgs, J., de Rijcke, S., Dejonghe, H., Bekaert, P. 2009, MNRAS, 397, 341
"Non-parametric strong lens inversion of SDSS J1004+4112"

Liesenborgs, J., de Rijcke, S., Dejonghe, H. & Bekaert, P. 2007, MNRAS, 380, 1729
"Non-parametric inversion of gravitational lensing systems with few images using a 
multi-objective genetic algorithm"

Liesenborgs, J., de Rijcke, S. & Dejonghe, H. 2006, MNRAS, 367, 1209
"A genetic algorithm for the non-parametric inversion of strong lensing systems"


COSMOLOGY

Omega_matter=0.3
Omega_Lambda=0.7
H_0=70 km/s/Mpc

DELIVERABLES

FITS maps with Dls/Ds=1: kappa, gamma, gamma1, gamma2, deflect_x (per pixel), deflect_y (per pixel) 
FITS maps of magnifications for sources at z = 1, 2, 4, 9

RA box limits (arcsec): -84.75 --> 84.75
Dec box limits (arcsec): -84.75 --> 84.75
The maps are 169.5 x 169.5 arcsec^2 and 678 x 678 pixels^2, with each pixel = 0.25 arcsec
The center of the reconstructed map is 
      RA = 3.5832485797
      Dec = -30.397713788

The image set used (91 images from 29 sources) is given below
(source redshifts were determined spectroscopically for at least one of the images in the system)
SOURCE.IMAGE  RA                 Dec                   z
    1.1       00:14:23.41       -30:24:14.10          1.688     
    1.2       00:14:23.03       -30:24:24.56          1.688 
    1.3       00:14:20.69       -30:24:35.95          1.688 
    2.1       00:14:19.98       -30:24:12.06          1.8876    
    2.2       00:14:23.35       -30:23:48.21          1.8876                            
    2.3       00:14:20.50       -30:23:59.63          1.8876                          
    2.4       00:14:20.74       -30:24:07.66          1.8876                          
    3.1       00:14:21.45       -30:23:37.95          3.9803   
    3.2       00:14:21.31       -30:23:37.69          3.9803 
    3.3       00:14:18.39       -30:24:06.53          3.9803                          
    4.1       00:14:22.11       -30:24:09.48          3.5719    
    4.2       00:14:22.95       -30:24:05.84          3.5719
    4.3       00:14:19.30       -30:24:32.13          3.5719  
    4.4       00:14:22.37       -30:24:17.69          3.5719  
    4.5       00:14:22.46       -30:24:18.38          3.5719                   
    6.1       00:14:23.65       -30:24:06.48          2.016  
    6.2       00:14:22.57       -30:24:28.84          2.016 
    6.3       00:14:20.74       -30:24:33.74          2.016                           
    8.1       00:14:21.53       -30:23:39.62          3.975   
    8.2       00:14:21.32       -30:23:39.20          3.975 
    8.3       00:14:18.33       -30:24:09.23          3.975                                     
   10.1       00:14:21.22       -30:24:21.16          2.655  
   10.2       00:14:20.97       -30:24:23.33          2.655 
   10.3       00:14:24.17       -30:23:49.56          2.655                                
   18.1       00:14:21.78       -30:23:44.02          5.6605  
   18.2       00:14:21.21       -30:23:44.29          5.6605  
   18.3       00:14:18.27       -30:24:16.11          5.6605        
   22.1       00:14:21.10       -30:24:41.80          5.283    
   22.2       00:14:24.02       -30:24:15.90          5.283 
   22.3       00:14:23.17       -30:24:32.51          5.283                
   24.1       00:14:23.02       -30:24:16.14          1.043 
   24.2       00:14:22.83       -30:24:21.36          1.043 
   24.3       00:14:20.96       -30:24:32.77          1.043        
   26.1       00:14:22.55       -30:24:34.87          3.052 
   26.2       00:14:21.69       -30:24:38.11          3.052 
   26.3       00:14:24.02       -30:24:10.69          3.052 
   30.1       00:14:21.84       -30:23:50.80          1.025    
   30.2       00:14:20.81       -30:23:53.47          1.025 
   30.3       00:14:19.66       -30:24:06.13          1.025 
   31.1       00:14:20.62       -30:24:11.40          4.7584
   31.2       00:14:20.09       -30:24:14.82          4.7584
   31.3       00:14:23.96       -30:23:43.88          4.7584                                          
   33.1       00:14:20.33       -30:24:11.33          5.7235
   33.2       00:14:20.26       -30:24:12.20          5.7235
   33.3       00:14:24.1004     -30:23:42.3964        5.7235
   34.1       00:14:22.42       -30:24:39.03          3.785 
   34.2       00:14:22.52       -30:24:38.61          3.785 
   34.3       00:14:24.14       -30:24:16.32          3.785 
   35.1       00:14:19.46       -30:24:00.75          2.656 
   35.2       00:14:19.57       -30:23:57.81          2.656                           
   35.3       00:14:23.48       -30:23:43.95          2.656                                     
   37.1       00:14:21.37       -30:23:41.69          2.649 
   37.2       00:14:21.29       -30:23:41.47          2.649                           
   39.1       00:14:21.31       -30:23:33.11          4.015 
   39.2       00:14:21.25       -30:23:33.03          4.015 
   39.3       00:14:18.59       -30:23:58.43          4.015 
   40.1       00:14:21.38       -30:23:33.59          4.015    
   40.2       00:14:21.17       -30:23:33.19          4.015  
   40.3       00:14:18.61       -30:23:57.74          4.015                           
   41.1       00:14:23.80       -30:23:58.50          4.9098
   41.2       00:14:22.454      -30:24:27.97          4.9098
   41.3       00:14:20.03       -30:24:30.60          4.9098
   41.4       00:14:21.7481     -30:24:16.0524        4.9098
   42.1       00:14:23.35       -30:24:02.19          3.69  
   42.2       00:14:21.83       -30:24:11.74          3.69  
   42.3       00:14:19.58       -30:24:31.08          3.69  
   42.4       00:14:22.62       -30:24:23.00          3.69  
   42.5       00:14:22.179      -30:24:18.6984        3.69                    
   61.1       00:14:22.89       -30:24:13.62          2.952 
   61.2       00:14:22.86       -30:24:16.02          2.952 
   62.1       00:14:21.9182     -30:23:55.1148        4.1925
   62.2       00:14:21.7397     -30:23:56.1048        4.1925
   63.1       00:14:19.7427     -30:24:25.7976        5.6599
   63.2       00:14:22.2619     -30:24:25.2792        5.6599
   63.3       00:14:21.392      -30:24:12.3084        5.6599
   63.4       00:14:23.7133     -30:23:53.8044        5.6599
   64.1       00:14:19.4872     -30:23:55.3488        3.4072
   64.2       00:14:23.1199     -30:23:39.2352        3.4072
    5.1       00:14:20.8622     -30:23:26.5344        4.0225
    5.2       00:14:20.3956     -30:23:28.9464        4.0225
    5.3       00:14:19.19       -30:23:41.1792        4.0225
  105.1       00:14:20.0233     -30:23:31.452         4.0225
  105.2       00:14:19.75       -30:23:34.0404        4.0225
  105.3       00:14:19.2988     -30:23:39.5376        4.0225
  105.4       00:14:19.4545     -30:23:37.0464        4.0225
   47.1       00:14:21.639      -30:23:31.8516        4.0225  
   47.2       00:14:20.602      -30:23:32.0784        4.0225
   47.3       00:14:18.799      -30:23:53.2788        4.0225
  147.1       00:14:21.523      -30:23:31.6896        4.0225
  147.2       00:14:20.749      -30:23:31.6608        4.0225
  147.3       00:14:18.722      -30:23:54.2112        4.0225

The spectroscopic redshifts and image identifications quoted above were obtained by these groups:
Jauzac et al. 2015, MNRAS, 452, 1437  (arXiv:1409.8663) 
Johnson et al. 2014, ApJ, 797, 48  (arXiv:1405.0222)
Merten et al. 2011, MNRAS, 417, 333  (arXiv:1103.2772) 
Richard et al. 2014, MNRAS, 444, 268  (arXiv:1405.3303)
Wang et al. 2015, ApJ, 811, 29  (arXiv:1504.02405) 
Mahler et al. 2017 (in preparation)


ACKNOWLEDGMENTS

We gratefully acknowledge all the members of the Frontier Fields lens reconstruction teams for data they have contributed to this effort, and without which our mass reconstructions would not have been possible. We are also grateful to Dan Coe for coordinating this project and making it run smoothly. 
 
