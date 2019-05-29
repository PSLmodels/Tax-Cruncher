# Tax-Cruncher

Tax-Cruncher calculates federal tax liabilities from individual data under different policy proposals. 

Tax-Cruncher accepts  inputs similar to NBER's [TAXSIM Version 27](https://users.nber.org/~taxsim/taxsim27/), converts those inputs to a format usable by [Tax-Calculator](https://github.com/PSLmodels/Tax-Calculator), an open-source microsimulation model of federal individual income and payroll tax law, and uses Tax-Calculator capabilities to analyze the user-specified inputs under various tax policy proposals.

How to use Tax-Cruncher
------------
Tax-Cruncher can analyze individual data from one filer or multiple filers under different policy proposals. The procedures for the two uses are different.

**To analyze individual data from one filer:** 

- First, define your inputs. You may either edit `taxcrunch/adjustment_template.json` directly in your local repository or create a separate JSON file that includes just the parameters you would like to adjust.

- Second, pick the policy proposal you would like to analyze. Browse the Tax-Calculator [reforms folder](https://github.com/PSLmodels/Tax-Calculator/tree/master/taxcalc/reforms) for a preset reform, or specify your own reform in a JSON file in accordance with the [instructions](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/reforms/REFORMS.md#how-to-specify-a-tax-reform-in-a-json-policy-reform-file) in the Tax-Calculator repository. Fill out the `reform_options` field in your adjustment file with the appropriate preset reform name. Do not specify a preset reform if you specified a file path to a custom reform.

- Third, initiate the Cruncher class. If you modified `taxcrunch/adjustment_template.json` directly and chose a preset policy reform file, you can initiate the class with `c = Cruncher()`. Otherwise, initiate the Cruncher class with: 
`c = Cruncher(file='ADJUSTMENT_FILE_NAME', custom_reform='REFORM_FILE_NAME')`.

- Fourth, analyze your reform. Try out the following methods:
```python
#basic outputs
c.basic_table()
#marginal tax rates
c.mtr_table()
#detailed outputs with marginal tax rate analysis 
c.calc_table()
#detailed outputs with difference between reform and baseline
c.calc_diff_table()
```

**To analyze individual data from multiple filers:**

- First, define your inputs in a csv file. Instructions on how to make this CSV file can be found [here](docs/INPUT_INSTRUCTIONS.md).

- Second, initiate the `Batch` class. The Batch class can be found in the `multi_cruncher` module. Initiate the Batch class with `b = Batch('INPUT_DATA_FILE')`

- Third, analyze your data. You can analyze your data under current law or under a policy reform with two separate methods. To analyze your data under current law, use the method: `b.baseline_table()`. To analyze your data under a policy reform, first either choose a reform from the Tax-Calculator [reforms folder](https://github.com/PSLmodels/Tax-Calculator/tree/master/taxcalc/reforms) or create a custom JSON reform file, and then use the methods:

```python
#liabilities under current law
b.baseline_table()
#liabilities under reform 
b.reform_table('REFORM_FILE_NAME')
```

How to install Tax-Cruncher
-------------
Install from source:

```
git clone https://github.com/Peter-Metz/Tax-Cruncher
cd Tax-Cruncher
conda env create
conda activate taxcrunch-env
pip install -e .
```

