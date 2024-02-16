import sys
import os
import numpy as np
import pandas as pd
import taxcalc as tc
import behresp as br
from paramtools import Parameters
from taxcrunch import cruncher as cr
from datetime import date


CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))

FINITE_DIFF = 0.01


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
    path: file path to csv file with input data or a Pandas DataFrame
        Make sure that the file is formatted according to the instructions in the README

    Returns
    -------
    class instance: Batch

    """

    def __init__(self, path):
        self.path = path
        self.invar, self.invar_marg, self.rows = self.read_input()

        self.TC_VARS = [
            "RECID",
            "iitax",
            "payrolltax",
            "e00200",
            "c00100",
            "e02300",
            "c02500",
            "c04470",
            "c04800",
            "c07220",
            "c11070",
            "c07180",
            "eitc",
            "c62100",
            "c09600",
            "niit",
            "c05800",
            "ptax_was",
            "qbided",
        ]

        self.TC_LABELS = [
            "ID",
            "Individual Income Tax",
            "Payroll Tax",
            "Wages",
            "AGI",
            "UI in AGI",
            "OASDI in AGI",
            "Itemized Deductions",
            "Taxable Inc",
            "CTC",
            "CTC Refundable",
            "Child care credit",
            "EITC",
            "AMT Taxable Income",
            "AMT Liability",
            "Net Investment Income Tax",
            "Income Tax Before Credits",
            "FICA",
            "Qualified Business Income Deduction",
        ]

        self.MTR_LABELS = ["Payroll Tax MTR", "Income Tax MTR", "Combined MTR"]

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
            ivar = pd.read_csv(
                self.path, sep=",", engine="python", header=None
            )
        # check that input CSV has 28 columns
        assert len(ivar.columns) == 28
        # check that year is the same across all rows
        assert ivar[1].max() == ivar[1].min()
        rows = len(ivar)
        params = BatchParams()
        # validate input
        params.adjust(ivar)
        array = np.empty((0, rows))
        for label in params._data:
            array = np.append(
                array, [params._data[label]["value"][0]["value"]], axis=0
            )
        params_df = pd.DataFrame(array).transpose()

        params_marg = params_df.copy()
        params_marg.loc[:, 9] = params_marg.loc[:, 9] + FINITE_DIFF

        # translate INPUT variables into OUTPUT variables
        c = cr.Cruncher()
        self.invar = c.translate(params_df)
        self.invar_marg = c.translate(params_marg)
        self.rows = len(self.invar.index)
        return self.invar, self.invar_marg, self.rows

    def create_table(
        self,
        reform_file=None,
        tc_vars=None,
        tc_labels=None,
        include_mtr=True,
        be_sub=0,
        be_inc=0,
        be_cg=0,
    ):
        """
        Creates table of liabilities. Default is current law with no behavioral response
            (i.e. static analysis). User may specify a policy reform which is read and
            implemented below in get_pol() and/or or may specify elasticities for partial-
            equilibrium behavioral responses.

        reform_file: name of a reform file in the Tax-Calculator reforms folder,
            a file path to a custom JSON reform file, or a dictionary with a policy reform.

        tc_vars: list of Tax-Calculator output variables.

        tc_labels: list of labels for output table

        include_mtr: include MTR calculations in output table

        be_sub: Substitution elasticity of taxable income. Defined as proportional change
            in taxable income divided by proportional change in marginal net-of-tax rate
            (1-MTR) on taxpayer earnings caused by the reform.  Must be zero or positive.

        be_inc: Income elasticity of taxable income. Defined as dollar change in taxable
            income divided by dollar change in after-tax income caused by the reform.
            Must be zero or negative.

        be_cg: Semi-elasticity of long-term capital gains. Defined as change in logarithm
            of long-term capital gains divided by change in marginal tax rate (MTR) on
            long-term capital gains caused by the reform.  Must be zero or negative.

        Returns:
            df_res: a Pandas dataframe. Each observation is a separate tax filer
        """
        year = self.invar["FLPDYR"][0]
        year = int(year.item())
        recs = tc.Records(
            data=self.invar,
            start_year=year,
            gfactors=None,
            weights=None,
            adjust_ratios=None,
        )

        # if tc_vars and tc_labels are not specified, defaults are used
        if tc_vars is None:
            tc_vars = self.TC_VARS
        if tc_labels is None:
            tc_labels = self.TC_LABELS

        assert len(tc_vars) > 0
        assert len(tc_vars) == len(tc_labels)

        # if no reform file is passed, table will show current law values
        if reform_file is None:
            pol = tc.Policy()
            assert be_sub == be_inc == be_cg == 0
            calc = tc.Calculator(policy=pol, records=recs)
            calc.advance_to_year(year)
            calc.calc_all()
            calcs = calc.dataframe(tc_vars)
        # if a reform file is passed, table will show reform values
        else:
            pol = self.get_pol(reform_file)
            calc = tc.Calculator(policy=pol, records=recs)
            pol_base = tc.Policy()
            calc_base = tc.Calculator(policy=pol_base, records=recs)
            response_elasticities = {"sub": be_sub, "inc": be_inc, "cg": be_cg}
            _, df2br = br.response(
                calc_base, calc, response_elasticities, dump=True
            )
            calcs = df2br[tc_vars]

        # if include_mtr is True, the tables includes three columns with MTRs
        if include_mtr:
            mtr = self.calc_mtr(reform_file)
            mtr_df = pd.DataFrame(data=mtr).transpose()
            df_res = pd.concat([calcs, mtr_df], axis=1)
            col_labels = tc_labels + self.MTR_LABELS
            df_res.columns = col_labels
            df_res.index = range(self.rows)
        else:
            df_res = calcs
            df_res.columns = tc_labels
            df_res.index = range(self.rows)

        return df_res

    def create_diff_table(
        self,
        reform_file,
        tc_vars=None,
        tc_labels=None,
        include_mtr=True,
        baseline=None,
        be_sub=0,
        be_inc=0,
        be_cg=0,
    ):
        """
        Creates a table that displays differences between baseline and reform. See the above
            docstring for a discussion on the method's arguments.

        NOTE: if a policy other than current law is selected as the baseline policy, behavioral
            responses must remain 0.

        """
        if tc_vars is None:
            tc_vars = self.TC_VARS

        if tc_labels is None:
            tc_labels = self.TC_LABELS

        if baseline is None:
            t_base = self.create_table(
                tc_vars=tc_vars, tc_labels=tc_labels, include_mtr=include_mtr
            )
        else:
            # a behavioral response can only be simulated if the baseline is
            # current law
            assert be_sub == be_inc == be_cg == 0
            t_base = self.create_table(
                baseline, tc_vars, tc_labels, include_mtr
            )
        t_reform = self.create_table(
            reform_file, tc_vars, tc_labels, include_mtr, be_sub, be_inc, be_cg
        )
        df_all = pd.merge(t_reform, t_base, on="ID")
        df_ids = df_all["ID"]
        cols = len(t_base.columns)
        df_diff = df_all.diff(periods=-(cols - 1), axis=1).iloc[:, 1:cols]
        df_diff_id = pd.concat([df_ids, df_diff], axis=1)
        # new column labels that have "Diff" at the end
        diff_labels = ["ID"]

        if include_mtr:
            col_labels = tc_labels + self.MTR_LABELS
        else:
            col_labels = tc_labels

        for label in col_labels:
            if label == "ID":
                pass
            else:
                diff_labels.append(label + " Diff")
        df_diff_id.columns = diff_labels
        return df_diff_id

    def get_pol(self, reform_file):
        """
        Reads the specified reform and implements it
        """

        REFORMS_URL = (
            "https://raw.githubusercontent.com/"
            "PSLmodels/Tax-Calculator/master/taxcalc/reforms/"
        )

        # check to see if file path to reform_file exists
        if isinstance(reform_file, str) and os.path.isfile(reform_file):
            pol = tc.Policy()
            pol.implement_reform(tc.Policy.read_json_reform(reform_file))
        # try reform_file as dictionary
        elif isinstance(reform_file, dict):
            pol = tc.Policy()
            try:
                pol.implement_reform(reform_file)
            except:
                # use adjust method for web app
                pol.adjust(reform_file)
        # if file path does not exist, check Tax-Calculator reforms file
        else:
            try:
                reform_url = REFORMS_URL + reform_file
                pol = tc.Policy()
                pol.implement_reform(tc.Policy.read_json_reform(reform_url))
            except:
                raise "Reform file does not exist"
        return pol

    def calc_mtr(self, reform_file):
        """
        Calculates income tax, payroll tax, and combined marginal rates
        """
        year = self.invar["FLPDYR"][0]
        year = int(year.item())
        recs_base = tc.Records(
            data=self.invar,
            start_year=year,
            gfactors=None,
            weights=None,
            adjust_ratios=None,
        )
        if reform_file is None:
            pol = tc.Policy()
        else:
            pol = self.get_pol(reform_file)

        calc_base = tc.Calculator(policy=pol, records=recs_base)
        calc_base.advance_to_year(year)
        calc_base.calc_all()
        payrolltax_base = calc_base.array("payrolltax")
        incometax_base = calc_base.array("iitax")
        combined_taxes_base = incometax_base + payrolltax_base

        recs_marg = tc.Records(
            data=self.invar_marg,
            start_year=year,
            gfactors=None,
            weights=None,
            adjust_ratios=None,
        )
        calc_marg = tc.Calculator(policy=pol, records=recs_marg)
        calc_marg.advance_to_year(year)
        calc_marg.calc_all()
        payrolltax_marg = calc_marg.array("payrolltax")
        incometax_marg = calc_marg.array("iitax")
        combined_taxes_marg = incometax_marg + payrolltax_marg

        payrolltax_diff = payrolltax_marg - payrolltax_base
        incometax_diff = incometax_marg - incometax_base
        combined_diff = combined_taxes_marg - combined_taxes_base

        mtr_payrolltax = payrolltax_diff / FINITE_DIFF
        mtr_incometax = incometax_diff / FINITE_DIFF
        mtr_combined = combined_diff / FINITE_DIFF

        return (mtr_payrolltax, mtr_incometax, mtr_combined)
