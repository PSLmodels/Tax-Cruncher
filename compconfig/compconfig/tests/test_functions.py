from compdevkit import FunctionsTest

from compconfig import functions


def test_functions():
	ta = FunctionsTest(
		get_inputs=functions.get_inputs,
		validate_inputs=functions.validate_inputs,
		run_model=functions.run_model,
		ok_adjustment={"Tax Information": {"mstat": [{"value": "Joint"}]}, "Policy":{}},
		bad_adjustment={"Tax Information": {"mstat": [{"value": 2}]}, "Policy":{"STD": -1}}
	)
	ta.test()