import pytest
import json
import os
import numpy as np
import pandas as pd
import taxcalc as tc
from taxcrunch import cruncher as cr

CURR_PATH = os.path.abspath(os.path.dirname(__file__))
input_path = os.path.join(CURR_PATH, "test_adjustment.json")
reform_path = os.path.join(CURR_PATH, "test_reform.json")
no_reform_path = os.path.join(CURR_PATH, "test_adjustment_noreform.json")


def test_baseline_choice():
    c = cr.Cruncher(baseline=reform_path)
    assert isinstance(c, cr.Cruncher)


def test_reform_choice():
    c = cr.Cruncher(
        inputs=no_reform_path, custom_reform=reform_path
    )
    assert isinstance(c, cr.Cruncher)
    with pytest.raises(AttributeError):
        cr.Cruncher(
            inputs=input_path, custom_reform=reform_path
        )


def test_basic_table(cr_data):
    table = cr_data.basic_table()
    assert isinstance(table, pd.DataFrame)


def test_calc_table(cr_data):
    table = cr_data.calc_table()
    assert isinstance(table, pd.DataFrame)
    assert table.iloc[0]["Reform"] + 1 == table.iloc[0]["+ $1 (Taxpayer Earnings)"]
    table_path = os.path.join(CURR_PATH, "expected_calc_table.csv")
    # table.to_csv(table_path)
    expected_table = pd.read_csv(table_path, index_col=0)
    diffs = False
    for col in table.columns:
        assert np.allclose(table[col], expected_table[col])


def test_mtr_table(cr_data):
    table = cr_data.mtr_table()
    assert isinstance(table, pd.DataFrame)
    assert abs(table.all(axis=None)) < 1
