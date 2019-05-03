import sys
import numpy as np
import pandas as pd
import taxcalc as tc
from taxcrunch import cruncher as cr


class Batch:
    """
    Constructor for the Batch class

    Parameters
    ----------
    path: file path to csv file with input data
        Make sure that the file is formatted according to the instructions in the README

    Returns
    -------
    class instance: Batch

    """
    def __init__(self, path):
        self.path = path

        self.tc_vars = [
            "iitax",
            "payrolltax",
            "c00100",
            "e02300",
            "c02500",
            "c04470",
            "c04800",
            "c05200",
            "c07220",
            "c11070",
            "c07180",
            "eitc",
            "c09600",
            "niit",
            "taxbc",
            "ptax_was",
        ]
        self.labels = [
            "Individual Income Tax",
            "Payroll Tax",
            "AGI",
            "UI in AGI",
            "OASDI in AGI",
            "Itemized Deductions",
            "Taxable Inc",
            "Regular Tax",
            "CTC",
            "CTC Refundable",
            "Child care credit",
            "EITC",
            "AMT",
            "Net Investment Income Tax",
            "Income Tax Before Credits",
            "FICA",
        ]

    def baseline_table(self):
        """
        Creates table of liabilities under current law. 

        Returns:
            df_base: a Pandas dataframe. Each observation is a separate tax filer
        """
        ivar = pd.read_csv(self.path, delim_whitespace=True, header=None)
        # translate INPUT variables into OUTPUT variables
        c = cr.Cruncher()
        invar = c.translate(ivar)
        rows = len(invar.index)
        df_base = []
        # create Tax-Calculator records object from each row of csv file and run calculator
        for r in range(rows):
            unit = invar.iloc[r]
            unit = pd.DataFrame(unit).transpose()

            year = unit.iloc[0][1]
            year = year.item()
            recs = tc.Records(data=unit, start_year=year)
            pol = tc.Policy()
            calc = tc.Calculator(policy=pol, records=recs)
            calc.calc_all()

            table = calc.dataframe(self.tc_vars)
            df_base.append(table)
        df_base = pd.concat(df_base)
        df_base.columns = self.labels
        df_base.index = range(rows)
        return df_base

    def reform_table(self, reform):
        """
        Creates table of liabilities under specified reform. 

        Returns:
            df_base: a Pandas dataframe. Each observation is a separate tax filer
        """
        ivar = pd.read_csv(self.path, delim_whitespace=True, header=None)
        # translate INPUT variables into OUTPUT variables
        c = cr.Cruncher()
        invar = c.translate(ivar)
        rows = len(invar.index)
        # choose and implement reform from Tax-Calculator reforms folder
        REFORMS_URL = (
            "https://raw.githubusercontent.com/"
            "PSLmodels/Tax-Calculator/master/taxcalc/reforms/"
        )
        reform_name = reform
        reform_url = REFORMS_URL + reform_name
        reform = tc.Calculator.read_json_param_objects(reform_url, None)
        pol = tc.Policy()
        pol.implement_reform(reform["policy"])

        df_reform = []
        # create Tax-Calculator records object from each row of csv file and run calculator
        for r in range(rows):
            unit = invar.iloc[r]
            unit = pd.DataFrame(unit).transpose()

            year = unit.iloc[0][1]
            year = year.item()
            recs = tc.Records(data=unit, start_year=year)
            calc = tc.Calculator(policy=pol, records=recs)
            calc.calc_all()

            table = calc.dataframe(self.tc_vars)
            df_reform.append(table)
        df_reform = pd.concat(df_reform)
        df_reform.columns = self.labels
        df_reform.index = range(rows)
        return df_reform
