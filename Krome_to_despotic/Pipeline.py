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

import numpy as np
import os 
from Krome_to_despotic.utils import *
from Krome_to_despotic.cosmology import age_universe
import glob
import warnings
from despotic import cloud


class KROME_FileEditor: 
    def __init__(self, density:float, metallicity:float, redshift:float): 
        """
        Initialize the editor for modifying KROME test files.
        Initial total density in cm^-3.
        Metallicity in Solar units.
        Cosmological redshift.
        """
        self.density = density 
        self.metallicity = metallicity
        self.redshift = redshift
        
    def change_variables(self, path:str, density_array:np.ndarray, crate:float = None, chi:float = None, sigmaNT:float = None, d2g:float = None):
        """Modify key variables in a KROME test file in place.
        This method updates specific variables and parameters within a KROME .f90 test file,
        such as density, cosmic ray ionization rate (crate), FUV field strength (chi), 
        non-thermal velocity dispersion (sigmaNT), and dust-to-gas ratio (d2g), according to 
        the provided arguments. The file is overwritten with the new values.
            
        path: str
            Path to the KROME .f90 test file to modify.
        density_array : np.ndarray
            Array of density values; the last value is used as the target density for stopping conditions.
        crate : float, optional
            Cosmic ray ionization rate to set in the file (default: None, no change).
        chi : float, optional
            FUV field strength to set in the file (default: None, no change).
        sigmaNT : float, optional
            Non-thermal velocity dispersion to set in the file (default: None, no change).
        d2g : float, optional
            Dust-to-gas ratio to set in the file (default: None, no change).
        
        Notes
        -----
        - The file is modified in place; the original file is overwritten.
        - Assumes the presence of specific KROME formatting and keywords.
        - Only the variables for which a new value is provided (not None) are updated.
        - The method relies on the presence of certain attributes in the class (e.g., self.density, self.metallicity, self.redshift).
        """
        
        target_density = density_array[-1]
        ntot_list = [str("{0:.0E}".format(self.density)), None, str("{0:.0E}".format(target_density))]
        idx_ntot_list = 0

        newlines = []
        
        with open(path, 'r') as file: 
                lines = file.readlines()
                   
        for line in lines: 

            if 'crate_0 = ' in line and 'calculate_F' not in line: 
                if crate is not None:
                    # Change crate
                    line_split = line.split(' ')
                    line_split[line_split.index('=') + 1] = str("{0:.0E}".format(crate))
                    line = ((' ').join(line_split))
                    line = d_formatter(line)
                    
            elif """write(22, '(A)', ADVANCE='NO') "#ntot """ in line:  
                if crate is not None and 'crate' not in line: 
                    line_split = line.split(' ')
                    line_split.insert(line_split.index('Tgas'), 'crate')
                    line = (' ').join(line_split)
                
            elif "write(22,'(99E17.8e3)')" in line: 
                if crate is not None and 'crate' not in line:
                    line_split = line.split(',')
                    line_split.insert(line_split.index('Tgas'), 'crate')
                    line = (',').join(line_split)
                    
            if 'chiFUV = ' in line or 'chi0 = ' in line: 
                if chi is not None:
                    if 'chiFUV = (' not in line:
                        line_split = line.split(' ')
                        line_split[line_split.index('=') + 1] = str(chi)
                        line = (' ').join(line_split)
            
            elif 'call krome_set_user_sigmavel' in line: 
                line_split = line.split('(')
                line_split[1] = str("{0:.0E}".format(sigmaNT)) + ')'
                line = ('(').join(line_split)
                line = d_formatter(line)
            
            #elif 'total density' in line: 
            #    line_split = line.split(' ')
            #    line_split[line_split.index('=') + 1] = str(self.density)
            #    line = (' ').join(line_split)
            
            elif 'ntot = ' in line: 
                print('idx:', idx_ntot_list)
                if idx_ntot_list == 0 or idx_ntot_list == 2:
                    line_split = line.split(' ')
                    line_split[line_split.index('=') + 1] = str(ntot_list[idx_ntot_list])
                    line = (' ').join(line_split)
                    line = d_formatter(line)

                idx_ntot_list += 1

            elif 'zs = ' in line: 
                start = line.find('(/')
                end = line.find('/)', start) + 2
                line = line[:start] + f'(/{self.metallicity}/)' + line[end:]

            elif 'krome_redshift = ' in line:
                line_split = line.split(' ')
                line_split[line_split.index('=') + 1] = str(self.redshift)
                line = (' ').join(line_split)
  
            elif 'nz=' in line: 
                loc_equal = line.find('=')
                loc = []
                for idx, i in enumerate(line): 
                    if i.isdigit() == True:
                        loc.append(idx)
                 
                if len(loc) > 1: 
                    line = line.replace(line[loc_equal + 1: loc_equal + 1 + len(loc)], '1')
                
                else: 
                    line = line.replace(line[loc_equal + 1], '1')
                
            elif 'call krome_set_dust_to_gas' in line and 'd2g' not in line: 
                line_split = line.split('(')
                line_split[-1] = d2g + ')'
                line = ('(').join(line_split)
                   
            elif 'd2g = ' in line: 
                line_split = line.split(' ')
                line_split[-1] = str(d2g)
                line = (' ').join(line_split)

                    
            elif 'dd.gt' in line: 
                line_split = line.split('.')
                line_split[line_split.index('gt') + 1] = str("{0:.0E}".format(target_density)) + ') exit'
                line = ('.').join(line_split)
                line = d_formatter(line)
            
            elif 'ntot .gt. ' in line and 'then' in line: 
                line_split = line.split('.gt.')
                line_split[1] = " " + str("{0:.0E}".format(target_density)) + ') then'
                line = ('.gt.').join(line_split)
                line = d_formatter(line)
            
            elif 'dens_array = (/' in line: 
                line_split = line.split('(/')
                values_str = ", ".join(f"{v:.1f}" for v in density_array)
                line_split[1] = f'{values_str}' + '/)'
                line = ('(/').join(line_split)

            elif 'max_time=' in line: 
                age_of_universe = age_universe(self.redshift) - 1e8 # Subtract first 100 Myr to allow for star formation at high z
                print('The max_time is set to the age of the universe at z =', self.redshift, 'which is', "{0:.3E}".format(age_of_universe), 'years')
                print('The first 100 Myr are subtracted, because stars were not formed before that time')
                if 'MIN' in line: 
                    line_split = line.split('MIN(')
                    line_split[1] = str("{0:.3E}".format(age_of_universe)) + f',1e9)'
                    line = ('MIN(').join(line_split)
                    line = d_formatter(line)
                else:
                    line_split = line.split('*')
                    line_split[1] = 'MIN(' + str("{0:.3E}".format(age_of_universe)) + ',1e9)'
                    line = ('*').join(line_split)
                    line = d_formatter(line)
 
            newlines.append(line)
                
        
        with open(path, 'w') as file: 
            for line in newlines: 
                file.write(line if line.endswith('\n') else line + '\n')    
                    
