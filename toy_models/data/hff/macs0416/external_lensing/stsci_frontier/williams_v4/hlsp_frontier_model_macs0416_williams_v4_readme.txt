
=================================================
MACS J0416 HFFv4 reconstruction by the GRALE team
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

RA box limits (arcsec): -64.8 --> 64.8  
Dec box limits (arcsec): -64.8 --> 64.8 
The maps are 129.6 x 129.6 arcsec^2 and 648 x 648 pixels^2, with each pixel = 0.2 arcsec
The center of the reconstructed map is 
      RA = 64.0354947759
      Dec = -24.0730804968

IMAGES USED

The image set used (101 images from 37 sources) is given below
(source redshifts were determined spectroscopically for at least one of the images in the system; all systems are GOLD)
SOURCE.IMAGE    RA               Dec             z       NOTES
1.1     	64.04075	-24.061592	1.896		
1.2     	64.043479	-24.063542	1.896
1.3     	64.047354	-24.068669	1.896
2.1     	64.041183	-24.061881	1.8950
2.2     	64.043004	-24.063036	1.8950
2.3     	64.047475	-24.06885	1.8950
3.1     	64.030783	-24.067117	1.9894
3.2     	64.035254	-24.070981	1.9894
3.3     	64.041817	-24.075711	1.9894
4.1     	64.030825	-24.067225	1.990
4.2     	64.035154	-24.070981	1.990
4.3     	64.041879	-24.075856	1.990
5.1     	64.032375	-24.068411	2.0948
5.2     	64.032663	-24.068669	2.0948
5.3     	64.033513	-24.069447	2.0948
7.1     	64.0398		-24.063092	2.0881
7.2     	64.040633	-24.063561	2.0881
7.3     	64.047117	-24.071108	2.0881
10.1     	64.026017	-24.077156	2.2982
10.2	        64.028471	-24.079756	2.2982
10.3	        64.036692	-24.083901	2.2982
11.1	        64.039208	-24.070367	1.0054
11.2	        64.038317     	-24.069753	1.0054
11.3	        64.034259     	-24.066018	1.0054
13.1	        64.027579	-24.072786	3.2175
13.2        	64.032129	-24.075169	3.2175
13.3        	64.040338	-24.081544	3.2175
14.1	        64.026233	-24.074339	1.6333
14.2	        64.031042	-24.078961	1.6333
14.3	        64.035825	-24.081328	1.6333
16.1	        64.024058	-24.080894	1.966
16.2	        64.028329	-24.084542	1.966
16.3	        64.031596	-24.085769	1.966
17.1	        64.029875	-24.086364	2.2182
17.2	        64.028608	-24.085986	2.2182
17.3	        64.023329	-24.081581	2.2182
23.1	        64.044546	-24.0721	2.09
23.3	        64.034342	-24.063742	2.09
26.1	        64.04647	-24.060393	3.2355
26.2	        64.046963	-24.060793	3.2355
26.3	        64.049089	-24.062876	3.2355
15.1	27.1	64.048159	-24.066959	2.1067
15.2	27.2	64.047465	-24.066026	2.1067	
15.3	27.3	64.042226	-24.060543	2.1067	
28.1	        64.036457	-24.067026	0.9397
28.2	        64.03687	-24.067498	0.9397
33.1	        64.028427	-24.082995	5.3650
33.2	        64.035052	-24.085486	5.3650
33.3	        64.02298	-24.077275	5.3659
34.1	        64.029254	-24.073289	5.1060
34.2	        64.030798	-24.07418	5.1060
35.1	        64.037492	-24.083636	3.4909
35.2	        64.029418	-24.079861	3.4909
35.3	        64.024937	-24.075016	3.4909
38.1	        64.033625	-24.083178	3.4406
38.2	        64.031255	-24.081905	3.4406
38.3	        64.022701	-24.074589	3.4406
44.1	        64.045259	-24.062757	3.2885
44.2	        64.041543	-24.059997	3.2885
44.3	        64.049237	-24.068168	3.2885
47.1	        64.026328	-24.076694	3.2526
47.2	        64.028329	-24.078999	3.2526
48.1	        64.035489	-24.084668	4.1218
48.2	        64.029244	-24.081802	4.1218
48.3	        64.023416	-24.076122	4.1218
49.1        	64.033944	-24.074569	3.8710
49.2	        64.040175	-24.079864	3.8710
51.1	        64.04016	-24.08029	4.1032
51.2	        64.033663	-24.074752	4.1032
51.3	        64.02662	-24.070494	4.1032
55.1	        64.035233	-24.064726	3.2922 
55.3	        64.038514	-24.065965	3.2922 
58.1	        64.025187	-24.073582	3.0773
58.2	        64.03773	-24.08239	3.0773
58.3	        64.030481	-24.07922	3.0773
67.1	        64.038075	-24.082404	3.1103
67.2	        64.025451	-24.073651	3.1103
67.3	        64.030363	-24.079019	3.1103
22.1 	        64.034485	-24.066919	3.2215   Diego+ image labels
22.2 	        64.034181	-24.066489	3.2215     "
22.3 	        64.034006	-24.066447	3.2215     "
32.1	        64.045119	-24.072336	3.2882     "
32.2	        64.040081	-24.06673	3.2882     "
2.1        	64.050865	-24.066538	6.1452   Caminha+ image labels
2.2        	64.048179	-24.062406	6.1452     "
2.3	        64.043572	-24.059004	6.1452     "
6.1	        64.047808	-24.070164	3.6065     "
6.2	        64.043657	-24.064401	3.6065     "
6.3	        64.037676	-24.060756	3.6065     "
22.2	        64.030997	-24.077173	3.9230     "
22.3	        64.027127	-24.073572	3.9230     "
23.1	        64.035668	-24.079920	2.5425     "
23.2	        64.032638	-24.078508	2.5425     "
33.1	        64.032017	-24.084230	5.9729     "
33.2	        64.030821	-24.083697	5.9729     "
34.2	        64.027632	-24.082609	3.9228     "
34.3        	64.023731	-24.078477	3.9228     "
35.1        	64.033681	-24.085855	5.6390     "
35.2	        64.028654	-24.084240	5.6390     "
35.3	        64.022187	-24.077559	5.6390     "

The spectroscopic redshifts and image identifications quoted above were obtained by these groups:
Balestra et al. 2016,  ApJS, 224, 33  (arXiv:1511.02522)
Caminha et al. 2016,  Preprint  (arXiv:1607.03462)
Grillo et al. 2015, ApJ, 800, 38  (arXiv:1407.7866)
Hoag et al. 2016, ApJ, 831, 182  (arXiv:1603.00505)
Jauzac et al. 2014, MNRAS, 443, 1549  (arXiv:1405.3582) 
Zitrin et al. 2013, ApJL, 762, 30  (arXiv:1211.2797)

ACKNOWLEDGMENTS

We gratefully acknowledge all the members of the Frontier Fields lens reconstruction teams for data they have contributed to this effort, and without which our mass reconstructions would not have been possible. We are also grateful to Dan Coe for coordinating this project and making it run smoothly. 
 
