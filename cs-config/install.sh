# bash commands for installing your package

git clone https://github.com/PSLmodels/Tax-Cruncher
cd Tax-Cruncher
conda install PSLmodels::taxcalc PSLmodels::behresp "conda-forge::paramtools>=0.15.1" "bokeh<2.0.0" ipython
pip install -e .