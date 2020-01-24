# Tax-Cruncher

Tax-Cruncher calculates federal tax liabilities from individual data under different policy proposals. 

Tax-Cruncher accepts inputs similar to NBER's [TAXSIM Version 27](https://users.nber.org/~taxsim/taxsim27/), converts those inputs to a format usable by [Tax-Calculator](https://github.com/PSLmodels/Tax-Calculator), an open-source microsimulation model of federal individual income and payroll tax law, and uses Tax-Calculator capabilities to analyze the user-specified inputs under various tax policy proposals.

Tax-Cruncher's web application is hosted on [Compute Studio](https://compute.studio/PSLmodels/Tax-Cruncher/). The code that powers the web application can be found in this repository in the [cs-config](https://github.com/PSLmodels/Tax-Cruncher/tree/master/cs-config) directory.

How to use Tax-Cruncher
------------
Tax-Cruncher can analyze individual data from one filer or multiple filers.

**To analyze individual data from one filer:** 

- The easiest way to analyze one tax filer is with the [web application](https://compute.studio/PSLmodels/Tax-Cruncher/) hosted on Compute Studio.

**To analyze individual data from multiple filers:**

*For a more complete demo of Tax-Cruncher's multi-filer capabalities, explore this [Jupyter Notebook](https://github.com/PSLmodels/Tax-Cruncher/blob/master/docs/cruncher_demo.ipynb).*

- First, define your inputs in a csv file. Each row of the file represents one filing unit. Instructions on how to construct a csv input file can be found [here](docs/INPUT_INSTRUCTIONS.md).

- Second, initiate the `Batch` class found in the `taxcrunch/multi_cruncher` module. Initiate the Batch class with `b = Batch('INPUT_DATA_FILE_PATH')`.

- Third, analyze your data. You can analyze your data under current law or under a policy reform using the `create_table()` method. If you do not pass an argument to the method, Tax-Cruncher will analyze your data under current law. To analyze your data under a policy reform, pass a JSON reform file, a reform dictionary, or a preset reform from the Tax-Calculator [reforms folder](https://github.com/PSLmodels/Tax-Calculator/tree/master/taxcalc/reforms) to the `create_table()` method.

```python
# initiate Batch class
b = Batch('FILE_PATH')
# liabilities under current law
b.create_table()
# liabilities under reform 
b.create_table('REFORM_FILE_PATH')
```

How to install Tax-Cruncher
-------------
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
