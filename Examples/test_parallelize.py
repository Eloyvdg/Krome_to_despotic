'''
  ! *************************************************************
  !  Krome_to_despotic
  !
  !  Written by Eloy van de Genugten (Leiden University, 2025)
  !  With Piyush Sharda (LU), Jackie Hodge (LU) and Shyam Menon (CCA)
  !  Email: eloyvandegenugten@gmail.com, sharda@strw.leidenuniv.nl
  !  Krome_to_despotic is provided "as it is", without any warranty.
  ! *************************************************************
'''

from Krome_to_despotic.Pipeline import KromeDespoticPipeline
import numpy as np
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import traceback
from tqdm import tqdm
import os
import time


# Change the following paths to your local paths
cwd = os.getcwd()
path_krome = os.path.join(cwd, 'krome/')
path_cloud = 'Examples/Example_cloud.desp' 

 # Initial conditions 
metallicity_input = 1 # Solar metallicity
redshift_input = 0 # Redshift
d2g = None # dust-to-gas ratio, if None, taken from metallicity
density_array = [0.1, 1e6] # Initial and target density

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
skip_krome = False # Skip KROME and run despotic only
points = 50 # Number of densities to save

# --- Setup ---
crate_array = np.logspace(-3, 3, num=2, base=10)
chi0_array = np.logspace(-1, 4, num=2, base=10)

def run_case(trial_idx, i, j):
    krome_start = KromeDespoticPipeline(path_krome, path_cloud,
                                    test_name = test_name,
                                    test = test,
				    verbose = verbose)
    try:
        krome_start.run(
            density_array=density_array,
            metallicity_input=metallicity_input,
            redshift_input=redshift_input,
            crate=crate*crate_array[i],
            chi0=chi0_array[j],
            include_chemistry=include_chemistry,
            clean=clean,
            save=save,
            safe=safe,
            LTE=LTE,
            dVdr_input=dVdr,
            sigmaNT=sigmaNT,
            d2g=d2g,
            species=species,
            properties=properties,
            points = 50,
            length=length,
            geometry=geometry,
            folder_name_save=f'build_crate_chi0_solar_z10/build_{i}_{j}',
            project = str(trial_idx)
        )
        return (trial_idx, i, j, "success")
    except Exception as e:
        return (trial_idx, i, j, f"error: {e}")
    

tasks = [(trial_idx, i, j) 
         for trial_idx, (i,j) in enumerate([(i, j) for i in range(len(crate_array)) for j in range(len(chi0_array))])]

N_TRIALS = len(tasks)
max_workers = 2 #Number of cores used 

with ThreadPoolExecutor(max_workers=max_workers) as executor:
    futures = {}
    for trial_idx, i, j in tasks:
        # Submit one task
        futures[executor.submit(run_case, trial_idx, i, j)] = trial_idx
        
        # Sleep to prevent simultaneous starts
        time.sleep(1)   # adjust delay as needed (seconds)

    # Collect results as they complete
    for future in tqdm(as_completed(futures), total=N_TRIALS):
        trial_idx = futures[future]
        try:
            result = future.result()
            print("Finished:", result)
        except Exception:
            traceback.print_exc()
            print(f"Failed at trial {trial_idx}")


