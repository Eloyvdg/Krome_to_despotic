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
import subprocess
import sys
import pexpect
import glob

__all__ = ["open_krome", "find_nearest", "run_subprocess_no_input", 
           "run_subprocess_input", "validate_string", "validate_int", 
           "validate_float",
           "validate_test_names", "validate_redshift", "validate_metallicity",
           "jeans_length", "ncol", "get_species_name", "validate_crate",
           "validate_chi","d_formatter", "check_points", "validate_properties",
           "safety_check_H2", "validate_species_transitions", 
           "validate_density_array", "validate_sigmaNT", "validate_length", 
           "validate_d2g", "validate_dVdr", 'shielding_length', 
           'validate_geometry']

def open_krome(path, list_metallicities = None, metallicity = None): 
    """
    Loads and processes KROME output data from a file, optionally selecting data for a specific metallicity.
    Parameters
    ----------
    path : str
        Path to the KROME output file to be loaded.
    list_metallicities : list, optional
        List of metallicity values corresponding to the data splits in the file. Required if the file contains data for multiple metallicities.
    metallicity : any, optional
        The specific metallicity value to select from the data. Must be present in `list_metallicities`.
    Returns
    -------
    numpy.ndarray
        Structured array containing the loaded data. If a specific metallicity is selected, only the corresponding subset is returned.
    Raises
    ------
    TypeError
        If the file contains multiple metallicities but `list_metallicities` or `metallicity` is not provided.
    IndexError
        If the length of `list_metallicities` does not match the number of data splits in the file.
    Notes
    -----
    - Assumes the first column in the file can be used to identify splits between different metallicity datasets.
    - Uses `numpy.genfromtxt` to load the data with column names inferred from the file.
    """
    data = np.genfromtxt(path, names = True)
    names = data.dtype.names
    loc_split = np.where(data[names[0]] == data[names[0]][0])[0]
    if len(loc_split) == 1:
        return data
    else:   
        if (list_metallicities == None) or (metallicity == None): 
            raise TypeError('Please enter the list of metallicities and desired metallicity')
        if len(list_metallicities) != len(loc_split): 
            raise IndexError('Length of metallicity list is not the same size as KROME output')
            
        metallicity_index = np.where(np.array(list_metallicities) == metallicity)[0][0]
        loc_split1 = loc_split[metallicity_index]
        if metallicity_index == len(list_metallicities) -1:
            data = data[loc_split1:len(data) - 1]
        else:
            data = data[loc_split1 : loc_split[metallicity_index + 1]]
        return data
    
def find_nearest(array, value):
    """
    Find the index of the element in the array closest to a given value.
    Parameters
    ----------
    array : array-like
        Input array to search.
    value : float or int
        The value to find the closest element to.
    Returns
    -------
    int
        Index of the element in the array closest to the specified value.
    """
    array = np.asarray(array)
    return np.abs(array - value).argmin()

def run_subprocess_no_input(executable, args = None, cwd = None, capture_output = True, text = True, verbose = True): 
    """
    Runs a subprocess with the specified executable and arguments, without providing any input.
    Parameters:
        executable (str): The path to the executable to run.
        args (list, optional): A list of arguments to pass to the executable. Defaults to None.
        cwd (str, optional): The working directory in which to run the subprocess. Defaults to None.
        capture_output (bool, optional): If True, captures stdout and stderr. Defaults to True.
        text (bool, optional): If True, captures output as text (str), otherwise as bytes. Defaults to True.
        verbose (bool, optional): If True, outputs subprocess output; if False, suppresses output. Defaults to True.
    Raises:
        subprocess.CalledProcessError: If the subprocess exits with a non-zero status.
    """

    if args == None: 
        args = []
        
    if verbose:
        subprocess.run([executable] + args, cwd = cwd, check=True, capture_output=capture_output, text=text)
        
    else: 
        subprocess.run([executable] + args, cwd = cwd, check=True, stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL)

           
