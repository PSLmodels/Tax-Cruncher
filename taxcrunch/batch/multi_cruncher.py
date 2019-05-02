import os
import sys
import numpy as np
import pandas as pd
import taxcalc as tc
from taxcrunch import cruncher as cr


class Batch:
    def __init__(self, path):
        self.path = path

    tc_vars = [
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
    labels = [
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
        ivar = pd.read_csv(self.path, delim_whitespace=True, header=None)
        # translate INPUT variables into OUTPUT variables
        c = cr.Cruncher()
        invar = c.translate(ivar)
        rows = len(invar.index)
        df_base = []
        for r in range(rows):
            unit = invar.iloc[r]
            unit = pd.DataFrame(unit).transpose()

            year = unit.iloc[0][1]
            year = year.item()
            recs = tc.Records(data=unit, start_year=year)
            pol = tc.Policy()
            calc = tc.Calculator(policy=pol, records=recs)
            calc.calc_all()

            table = calc.dataframe(tc_vars)
            df_base.append(table)
        df_base = pd.concat(df_base)
        df_base.columns = labels
        df_base.index = range(rows)
        return df_base

    def reform_table(self, reform):
        ivar = pd.read_csv(self.path, delim_whitespace=True, header=None)
        # translate INPUT variables into OUTPUT variables
        c = cr.Cruncher()
        invar = c.translate(ivar)
        rows = len(invar.index)
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
        for r in range(rows):
            unit = invar.iloc[r]
            unit = pd.DataFrame(unit).transpose()

            year = unit.iloc[0][1]
            year = year.item()
            recs = tc.Records(data=unit, start_year=year)
            calc = tc.Calculator(policy=pol, records=recs)
            calc.calc_all()

            table = calc.dataframe(tc_vars)
            df_reform.append(table)
        df_reform = pd.concat(df_reform)
        df_reform.columns = labels
        df_reform.index = range(rows)
        return df_reform
