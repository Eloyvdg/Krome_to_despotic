#!/bin/bash

cd "$(dirname "$0")"

git clone https://genugten-admin@bitbucket.org/psharda1/krome.git
git clone https://krumholz@bitbucket.org/krumholz/despotic.git

mkdir -p despotic_package
mv despotic despotic_package/
mv despotic_package/despotic/despotic ./

python3 -m venv venv
source venv/bin/activate

cd Krome_to_despotic
pip install .