class KromeRunner():
    def __init__(self, path:str, file_editor, test_name:str='popsicle_semenov', test:str='test'): 
        """
        Create a runner for KROME tests.

        Parameters
        ----------
        path : str
            The path to where KROME is stored
        test_name : str
            Name of the test case to run: 
        file_editor : KROME_FileEditor
            Instance of `KROME_FileEditor` used to modify the test file
        test : str, optional
            Name of specific test case to run:
        """

        self.path = path
        self.test_name = test_name
        self.test = test
        self.file_editor = file_editor
        
    def run_krome(self, density_array:np.ndarray, crate:float = None, chi:float = None, sigmaNT:float = None, d2g:float = None, verbose:bool = True, clean:bool = True, safe:bool = False, folder_name_save = 'build', project:str = None):
        """
        Runs the KROME chemical modeling pipeline for a given test case, allowing customization of physical parameters and build options.
        Parameters:
            density_array (np.ndarray): Array of density values to be used in the model. cm^-3
            crate (float, optional): Cosmic ray ionization rate. If None, the default value is used. s^-1 H_2^-1
            chi (float, optional): UV radiation field scaling factor. If None, the default value is used. Relative to Solar neighborhood
            sigmaNT (float, optional): Non-thermal velocity dispersion. If None, the default value is used. cm s^-1
            d2g (float, optional): Dust-to-gas mass ratio. If None, the default value is used. 
            verbose (bool, optional): If True, prints detailed output during execution. Default is True.
            clean (bool, optional): If True, cleans and recreates the build directory before running. Default is True.
            safe (bool, optional): If True, runs the subprocess in safe mode. Default is False.
        Notes:
            - Modifies the test input file with the provided parameters.
            - Optionally cleans the build directory before running.
            - Compiles and executes the test using the specified parameters.
        """

        path_to_test = os.path.join(self.path, 'tests/' + self.test_name + '/' + self.test + '.f90')
        self.file_editor.change_variables(path_to_test, density_array, crate, chi, sigmaNT, d2g = d2g)
        
        if clean == True: 
            try: 
                path_to_build = os.path.join(self.path, 'build' + f'_{project}' if project is not None else 'build')
                run_subprocess_no_input('rm', args = ['-rf', path_to_build], verbose = verbose)
                run_subprocess_no_input('mkdir', args = [path_to_build], verbose = verbose)
                if verbose: 
                    print("Build directory is cleaned")
            except FileNotFoundError: 
                run_subprocess_no_input('mkdir', args = [path_to_build + f'_{project}' if project is not None else path_to_build], verbose = verbose)
        
        if project is None:
            run_subprocess_input(os.path.join(self.path, 'krome'), args = ['-test', self.test_name], cwd = self.path, safe = safe, verbose = verbose)
            build_folder = self.path + 'build/'

        else: 
            run_subprocess_input(os.path.join(self.path, 'krome'), args = ['-test', self.test_name, '-project', project], cwd = self.path, safe = safe, verbose = verbose)
            build_folder = self.path + 'build' + f'_{project}/'

        #try: 
        #    build_folder = glob.glob(os.path.join(self.path, 'build/fort.22'))[0]
        #except: 
        #    build_folder = glob.glob(self.path + 'build/AB*')[0]

        #build_folder = self.path + 'build'

        run_subprocess_no_input('mv', args = [build_folder, folder_name_save + '/build/'], verbose = verbose)

        #cwd = os.path.join(self.path, 'build')
        #cwd = 'build/build'
        cwd = folder_name_save + '/build'
        print('cwd =', cwd)
        run_subprocess_no_input('make', args = ['gfortran'], cwd = cwd, capture_output = False, text = False, verbose = verbose)
        run_subprocess_no_input('./' + self.test, cwd = cwd, capture_output = False, text = False, verbose = verbose)
   
