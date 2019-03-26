import json
import argparse
import os
import sys
import numpy as np
import pandas as pd
import taxcalc as tc

from paramtools import Parameters

CURRENT_PATH = os.path.abspath(os.path.dirname('/Users/petermetz/taxsim-app/taxsim.py'))
REFORMS_URL = ('https://raw.githubusercontent.com/'
               'PSLmodels/Tax-Calculator/master/taxcalc/reforms/')

class TaxsimParams(Parameters):
    schema = os.path.join(CURRENT_PATH, "schema.json")
    defaults = os.path.join(CURRENT_PATH, "defaults.json")
    
def get_inputs():
    params = TaxsimParams()
    spec = params.specification(meta_data=True)
    return {"filer": spec}

params = TaxsimParams()

def parse_inputs(inputs, jsonparams, errors_warnings):
    adjustments = inputs["filer"]
    params = TaxsimParams()
    params.adjust(adjustments, raise_errors=False)
    errors_warnings["filer"]["errors"].update(params.errors)
    return (inputs, {"filer": json.dumps(inputs, indent=4)}, errors_warning)

def taxsim_inputs(params):
    """
    Iterates through params object to extract parameter values
    
    Returns:
    ivar: a Pandas dataframe with Taxsim-style variables
    mtr_options: a string with the user's choice of how to calculate marginal tax rates
    reform_options: a string with the user's choice of reform
    
    """
    for param in params.taxsimid:
        taxsimid = param['value']
    for param in params.year:
        year = param['value']
    for param in params.SOI:
        state = param['value']
    for param in params.mstat:
        mstat = param['value']
    for param in params.page:
        page = param['value']
    for param in params.sage:
        sage = param['value']
    for param in params.depx:
        depx = param['value']
    for param in params.dep13:
        dep13 = param['value']
    for param in params.dep17:
        dep17 = param['value']
    for param in params.dep18:
        dep18 = param['value']
    for param in params.pwages:
        pwages = param['value']
    for param in params.swages:
        swages = param['value']
    for param in params.dividends:
        dividends = param['value']
    for param in params.intrec:
        intrec = param['value']
    for param in params.stcg:
        stcg = param['value']
    for param in params.ltcg:
        ltcg = param['value']
    for param in params.otherprop:
        otherprop = param['value']
    for param in params.nonprop:
        nonprop = param['value']
    for param in params.pensions:
        pensions = param['value']
    for param in params.gssi:
        gssi = param['value']
    for param in params.ui:
        ui = param['value']
    for param in params.transfers:
        transfers = param['value']
    for param in params.rentpaid:
        rentpaid = param['value']
    for param in params.proptax:
        proptax = param['value']
    for param in params.otheritem:
        otheritem = param['value']
    for param in params.childcare:
        childcare = param['value']
    for param in params.mortgage:
        mortgage = param['value']
    for param in params.mtr_options:
        mtr_options = param['value']
    for param in params.reform_options:
        reform_options = param['value']

    ts_vars = [taxsimid, year, state, mstat, page, sage, depx, 
                  dep13, dep17, dep18, pwages, swages, dividends, 
                  intrec, stcg, ltcg, otherprop, nonprop, pensions,
                  gssi, ui, transfers, rentpaid, proptax, otheritem,
                  childcare, mortgage]

    ts_values = []
    for ts_var in ts_vars:
        ts_values.append(ts_var)

    array_var = np.asarray(ts_values)
    ivar = pd.DataFrame(array_var.reshape(1, len(array_var)))
    ivar = ivar.astype(int)
    return ivar, mtr_options, reform_options

ivar, mtr_options, reform_options = taxsim_inputs(params)

