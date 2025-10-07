from Krome_to_despotic.Pipeline import KromeDespoticPipeline
import numpy as np

# Change the following paths to your local paths
path_krome = 'YOUR_PATH_TO_KROME'
path_cloud = 'Examples/Example_cloud.desp' 

 # Initial conditions 
metallicity_input = 1 # Solar metallicity
redshift_input = 0 # Cosmological redshift
d2g = None # dust-to-gas ratio, if None, taken from metallicity

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

start_density = 1e1   # Density to start the calculations at, cm^-3
stop_density  = 3e6   # Density to stop the calculations at, cm^-3
factor = 1.25 # Factor between consecutive densities

# number of steps = log(stop/start) / log(factor)
num_steps = int(np.floor(np.log(stop_density/start_density) / np.log(factor))) + 1

# Array of densities to calculate at   
density_array = start_density * factor**np.arange(num_steps)

# Initialize and run the pipeline
krome_start = KromeDespoticPipeline(path_krome, path_cloud,
                                    test_name = test_name,
                                    test = test,
				    verbose = verbose)

krome_start.run(density_array = density_array,
                          metallicity_input = metallicity_input, 
                          redshift_input = redshift_input,
                          crate = crate, chi0 = chi0, include_chemistry = include_chemistry, clean = clean, save = save, safe = safe, 
                          LTE = LTE, dVdr_input = dVdr, sigmaNT = sigmaNT, d2g = d2g,
                          species = species, properties = properties, length = length, geometry = geometry,
			  folder_name_save = 'build_test')
