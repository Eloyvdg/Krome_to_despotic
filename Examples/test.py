from Krome_to_despotic.Pipeline import KromeDespoticPipeline
import numpy as np


path_krome = '/home/eloy/Documents/Master_Astronomy/Master_Project/krome_new/'
path_cloud = '/home/eloy/Documents/Master_Astronomy/Master_Project/mydespotic/cloudfiles_own/MilkyWayGMC.desp' 
#path_krome_build = '/home/eloy/Documents/Master_Astronomy/Master_Project/krome_new/build/AB_Z0'
# Popsicle_semenov_photo_cr_ismEqTest/build_z0_Z1e-1/AB_Z-1' 

metallicity_input = 1 # Solar metallicity
redshift_input = 10 



crate = 2e-16 # s^-1 H_2^-1
chi0 = 1.0 # ISRF relative to Solar neighborhood
sigmaNT = 5e6  # non-ther cm s^-1
dVdr = None # s^-1
d2g = None
LTE = False
species = [('CO', 5), ('C', 2), ('NH', 3)]
properties = ['intTB', 'tau', 'Tex']
include_chemistry = True
length = 'jeans'
geometry = 'LVG'
save = True
safe = False
clean = True
verbose = True

start = 1e1   # 10
stop  = 3e6   # 1,000,000
factor = 1.25

# number of steps = log(stop/start) / log(factor)
num_steps = int(np.floor(np.log(stop/start) / np.log(factor))) + 1

density_array = start * factor**np.arange(num_steps)

#density_array = np.array([0.2, 3.0, 10.0, 30.0, 60.0, 100.0])

krome_start = KromeDespoticPipeline(path_krome, path_cloud,
                                    test_name = 'popsicle_semenov_photo_cr_full_ismEqTest',
                                    test = 'test_shielded',
				    verbose = verbose)

krome_start.run(density_array = density_array,
                          metallicity_input = metallicity_input, 
                          redshift_input = redshift_input,
                          crate = crate, chi0 = chi0, include_chemistry = include_chemistry, clean = clean, save = save, safe = safe, 
                          LTE = LTE, dVdr_input = dVdr, sigmaNT = sigmaNT, d2g = d2g,
                          species = species, properties = properties, length = length, geometry = geometry)

#krome_start.run()