def translate(ivar):
    """
    Translate TAXSIM-27 input variables into Tax-Calculator input variables.
    Both ivar and returned invar are pandas DataFrame objects.
    """
    assert isinstance(ivar, pd.DataFrame)
    invar = pd.DataFrame()
    invar['RECID'] = ivar.loc[:, 0]
    invar['FLPDYR'] = ivar.loc[:, 1]
    # no Tax-Calculator use of TAXSIM variable 3, state code
    mstat = ivar.loc[:, 3]
    invar['age_head'] = ivar.loc[:, 4]
    invar['age_spouse'] = ivar.loc[:, 5]
    num_deps = ivar.loc[:, 6]
    mars = np.where(mstat == 1, np.where(num_deps > 0, 4, 1), 2)
    invar['MARS'] = mars
    invar['f2441'] = ivar.loc[:, 7]
    invar['n24'] = ivar.loc[:, 8]
    num_eitc_qualified_kids = ivar.loc[:, 9]
    invar['EIC'] = np.minimum(num_eitc_qualified_kids, 3)
    num_taxpayers = np.where(mars == 2, 2, 1)
    invar['XTOT'] = num_taxpayers + num_deps
    invar['e00200p'] = ivar.loc[:, 10]
    invar['e00200s'] = ivar.loc[:, 11]
    invar['e00200'] = invar['e00200p'] + invar['e00200s']
    invar['e00650'] = ivar.loc[:, 12]
    invar['e00300'] = ivar.loc[:, 13]
    invar['p22250'] = ivar.loc[:, 14]
    invar['p23250'] = ivar.loc[:, 15]
    nonqualified_dividends = ivar.loc[:, 16]
    invar['e00600'] = invar['e00650'] + nonqualified_dividends
    invar['e00800'] = ivar.loc[:, 17]
    invar['e01700'] = ivar.loc[:, 18]
    invar['e01500'] = invar['e01700']
    invar['e02400'] = ivar.loc[:, 19]
    invar['e02300'] = ivar.loc[:, 20]
    # no Tax-Calculator use of TAXSIM variable 22, non-taxable transfers
    # no Tax-Calculator use of TAXSIM variable 23, rent paid
    invar['e18500'] = ivar.loc[:, 23]
    invar['e18400'] = ivar.loc[:, 24]
    invar['e32800'] = ivar.loc[:, 25]
    invar['e19200'] = ivar.loc[:, 26]
    return invar

data = translate(ivar)

def choose_mtr(ivar, mtr_options):
    """
    Creates data to analyze MTR
    
    Returns:
    ivar2: a Pandas dataframe with Taxsim-style variables
    mtr_wrt: User's choice for MTR analysis as a Tax-Calculator variable
    """
    ivar2 = ivar.copy()
    if mtr_options == "Taxpayer Earnings":
        ivar2.loc[:, 10] = ivar2.loc[:, 10] + 1
        return ivar2, 'e00200p'
    elif mtr_options == "Spouse Earnings":
        ivar2.loc[:, 11] = ivar2.loc[:, 11] + 1
        return ivar2, 'e00200s'
    elif mtr_options == "Short Term Gains":
        ivar2.loc[:, 15] = ivar2.loc[:, 14] + 1
        return ivar2, 'p22250'    
    elif mtr_options == "Long Term Gains":
        ivar2.loc[:, 15] = ivar2.loc[:, 15] + 1
        return ivar2, 'p23250' 
    elif mtr_options == "Qualified Dividends":
        ivar2.loc[:, 12] = ivar2.loc[:, 12] + 1
        return ivar2, 'e00650'
    elif mtr_options == "Interest Received":
        ivar2.loc[:, 13] = ivar2.loc[:, 13] + 1
        return ivar2, 'e00300'
    elif mtr_options == "Pensions":
        ivar2.loc[:, 18] = ivar2.loc[:, 18] + 1
        return ivar2, 'e01700'
    elif mtr_options == "Gross Social Security Beneifts":
        ivar2.loc[:, 19] = ivar2.loc[:, 19] + 1
        return ivar2, 'e02400'
    elif mtr_options == "Real Estate Taxes Paid":
        ivar2.loc[:, 23] = ivar2.loc[:, 23] + 1
        return ivar2, 'e18500'
    elif mtr_options == "Mortgage":
        ivar2.loc[:, 26] = ivar2.loc[:, 26] + 1
        return ivar2, 'e19200'
    elif mtr_options == "Don't Bother":
        return ivar2, 'None'
    
