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

def create_data():
    c = cr.Cruncher(inputs=input_path)
    return c


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


def test_basic_table():
    c = create_data()
    table = c.basic_table()
    assert isinstance(table, pd.DataFrame)


def test_calc_table():
    c = create_data()
    table = c.calc_table()
    assert isinstance(table, pd.DataFrame)
    assert table.iloc[0]["Reform"] + 1 == table.iloc[0]["+ $1 (Taxpayer Earnings)"]
    # table.to_csv("expected_calc_table.csv")
    expected_table = pd.read_csv(
        os.path.join(CURR_PATH, "expected_calc_table.csv"), index_col=0
    )
    diffs = False
    for col in table.columns:
        assert np.allclose(table[col], expected_table[col])


def test_mtr_table():
    c = create_data()
    table = c.mtr_table()
    assert isinstance(table, pd.DataFrame)
    assert abs(table.all(axis=None)) < 1
