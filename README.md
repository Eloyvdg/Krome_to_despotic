# Krome_to_despotic

**Krome_to_despotic** is a Python package that provides a pipeline to combine [KROME](https://bitbucket.org/psharda1/krome) thermo-chemical modeling with [Despotic](https://bitbucket.org/krumholz/despotic) radiative transfer calculations. This tool allows you to run KROME thermo-chemical models, modify their parameters, and use the results as input for Despotic to compute line emission properties for astrophysical clouds. **Krome_to_despotic** is provided "as it is", without any warranty.


## Features

- Edit and run KROME test files with custom physical parameters (density, metallicity, redshift, cosmic ray rate, FUV field, etc.).
- Automatically process KROME output and feed it into Despotic.
- Modify Despotic cloud files and run line emission calculations for various species and transitions.
- Supports batch processing and logging of results.
- Utilities for validating input parameters and managing the workflow.

## Installation



You can easily clone this repository by typing: 

```sh
git clone https://github.com/Eloyvdg/Krome_to_despotic.git

```

To install KROME and despotic in the right folder, run: 

```sh
bash install.sh

```


**Dependencies:**
- numpy
- pexpect
- despotic
- KROME

You must have gfortran as a Fortran compiler installed before building this package.
On Ubuntu/Debian:
```sh
sudo apt install gfortran

```

## Running tests
An example test can be found in the Examples folder. 
To run the test, type:

```sh
python3 Examples/test.py
```

## Authors
Written by Eloy van de Genugten
```
eloyvandegenugten@gmail.com
Leiden University, Netherlands
```

Collaborators:
Piyush Sharda
```
sharda@strw.leidenuniv.nl
Leiden University, Netherlands
```
Jackie Hodge
```
hodge@strw.leidenuniv.nl
Leiden University, Netherlands
```
Shyam Menon
```
smenon@flatironinstitute.org
Flatiron Institute, USA
```

## License

See [LICENSE](LICENSE) for details.

## Acknowledgements

- [KROME](https://bitbucket.org/tgrassi/krome) by Shyam Menon, Piyush Sharda, Tomasso Grassi, et al.
- [Despotic](https://bitbucket.org/krumholz/despotic) by Mark Krumholz

---

For more details, see the docstrings in the code and the Examples/test.py file.