class Despotic_FileEditor(): 
    def __init__(self, cloud): 
        """
        Initialize the editor for modifying despotic cloud files.
        cloud : despotic.cloud
            Instance of the despotic cloud class
        """
        self.gmc = cloud #(file, verbose = True)
        
    def change_constants(self, data:np.ndarray, metallicity:float, redshift:float, LTE:bool = False, dVdr_input:float = None, 
                        sigmaNT:float = None, species_KROME:str = 'CO', species_despotic:str = 'co'):
        """
        Changes the constant chemical independent values in the cloud file
        Parameters
        ----------
        data : np.ndarray
            Output data of KROME test
        metallicity : float     
            Metallicity in Solar units
        redshift : float
            Cosmological redshift
        LTE : bool, optional
            If True, LTE is enabled
            If False, LTE is denabled.  
            The default is True.    
        dVdr_input : float, optional
            Velocity gradient in s^-1 used for LVG and non-LTE calculations. 
            If None, it is set to sigmaNT divided by the Jeans length. The default is None.    
        sigmaNT : float, optional
            Non-thermal velocity dispersion in cm s^-1. The default is None.
        species_KROME : str, optional 
            Species to calculate properties of. The default is 'CO'
        species_despotic : str, optional   
            Species to calculate properties of. The default is 'co'
        Returns 
        ------- 
        None.

        """

        self.gmc.rad.TCMB = 2.725 * (redshift + 1)
        self.gmc.dust.Zd = metallicity
        
        
        if species_despotic in self.gmc.emitters: 
            self.gmc.emitters[species_despotic].abundance = np.max(data[species_KROME]) # Set the CO abundance to the max of the array
        else: 
            self.gmc.addEmitter(species_despotic, np.max(data[species_KROME]))
        
        if dVdr_input != None: 
            LTE = False
        
        if sigmaNT != None: 
            self.gmc.sigmaNT = sigmaNT
        else: 
            self.gmc.sigmaNT = 2e5 # cm s^-1
            
            
            
    def change_variables(self, data:np.ndarray, chem:bool = True, crate:float = None, chi:float = None, LTE:bool = False, dVdr_input:float = None, 
                        sigmaNT:float = None, species_KROME:str = 'CO', species_despotic:str = 'co', mu:float = 2.3333, idx:int = -1,
                        length:str = 'jeans'): 
        """
        Changes the variable chemical dependent values in the cloud file    
        Parameters  
        ----------  
        data : np.ndarray
            Output data of KROME test
        chem : bool, optional   
            If True, the chemical abundances are taken from KROME. 
            If False, the default abundances are used. 
            The default is True.
        crate : float, optional
            Cosmic ray ionization rate. If None, the default value is used. s^-1 H_2^-1
        chi : float, optional
            UV radiation field scaling factor. If None, the default value is used. Relative to Solar neighborhood
        LTE : bool, optional    
            If True, LTE is enabled
            If False, LTE is denabled.
            The default is True.
        dVdr_input : float, optional
            Velocity gradient in s^-1 used for LVG and non-LTE calculations. 
            If None, it is set to sigmaNT divided by the Jeans length. The default is None.
        sigmaNT : float, optional
            Non-thermal velocity dispersion in cm s^-1. The default is None.
        species_KROME : str, optional
            Species to calculate properties of. The default is 'CO'
        species_despotic : str, optional
            Species to calculate properties of. The default is 'co' 
        mu : float, optional    
            Mean molecular weight. The default is 2.3333
        idx : int, optional
            Index of the data array to use. The default is -1 (last index)
        length : {'jeans', 'shielding'}, optional
            Method to calculate the length scale:
            - 'jeans'     : Jeans length
            - 'shielding' : Shielding length
            The default is 'jeans'
        Returns 
        -------
        None.   
        """
        
        # Set the initial parameters of the despotic file
        self.gmc.Tg = data['Tgas'][idx]
        self.gmc.Td = data['Tdust'][idx]
        self.gmc.rad.TradDust = data['Tdust'][idx]
        try: 
            self.gmc.nH = data['nH'][idx]
        except: 
            self.gmc.nH = data['ntot'][idx]
          
        if length == 'jeans':
            try: 
                L = jeans_length(self.gmc.Tg, data['rhotot'][idx], mu)
            except ValueError: 
                L = jeans_length(self.gmc.Tg, data['rho'][idx], mu)
                
        elif length == 'shielding':
            L = shielding_length(data['ntot'][idx])
            
            
        if ((LTE == False) and (dVdr_input is None)):
            self.gmc.dVdr = self.gmc.sigmaNT/L
        elif LTE == False: 
            self.gmc.dVdr = dVdr_input

        self.gmc.colDen = ncol(self.gmc.nH, L)
        
        if chem == True:
            # Change the abundances of CO, H2 and He if chemistry is included
            
            self.gmc.emitters[species_despotic].abundance = data[species_KROME][idx]
            self.gmc.comp.xH2 = data['H2'][idx]
            self.gmc.comp.xHe = data['HE'][idx]
            self.gmc.comp.xHI = data['H_1'][idx]
            # self.gmc.comp.xHplus = data['H_2'][idx]
            self.gmc.comp.xHplus = 1.0 - self.gmc.comp.xHI - \
                                     2.0*self.gmc.comp.xH2
        
        if crate != None: 
            # Times .5 for unit conversion
            try: 
                self.gmc.rad.ionRate = data['crate'][idx] * 0.5
            except ValueError: 
                self.gmc.rad.ionRate = crate * 0.5
        
        if chi != None: 
            self.gmc.rad.chi = chi
                    
        
    