def run_subprocess_input(executable, args=None, cwd=None, safe=False, verbose = True):
    """
    Runs a subprocess using the specified executable and arguments, handling interactive prompts.
    This function spawns a subprocess using `pexpect`, monitors its output for specific prompt patterns,
    and responds to them automatically or interactively based on the `safe` flag. It is useful for automating
    command-line tools that require user input during execution.
    Args:
        executable (str): The path to the executable to run.
        args (list, optional): List of arguments to pass to the executable. Defaults to None.
        cwd (str, optional): Working directory to run the subprocess in. Defaults to None.
        safe (bool, optional): If True, prompts the user for input when a prompt is detected; otherwise, sends 't' automatically. Defaults to False.
        verbose (bool, optional): If True, prints subprocess output to stdout. Defaults to True.
    Raises:
        KeyboardInterrupt: If the user interrupts execution (Ctrl+C).
    """
    if args is None:
        args = []

    cmd = ' '.join([executable] + args)
    child = pexpect.spawn(cmd, cwd=cwd, encoding='utf-8')
    if verbose:
        child.logfile = sys.stdout
    else:
        child.logfile = None

    prompt_patterns = ['Any key to ignore q to quit...', 'Any key to continue q to quit...']
    try:
        while True:
            try: 
                index = child.expect(
                    prompt_patterns, timeout=10)
    
                if index == 0:
                    if safe == True:
                        child.sendline(input('>>>'))  # or any safe key except 'q'
                    else: 
                        child.sendline('t')
                
                elif index == 1:
                    if safe == True:
                        child.sendline(input('>>>'))  # or any safe key except 'q'
                    else: 
                        child.sendline('t')
                    
                elif index == 2:
                    pass
            
            except pexpect.EOF:
                if verbose:
                    print("\n[Caught EOF] Process exited.")
                break
            except pexpect.TIMEOUT:
                if verbose:
                    print("\n[Timeout] No prompt matched. Still waiting...")
                # Optionally break or continue
                continue
            

    except KeyboardInterrupt:
        child.terminate()
        raise

def validate_redshift(redshift, verbose):
    """
    Validates and adjusts the input redshift value.
    Parameters
    ----------
    redshift : float or None
        The redshift value to validate. If None, defaults to 0.
    verbose : bool
        If True, prints informational messages.
    Returns
    -------
    float
        The validated redshift value.
    Raises
    ------
    ValueError
        If the redshift is negative and the user does not confirm to proceed with 0.
    Notes
    -----
    - If `redshift` is None, it is set to 0 and a message is printed if `verbose` is True.
    - If `redshift` is negative, prompts the user to confirm using 0 or raises a ValueError.
    - If `redshift` is greater than 10, prints a warning about CMB temperature factors.
    """

    if redshift is None: 
        redshift = 0
        if verbose:
            print('A redshift of 0 is assumed')
        
    if redshift < 0: 
        print('redshift must be at least 0. Do you want to continue with redshift 0?')
        user_input = input('Type y to confirm or any key to exit ')
        if user_input == 'y' or user_input == 'Y': 
            redshift = 0
        else: 
            raise ValueError(f'Redshift must be at least 0')
        
    if redshift > 10: 
        print('WARNING: At this redshift the CMB temperature factors are not calculated yet.')
    
    return redshift

def validate_metallicity(metallicity, verbose): 
    """
    Validates the input metallicity value, ensuring it is not negative and providing user interaction if it is.
    Parameters
    ----------
    metallicity : float or None
        The metallicity value to validate. If None, defaults to 1 (Solar metallicity).
    verbose : bool
        If True, prints messages about the assumed or corrected metallicity.
    Returns
    -------
    float
        The validated metallicity value.
    Raises
    ------
    ValueError
        If the metallicity is negative and the user does not confirm to proceed with metallicity 1.
    Notes
    -----
    If `metallicity` is None, it is set to 1 and a message is printed if `verbose` is True.
    If `metallicity` is negative, prompts the user to confirm proceeding with metallicity 1.
    """
    if metallicity is None: 
        metallicity = 1
        if verbose: 
            print('A metallicity of 1 Solar metallicity is assumed')
        
    if metallicity < 0: 
        print('Metallicity must be at least 0. Do you want to continue with metallicity 1?')
        user_input = input('Type y to confirm or any key to exit ')
        if user_input == 'y' or user_input == 'Y': 
            redshift = 0
        else: 
            raise ValueError(f'Metallicity must be at least 0')
    
    return metallicity

def lognormal_density(mean, std, points:int = None): 
    if points is None: 
        points = 50
    sigma_sqr = np.log(1 + std**2 / mean**2)
    sigma = np.sqrt(sigma_sqr)
    mu = np.log(mean) - 0.5 * sigma_sqr
    densities = np.random.lognormal(mu, sigma, points)
    return densities
                
