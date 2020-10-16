import pytest
import os
import numpy as np
import pandas as pd
import taxcrunch.multi_cruncher as mcr

CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))


def test_a18_validation():
    taxcrunch_in = os.path.join(CURRENT_PATH, "taxsim_validation/taxcrunch_in_a18.csv")
    crunch = mcr.Batch(taxcrunch_in)
    table_a18 = crunch.create_table()

    taxsim_out = os.path.join(CURRENT_PATH, "taxsim_validation/taxsim_out_a18.csv")
    taxsim_df = pd.read_csv(taxsim_out)

    taxcrunch_frate = table_a18["Income Tax MTR"]*100

    assert np.allclose(table_a18["Individual Income Tax"], taxsim_df["fiitax"], atol=0.01)
    assert np.allclose(table_a18["Payroll Tax"], taxsim_df["fica"], atol=0.01)
    assert np.allclose(taxcrunch_frate, taxsim_df["frate"], atol=0.01)

def test_c18_validation():
    taxcrunch_in = os.path.join(CURRENT_PATH, "taxsim_validation/taxcrunch_in_c18.csv")
    crunch = mcr.Batch(taxcrunch_in)
    emulation = os.path.join(CURRENT_PATH, "taxsim_validation/taxsim_emulation.json")
    table_c18 = crunch.create_table(reform_file=emulation)

    taxsim_out = os.path.join(CURRENT_PATH, "taxsim_validation/taxsim_out_c18.csv")
    taxsim_df = pd.read_csv(taxsim_out)

    taxcrunch_frate = table_c18["Income Tax MTR"]*100

    assert np.allclose(table_c18["Individual Income Tax"], taxsim_df["fiitax"], atol=.01)
    assert np.allclose(table_c18["Payroll Tax"], taxsim_df["fica"], atol=0.01)
    assert np.allclose(taxcrunch_frate, taxsim_df["frate"], atol=0.01)