class DespoticRunner():
    def __init__(self, path:str, path_to_cloud:str, gmc:object, test_name:str, density:float, metallicity:float, redshift:float, file_editor):
        """
        Create a runner for despotic    
        Parameters
        ----------  
        path : str
            The path to where KROME is stored
        path_to_cloud : str
            The path to where the cloud file is stored
        gmc : despotic.cloud    
            Instance of the despotic cloud class
        test_name : str
            Name of the test case to run:
        density : float
            Initial total density in cm^-3.
        metallicity : float 
            Metallicity in Solar units.
        redshift : float
            Cosmological redshift.
        file_editor : Despotic_FileEditor
            Instance of `Despotic_FileEditor` used to modify the cloud file
        Returns 
        -------
        None.
        """
        self.path = path
        self.path_to_cloud = path_to_cloud
        self.gmc = gmc
        self.density = density
        self.metallicity = metallicity
        self.redshift = redshift
        self.test_name = test_name
        
        self.file_editor = file_editor
        
        warnings.filterwarnings('ignore')
       
    @staticmethod
    def _calc_properties(cloud_file:str, LTE:bool = False, species_despotic:str = 'co', geometry:str='LVG'): 
        """
        Calculate 'lineLum' properties with despotic
        Parameters  
        ----------
        cloud_file : despotic.cloud
            Instance of the despotic cloud class
        LTE : bool, optional
            If True, LTE is enabled
            If False, LTE is denabled.
            The default is True.
        species_despotic : str, optional
            Species to calculate properties of. The default is 'co'
        geometry : {'LVG', 'sphere', 'slab'}, optional
            Geometry used for escape probability calculations when LTE is False:
            - 'LVG'   : Large Velocity Gradient 
            - 'sphere': Expanding sphere
            - 'slab'  : Static slab
            The default is 'LVG'
        Returns
        -------
        linelum : list
            List with 'lineLum' calculated with despotic
        Notes
        -----
        - If LTE is True, geometry is ignored   
        """
        
        linelum = []
        if LTE == False:
            linelum += [cloud_file.lineLum(species_despotic, escapeProbGeom=geometry)]
        else: 
            linelum += [cloud_file.lineLum(species_despotic)]
        
        return linelum

    @staticmethod
    def _transitions(properties:list, n_transitions:int, line:list, points:int = None): 
        """
        Extract line properties from despotic 'lineLum' output  
        Parameters
        ----------
        properties : list
            List of line properties {intTB, Tex, tau, tauDust, intIntensity, lumPerH, Tupper, freq}
        n_transitions : int
            Number of transitions you want to know the properties of
        line : list 
            List with 'lineLum' calculated with despotic
        points : int, optional
            Number of densities to calculate the properties at. The default is None.

        Returns
        ------- 
        dict_properties : dict
            Dictionary with 2D arrays of size (number of transitions, number of points) for all input properties
        transitions_list : np.ndarray   
            2D array of size (2, number of transitions), with the upper and lower levels of all the transitions     
        Notes   
        -----
        - If points is None, all the points in the line list are used
        - If n_transitions is larger than the number of transitions in the line list, it is set to the maximum number of transitions    
        """

        if points is None: 
            points = np.arange(0, len(line))

        if len(line[0]) < n_transitions: 
            transitions = len(line[0])
            
        dict_properties = {key: np.zeros((n_transitions, 1)) for key in properties}

        transitions_list = np.zeros((2,n_transitions))
        
        
        
        for i in range(n_transitions):
            transitions_list[0,i] = line[0][i]['lower']
            transitions_list[1,i] = line[0][i]['upper']
            for j in dict_properties: 

                dict_properties[j][i,:] = np.array([line[k][i][j] for k in points])
            
        return dict_properties, transitions_list

    def run_despotic(self, density_array:np.ndarray, n_transitions:int, data:np.ndarray = None, properties:list = ['intTB', 'Tex', 'tau'], chem:bool = True,
                     crate:float = None, chi:float = None, LTE:bool = False, dVdr_input:float = None, sigmaNT:float = None, points:int = None,
                     species_KROME:str = 'CO', species_despotic:str = 'co', clean:bool = False, save:bool = True, safe:bool = False, mu:float = 2.3333, idx:int = -1,
                     verbose:bool = True, length:str='jeans', geometry:str='LVG', folder_name_save = 'build'):
        """
        Runs the despotic line emission calculation pipeline for a given cloud model, allowing customization of physical parameters and output options.

        Parameters
        ----------
        density_array : np.ndarray
            Array of density values to be used in the model. cm^-3
        n_transitions : int
            Number of transitions you want to know the properties of
        data : np.ndarray, optional 
            Output data of KROME test. If None, it tries to open the fort.22 file in the build directory. The default is None.
        properties : list, optional
            List of line properties {intTB, Tex, tau, tauDust, intIntensity, lumPerH, Tupper, freq}. 
            The default is ['intTB', 'Tex', 'tau'].
        chem : bool, optional
            If True, the chemical abundances are taken from KROME. 
            If False, the default abundances are used. 
            The default is True.
        crate : float, optional 
            Cosmic ray ionization rate. If None, the default value is used. s^-1 H_2^-1
        chi : float, optional   
            UV radiation field scaling factor. If None, the default value is used. Relative to Solar neighborhood
        LTE : bool, optional
            If True, LTE is enabled
            If False, LTE is denabled.
            The default is True.
        dVdr_input : float, optional
            Velocity gradient in s^-1 used for LVG and non-LTE calculations. 
            If None, it is set to sigmaNT divided by the Jeans length. The default is None.
        sigmaNT : float, optional
            Non-thermal velocity dispersion in cm s^-1. The default is None.
        species_KROME : str, optional
            Species to calculate properties of. The default is 'CO'
        species_despotic : str, optional    
            Species to calculate properties of. The default is 'co'
        clean : bool, optional
            Cleans the build directory if set to True. The default is False.
        save : bool, optional
            If True, saves the output in a .txt file. The default is False.
        safe : bool, optional
            Ignores all warnings if True. The default is False.
        mu : float, optional    
            Mean molecular weight. The default is 2.3333
        idx : int, optional 
            Index of the data array to use. The default is -1 (last index)
        verbose : bool, optional
            If True, prints detailed output during execution. Default is True.
        length : {'jeans', 'shielding'}, optional
            Method to calculate the length scale:
            - 'jeans'     : Jeans length
            - 'shielding' : Shielding length
            The default is 'jeans'
        geometry : {'LVG', 'sphere', 'slab'}, optional
            Geometry used for escape probability calculations when LTE is False:    
            - 'LVG'   : Large Velocity Gradient
            - 'sphere': Expanding sphere
            - 'slab'  : Static slab
            The default is 'LVG'    

        Returns
        -------
        None.

        """
        
        properties = validate_properties(properties)
            
        if data is None: 
            try: 
                data = open_krome(os.path.join(folder_name_save + '/build/fort.22'))
            except: 
                file = glob.glob(folder_name_save + '/build/AB*')
                data = open_krome(file[0])
        else: 
            data = data


        if len(density_array) == 2: 
            data_len  = len(data)
            print('data_len =', data_len)
            if points == None: 
                points = data_len
                if verbose is True:
                    print(f'The properties will be calculated at {points} points between the two densities provided')
            else: 
                if points > data_len:
                    points = data_len
                    if verbose:
                        print(f'The properties will be calculated at the maximum number of points available in the KROME output: {points}')
            try:
                density_tot = data['ntot']
            except ValueError:
                density_tot = data['nH']

            indices_list = np.linspace(0, data_len - 1, points, dtype=int)  
            density_array = [density_tot[i] for i in indices_list]            

        points = len(density_array)
        n = []
        
        for i in density_array: 
            n += [find_nearest(data['ntot'], i)]
            
        safety_check_H2(data['H2'])
        
        self.file_editor.change_constants(data, self.metallicity, self.redshift, LTE, dVdr_input, sigmaNT, species_KROME = species_KROME, species_despotic=species_despotic)
        self.gmc.comp._check_abundance(tolerance=1e-3)
        
        results = np.zeros((len(properties), n_transitions, points))
        nH_array = np.zeros(points)
        krome_array = np.zeros((4,points))
        for step_idx, i in enumerate(n):    
            self.file_editor.change_variables(data, chem, crate, chi, LTE, dVdr_input, sigmaNT, mu=mu, species_KROME = species_KROME, species_despotic = species_despotic, idx = i,
                                              length = length)
                
            linelum = DespoticRunner._calc_properties(self.gmc, species_despotic = species_despotic, LTE = LTE, geometry = geometry)
        
            list_properties, trans = DespoticRunner._transitions(properties, n_transitions, linelum)
        
            list_property_data = [0]*len(properties)
            nH_array[step_idx] = self.gmc.nH
            krome_array[0,step_idx] = self.gmc.nH
            krome_array[1,step_idx] = data['Tgas'][i]
            krome_array[2,step_idx] = data['Tdust'][i]
            krome_array[3,step_idx] = data[species_KROME][i]
            
            for j in range(len(properties)): 
                list_property_data[j] = list_properties[properties[j]]
                results[j,:,step_idx] = list_properties[properties[j]][:,0]

        
        if save == True: 
            #with open(f'build/{species_KROME}_z{self.redshift}_Z{self.metallicity:.0e}.txt', 'w') as file:
            with open(folder_name_save + f'/{species_KROME}_z{self.redshift}_Z{self.metallicity:.0e}.txt', 'w') as file:

                valid_properties = np.array(['freq','upper','lower','Tupper','Tex','lumperH','intIntensity','intTB','tau','taudust'])
                units = np.array(['GHz', 'dimensionless', 'dimensionless', 'K', 'K', 'erg_s^-1', 'erg_cm^−2_s^−1_sr^−1', 'K_km_s^-1', 'dimensionless', 'dimensionless'])
                
                indices = [i for t in properties for i in np.where(valid_properties == t)[0]]
                
                file.write(f"#J_upper J_lower nH Tgas Tdust n_{species_KROME} " + " ".join(properties) + "\n")
                file.write('#dimensionless dimensionless cm^-3 K K dimensionless (nX/nH) ' + " ".join(units[indices]) + "\n")
                for k in range(results.shape[1]):
                
                    for j in range(results.shape[2]): 
                        arr = [f"{int(trans[1,k])}", f"{int(trans[0,k])}"]
                        arr_temp = [f"{y}" for y in krome_array[:,j]]
                        prop = [f"{x}" for x in results[:, k, j]]
                        file.write(" ".join(list(map(str, arr)) + [f"{float(x):.3e}" for x in arr_temp + prop]) + "\n")
                    file.write("\n")
                
        
        if verbose:
            for l in range(trans.shape[1]):
                print('-------------------------------------------------------')
                print(f'For {species_KROME}: J = {trans[1, l]:.0f} --> {trans[0, l]:.0f}, the properties are:')
                for j in range(len(properties)):
                    print(f'{properties[j]} : {results[j,l,0]}')
            print('-------------------------------------------------------')
    
    
