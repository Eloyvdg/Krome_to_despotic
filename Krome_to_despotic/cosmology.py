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

from astropy.cosmology import FlatLambdaCDM
import astropy.units as u

def age_universe(z): 
    H0 = 70 * u.km / u.s / u.Mpc  # Hubble constant
    Om0 = 0.3  # Matter density parameter
    Tcmb0 = 2.725 * u.K  # CMB temperature at z = 0
    cosmo = FlatLambdaCDM(H0=H0, Tcmb0=Tcmb0, Om0= Om0)
    return cosmo.age(z).to(u.yr).value

if __name__ == "__main__":
    print(f"Age of the universe at z=0: {age_universe(0):.2e} years")
