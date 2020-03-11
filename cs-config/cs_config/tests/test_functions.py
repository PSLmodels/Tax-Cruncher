from cs_kit import CoreTestFunctions

from cs_config import functions, helpers


class TestFunctions1(CoreTestFunctions):

    validate_inputs = functions.validate_inputs
    run_model = functions.run_model
    bad_adjustment = {"Tax Information": {"mstat": [{"value": 2}]}, "Policy":{"STD": -1}}
    ok_adjustment = {"Tax Information": {"mstat": [{"value": "Joint"}]}, "Policy":{}}
    get_inputs = functions.get_inputs
    get_version = functions.get_version


def test_convert_adj():
    adj = {
        "STD": [
            {"MARS": "single", "year": "2019", "value": 0},
            {"MARS": "mjoint", "year": 2019, "value": 1}
        ],
        "EITC_c": [{"EIC": "0kids", "year": "2019", "value": 1000.0}],
        "BEN_ssi_repeal": [
            {"year": 2019, "value": True}
        ]
    }

    res = helpers.convert_adj(adj, 2019)

    assert res == {
        "STD": {
            2019: [0, 1, 12200.0, 18350.0, 24400.0]
        },
        "EITC_c": {
            2019: [1000.0, 3526.0, 5828.0, 6557.0]
        },
        "BEN_ssi_repeal": {
            2019: True
        }
    }