ivar2, mtr_wrt = choose_mtr(ivar, mtr_options)
data_mtr = translate(ivar2)

def choose_reform(reform_options, REFORMS_URL):
    """
    Creates Tax-Calculator Policy object for reform analysis
    User can choose any reform in taxcalc/reforms folder
    
    Returns:
    pol2: Tax-Calculator Policy object for reform analysis 
    """
    if reform_options != "None":
        reform_name = reform_options
        reform_url = REFORMS_URL + reform_name
        reform = tc.Calculator.read_json_param_objects(reform_url, None)
        pol2 = tc.Policy()
        pol2.implement_reform(reform['policy'])
    else:
        pol2 = tc.Policy()
    return pol2

pol2 = choose_reform(reform_options, REFORMS_URL)

def run_calc(data, pol2, data_mtr):
    """
    Creates baseline, reform, and + $1 Tax-Calculator objects
    
    Returns:
    calc1: Calculator object for current law
    calc_reform: Calculator object for reform
    calc_mtr: Calculator object for + $1
    """
    
    year = data.iloc[0][1]
    year = year.item()
    recs = tc.Records(data=data, start_year=year)
    pol = tc.Policy()
    
    calc1 = tc.Calculator(policy=pol, records=recs)
    calc1.calc_all()
    
    calc_reform = tc.Calculator(policy=pol2, records=recs)
    calc_reform.calc_all()
    
    recs_mtr = tc.Records(data=data_mtr, start_year=year)
    calc_mtr = tc.Calculator(policy=pol2, records=recs_mtr)
    calc_mtr.calc_all()
    
    return calc1, calc_reform, calc_mtr

calc1, calc_reform, calc_mtr = run_calc(data, pol2, data_mtr)

def basic_vals(calc1, calc_reform):
    """
    Creates basic output table
    
    Returns:
    basic_vals: a Pandas dataframe with basic results
    """
    
    basic = ['iitax', 'payrolltax']
    basic_vals1 = calc1.dataframe(basic)
    basic_vals1 = basic_vals1.transpose()

    basic_vals2 = calc_reform.dataframe(basic)
    basic_vals2 = basic_vals2.transpose()


    basic_vals = pd.concat([basic_vals1, basic_vals2], axis=1)
    basic_vals.columns = ['Base', 'Reform']
    basic_vals.index = ['Individual Income Tax', 'Payroll Tax']
    
    basic_vals['Change'] = basic_vals['Reform'] - basic_vals['Base']
    
    basic_vals = basic_vals.round(2)

    return basic_vals

basic_vals = basic_vals(calc1, calc_reform)

def mtr_table(ivar, mtr_options, calc1, calc_reform):
    """
    Creates MTR table
    
    Returns:
    df_basic: a Pandas dataframe MTR results with respect to mtr_options
    """
    if mtr_options != "Don't Bother":
    
        mtr_calc = calc1.mtr(variable_str=mtr_wrt, wrt_full_compensation=False)
        mtr_df = pd.DataFrame(data=[mtr_calc[1],mtr_calc[0]], index=['Income Tax MTR', 'Payroll Tax MTR'])

        mtr_calc_reform = calc_reform.mtr(variable_str=mtr_wrt, wrt_full_compensation=False)
        mtr_df_reform = pd.DataFrame(data=[mtr_calc_reform[1],mtr_calc_reform[0]], index=['Income Tax MTR', 'Payroll Tax MTR'])

        df_mtr = pd.concat([mtr_df, mtr_df_reform], axis=1)
        df_mtr.columns = ['Base', 'Reform']
        
        df_mtr['Change'] = df_mtr['Reform'] - df_mtr['Base']

        return df_mtr
    
    else:
        pass

mtr_table = mtr_table(ivar, mtr_options, calc1, calc_reform)

