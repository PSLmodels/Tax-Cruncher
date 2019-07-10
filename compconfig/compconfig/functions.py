import os
import json
import traceback
import paramtools
import pandas as pd
import inspect
from .helpers import convert_defaults, convert_adj
from .outputs import credit_plot, rate_plot, liability_plot
from .constants import MetaParameters
from bokeh.models import ColumnDataSource
from taxcrunch.cruncher import Cruncher, CruncherParams
from taxcrunch.multi_cruncher import Batch
from taxcalc import Policy
from IPython.display import HTML

TCPATH = inspect.getfile(Policy)
TCDIR = os.path.dirname(TCPATH)

with open(os.path.join(TCDIR, "policy_current_law.json"), "r") as f:
    pcl = json.loads(f.read())

RES = convert_defaults(pcl)


class TCParams(paramtools.Parameters):
    defaults = RES


def get_inputs(meta_params_dict):
    """
	Return default parameters from Tax-Cruncher
	"""
    metaparams = MetaParameters()
    metaparams.adjust(meta_params_dict)

    params = CruncherParams()
    policy_params = TCParams()

    keep = [
        "mstat",
        "page",
        "sage",
        "depx",
        "dep13",
        "dep17",
        "dep18",
        "pwages",
        "swages",
        "dividends",
        "intrec",
        "stcg",
        "ltcg",
        "otherprop",
        "nonprop",
        "pensions",
        "gssi",
        "ui",
        "proptax",
        "otheritem",
        "childcare",
        "mortgage",
        "mtr_options"
    ]
    full_dict = params.specification(
        meta_data=True, include_empty=True, serializable=True
    )

    params_dict = {var: full_dict[var] for var in keep}

    cruncher_params = params_dict

    pol_params = policy_params.specification(
        meta_data=True, include_empty=True, serializable=True, year=metaparams.year
    )

    meta = metaparams.specification(meta_data=True, include_empty=True, serializable=True)

    return meta, {"Tax Information": cruncher_params, "Policy": pol_params}


def validate_inputs(meta_params_dict, adjustment, errors_warnings):
    params = CruncherParams()
    params.adjust(adjustment["Tax Information"], raise_errors=False)
    errors_warnings["Tax Information"]["errors"].update(params.errors)

    pol_params = {}
    # drop checkbox parameters.
    for param, data in list(adjustment["Policy"].items()):
        if not param.endswith("checkbox"):
            pol_params[param] = data

    policy_params = TCParams()
    policy_params.adjust(pol_params, raise_errors=False)
    errors_warnings["Policy"]["errors"].update(policy_params.errors)

    return errors_warnings


def run_model(meta_params_dict, adjustment):
    meta_params = MetaParameters()
    meta_params.adjust(meta_params_dict)

    policy_mods = convert_adj(adjustment["Policy"], meta_params.year.tolist())

    params = CruncherParams()
    params.adjust(adjustment["Tax Information"], raise_errors=False)
    newvals = params.specification()

    crunch = Cruncher(inputs=newvals, custom_reform=policy_mods)

    #make dataset for bokeh plots
    ivar = crunch.ivar
    df = pd.concat([ivar]*5000, ignore_index=True)
    increments = pd.DataFrame(list(range(0,500000,100)))
    zeros = pd.DataFrame([0]*5000)
    #ivar position of e00200p
    df[9] = increments
    #set spouse earning to zero
    df[10] = zeros
    b = Batch(df)
    df_base = b.create_table()
    df_reform = b.create_table(policy_mods)
    #compute average tax rates
    df_base['IATR'] = df_base['Individual Income Tax'] / df_base['AGI']
    df_base['PATR'] = df_base['Payroll Tax'] / df_base['AGI']
    df_reform['IATR'] = df_reform['Individual Income Tax'] / df_reform['AGI']
    df_reform['PATR'] = df_reform['Payroll Tax'] / df_reform['AGI']

    return comp_output(crunch, df_base, df_reform)
    

def comp_output(crunch, df_base, df_reform):

    liabilities = liability_plot(df_base, df_reform)
    rates = rate_plot(df_base, df_reform)
    credits = credit_plot(df_base, df_reform)
    

    basic = crunch.basic_table()
    detail = crunch.calc_table()

    table_basic = basic.to_html(
        classes="table table-striped table-hover"
    )
    table_detail = detail.to_html(
        classes="table table-striped table-hover"
    )

    comp_dict = {
        "model_version": "0.0.1",
        "renderable": [
            {"media_type": "table", "title": "Basic Liabilities", "data": table_basic},
            liabilities, rates, credits,
            {
                "media_type": "table",
                "title": "Calculation of Liabilities",
                "data": table_detail,
            },
        ],
        "downloadable": [
            {
                "media_type": "CSV",
                "title": "basic_table",
                "data": basic.to_csv(),
            },
            {
                "media_type": "CSV",
                "title": "calculation_table",
                "data": detail.to_csv(),
            },
        ],
    }
    return comp_dict