class KromeDespoticPipeline(): 
    def __init__(self, path:str, path_to_cloud:str, test_name:str, test:str = 'test', verbose:bool = True): 
        """
        Create a pipeline to go from KROME to despotic
        Parameters
        ----------  
        path : str          
            The path to where KROME is stored
        path_to_cloud : str
            The path to where the cloud file is stored
        test_name : str
            Name of the test case to run:
        test : str, optional
            Name of specific test case to run:
        verbose : bool, optional
            If True, prints detailed output during execution. Default is True.
        Returns
        -------
        None.
        Notes
        -----       
        - Make sure that the test_name and test are valid KROME tests
        - Make sure that the cloud file is a valid despotic cloud file
        """

        print('##################################')
        print('## WELCOME TO KROME_TO_DESPOTIC ##')
        print('##################################\n\n')
        
        
        validate_string(path = path, path_to_cloud = path_to_cloud, test_name = test_name)


        self.verbose = verbose
        self.path = path
        self.path_to_cloud = path_to_cloud
        self.cloud = cloud(self.path_to_cloud, verbose = verbose)

    
        self.test_name, self.test = validate_test_names(test_name, test, self.path)
        self.path_to_test = os.path.join(self.path, 'tests/' + test_name + '/' + self.test + '.f90')       
                
    def run(self, density_array:np.ndarray = None, metallicity_input:float = None, 
            redshift_input:float = None, crate:float = None, chi0:float = None, 
            d2g:float = None, include_chemistry:bool = True, 
            species:str = None, properties:list = None, skip_krome:bool=False,
            sigmaNT:float = None, dVdr:float = None, LTE:bool=False, safe:bool = False,
            length:str = None, geometry:str = None, folder_name_save:str = 'build', project:str = None, 
            path_to_krome_data:str = None, points:int = None, **kwargs):
        
        """
        Runs the KROME to despotic pipeline, integrating chemical modeling with line emission calculations.
        Parameters
        ----------      
        density_array : np.ndarray, optional
            Array of density values to be used in the model. If None, a default array is
            used. The default is None. cm^-3
        metallicity_input : float, optional
            Metallicity in Solar units. If None, the default value is used. The default is None.
        redshift_input : float, optional            
            Cosmological redshift. If None, the default value is used. The default is None.
        crate : float, optional 
            Cosmic ray ionization rate. If None, the default value is used. s^-1 H_2^-1 
        chi0 : float, optional
            UV radiation field scaling factor. If None, the default value is used. Relative to Solar neighborhood
        d2g : float, optional
            Dust-to-gas mass ratio. If None, the default value is used.
        include_chemistry : bool, optional      
            If True, the chemical abundances are taken from KROME. 
            If False, the default abundances are used. 
            The default is True.
        species : str, optional
            Species to calculate properties of. If None, 'CO' is used. The default is None.
        properties : list, optional
            List of line properties {intTB, Tex, tau, tauDust, intIntensity, lumPerH, Tupper, freq}. 
            If None, ['intTB', 'Tex', 'tau'] is used. The default is None.
        skip_krome : bool, optional 
            If True, skips the KROME run and only runs despotic. The default is False.
        sigmaNT : float, optional
            Non-thermal velocity dispersion. If None, the default value is used. cm s^-1
        dVdr : float, optional
            Velocity gradient in s^-1 used for LVG and non-LTE calculations.
            If None, it is set to sigmaNT divided by the Jeans length. The default is None.
        LTE : bool, optional
            If True, LTE is enabled
            If False, LTE is denabled.
            The default is True.
        length : {'jeans', 'shielding'}, optional
            Method to calculate the length scale:
            - 'jeans'     : Jeans length        
            - 'shielding' : Shielding length
            The default is 'jeans'
        geometry : {'LVG', 'sphere', 'slab'}, optional
            Geometry used for escape probability calculations when LTE is False:
            - 'LVG'   : Large Velocity Gradient
            - 'sphere': Expanding sphere    
            - 'slab'  : Static slab 
            The default is 'LVG'    
        kwargs : dict, optional     
            Additional keyword arguments passed to KromeRunner.run_krome method:
            - clean (bool): If True, cleans and recreates the build directory before running. Default is True.
            - safe (bool): If True, runs the subprocess in safe mode. Default is False.
        Returns
        -------
        None.   
        Notes
        -----
        - If skip_krome is True, ensure that the KROME output files are present in the build directory
        """
        
        if folder_name_save is None:
            folder_name_save = 'build'


        density_array, density = validate_density_array(density_array, self.test_name, safe, self.verbose)

        #target_density = density_array[-1]
        
        metallicity = validate_metallicity(metallicity_input, self.verbose)
        redshift = validate_redshift(redshift_input, self.verbose)
        crate = validate_crate(crate, self.test_name, self.verbose)
        chi = validate_chi(chi0, self.test_name, self.verbose)
        sigmaNT = validate_sigmaNT(sigmaNT, self.verbose)
        dVdr = validate_dVdr(dVdr, LTE, self.verbose)
        d2g = validate_d2g(d2g, self.verbose)
        properties = validate_properties(properties)
        length = validate_length(length, self.test, self.verbose)
       
        if LTE == False:
            geometry = validate_geometry(geometry, self.verbose)
        
        try:
            folder_name = folder_name_save.split('/')[-2]
        except IndexError:
            folder_name = folder_name_save
        
        try: 
            os.mkdir(folder_name)
        except FileExistsError:
            pass

        try: 
            os.mkdir(folder_name_save)

            if self.verbose: 
                print(f'Create {folder_name}/')
        except FileExistsError:
            if safe is True:
                print('This folder already exists, do you want to overwrite it? ')
                input_user = input('Type q to quit or any key to continue: ')
                if input_user == 'q':
                    raise FileExistsError('The folder already exists, quitting the program')
                else: 
                    run_subprocess_no_input('rm', args = ['-rf', folder_name], verbose = self.verbose)
            else: 
                run_subprocess_no_input('rm', args = ['-rf', folder_name], verbose = self.verbose)
            os.mkdir(folder_name_save)

        #log_file = open('build/info.log', 'w')
        log_file = open(folder_name_save + '/info.log', 'w')

        log_file.write('#####################################################################################\n')
        log_file.write('# This file shows the input parameters for the Krome_to_despotic package\n')
        log_file.write('# The authors of this package are: Eloy van de Genugten (genugten@strw.leidenuniv.nl)\n')
        log_file.write('#                                  Piyush Sharda (sharda@strw.leidenuniv.nl)\n')
        log_file.write('# The authors of KROME are       : Shyam Menon (smenon@flatironinstitute.org)\n')
        log_file.write('#                                  Piyush Sharda (sharda@strw.leidenuniv.nl)\n')
        log_file.write('# The author of despotic is      : Mark Krumholz (mark.krumholz@anu.edu.au) \n')
        log_file.write('#####################################################################################\n\n')

        log_file.write('#########################################################\n\n')
        log_file.write('The initial settings for this test are:\n')
        log_file.write('Test name          : '+ str(self.test_name) + ', ' + self.test + "\n")
        log_file.write('Redshift           : '+ str(redshift) + "\n")
        log_file.write('Metallicity        : '+ str(metallicity) + ' Solar metallicity\n')
        log_file.write('CR ionization rate : '+ str(crate) + ' s^-1 H_2^-1\n')
        log_file.write('Chi0               : '+ str(chi) + ', relative to Solar neighborhood\n')
        log_file.write('SigmaNT            : '+ str("{0:.0E}".format(sigmaNT)) + ' cm s^-1\n')
        if dVdr is None: 
            log_file.write('dVdr               : Calculated as sigmaNT divided by Jeans length, s^-1\n')
        else: 
            log_file.write('dVdr               : ' + str("{0:.0E}".format(dVdr)) + ' s^-1\n')
        if d2g == 'zs(jz2)':
            log_file.write('Dust-to-gas ratio  : linear to metallicity\n')
        else:
            log_file.write('Dust-to-gas ratio  : '+ str(d2g)+ "\n")
        log_file.write('Initial density    : '+ str(density) + ' cm^-3\n\n')
        log_file.write('#########################################################\n\n')
        log_file.write('The densities at which calculations are performed are (cm^-3):\n')
        log_file.write(", ".join(str("{0:.0E}".format(i)) for i in density_array) + '\n\n')
        log_file.write('#########################################################\n\n')
        log_file.write('The following species are calculated:\n')
        log_file.write(", ".join(i[0] for i in species) + '\n\n')
        log_file.write('#########################################################\n\n')

        log_file.write('Other settings:\n')
        
        if include_chemistry is True: 
            log_file.write('Chemistry is turned on for the calculations\n')
        else: 
            log_file.write('Chemistry is turned off for the calculations\n')
            
        if length == 'jeans': 
            log_file.write('Jeans length used for column density calculation\n')
        else: 
            log_file.write('Shielding length used for column density calculation\n')
        
        if LTE == False:
            log_file.write(f'Geometry for non-LTE calculations: {geometry}')

        if skip_krome is False:
            file_editor_krome = KROME_FileEditor(density, metallicity, redshift)
            krome_runner = KromeRunner(self.path, file_editor_krome, self.test_name, self.test)
        
        file_editor_despotic = Despotic_FileEditor(self.cloud)
        despotic_runner = DespoticRunner(self.path, self.path_to_cloud, self.cloud, self.test_name, 
                                         density, metallicity, redshift, file_editor_despotic)
        
        


        if skip_krome is False: 
            krome_runner.run_krome(density_array, crate, chi, sigmaNT = sigmaNT, d2g = d2g, verbose = self.verbose, clean=kwargs.get("clean", True), safe=kwargs.get("safe", False), folder_name_save = folder_name_save, project = project)
          
        log_file.write('\n\n')
        log_file.write('#########################################################\n')
        log_file.write('KROME LOGGING:\n')
        log_file.write('#########################################################\n\n')

        #krome_log = open('build/build/info.log')
        try:
            krome_log = open(folder_name_save +'/build/info.log')
        except FileNotFoundError:
            krome_log = open(path_to_krome_data +'/info.log')

        for line in krome_log: 
            if 'krome_nspec' in line:
                break
            
            log_file.write(line)
        
        log_file.close()
        
        species, n_transitions = validate_species_transitions(species, verbose = self.verbose)
        if self.verbose:
            print('\n-------------------------------------------------------')
            print('The initial conditions for this test are: ')
            print(f'Test name                       : {self.test_name}')
            print(f'Metallicity                     : {metallicity} Solar metallicity')
            print(f'Redshift                        : {redshift}')
            print(f'Initial density                 : {density} cm-3')
            print(f'Non-thermal velocity-dispersion : {sigmaNT} cm s^-1')
            if crate is not None: 
                print(f'crate                           : {crate} s^-1 H^-1')
            if chi is not None: 
                print(f'chi0                            : {chi}, Relative to Solar neighborhood')
            print('-------------------------------------------------------')
        
        for i,specy in enumerate(species): 
            if specy == 'HCO+': 
                if not 'densegas' in self.test_name or 'full' in self.test_name: 
                    print(f'{species} not present in this test and therefore not calculated')
                    continue
                    
            elif 'N' in specy: 
                if not 'densegas' in self.test_name: 
                
                    print(f'{specy} not present in this test and therefore not calculated')
                    continue
                
            species_KROME, species_despotic = get_species_name(specy)

            if skip_krome is True:
                try: 
                    data = open_krome(os.path.join(path_to_krome_data + '/fort.22'))
                except: 
                    file = glob.glob(path_to_krome_data + '/AB*')
                    data = open_krome(file[0])
            else: 
                data = None
            
            despotic_runner.run_despotic(density_array, n_transitions[i], data = data, species_KROME = species_KROME, species_despotic = species_despotic, crate = crate, chi = chi, sigmaNT = sigmaNT, chem = include_chemistry, properties = properties, LTE = LTE, 
                                         verbose = self.verbose, length = length, geometry = geometry, folder_name_save = folder_name_save, points = points, **kwargs)
