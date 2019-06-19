from compdevkit import FunctionsTest

from compconfig import functions, helpers


def test_functions():
	ta = FunctionsTest(
		get_inputs=functions.get_inputs,
		validate_inputs=functions.validate_inputs,
		run_model=functions.run_model,
		ok_adjustment={"Tax Information": {"mstat": [{"value": "Joint"}]}, "Policy":{}},
		bad_adjustment={"Tax Information": {"mstat": [{"value": 2}]}, "Policy":{"STD": -1}}
	)
	ta.test()

def test_convert_adj():
    adj = {
        "STD": [
            {"MARS": "single", "year": 2019, "value": 0},
            {"MARS": "mjoint", "year": 2019, "value": 1}
        ],
        "EITC_c": [{"EIC": "0kids", "year": 2019, "value": 1000.0}],
        "BEN_ssi_repeal": [
            {"year": 2019, "value": True}
        ]
    }

    res = helpers.convert_adj(adj, 2019)

    assert res == {
        "STD": {
            2019: [0, 1, 12268.8, 18403.2, 24537.6]
        },
        "EITC_c": {
            2019: [1000.0, 3529.87, 5829.75, 6558.98]
        },
        "BEN_ssi_repeal": {
            2019: True
        }
    }