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

#!/bin/bash

cd "$(dirname "$0")"

git clone https://genugten-admin@bitbucket.org/psharda1/krome.git
git clone https://krumholz@bitbucket.org/krumholz/despotic.git

mkdir -p despotic_package
mv despotic despotic_package/
mv despotic_package/despotic/despotic ./

python3 -m venv venv
source venv/bin/activate

pip install .
