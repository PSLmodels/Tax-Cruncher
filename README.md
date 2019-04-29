# Tax-Cruncher

Tax-Cruncher calculates federal tax liabilities from individual data under different policy proposals. 

Tax-Cruncher accepts  inputs similar to NBER's [TAXSIM Version 27](https://users.nber.org/~taxsim/taxsim27/), converts those inputs to a format usable by [Tax-Calculator](https://github.com/PSLmodels/Tax-Calculator), an open-source microsimulation model of federal individual income and payroll tax law, and uses Tax-Calculator capabilities to analyze the user-specified inputs under various tax policy proposals.

How to use Tax-Cruncher
------------
**First, define your inputs.** You may either edit `taxcrunch/adjustment_template.json` directly in your local repository or create a separate json file that includes just the parameters you would like to adjust.

**Second, pick the policy proposal you would like to analyze.** Browse the Tax-Calculator [reforms folder](https://github.com/PSLmodels/Tax-Calculator/tree/master/taxcalc/reforms) for a preset reform, or specify your own reform in a json file in accordance with the [instructions](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/reforms/REFORMS.md#how-to-specify-a-tax-reform-in-a-json-policy-reform-file) in the Tax-Calculator repository. Fill out the `reform_options` field in your adjustment file with the appropriate reform name or set the field to `Custom` if you specified your own reform.

**Third, initiate the Cruncher class.** If you modified `taxcrunch/adjustment_template.json` directly and chose a preset policy reform file, you can initiate the class with `c = Cruncher()`. Otherwise, initiate the Cruncher class with 

`c = Cruncher(file=PATH_TO_ADJUSTMENT_FILE, custom_reform=PATH_TO_REFORM_FILE)`.

**Fourth, analyze your reform.** Try out the following methods:

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

