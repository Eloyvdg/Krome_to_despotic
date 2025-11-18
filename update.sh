#  ! *************************************************************
#  !  Krome_to_despotic
#  !
#  !  Written by Eloy van de Genugten (Leiden University, 2025)
#  !  With Piyush Sharda (LU), Jackie Hodge (LU) and Shyam Menon (CCA)
#  !  Email: eloyvandegenugten@gmail.com, sharda@strw.leidenuniv.nl
#  !  Krome_to_despotic is provided "as it is", without any warranty.
#  ! *************************************************************

#!/bin/bash

cd "$(dirname "$0")"

git pull

mv despotic despotic_package/despotic/
cd despotic_package/despotic/
git pull
cd ../../
mv despotic_package/despotic/despotic ./

cd krome/
git pull 
cd ../