def validate_density_array(density_array, test_name, safe, verbose):
    """
    Validates and processes a density array.
    Parameters
    ----------
    density_array : array-like, optional
        The array of densities (in cm^-3) to validate. If None, a default log-spaced array
        from 0.1 to 1e6 (8 points) is used.
    test_name : str
        The name of the test, used to determine upper density limits.
    verbose : bool
        If True, prints informative messages about the validation process and any modifications
        made to the density array.
    Returns
    -------
    density_array : numpy.ndarray
        The validated and sorted array of densities, with values outside the allowed range removed.
    initial_density : float
        The initial density value to use, set to 0.01 if the minimum density is <= 0.1,
        otherwise set to 0.1.
    Notes
    -----
    - Densities lower than 0.01 cm^-3 are removed.
    - For tests containing 'ismEqTest' in their name, densities above 1e8 cm^-3 are removed.
    - For other tests, densities above 1e18 cm^-3 are removed.
    - The function prints details of any modifications if `verbose` is True.
    """

    #if safe is True:
    #    print('Do you want to use a log normal density distribution?')
    #    input_user = input('Type y to confirm or any key to continue with default values: ')
    #    if input_user == 'y':
    #        mean = float(input('Enter the mean density (cm^-3): '))
    #        std = float(input('Enter the standard deviation of the density (cm^-3): '))
    #       points = int(input('Enter the number of density points to generate: '))
    #        density_array = lognormal_density(mean, std, points)

    if density_array is None: 
        if 'ismEqTest' in test_name: 
            density_array = np.array([0.01, 1e8]) 
            if verbose is True: 
                print('The test will run from 1e-2 to 1e8 cm^-3 by default')
        else:
            density_array = np.array([0.01, 1e18])
            if verbose is True: 
                print('The test will run from 1e-2 to 1e18 cm^-3 by default')
        
    if isinstance(density_array, list): 
        density_array = np.array(density_array)
        
    density_array = density_array.astype(float)
    density_array = np.sort(density_array)
    
    if density_array[0] < 0.01: 
        density_array = density_array[density_array >= 0.01]
        if verbose:
            print('Densities lower than 0.01 cm^-3 are too low for this test')
            print('All values lower than 0.01 cm^-3 are removed from the density array')
        
    if density_array[-1] > 1e8: 
        if 'ismEqTest' in test_name: 
            density_array = density_array[density_array <= 1e8]
            if verbose:
                print('Densities higher than 1e8 cm^-3 are too high for this test')
                print('All values higher than 1e8 cm^-3 are removed from the density array')
        else: 
            if density_array[-1] > 1e18: 
                density_array = density_array[density_array <= 1e18]
                if verbose: 
                    print('Densities higher than 1e18 cm^-3 are too high for this test')
                    print('All values higher than 1e18 cm^-3 are removed from the density array')

    
    if density_array[0] <= 0.1: 
        initial_density = 0.01
    else: 
        initial_density = 0.1
        
    return density_array, initial_density

def levenshtein(string1, string2): 
    """
    Compute the Levenshtein distance between two strings.
    The Levenshtein distance is a measure of the minimum number of single-character edits
    (insertions, deletions, or substitutions) required to change one string into the other.
    Parameters
    ----------
    string1 : str
        The first string to compare.
    string2 : str
        The second string to compare.
    Returns
    -------
    int
        The Levenshtein distance between `string1` and `string2`.
    """

    n = len(string1)
    m = len(string2)
    lev = np.zeros((n+1, m+1))
    lev[0,:] = np.arange(m+1)
    lev[:,0] = np.arange(n+1)
    for i in range(1, n+1):
        for j in range(1, m+1):
            cost = 0 if string1[i-1] == string2[j-1] else 1
            lev[i,j] = min(lev[i-1,j] + 1, 
                           lev[i,j-1] + 1,
                           lev[i-1,j-1] + cost)
            
    return lev[n,m]

