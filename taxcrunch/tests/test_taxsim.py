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

    assert np.allclose(table_a18["Individual Income Tax"], taxsim_df["fiitax"], atol=1)
    assert np.allclose(table_a18["Payroll Tax"], taxsim_df["fica"], atol=1)
