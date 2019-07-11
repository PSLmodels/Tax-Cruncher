# bash commands for installing your package

git clone https://github.com/PSLmodels/Tax-Cruncher
cd Tax-Cruncher
conda install PSLmodels::taxcalc conda-forge::paramtools ipython
pip install -e .