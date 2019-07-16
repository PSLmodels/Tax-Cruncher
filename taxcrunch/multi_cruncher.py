import sys
import os
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
        self.invar, self.rows = self.read_input()

        self.tc_vars = [
            "RECID",
            "iitax",
            "payrolltax",
            "e00200",
            "c00100",
            "e02300",
            "c02500",
            "c04470",
            "c04800",
            "taxbc",
            "c07220",
            "c11070",
            "c07180",
            "eitc",
            "c62100",
            "c09600",
            "niit",
            "c05800",
            "ptax_was"
        ]
        self.labels = [
            "ID",
            "Individual Income Tax",
            "Payroll Tax",
            "Wages",
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
            "AMT Taxable Income",
            "AMT Liability",
            "Net Investment Income Tax",
            "Income Tax Before Credits",
            "FICA",
            "Payroll Tax MTR",
            "Income Tax MTR",
            "Combined MTR"
        ]

    def read_input(self):
        """
        Reads csv input file

        Returns
            self.invar: Tax-Calculator style dataframe of inputs
            self.rows: number of rows of input file
        """

        if isinstance(self.path, pd.DataFrame):
            ivar = self.path
        else:
            ivar = pd.read_csv(self.path, sep=',', engine="python", header=None)
        # translate INPUT variables into OUTPUT variables
        c = cr.Cruncher()
        self.invar = c.translate(ivar)
        self.rows = len(self.invar.index)
        return self.invar, self.rows

    def create_table(self, reform_file=None):
        pol = self.get_pol(reform_file)
        year = self.invar['FLPDYR'][0]
        year = year.item()
        recs = tc.Records(data=self.invar, start_year=year)
        calc = tc.Calculator(policy=pol, records=recs)
        calc.advance_to_year(year)
        calc.calc_all()
        calcs = calc.dataframe(self.tc_vars)
        mtr = calc.mtr(wrt_full_compensation=False)
        mtr_df = pd.DataFrame(data=mtr).transpose()
        df_res = pd.concat([calcs, mtr_df], axis=1)
        df_res.columns = self.labels
        df_res.index = range(self.rows)
        return df_res

    def get_pol(self, reform_file):
       
        # if a reform file is not specified, the default policy is current law
        """
        Creates table of liabilities. Default is current law, but user may specify
            a policy reform.

        The reform_file argument can be the name of a reform file in the
            Tax-Calculator reforms folder, a file path to a custom JSON
            reform file, or a dictionary with a policy reform.

        Returns:
            df_res: a Pandas dataframe. Each observation is a separate tax filer
        """
        REFORMS_URL = (
            "https://raw.githubusercontent.com/"
            "PSLmodels/Tax-Calculator/master/taxcalc/reforms/"
        )
        CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))
        if reform_file == None:
            pol = tc.Policy()
        else:
            # check to see if file path to reform_file exists
            if isinstance(reform_file, str) and os.path.isfile(os.path.join(CURRENT_PATH, reform_file)):
                reform_path = os.path.join(CURRENT_PATH, reform_file)
                pol = tc.Policy()
                pol.implement_reform(tc.Policy.read_json_reform(reform_path))
            # try reform_file as dictionary
            elif isinstance(reform_file, dict):
                reform = reform_file
                pol = tc.Policy()
                pol.implement_reform(reform)
            # if file path does not exist, check Tax-Calculator reforms file
            else:
                try:
                    reform_url = REFORMS_URL + reform_file
                    pol = tc.Policy()
                    pol.implement_reform(tc.Policy.read_json_reform(reform_url))
                except:
                    raise 'Reform file does not exist'
        return pol
