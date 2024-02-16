import paramtools
from marshmallow import fields, Schema

POLICY_SCHEMA = {
    "labels": {
        "year": {
            "type": "int",
            "validators": {
                "choice": {"choices": [yr for yr in range(2013, 2030 + 1)]}
            },
        },
        "MARS": {
            "type": "str",
            "validators": {
                "choice": {
                    "choices": [
                        "single",
                        "mjoint",
                        "mseparate",
                        "headhh",
                        "widow",
                    ]
                }
            },
        },
        "idedtype": {
            "type": "str",
            "validators": {
                "choice": {
                    "choices": [
                        "med",
                        "sltx",
                        "retx",
                        "cas",
                        "misc",
                        "int",
                        "char",
                    ]
                }
            },
        },
        "EIC": {
            "type": "str",
            "validators": {
                "choice": {"choices": ["0kids", "1kid", "2kids", "3+kids"]}
            },
        },
        "data_source": {
            "type": "str",
            "validators": {"choice": {"choices": ["PUF", "CPS", "other"]}},
        },
    },
    "additional_members": {
        "section_1": {"type": "str"},
        "section_2": {"type": "str"},
        "start_year": {"type": "int"},
        "checkbox": {"type": "bool"},
    },
}


class MetaParameters(paramtools.Parameters):
    array_first = True
    defaults = {
        "year": {
            "title": "Year",
            "description": "Year for parameters.",
            "type": "int",
            "value": 2019,
            "validators": {
                "choice": {"choices": [yr for yr in range(2013, 2030 + 1)]}
            },
        }
    }
