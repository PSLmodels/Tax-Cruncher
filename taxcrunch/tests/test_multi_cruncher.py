import pytest
import json
import os
import numpy as np
import pandas as pd
import taxcalc as tc
import taxcrunch.cruncher as cr
import taxcrunch.multi_cruncher as mcr

CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))

input_path = os.path.join(CURRENT_PATH, "example_test_input.csv")
reform_path = os.path.join(CURRENT_PATH, "test_reform.json")
b = mcr.Batch(input_path)

reform_dict = {
    "CTC_c": {2013: 1300, 2018: 1800}
    }

def test_read_input(crunch=b):
    
    invar, invar_marg, rows = b.read_input()
    assert isinstance(invar, pd.DataFrame)
    assert isinstance(rows, int)

    # check that number of input rows matches output rows
    assert rows == len(b.create_table().index)

def test_get_pol_directory_file(crunch=b):

    n = b.get_pol(reform_file=reform_path) 
    assert n._CTC_c[2018-2013] == 1000

def test_get_pol_dict(crunch=b):
    
    m = b.get_pol(reform_file=reform_dict)
    assert m._CTC_c[2018-2013] == 1800

def test_get_pol_link(crunch=b):
    
    reform_preset = "Trump2016.json"
    m = b.get_pol(reform_file=reform_preset)
    assert m._II_rt1[2017-2013] == 0.12

CURR_PATH = os.path.abspath(os.path.dirname(__file__))

def test_calc_table(crunch=b):
    
    table = b.create_table()
    assert isinstance(table, pd.DataFrame)
    # table.to_csv("expected_multi_table.csv")
    expected_table = pd.read_csv(
        os.path.join(CURR_PATH, "expected_multi_table.csv"), index_col=0
    )
    for col in table.columns:
        assert np.allclose(table[col], expected_table[col])

def test_create_table_behresp_args(crunch=b):
    
    table = b.create_table(reform_file=reform_dict, be_sub=0.25)
    assert isinstance(table, pd.DataFrame)

    # be_sub must be positive
    with pytest.raises(AssertionError):
        b.create_table(reform_file=reform_dict, be_sub=-0.25)

    # can only specify response if there is a reform
    with pytest.raises(AssertionError):
        b.create_table(be_sub=0.25)

def test_diff_tables(crunch=b):

    table = b.create_diff_table(reform_file=reform_dict)
    assert isinstance(table,pd.DataFrame)

    # can only specify response if there is a reform
    with pytest.raises(AssertionError):
        b.create_diff_table(reform_file=None, be_sub=0.25)

    # baseline must be current law if response
    with pytest.raises(AssertionError):
        b.create_diff_table(reform_file="Trump2016.json", baseline=reform_dict, be_sub=0.25)