def validate_test_names(test_name, test, path): 
    """
    Validates and corrects the provided test name and test type based on available test folders and special test types.
    This function checks if the given `test_name` exists among the available test folders (filtered by containing 'popsicle_semenov').
    If not, it suggests the closest match using the Levenshtein distance and prompts the user for confirmation.
    Similarly, it validates the `test` argument against a list of special test types, suggesting corrections if necessary.
    Parameters
    ----------
    test_name : str
        The name of the test to validate.
    test : str
        The type of test to validate (e.g., 'test_shielded', 'test_unshielded', 'test_cooling', or 'test').
    path : str
        The base path where the 'tests' directory is located.
    Returns
    -------
    tuple
        A tuple (test_name, test) with validated (and possibly corrected) test name and test type.
    Raises
    ------
    ValueError
        If the user does not confirm the suggested correction or if the provided test name or test type is invalid.
    """

    special_tests = ['test_shielded', 'test_unshielded', 'test_cooling']
    list_names = []
    folders = glob.glob(path + 'tests/*')
    
    for i in folders: 
        name = i.split('/')[-1]
        if 'popsicle_semenov' in name: 
            list_names += [name] 

    if len(folders) == 0: 
        raise ValueError('No test folders found in the specified path')
            
    if test_name not in list_names: 
        lev_results = []
        for i in range(len(list_names)): 
            lev_results += [levenshtein(test_name, list_names[i])]
        
        idx = np.argmin(lev_results)            
        print(f'Invalid test_name: {test_name}. Did you mean {list_names[idx]}?')
        user_input = input('Type y to confirm or any key to exit ')
        if user_input == 'y' or user_input == 'Y': 
            test_name = list_names[idx]
        else: 
            raise ValueError(f'Invalid test_name: {test_name}. Valid options: {list_names}')
            
    if 'ismEqTest' in test_name: 
        if test not in special_tests: 
            lev_results = []
            for i in range(len(special_tests)): 
                lev_results += [levenshtein(test, special_tests[i])]
            
            idx = np.argmin(lev_results)
            print(f'Invalid test: {test}. Did you mean {special_tests[idx]}?')
            user_input = input('Type y to confirm or any key to exit ')
            if user_input == 'y' or user_input == 'Y': 
                test = special_tests[idx]
            else:
                raise ValueError(f'invalid test: {test}. Valid options: {special_tests}')
                
    else: 
        if test in special_tests: 
            print(f'Invalid test: {test}. Did you mean test?')
            user_input = input('Type y to confirm or any key to exit ')
            if user_input == 'y' or user_input == 'Y': 
                test = 'test'
            else: 
                raise ValueError(f'invalid test: {test}. Valid option: test')
    
    return test_name, test

def validate_properties(properties): 
    """
    Validates and corrects a list of property names against a set of valid properties.
    Parameters
    ----------
    properties : list of str or None
        List of property names to validate. If None, defaults to ['intTB', 'tau'].
        If not a list, attempts to convert to a list.
    Returns
    -------
    list of str
        The validated (and possibly corrected) list of property names.
    Raises
    ------
    TypeError
        If any element in the properties list is not a string.
    ValueError
        If an invalid property is provided and not corrected by the user.
    Notes
    -----
    If an invalid property is found, suggests the closest valid property using Levenshtein distance.
    Prompts the user to confirm the suggested correction or raise an error.
    """

    if properties is None: 
        properties = ['intTB', 'tau']
        
    if not isinstance(properties, list):
        properties = list(properties)
    
    if not all(isinstance(item, str) for item in properties):
        raise TypeError("Please enter valid strings in properties list")
    
    valid_properties = ['freq','upper','lower','Tupper','Tex','lumperH','intIntensity','intTB','tau','taudust']
    for i, prop in enumerate(properties): 
        if prop not in valid_properties:
            lev_results = []
            for j in valid_properties: 
                lev_results += [levenshtein(prop, j)]
                
            idx = np.argmin(lev_results)
            print(f'Invalid property: {prop}. Did you mean {valid_properties[idx]}?')
            user_input = input('Type y to confirm or any key to exit ')
            if user_input == 'y' or user_input == 'Y': 
                properties[i] = valid_properties[idx]
            else: 
                raise ValueError(f'invalid property: {prop}')
                
    return properties            

def validate_string(**kwargs):
    """
    Validates that all keyword arguments are of type `str`.
    Raises:
        TypeError: If any of the provided keyword arguments is not a string, 
            indicating which argument failed and its actual type.
    """
    for name, value in kwargs.items():
        if not isinstance(value, str): 
            raise TypeError(f'The argument {name} must be a str, got {type(value).__name__}')
        
def validate_int(**kwargs):
    """
    Validates that all provided keyword arguments are integers.
    Raises:
        TypeError: If any argument is not of type int, specifying the argument name and its actual type.
    """
    for name, value in kwargs.items():
        if not isinstance(value, int): 
            raise TypeError(f'The argument {name} must be a int, got {type(value).__name__}')
        
def validate_float(**kwargs):
    """
    Validates that all keyword arguments are floats.
    If a value is an integer, it is converted to a float.
    If a value is not a float or integer, raises a TypeError.
    Parameters
    ----------
    **kwargs : dict
        Arbitrary keyword arguments to validate as floats.
    Raises
    ------
    TypeError
        If any argument is not a float or integer.
    """
    for name, value in kwargs.items():
        if isinstance(value, int): 
            value = float(value)
        elif not isinstance(value, float): 
            raise TypeError(f'The argument {name} must be a float, got {type(value).__name__}')