def basic_table(basic_vals, mtr_table):
    df_basic = pd.concat([basic_vals.iloc[:1], df_mtr.iloc[:1], basic_vals.iloc[1:], df_mtr.iloc[1:]])
    df_basic = df_basic.round(2)
    return df_basic

def zero_bracket(calc1, calc_reform, calc_mtr):
    """
    Calculates the variable 'Zero Bracket Amount' by subtracting taxable income from income
    
    Returns:
    zero_brk: a Pandas dataframe with 'Zero Bracket Amount'
    zero_brk_mtr: a Pandas dataframe with 'Zero Bracket Amount'. 
        Includes column for + $1 analysis
    """
    ii1 = calc1.array('e00200')
    taxable1 = calc1.array('c04800')
    zero_brk1 = ii1 - taxable1

    ii2 = calc_reform.array('e00200')
    taxable2 = calc_reform.array('c04800')
    zero_brk2 = ii2 - taxable2

    ii3 = calc_mtr.array('e00200')
    taxable3 = calc_mtr.array('c04800')
    zero_brk3 = ii3 - taxable3

    if mtr_options == "Don't Bother":
        zero_brk = np.concatenate((zero_brk1, zero_brk2))
        zero_brk = pd.DataFrame(zero_brk).transpose()
        zero_brk.columns = ['Base', 'Reform']
        zero_brk.index = ['Zero Bracket Amount']
        return zero_brk
    else:
        zero_brk = np.concatenate((zero_brk1, zero_brk2, zero_brk3))
        zero_brk = pd.DataFrame(zero_brk).transpose()
        zero_brk.columns = ['Base', 'Reform', '+ $1']
        zero_brk.index = ['Zero Bracket Amount']
        return zero_brk
    

zero_brk = zero_bracket(calc1, calc_reform, calc_mtr)

def calc_table(calc1, calc_reform, calc_mtr, mtr_options, zero_brk):
    """
    Creates federal tax calculation table
    
    Returns:
    df_calc: a Pandas dataframe with federal tax calculations for base, reform, and + $1
    
    """
    calculation = ['c00100', 'e02300', 'c02500', 'c04470', 
                   'c04800', 'c05200', 'c07220', 'c11070', 'niit', 'c07100', 'c09600',
                   'eitc', 'taxbc', 'ptax_was']
    labels = ['AGI', 'UI in AGI', 'OASDI in AGI', 'Itemized Deductions',
                   'Taxable Inc', 'Regular Tax', 'CTC', 'CTC Refundable', 'Child care credit', 'AMT',
                    'EITC', 'Net Investment Income Tax', 'Income Tax Before Credits', 'FICA']

    df_calc1 = calc1.dataframe(calculation).transpose()

    df_calc2 = calc_reform.dataframe(calculation).transpose()

    df_calc_mtr = calc_mtr.dataframe(calculation).transpose()

    if mtr_options == "Don't Bother":
        df_calc = pd.concat([df_calc1, df_calc2], axis=1)
        df_calc.columns = ['Base', 'Reform']
        df_calc.index = labels
        df_calc = pd.concat([df_calc.iloc[:3], zero_brk, df_calc.iloc[3:]])
    else:
        df_calc = pd.concat([df_calc1, df_calc2, df_calc_mtr], axis=1)
        df_calc.columns = ['Base', 'Reform', '+ $1']
        df_calc.index = labels
        df_calc = pd.concat([df_calc.iloc[:3], zero_brk, df_calc.iloc[3:]])
        
    df_calc = df_calc.round(2)    

    return df_calc

calc_table = calc_table(calc1, calc_reform, calc_mtr, mtr_options, zero_brk)

def calc_diff_table(calc_table):
    calc_diff_table = calc_table.copy()
    if len(calc_diff_table.columns) == 3:
        del calc_diff_table['+ $1']
    calc_diff_vals = calc_diff_table['Reform'] - calc_diff_table['Base']
    calc_diff_table['Change'] = calc_diff_vals
    return calc_diff_table
