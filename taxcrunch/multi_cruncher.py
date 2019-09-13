import sys
import os
import numpy as np
import pandas as pd
import taxcalc as tc
from paramtools import Parameters
from taxcrunch import cruncher as cr
from datetime import date


CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))


class BatchParams(Parameters):

    defaults = os.path.join(CURRENT_PATH, "defaults_batch.json")

    # custom adjust method to validate Batch inputs
    def adjust(self, ivar):
        input_list = ivar.transpose().to_numpy().tolist()
        params = {}
        for label, row in zip(self, range(len(input_list))):
            params[label] = input_list[row]

        return super().adjust(params)


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
        CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))

        if isinstance(self.path, pd.DataFrame):
            ivar = self.path
        else:
            input_file = os.path.join(CURRENT_PATH, self.path)
            ivar = pd.read_csv(input_file, sep=',',
                               engine="python", header=None)
        # check that input CSV has 24 columns
        assert len(ivar.columns) == 24
        # check that year is the same across all rows
        assert ivar[1].max() == ivar[1].min()
        rows = len(ivar)
        params = BatchParams()
        # validate input
        params.adjust(ivar)
        array = np.empty((0, rows))
        for label in params._data:
            array = np.append(array, [params._data[label][
                              'value'][0]['value']], axis=0)
        params_df = pd.DataFrame(array).transpose()

        # translate INPUT variables into OUTPUT variables
        c = cr.Cruncher()
        self.invar = c.translate(params_df)
        self.rows = len(self.invar.index)
        return self.invar, self.rows

    def create_table(self, reform_file=None):
        """
        Creates table of liabilities. Default is current law, but user may specify
            a policy reform which is read and implemented below in get_pol()

        The reform_file argument can be the name of a reform file in the
            Tax-Calculator reforms folder, a file path to a custom JSON
            reform file, or a dictionary with a policy reform. 

        Returns:
            df_res: a Pandas dataframe. Each observation is a separate tax filer
        """
        pol = self.get_pol(reform_file)
        year = self.invar['FLPDYR'][0]
        year = int(year.item())
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

    def write_output_file(self, output_filename=None, reform_file=None):
        """
        Writes an output table as a csv. Like the create_table() method, default is current
            law and optional reform_file argument is a file path to or dictionary of a reform.

        Default output filename is "cruncher-mm-dd-YYYY.csv" but user can change output filename
            with output_filename argument.
        """
        if output_filename is None:
            today = date.today()
            today_str = today.strftime("%m-%d-%Y")
            output_filename = "cruncher-" + today_str + ".csv"
        df_res = self.create_table(reform_file)
        assert isinstance(df_res, pd.DataFrame)
        df_res.to_csv(output_filename, index=False, float_format='%.2f')

    def get_pol(self, reform_file):
        """
        Reads the specified reform and implements it
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
                    pol.implement_reform(
                        tc.Policy.read_json_reform(reform_url))
                except:
                    raise 'Reform file does not exist'
        return pol
