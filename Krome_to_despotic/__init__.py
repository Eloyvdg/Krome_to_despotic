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

__version__ = "0.0.1"
__all__ = ["Pipeline", "utils"]

from .Pipeline import KromeDespoticPipeline
from .utils import open_krome, find_nearest, run_subprocess_no_input, run_subprocess_input
from .cosmology import age_universe
