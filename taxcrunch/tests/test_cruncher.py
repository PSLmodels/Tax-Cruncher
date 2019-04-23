import pytest
import json
from taxcrunch.cruncher import Cruncher

def test_adjust():
	f = open('test_adjustment.json')
	data = json.load(f)
	mstat1 = data['mstat'][0]['value']
	c = cruncher.Cruncher()
	adjustment = c.adjust_file(file="test_adjustment.json")
	mstat2 = adjustment['mstat'][0]['value']
	assert mstat1 == mstat2

# def test_run_calc():
# 	c = c.Cruncher()

        