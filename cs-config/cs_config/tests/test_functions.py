from cs_kit import CoreTestFunctions

from cs_config import functions


class TestFunctions1(CoreTestFunctions):

    validate_inputs = functions.validate_inputs
    run_model = functions.run_model
    bad_adjustment = {"Tax Information": {"mstat": [{"value": 2}]}, "Policy":{"STD": -1}}
    ok_adjustment = {"Tax Information": {"mstat": [{"value": "Joint"}]}, "Policy":{}}
    get_inputs = functions.get_inputs
    get_version = functions.get_version