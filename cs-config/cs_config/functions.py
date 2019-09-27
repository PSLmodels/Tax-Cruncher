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
import taxcrunch
from taxcalc import Policy
from IPython.display import HTML
from collections import OrderedDict

TCPATH = inspect.getfile(Policy)
TCDIR = os.path.dirname(TCPATH)

with open(os.path.join(TCDIR, "policy_current_law.json"), "r") as f:
    pcl = json.loads(f.read())

RES = convert_defaults(pcl)


class TCParams(paramtools.Parameters):
    defaults = RES


def get_version():
    version = taxcrunch.__version__
    return f"Tax-Cruncher v{version}"


def get_inputs(meta_params_dict):
    """
    Return default parameters from Tax-Cruncher
    """
    metaparams = MetaParameters()
    metaparams.adjust(meta_params_dict)

    params = CruncherParams()
    policy_params = TCParams()

    policy_params.set_state(
        year=metaparams.year.tolist())

    filtered_pol_params = OrderedDict()
    for k, v in policy_params.dump().items():
        if k =="schema" or v.get("section_1", False):
            filtered_pol_params[k] = v

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
        "mtr_options",
        "schema"
    ]
    cruncher_dict = params.dump()

    default_params = {
        "Tax Information": {k: v for k, v in cruncher_dict.items() if k in keep},
        "Policy": filtered_pol_params
    }

    meta = metaparams.dump()

    return {"meta_parameters": meta, "model_parameters": default_params}


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

    return {"errors_warnings": errors_warnings}


def run_model(meta_params_dict, adjustment):
    meta_params = MetaParameters()
    meta_params.adjust(meta_params_dict)

    policy_mods = convert_adj(adjustment["Policy"], meta_params.year.tolist())

    adjustment["Tax Information"]["year"] = meta_params.year
    params = CruncherParams()
    params.adjust(adjustment["Tax Information"], raise_errors=False)
    newvals = params.specification()

    crunch = Cruncher(inputs=newvals, custom_reform=policy_mods)

    # make dataset for bokeh plots
    ivar = crunch.ivar
    _, mtr_opt, _ = crunch.taxsim_inputs()
    df = pd.concat([ivar] * 5000, ignore_index=True)
    increments = pd.DataFrame(list(range(0, 500000, 100)))

    # use Calculation Option to determine what var to increment
    if mtr_opt == 'Taxpayer Earnings':
        span = int(ivar[9])
        df[9] = increments
    elif mtr_opt == 'Spouse Earnings':
        span = int(ivar[10])
        df[10] = increments
    elif mtr_opt == 'Short Term Gains':
        span = int(ivar[13])
        df[13] = increments
    elif mtr_opt == 'Long Term Gains':
        span = int(ivar[14])
        df[14] = increments
    elif mtr_opt == 'Qualified Dividends':
        span = int(ivar[14])
        df[11] = increments
    elif mtr_opt == 'Interest Received':
        span = int(ivar[12])
        df[12] = increments
    elif mtr_opt == 'Pensions':
        span = int(ivar[17])
        df[17] = increments
    elif mtr_opt == 'Gross Social Security Benefits':
        span = int(ivar[18])
        df[18] = increments
    elif mtr_opt == 'Real Estate Taxes Paid':
        span = int(ivar[20])
        df[20] = increments
    elif mtr_opt == 'Mortgage':
        span = int(ivar[23])
        df[23] = increments    

    b = Batch(df)
    df_base = b.create_table()
    df_reform = b.create_table(policy_mods)

    # compute average tax rates
    df_base['IATR'] = df_base['Individual Income Tax'] / df_base['AGI']
    df_base['PATR'] = df_base['Payroll Tax'] / df_base['AGI']
    df_reform['IATR'] = df_reform['Individual Income Tax'] / df_reform['AGI']
    df_reform['PATR'] = df_reform['Payroll Tax'] / df_reform['AGI']
    df_base['Axis'] = increments
    df_reform['Axis'] = increments

    return comp_output(crunch, df_base, df_reform, span, mtr_opt)


def comp_output(crunch, df_base, df_reform, span, mtr_opt):

    liabilities = liability_plot(df_base, df_reform, span, mtr_opt)
    rates = rate_plot(df_base, df_reform, span, mtr_opt)
    credits = credit_plot(df_base, df_reform, span, mtr_opt)

    basic = crunch.basic_table()
    detail = crunch.calc_table()

    table_basic = basic.to_html(
        classes="table table-striped table-hover"
    )
    table_detail = detail.to_html(
        classes="table table-striped table-hover"
    )

    comp_dict = {
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
