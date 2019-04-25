import json
import os
import numpy as np
import pandas as pd
import taxcalc as tc

from paramtools import Parameters

CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))


class CruncherParams(Parameters):

    defaults = os.path.join(CURRENT_PATH, "defaults.json")


class Cruncher:
    def __init__(self, file="adjustment_template.json", custom_reform=None):
        self.file = file
        self.custom_reform = custom_reform
        self.params = CruncherParams()
        self.adjustment = self.adjust_file()
        self.params.adjust(self.adjustment)
        self.ivar, self.mtr_options, self.reform_options = self.taxsim_inputs()
        self.data = self.translate(self.ivar)
        self.ivar2, self.mtr_wrt = self.choose_mtr()
        self.data_mtr = self.translate(self.ivar2)
        self.pol2 = self.choose_reform()
        self.calc1, self.calc_reform, self.calc_mtr = self.run_calc()
        self.df_basic_vals = self.basic_vals()
        self.df_mtr = self.mtr_table()
        self.zero_brk = self.zero_bracket()
        self.df_calc = self.calc_table()

    def adjust_file(self):
        """
        Alter inputs in adjustment_template.json or create your own adjustment file
        """
        CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))
        self.adjustment = os.path.join(CURRENT_PATH, self.file)
        return self.adjustment

    def taxsim_inputs(self):
        """
        Iterates through params object to extract parameter values

        Returns:
        ivar: a Pandas dataframe with Taxsim-style variables
        mtr_options: a string with the user's choice of how to calculate marginal tax rates
        reform_options: a string with the user's choice of reform

        """
        for param in self.params.RECID:
            RECID = param["value"]
        for param in self.params.year:
            year = param["value"]
        for param in self.params.mstat:
            mstat = param["value"]
        for param in self.params.page:
            page = param["value"]
        for param in self.params.sage:
            sage = param["value"]
        for param in self.params.depx:
            depx = param["value"]
        for param in self.params.dep13:
            dep13 = param["value"]
        for param in self.params.dep17:
            dep17 = param["value"]
        for param in self.params.dep18:
            dep18 = param["value"]
        for param in self.params.pwages:
            pwages = param["value"]
        for param in self.params.swages:
            swages = param["value"]
        for param in self.params.dividends:
            dividends = param["value"]
        for param in self.params.intrec:
            intrec = param["value"]
        for param in self.params.stcg:
            stcg = param["value"]
        for param in self.params.ltcg:
            ltcg = param["value"]
        for param in self.params.otherprop:
            otherprop = param["value"]
        for param in self.params.nonprop:
            nonprop = param["value"]
        for param in self.params.pensions:
            pensions = param["value"]
        for param in self.params.gssi:
            gssi = param["value"]
        for param in self.params.ui:
            ui = param["value"]
        for param in self.params.proptax:
            proptax = param["value"]
        for param in self.params.otheritem:
            otheritem = param["value"]
        for param in self.params.childcare:
            childcare = param["value"]
        for param in self.params.mortgage:
            mortgage = param["value"]
        for param in self.params.mtr_options:
            self.mtr_options = param["value"]
        for param in self.params.reform_options:
            self.reform_options = param["value"]

        ts_vars = [
            RECID,
            year,
            mstat,
            page,
            sage,
            depx,
            dep13,
            dep17,
            dep18,
            pwages,
            swages,
            dividends,
            intrec,
            stcg,
            ltcg,
            otherprop,
            nonprop,
            pensions,
            gssi,
            ui,
            proptax,
            otheritem,
            childcare,
            mortgage,
        ]

        ts_values = []
        for ts_var in ts_vars:
            ts_values.append(ts_var)

        array_var = np.asarray(ts_values)
        self.ivar = pd.DataFrame(array_var.reshape(1, len(array_var)))
        self.ivar = self.ivar.astype(int)
        return self.ivar, self.mtr_options, self.reform_options

    def translate(self, ivar):
        """
        Translate TAXSIM-27 input variables into Tax-Calculator input variables.
        Both ivar and returned invar are pandas DataFrame objects.
        """
        self.invar = pd.DataFrame()
        self.invar["RECID"] = ivar.loc[:, 0]
        self.invar["FLPDYR"] = ivar.loc[:, 1]
        # no Tax-Calculator use of TAXSIM variable 3, state code
        mstat = self.ivar.loc[:, 2]
        self.invar["age_head"] = ivar.loc[:, 3]
        self.invar["age_spouse"] = ivar.loc[:, 4]
        num_deps = ivar.loc[:, 5]
        mars = np.where(mstat == 1, np.where(num_deps > 0, 4, 1), 2)
        self.invar["MARS"] = mars
        self.invar["f2441"] = ivar.loc[:, 6]
        self.invar["n24"] = ivar.loc[:, 7]
        num_eitc_qualified_kids = ivar.loc[:, 8]
        self.invar["EIC"] = np.minimum(num_eitc_qualified_kids, 3)
        num_taxpayers = np.where(mars == 2, 2, 1)
        self.invar["XTOT"] = num_taxpayers + num_deps
        self.invar["e00200p"] = ivar.loc[:, 9]
        self.invar["e00200s"] = ivar.loc[:, 10]
        self.invar["e00200"] = self.invar["e00200p"] + self.invar["e00200s"]
        self.invar["e00650"] = ivar.loc[:, 11]
        self.invar["e00300"] = ivar.loc[:, 12]
        self.invar["p22250"] = ivar.loc[:, 13]
        self.invar["p23250"] = ivar.loc[:, 14]
        nonqualified_dividends = ivar.loc[:, 15]
        self.invar["e00600"] = self.invar["e00650"] + nonqualified_dividends
        self.invar["e00800"] = ivar.loc[:, 16]
        self.invar["e01700"] = ivar.loc[:, 17]
        self.invar["e01500"] = self.invar["e01700"]
        self.invar["e02400"] = ivar.loc[:, 18]
        self.invar["e02300"] = ivar.loc[:, 19]
        # no Tax-Calculator use of TAXSIM variable 22, non-taxable transfers
        # no Tax-Calculator use of TAXSIM variable 23, rent paid
        self.invar["e18500"] = ivar.loc[:, 20]
        self.invar["e18400"] = ivar.loc[:, 21]
        self.invar["e32800"] = ivar.loc[:, 22]
        self.invar["e19200"] = ivar.loc[:, 23]
        return self.invar

    def choose_mtr(self):
        """
        Creates data to analyze MTR

        Returns:
        ivar2: a Pandas dataframe with Taxsim-style variables
        mtr_wrt: User's choice for MTR analysis as a Tax-Calculator variable
        """
        self.ivar2 = self.ivar.copy()
        if self.mtr_options == "Taxpayer Earnings":
            self.ivar2.loc[:, 9] = self.ivar2.loc[:, 9] + 1
            self.mtr_wrt = "e00200p"
            return self.ivar2, self.mtr_wrt
        elif self.mtr_options == "Spouse Earnings":
            self.ivar2.loc[:, 10] = self.ivar2.loc[:, 10] + 1
            return self.ivar2, "e00200s"
        elif self.mtr_options == "Short Term Gains":
            self.ivar2.loc[:, 13] = self.ivar2.loc[:, 13] + 1
            return self.ivar2, "p22250"
        elif self.mtr_options == "Long Term Gains":
            self.ivar2.loc[:, 14] = self.ivar2.loc[:, 14] + 1
            return self.ivar2, "p23250"
        elif self.mtr_options == "Qualified Dividends":
            self.ivar2.loc[:, 11] = self.ivar2.loc[:, 11] + 1
            return self.ivar2, "e00650"
        elif self.mtr_options == "Interest Received":
            self.ivar2.loc[:, 12] = self.ivar2.loc[:, 12] + 1
            return self.ivar2, "e00300"
        elif self.mtr_options == "Pensions":
            self.ivar2.loc[:, 17] = self.ivar2.loc[:, 17] + 1
            return self.ivar2, "e01700"
        elif self.mtr_options == "Gross Social Security Beneifts":
            self.ivar2.loc[:, 18] = self.ivar2.loc[:, 18] + 1
            return self.ivar2, "e02400"
        elif self.mtr_options == "Real Estate Taxes Paid":
            self.ivar2.loc[:, 20] = self.ivar2.loc[:, 20] + 1
            return self.ivar2, "e18500"
        elif mtr_options == "Mortgage":
            self.ivar2.loc[:, 23] = self.ivar2.loc[:, 23] + 1
            return self.ivar2, "e19200"
        elif self.mtr_options == "Don't Bother":
            return self.ivar2, "None"

    def choose_reform(self):
        """
        Creates Tax-Calculator Policy object for reform analysis
        User can choose any reform in taxcalc/reforms folder

        Returns:
        pol2: Tax-Calculator Policy object for reform analysis 
        """
        REFORMS_URL = (
            "https://raw.githubusercontent.com/"
            "PSLmodels/Tax-Calculator/master/taxcalc/reforms/"
        )

        if self.reform_options == "None":
            self.pol2 = tc.Policy()
        elif self.reform_options == "Custom":
            reform_filename = self.custom_reform
            reform = tc.Calculator.read_json_param_objects(reform_filename, None)
            self.pol2 = tc.Policy()
            self.pol2.implement_reform(reform["policy"])
        else:
            reform_name = self.reform_options
            reform_url = REFORMS_URL + reform_name
            reform = tc.Calculator.read_json_param_objects(reform_url, None)
            self.pol2 = tc.Policy()
            self.pol2.implement_reform(reform["policy"])
        return self.pol2

    def run_calc(self):
        """
        Creates baseline, reform, and + $1 Tax-Calculator objects

        Returns:
        calc1: Calculator object for current law
        calc_reform: Calculator object for reform
        calc_mtr: Calculator object for + $1
        """

        year = self.data.iloc[0][1]
        year = year.item()
        recs = tc.Records(data=self.data, start_year=year)
        pol = tc.Policy()

        self.calc1 = tc.Calculator(policy=pol, records=recs)
        self.calc1.calc_all()

        self.calc_reform = tc.Calculator(policy=self.pol2, records=recs)
        self.calc_reform.calc_all()

        recs_mtr = tc.Records(data=self.data_mtr, start_year=year)
        self.calc_mtr = tc.Calculator(policy=self.pol2, records=recs_mtr)
        self.calc_mtr.calc_all()

        return self.calc1, self.calc_reform, self.calc_mtr

    def basic_vals(self):
        """
        Creates basic output table

        Returns:
        basic_vals: a Pandas dataframe with basic results
        """

        basic = ["iitax", "payrolltax"]
        basic_vals1 = self.calc1.dataframe(basic)
        basic_vals1 = basic_vals1.transpose()

        basic_vals2 = self.calc_reform.dataframe(basic)
        basic_vals2 = basic_vals2.transpose()

        self.basic_vals = pd.concat([basic_vals1, basic_vals2], axis=1)
        self.basic_vals.columns = ["Base", "Reform"]
        self.basic_vals.index = ["Individual Income Tax", "Payroll Tax"]

        self.basic_vals["Change"] = self.basic_vals["Reform"] - self.basic_vals["Base"]

        self.basic_vals = self.basic_vals.round(2)

        return self.basic_vals

    def mtr_table(self):
        """
        Creates MTR table

        Returns:
        df_mtr: a Pandas dataframe MTR results with respect to mtr_options
        """
        if self.mtr_options != "Don't Bother":

            mtr_calc = self.calc1.mtr(
                variable_str=self.mtr_wrt, wrt_full_compensation=False
            )
            self.mtr_df = pd.DataFrame(
                data=[mtr_calc[1], mtr_calc[0]],
                index=["Income Tax MTR", "Payroll Tax MTR"],
            )

            mtr_calc_reform = self.calc_reform.mtr(
                variable_str=self.mtr_wrt, wrt_full_compensation=False
            )
            mtr_df_reform = pd.DataFrame(
                data=[mtr_calc_reform[1], mtr_calc_reform[0]],
                index=["Income Tax MTR", "Payroll Tax MTR"],
            )

            self.df_mtr = pd.concat([self.mtr_df, mtr_df_reform], axis=1)
            self.df_mtr.columns = ["Base", "Reform"]

            self.df_mtr["Change"] = self.df_mtr["Reform"] - self.df_mtr["Base"]

            return self.df_mtr

        else:
            pass

    def basic_table(self):
        self.df_basic = pd.concat(
            [
                self.df_basic_vals.iloc[:1],
                self.df_mtr.iloc[:1],
                self.df_basic_vals.iloc[1:],
                self.df_mtr.iloc[1:],
            ]
        )
        self.df_basic = self.df_basic.round(2)
        return self.df_basic

    def zero_bracket(self):
        """
        Calculates the variable 'Zero Bracket Amount' by subtracting taxable income from income

        Returns:
        zero_brk: a Pandas dataframe with 'Zero Bracket Amount'
        zero_brk_mtr: a Pandas dataframe with 'Zero Bracket Amount'. 
            Includes column for + $1 analysis
        """
        ii1 = self.calc1.array("e00200")
        taxable1 = self.calc1.array("c04800")
        zero_brk1 = ii1 - taxable1

        ii2 = self.calc_reform.array("e00200")
        taxable2 = self.calc_reform.array("c04800")
        zero_brk2 = ii2 - taxable2

        ii3 = self.calc_mtr.array("e00200")
        taxable3 = self.calc_mtr.array("c04800")
        zero_brk3 = ii3 - taxable3

        if self.mtr_options == "Don't Bother":
            self.zero_brk = np.concatenate((zero_brk1, zero_brk2))
            self.zero_brk = pd.DataFrame(self.zero_brk).transpose()
            self.zero_brk.columns = ["Base", "Reform"]
            self.zero_brk.index = ["Zero Bracket Amount"]
            return self.zero_brk
        else:
            self.zero_brk = np.concatenate((zero_brk1, zero_brk2, zero_brk3))
            self.zero_brk = pd.DataFrame(self.zero_brk).transpose()
            self.zero_brk.columns = ["Base", "Reform", "+ $1"]
            self.zero_brk.index = ["Zero Bracket Amount"]
            return self.zero_brk

    def calc_table(self):
        """
        Creates federal tax calculation table

        Returns:
        df_calc: a Pandas dataframe with federal tax calculations for base, reform, and + $1

        """
        calculation = [
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

        df_calc1 = self.calc1.dataframe(calculation).transpose()

        df_calc2 = self.calc_reform.dataframe(calculation).transpose()

        df_calc_mtr = self.calc_mtr.dataframe(calculation).transpose()

        if self.mtr_options == "Don't Bother":
            self.df_calc = pd.concat([df_calc1, df_calc2], axis=1)
            self.df_calc.columns = ["Base", "Reform"]
            self.df_calc.index = labels
            self.df_calc = pd.concat(
                [self.df_calc.iloc[:3], self.zero_brk, self.df_calc.iloc[3:]]
            )
        else:
            self.df_calc = pd.concat([df_calc1, df_calc2, df_calc_mtr], axis=1)
            self.df_calc.columns = ["Base", "Reform", "+ $1"]
            self.df_calc.index = labels
            self.df_calc = pd.concat(
                [self.df_calc.iloc[:3], self.zero_brk, self.df_calc.iloc[3:]]
            )

        self.df_calc = self.df_calc.round(2)

        return self.df_calc

    def calc_diff_table(self):
        self.calc_diff_table = self.df_calc.copy()
        if len(self.calc_diff_table.columns) == 3:
            del self.calc_diff_table["+ $1"]
        calc_diff_vals = self.calc_diff_table["Reform"] - self.calc_diff_table["Base"]
        self.calc_diff_table["Change"] = calc_diff_vals
        return self.calc_diff_table