def validate_crate(crate, test_name, verbose): 
    """
    Validates and sets the value of the 'crate' parameter based on the test name and user input.
    Parameters
    ----------
    crate : float or None
        The cosmic ray ionization rate to validate. If None, a default value may be assigned.
    test_name : str
        The name of the test, used to determine if cosmic ray ionization is relevant.
    verbose : bool
        If True, prints informative messages about the validation process.
    Returns
    -------
    float or None
        The validated or defaulted value of 'crate', or None if not applicable.
    Raises
    ------
    ValueError
        If 'crate' is negative and the user does not confirm to proceed with the default value.
    Notes
    -----
    - If 'cr' is not in the test name, 'crate' is ignored and set to None.
    - If 'crate' is None and 'cr' is in the test name, a default value of 2e-16 s^-1 H_2^-1 is assumed.
    - If 'crate' is negative, prompts the user to confirm using the default value or raises an error.
    """
    if 'cr' not in test_name: 
        if verbose:
            print('Argument crate given, but the test does not include CR. Input value ignored')
        crate = None
    else: 
        if crate is None: 
            crate = 2e-16
            if verbose:
                print('A crate of 2e-16 s^-1 H_2^-1 is assumed')
        elif crate < 0:
            print('crate must be at least 0. Do you want to continue with crate 2e-16?')
            user_input = input('Type y to confirm or any key to exit ')
            if user_input == 'y' or user_input == 'Y': 
                crate = 2e-16
            else: 
                raise ValueError('crate must be at least 0')
        else: 
            validate_float(crate = crate)
            crate = crate
            
    return crate
    

def validate_chi(chi, test_name, verbose): 
    """
    Validates and adjusts the value of the radiation field parameter `chi` based on the test context.
    Parameters
    ----------
    chi : float or None
        The input value for the radiation field parameter. If None, a default value may be assigned.
    test_name : str
        The name of the test, used to determine if a radiation field is relevant (checks for 'photo' in the name).
    verbose : bool
        If True, prints informative messages about the validation process.
    Returns
    -------
    float or None
        The validated (and possibly adjusted) value of `chi`, or None if not applicable.
    Raises
    ------
    ValueError
        If `chi` is negative and the user does not confirm to proceed with a default value.
    Notes
    -----
    - If the test does not involve a radiation field (i.e., 'photo' not in `test_name`), `chi` is ignored and set to None.
    - If `chi` is None and a radiation field is required, it defaults to 1.0.
    - If `chi` is negative, prompts the user to confirm using a default value of 1.0 or raises an error.
    """
    if 'photo' not in test_name: 
        if verbose:
            print('Argument chi given, but the test does not include a radiation field. Input value ignored')
        chi = None
    else: 
        if chi is None:
            chi = 1.0
            if verbose: 
                print('A chi0 of 1 is assumed')
        if chi < 0: 
            print('chi0 must be at least 0. Do you want to continue with chi0 = 1?')
            user_input = input('Type y to confirm or any key to exit ')
            if user_input == 'y' or user_input == 'Y': 
                chi = 1.0
            else: 
                raise ValueError('chi0 must be at least 0')
        else: 
            validate_float(chi = chi)
            chi = chi
    
    return chi

def validate_sigmaNT(sigmaNT, verbose): 
    """
    Validates and returns a value for sigmaNT (non-thermal velocity dispersion).
    Parameters
    ----------
    sigmaNT : float or None
        The value of sigmaNT to validate. If None, a default value of 2e5 (corresponding to 2 km/s) is assumed.
    verbose : bool
        If True and sigmaNT is None, prints a message indicating the default value is used.
    Returns
    -------
    float
        The validated sigmaNT value.
    Raises
    ------
    ValueError
        If sigmaNT is negative and the user does not confirm to proceed with the default value.
    Notes
    -----
    If sigmaNT is negative, prompts the user to confirm using the default value of 2e5. If the user declines, raises a ValueError.
    """
    if sigmaNT is None:
        sigmaNT = 2e5
        if verbose:
            print("A sigmaNT of 2 km/s is assumed")
    
    elif sigmaNT < 0: 
        print('sigmaNT must be at least 0. Do you want to continue with sigmaNT = 2 km/s?')
        user_input = input('Type y to confirm or any key to exit ')
        if user_input == 'y' or user_input == 'Y': 
            sigmaNT = 2e5
        else: 
            raise ValueError('sigmaNT must be at least 0')
    else: 
        validate_float(sigmaNT=sigmaNT)
        sigmaNT = sigmaNT
        
    return sigmaNT

