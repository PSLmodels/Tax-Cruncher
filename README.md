[![PSL cataloged](https://img.shields.io/badge/PSL-cataloged-a0a0a0.svg)](https://www.PSLmodels.org)
[![Codecov](https://codecov.io/gh/PSLmodels/Tax-Cruncher/branch/master/graphs/badge.svg)](https://codecov.io/gh/PSLmodels/Tax-Cruncher)

# Tax-Cruncher

Tax-Cruncher calculates federal tax liabilities from individual data under different policy scenarios. 

Tax-Cruncher accepts inputs similar to NBER's [TAXSIM Version 27](https://users.nber.org/~taxsim/taxsim27/), converts those inputs to a format usable by [Tax-Calculator](https://github.com/PSLmodels/Tax-Calculator), and uses Tax-Calculator capabilities to analyze the user-provided data under various tax policy proposals.

Tax-Cruncher's web application is hosted on [Compute Studio](https://compute.studio/PSLmodels/Tax-Cruncher/). The code that powers the web application can be found in this repository in the [cs-config](https://github.com/PSLmodels/Tax-Cruncher/tree/master/cs-config) directory.

How to use Tax-Cruncher
------------
Tax-Cruncher can analyze individual data from one filer or multiple filers.

**To analyze individual data from one filer:** 

- The easiest way to analyze one tax filer is with the [web application](https://compute.studio/PSLmodels/Tax-Cruncher/) hosted on Compute Studio.

**To analyze individual data from multiple filers:**

*For a more complete demo of Tax-Cruncher's multi-filer capabalities, explore this [Jupyter Notebook](https://github.com/PSLmodels/Tax-Cruncher/blob/master/docs/cruncher_demo.ipynb).*

- First, follow [these steps](docs/INPUT_INSTRUCTIONS.md) to format your data in a csv file. Each row of the file represents one filing unit and each column is an input variable.

- Second, create a `Batch` object (the class can be found in `taxcrunch/multi_cruncher.py`). The `Batch` class takes one argument -- the file path to your input data.

- Third, analyze your data. You can analyze your data under current law or under a policy reform using the `create_table()` method. If you do not pass an argument to the method, Tax-Cruncher will analyze your data under current law. To analyze your data under a policy reform, pass the file path to a JSON reform file, a reform dictionary, or the name of a preset reform from the Tax-Calculator [reforms folder](https://github.com/PSLmodels/Tax-Calculator/tree/master/taxcalc/reforms) to the `create_table()` method.

```python
# create Batch object
b = Batch('DATA_FILE_PATH')
# liabilities under current law
base_table = b.create_table()
# liabilities under reform 
reform_table = b.create_table(reform_file='REFORM_FILE_PATH')
```

How to install Tax-Cruncher
-------------
Install with conda:
```
conda install -c pslmodels taxcrunch
```

Install from source:

```
git clone https://github.com/PSLmodels/Tax-Cruncher
cd Tax-Cruncher
conda env create
conda activate taxcrunch-env
pip install -e .
```

How to cite Tax-Cruncher
--------------
Please cite the source of your analysis as "Tax-Cruncher release #.#.#, author's calculations." If you would like to link to Tax-Cruncher, please use `https://github.com/PSLmodels/Tax-Cruncher`.
