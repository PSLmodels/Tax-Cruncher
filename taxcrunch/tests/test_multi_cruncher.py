import pytest
import json
import os
import numpy as np
import pandas as pd
import taxcalc as tc
import taxcrunch.cruncher as cr
import taxcrunch.multi_cruncher as mcr

def test_create_data():
    b = mcr.Batch(path="example_test_input.csv")
    assert isinstance(b, mcr.Batch)

def test_get_pol_no_reform():
    b = mcr.Batch(path="example_test_input.csv")
    m = b.get_pol(reform_file=None)
    assert isinstance(m,tc.Policy)

def test_get_pol_directory_file():
    b = mcr.Batch(path="example_test_input.csv")
    # use the full file pathname for testing purposes
    local_reform = "/Users/phillipsmclaughlin/Tax-Cruncher/taxcrunch/tests/test_reform.json"
    n = b.get_pol(reform_file=local_reform)
    assert n._CTC_c[2018-2013] == 1000

reform_dict = {
    "CTC_c": {2013: 1300, 2018: 1800}
    }

def test_get_pol_dict():
    b = mcr.Batch(path="example_test_input.csv")
    m = b.get_pol(reform_file=reform_dict)
    assert m._CTC_c[2018-2013] == 1800

def test_get_pol_link():
    b = mcr.Batch(path="example_test_input.csv")
    reform_preset = "Trump2016.json"
    m = b.get_pol(reform_file=reform_preset)
    assert m._II_rt1[2017-2013] == 0.12








        



