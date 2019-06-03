import os
import inspect
import copy
import hashlib
import gzip
import copy
import pandas as pd
import numpy as np
from collections import defaultdict
from taxcalc import (Policy, DIFF_TABLE_COLUMNS, DIFF_TABLE_LABELS,
                     DIST_TABLE_COLUMNS, DIST_TABLE_LABELS,
                     add_income_table_row_variable,
                     add_quantile_table_row_variable, STANDARD_INCOME_BINS)
from operator import itemgetter
from .constants import (POLICY_SCHEMA)


def convert_defaults(pcl):

    type_map = {
        "real": "float",
        "boolean": "bool",
        "integer": "int",
        "string": "str",
    }

    new_pcl = defaultdict(dict)
    new_pcl["schema"] = POLICY_SCHEMA
    LAST_YEAR = 2026
    pol = Policy()
    pol.set_year(2026)
    for param, item in pcl.items():
        values = []
        pol_val = getattr(pol, f"_{param}").tolist()
        min_year = min(item["value_yrs"])
        if isinstance(pol_val[0], list):
            for year in range(len(pol_val)):
                if min_year + year > LAST_YEAR:
                    break
                for dim1 in range(len(pol_val[0])):
                    values.append({
                        "year": min_year + year,
                        item["vi_name"]: item["vi_vals"][dim1],
                        "value": pol_val[year][dim1]
                    })
        else:
            for year in range(len(pol_val)):
                if min_year + year > LAST_YEAR:
                    break
                values.append({
                    "year": min_year + year,
                    "value": pol_val[year]
                })

        new_pcl[param]['value'] = values
        new_pcl[param]['title'] = pcl[param]["long_name"]
        new_pcl[param]['type'] = type_map[pcl[param]["value_type"]]

        new_pcl[param]["validators"] = {"range": pcl[param]["valid_values"]}

        # checkbox if indexable
        if item["indexable"]:
            if item["indexed"]:
                new_pcl[param]["checkbox"] = True
            else:
                new_pcl[param]["checkbox"] = False

        to_keep = list(POLICY_SCHEMA["additional_members"].keys()) + [
            "description", "notes",
        ]
        for k in to_keep:
            if k in pcl[param]:
                new_pcl[param][k] = pcl[param][k]

    return new_pcl


def convert_adj(adj, start_year):
    pol = Policy()
    new_adj = defaultdict(dict)
    for param, valobjs in adj.items():
        if param.endswith("checkbox"):
            param_name = param.split("_checkbox")[0]
            new_adj[f"{param_name}-indexed"][start_year] = valobjs[0]["value"]
            continue
        for valobj in valobjs:
            # has keys "year" and "value"
            if len(valobj) == 2:
                new_adj[param][valobj["year"]] = valobj["value"]
            # has keys "year", "value", and one of "MARS", "idedtype", or "EIC"
            elif len(valobj) == 3:
                other_label = next(k for k in valobj.keys()
                                   if k not in ("year", "value"))
                param_meta = pol._vals[f"_{param}"]
                if other_label != param_meta["vi_name"]:
                    msg = (f"Label {other_label} does not match expected"
                           f"label {param_meta['vi_name']}")
                    raise ValueError(msg)
                ol_ix = param_meta["vi_vals"].index(valobj[other_label])
                other_label_ix = ol_ix

                if valobj["year"] in new_adj[param]:
                    defaultlist = new_adj[param][valobj["year"]]
                else:
                    year_ix = valobj["year"] - min(param_meta["value_yrs"])
                    # shallow copy the list
                    defaultlist = list(param_meta["value"][year_ix])

                defaultlist[other_label_ix] = valobj["value"]

                new_adj[param][valobj["year"]] = defaultlist
            else:
                msg = (f"Dict should have 2 or 3 keys. It has {len(valobj)}"
                       f"instead (key={list(valobj.keys())}).")
                raise ValueError(msg)
    return new_adj