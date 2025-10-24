from Krome_to_despotic.Pipeline import KromeDespoticPipeline
import numpy as np
import glob
import os

# Change the following paths to your local paths
path_krome = 'YOUR_PATH_TO_KROME'
path_cloud = 'Examples/Example_cloud.desp' 
path_to_krome_data = 'YOUR_PATH_TO_KROME_DATA'

 # Initial conditions 
metallicity_input = 1 # Solar metallicity
redshift_input = 0 # Cosmological redshift
d2g = None # dust-to-gas ratio, if None, taken from metallicity
density_array = [0.1, 1e6] # Initial density and target density
# Physical parameters
crate = 2e-16 # Cosmic ray ionization rate,  s^-1 H_2^-1
chi0 = 1 # ISRF, relative to Solar neighborhood
sigmaNT = 2e5  # non-thermal velocity dispersion, cm s^-1
dVdr = None # Velocity gradient, s^-1
LTE = False # Local Thermal Equilibrium. If False, non-LTE
geometry = 'LVG' # Cloud geometry, 'LVG', 'sphere' or 'slab'
length = 'shielding' # Cloud length used for column density calculations, 'jeans' or 'shielding'

# KROME parameters
test_name = 'popsicle_semenov_photo_cr_full_ismEqTest' # Name of the test in KROME
test = 'test_shielded' # Name of the sub-test in KROME

# Despotic parameters
species = [('CO', 5), ('C', 2)] # List of tuples (species, n_transitions)
properties = ['intTB', 'tau', 'Tex'] # List of despotic properties to compute

# Additional parameters
include_chemistry = True # Include chemistry from KROME in despotic calculations
save = True # Save results to a .txt file
safe = False # Ignore warnings and errors
clean = True # Clean KROME build folder
verbose = True # Verbose output
skip_krome = True # Skip KROME, and run despotic directly

# Initialize and run the pipeline
krome_start = KromeDespoticPipeline(path_krome, path_cloud,
                                    test_name = test_name,
                                    test = test,
				    verbose = verbose)

path = '/home/eloy/Documents/Master_Astronomy/Master_Project/Models/'
files = glob.glob(path + 'build_crate_chi0_solar/*')
metallicities = [0.1, 0.5, 1]
crate_array = np.logspace(-3, 3, num=20, base=10)
chi0_array = np.logspace(-1, 4, num=20, base=10)


path_to_krome_data = file + '/build/'
krome_start.run(density_array = density_array,
                        metallicity_input = metallicity_input, 
                        redshift_input = redshift_input,
                        crate = crate*crate_array[i], chi0 = chi0_array[j], include_chemistry = include_chemistry,
                        clean = clean, save = save, safe = safe, 
                        LTE = LTE, dVdr_input = dVdr, sigmaNT = sigmaNT, d2g = d2g,
                        species = species, properties = properties, length = length, geometry = geometry,
                        folder_name_save = f'build_despotic/build', path_to_krome_data = path_to_krome_data, skip_krome=skip_krome)
