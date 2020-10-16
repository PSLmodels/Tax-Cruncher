import pytest
from taxcrunch.cruncher import CruncherParams
from taxcrunch.multi_cruncher import BatchParams


def test_compare_defaults():
	'''
	Test that defaults.json and defaults_batch.json have the same
	parameters in the same order.
	'''
	cp = CruncherParams()
	ignore = ['mtr_options', 'reform_options']
	cp_list = []
	for k,v in cp.dump().items():
	    cp_list.append(k)
	for item in ignore:
	    cp_list.remove(item)

	bp = BatchParams()
	bp_list = []
	for k,v in bp.dump().items():
	    bp_list.append(k)

	assert cp_list == bp_list