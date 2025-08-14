from Krome_to_despotic.Pipeline import KromeDespoticPipeline
import numpy as np


path_krome = '/home/eloy/Documents/Master_Astronomy/Master_Project/mykrome/'
path_cloud = '/home/eloy/Documents/Master_Astronomy/Master_Project/mydespotic/cloudfiles_own/MilkyWayGMC.desp' 

initial_density = 0.1
metallicity_input = 0.77
redshift_input = 0
target_density = 1e3

krome_start = KromeDespoticPipeline(path_krome, path_cloud, test_name = 'popsicle_semenov',
                                    initial_density_input = initial_density,
                                    redshift_input = redshift_input,
                                metallicity_input = metallicity_input)

krome_start.get_properties(target_density = target_density, n_transitions = 5, clean = True, run_krome = True,
                         LTE = True, dVdr_input = None, sigmaNT_input = 2e5, species = 'co', save = False, unsafe = True)