def validate_dVdr(dVdr, LTE, verbose): 
    """
    Validates the `dVdr` parameter based on the LTE (Local Thermodynamic Equilibrium) condition.
    Parameters
    ----------
    dVdr : float or None
        The velocity gradient to be validated. If None and LTE is False, a default assumption is made.
    LTE : bool
        Flag indicating whether calculations are in Local Thermodynamic Equilibrium.
    verbose : bool
        If True, prints informative messages about the validation process.
    Notes
    -----
    - If `dVdr` is None and LTE is False, assumes `dVdr` to be sigmaNT divided by the Jeans Length.
    - If LTE is False and `dVdr` is provided, validates that `dVdr` is a float.
    - If LTE is True, `dVdr` is ignored and a message is printed if verbose is True.
    """
    if dVdr is None and LTE is False: 
        if verbose:
            print('Assumming dVdr to be sigmaNT divided by the Jeans Length')
    elif LTE is False:
        validate_float(dVdr)
    else: 
        if verbose:
            print('Calculations are in LTE, no dVdr required and therefore ignored')
        

def validate_d2g(d2g, verbose): 
    """
    Validates and processes the dust-to-gas ratio (d2g) parameter.
    Parameters
    ----------
    d2g : float, str, or None
        The dust-to-gas ratio to validate. If None, a default value of 'zs(jz2)' is used,
        which assumes the dust-to-gas ratio is linear with metallicity.
    verbose : bool
        If True, prints messages about the assumptions or actions taken.
    Returns
    -------
    d2g : float or str
        The validated dust-to-gas ratio. Returns 'zs(jz2)' if d2g is None or if the user
        confirms to proceed with the default after providing a non-positive value.
    Raises
    ------
    ValueError
        If d2g is less than or equal to zero and the user does not confirm to proceed with
        the default value.
    """
    if d2g is None:
        d2g = 'zs(jz2)'
        if verbose:
            print('Dust-to-gas ratio assumed to be linear with metallicity')
    elif d2g <= 0: 
        print('d2g must be larger than 0. Do you want to continue with a dust-to-gas ratio linear with meatllicity?')
        user_input = input('Type y to confirm or any key to exit ')
        if user_input == 'y' or user_input == 'Y': 
             d2g = 'zs(jz2)'
        else: 
            raise ValueError('d2g must be larger than 0')
    else: 
        validate_float(d2g=d2g)
        d2g = d2g   
    
    return d2g

def validate_length(length, test, verbose):
    """
    Validates and determines the appropriate length type for column density calculations.
    Parameters
    ----------
    length : str or None
        The length type to use. Should be either 'jeans' or 'shielding'. If None, the function will infer the value based on the `test` parameter.
    test : str
        A string indicating the type of test being performed. Used to determine if 'shielding' or 'jeans' length should be used.
    verbose : bool
        If True, prints informative messages about the chosen length and any corrections made.
    Returns
    -------
    str
        The validated or inferred length type, either 'jeans' or 'shielding'.
    Raises
    ------
    ValueError
        If the provided length is invalid and the user does not confirm the suggested correction.
    Notes
    -----
    - If `length` is not provided, it is inferred from the `test` parameter.
    - If an invalid `length` is provided, the function suggests the closest valid option using Levenshtein distance and prompts the user for confirmation.
    - The function may override the chosen length based on the `test` parameter to ensure consistency.
    """
    if length is None: 
        if 'test_shielded' in test:
            length = 'shielding'
            if verbose is True: 
                print('Shielding length used for column density calculation')
        else: 
            length = 'jeans'
            if verbose: 
                print('Jeans length used for column density calculation')
    
    options = ['jeans', 'shielding']
    
    if length not in options:
        lev_results = []
        for j in options: 
            lev_results += [levenshtein(length, j)]
    
        idx = np.argmin(lev_results)
        print(f'Invalid length: {length}. Did you mean {options[idx]}?')
        user_input = input('Type y to confirm or any key to exit ')
        if user_input == 'y' or user_input == 'Y': 
            length = options[idx]
        else: 
            raise ValueError(f'invalid length: {length}')
    
    if length == 'shielding': 
        if 'test_shielded' not in test: 
            length = 'jeans'
            if verbose: 
                print('Not a shielded test. Jeans length used for calculations')
    
    if length == 'jeans': 
        if 'test_shielded' in test: 
            length = 'shielding'
            if verbose: 
                print('A shielded test. Shielding length used for calculations')
                
    return length
    
