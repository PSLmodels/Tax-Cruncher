import pytest
import pandas as pd
import numpy as np
import os
from taxcrunch import cruncher as cr

CURR_PATH = os.path.abspath(os.path.dirname(__file__))
input_path = os.path.join(CURR_PATH, "test_adjustment.json")


@pytest.fixture(scope="session")
def cr_data():
    return cr.Cruncher(inputs=input_path)