def validate_geometry(geometry, verbose): 
    """
    Validates and normalizes the input geometry string for non-LTE calculations.
    If the geometry is None, defaults to 'LVG' and optionally prints a message if verbose is True.
    If the geometry is not one of the allowed options ('LVG', 'slab', 'sphere'), suggests the closest valid option using the Levenshtein distance and prompts the user for confirmation.
    Raises a ValueError if the user does not confirm the suggested option.
    Args:
        geometry (str or None): The geometry type to validate. Can be 'LVG', 'slab', 'sphere', or None.
        verbose (bool): If True, prints informational messages.
    Returns:
        str: The validated geometry string.
    Raises:
        ValueError: If the geometry is invalid and the user does not confirm the suggested correction.
    """
    if geometry is None: 
        geometry = 'LVG'
        if verbose: 
            print('LVG geometry used for non-LTE calculations')
            
    options = ['LVG', 'slab', 'sphere']
    
    if geometry not in options:
        lev_results = []
        for j in options: 
            lev_results += [levenshtein(geometry, j)]
    
        idx = np.argmin(lev_results)
        print(f'Invalid geometry: {geometry}. Did you mean {options[idx]}?')
        user_input = input('Type y to confirm or any key to exit ')
        if user_input == 'y' or user_input == 'Y': 
            geometry = options[idx]
        else: 
            raise ValueError(f'invalid length: {geometry}')
    
    return geometry

def safety_check_H2(H2_abund, errtol = 1e-5): 
    """
    Checks if the maximum H2 abundance does not exceed 0.5 within a specified error tolerance.
    Parameters
    ----------
    H2_abund : array-like
        Array of H2 abundances to check.
    errtol : float, optional
        Error tolerance for the maximum allowed H2 abundance (default is 1e-5).
    Raises
    ------
    ValueError
        If the maximum H2 abundance exceeds 0.5 by more than the specified error tolerance.
    """

    if (np.max(H2_abund) - 0.5) < errtol: 
        pass
    else: 
        raise ValueError('max H2 abundance can not be larger than 0.5')
        
def validate_species_transitions(species, verbose): 
    """
    Validates and processes a list of species and their corresponding number of transitions.
    Parameters
    ----------
    species : list of tuple or None
        A list of tuples, where each tuple contains a species name (str) and the number of transitions (int),
        e.g., [('CO', 5), ('C', 2)]. If None, defaults to [('CO', 5)].
    verbose : bool
        If True, prints informative messages about the validation and any adjustments made.
    Returns
    -------
    list_species : list of str
        List of validated species names.
    list_transitions : list of int
        List of validated number of transitions for each species, capped at the maximum allowed per species.
    Raises
    ------
    ValueError
        If the input 'species' is not a list of (str, int) tuples in the correct format.
    Notes
    -----
    - If the requested number of transitions for a species exceeds the maximum available, it is capped and a message is printed if verbose is True.
    - Only species present in the predefined 'names_network' list are supported.
    """
    if species is None: 
        species = [('CO', 5)]
        if verbose:
            print('The calculations are only performed for the first 5 transitions of CO')
        
    if not isinstance(species, list) and all(
            isinstance(item, tuple) and len(item) == 2
            and isinstance(item[0], str) and 
            isinstance(item[1], int) for item in species):
        raise ValueError("Please enter the species and transitions in this format: [('CO', 5), ('C', 2)]")
        
    max_transitions = [3, 40, 1, 3, 4, 127, 13, 59, 8, 45, 1349, 50, 152, 77, 41, 25, 21, 158, 25, 30, 23]
    names_network = ['C', 'CO', 'C+', 'O', 'O2+', 'CH', 'CH+', 'CN', 'HD','NH', 'NO', 'OH', 'OH+', 'O2', 'CH2', 'HCN', 'HCO+', 'H2O', 'HNC', 'N2H+', 'H3O+']

    
    list_species, list_transitions = [], []
    for i, specy in enumerate(species): 
        idx = names_network.index(specy[0])
        list_species += [specy[0]]
        if max_transitions[idx] < specy[1]: 
            if verbose: 
                print(f'Only {max_transitions[idx]} transitions available for {specy[0]}. n_transitions set to {max_transitions[idx]}')
            list_transitions += [max_transitions[idx]]
        else: 
            list_transitions += [specy[1]]
    
    return list_species, list_transitions

def check_points(data, points): 
    """
    Returns the number of points to use, ensuring it does not exceed the length of the data.
    Parameters
    ----------
    data : sequence
        The data sequence to check the length of.
    points : int
        The desired number of points.
    Returns
    -------
    int
        The number of points to use, which is the smaller of `points` and the length of `data`.
    """
    len_data = len(data)
    if points > len_data: 
        return len_data
    else: 
        return points
            
def d_formatter(line): 
    """
    Replaces the first occurrence of 'E' with 'd' in the input string.
    This function is typically used to convert scientific notation from
    the format using 'E' (e.g., '1.23E+04') to the format using 'd'
    (e.g., '1.23d+04'), which is required for fortran.
    Parameters
    ----------
    line : str
        The input string potentially containing an 'E' character.
    Returns
    -------
    str
        The modified string with the first 'E' replaced by 'd'.
    Raises
    ------
    ValueError
        If 'E' is not found in the input string.
    """

    line_list = list(line)
    line_list[line_list.index('E')] = 'd'
    line = ''.join(line_list)
    return line
            
def jeans_length(T, rho, mu, gamma = 7/5): 
    """
    Calculate the Jeans length for a given temperature, density, mean molecular weight, and adiabatic index.

    The Jeans length is the critical scale at which thermal pressure can support a cloud against gravitational collapse.

    Parameters
    ----------
    T : float
        Temperature in Kelvin.
    rho : float
        Mass density in g/cm^3.
    mu : float
        Mean molecular weight (dimensionless).
    gamma : float, optional
        Adiabatic index (default is 7/5).

    Returns
    -------
    float
        Jeans length in centimeters.
    """

    kb = 1.381e-16
    G = 6.67e-8
    mH = 1.67e-24
    c_s = np.sqrt(gamma * kb * T / (mu * mH))
    return np.sqrt(np.pi * c_s**2 / (G * rho) )

def shielding_length(n):
    """
    Calculate the shielding length as a function of number density.
    Parameters
    ----------
    n : float or array-like
        The hydrogen number density (in cm^-3).
    Returns
    -------
    float or array-like
        The shielding length (in cm), calculated using the formula:
        L = L_0 * (n / n_0) ** (-a)
        where L_0 = 5 pc, n_0 = 100 cm^-3, and a = 0.7.
    Notes
    -----
    This function is typically used in astrophysical contexts to estimate
    the characteristic length scale over which shielding occurs in a medium
    with hydrogen number density `n`.
    """

    L_0 = 5 * 3.086e18
    a = 0.7
    n_0 = 100
    return L_0 * (n/n_0)**(-a)
    
    
def ncol(nH, L): 
    """
    Calculate the column density given the number density and path length.
    Parameters
    ----------
    nH : float
        Number density (e.g., of hydrogen atoms) in units of cm^-3.
    L : float
        Path length along the line of sight in units of cm.
    Returns
    -------
    float
        Column density (e.g., in units of cm^-2).
    """

    return nH * L 

def get_species_name(species):
    """
    Given a species name from the network list, returns the corresponding species names
    in the KROME and Despotic naming conventions.
    Parameters
    ----------
    species : str
        The species name as used in the network list.
    Returns
    -------
    tuple of str
        A tuple containing the species name in the KROME and Despotic naming conventions,
        respectively.
    Raises
    ------
    ValueError
        If the provided species name is not found in the network list.
    """

    names_network = ['C', 'CO', 'C+', 'O', 'O2+', 'CH', 'CH+', 'CN', 'HD','NH', 'NO', 'OH', 'OH+', 'O2', 'CH2', 'HCN', 'HCO+', 'H2O', 'HNC', 'N2H+', 'H3O+']
    names_KROME = ['C', 'CO', 'C_1', 'O', 'O2_1', 'CH', 'CH_1', 'CN', 'HD', 'NH','NO', 'OH', 'OH_1', 'O2', 'CH2', 'HCN', 'HCO', 'H2O', 'HNC', 'N2H', 'H3O']
    names_despotic = ['c', 'co', 'c+', 'o', 'o++', 'ch-h2', 'ch+', 'cn', 'hd', 'nh', 'no', 'oh', 'oh+', 'o2', 'ch2_h2_ortho', 'hcn', 'hco+', 'ph2o@daniel', 'hnc', 'n2h+@xpol', 'ph3o+-h2']
            
    idx = names_network.index(species)

    return names_KROME[idx], names_despotic[idx]       
