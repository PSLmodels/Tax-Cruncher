from bokeh.embed import components
from bokeh.layouts import column, row, WidgetBox, layout
from bokeh.palettes import Spectral4
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, CustomJS, Toggle, NumeralTickFormatter, LinearAxis, Range1d


def credit_plot(df_base, df_reform):
    df_base1 = ColumnDataSource(df_base)
    df_reform1 = ColumnDataSource(df_reform)

    fig = figure(plot_width=600, plot_height=500, x_range=(0, 70000))
    names = ['Earned Income Tax Credit', 'Child and Dependent Care Credit',
             'Child Tax Credit - Nonrefundable', 'Child Tax Credit - Refundable']
    calcs = ['EITC', 'Child care credit', 'CTC', 'CTC Refundable']
    lines_base = ['eitc_base', 'cdcc_base', 'ctc_base', 'ctc_refund_base']

    eitc_base = fig.line(x="Wages", y="EITC", line_color='#2b83ba', muted_color='#2b83ba',
                         line_width=2, legend="Earned Income Tax Credit", muted_alpha=0.1, source=df_base1)
    ctc_base = fig.line(x="Wages", y="CTC", line_color='#abdda4', muted_color='#abdda4',
                         line_width=2, legend='Nonrefundable Child Tax Credit', muted_alpha=0.1, source=df_base1)
    ctc_refund_base = fig.line(x="Wages", y="CTC Refundable", line_color='#fdae61', muted_color='#fdae61',
                               line_width=2, legend='Refundable Child Tax Credit', muted_alpha=0.1, source=df_base1)
    cdcc_base = fig.line(x="Wages", y="Child care credit", line_color='#d7191c', muted_color='#d7191c',
                         line_width=2, legend='Child and Dependent Care Credit', muted_alpha=0.1, source=df_base1)

    eitc_reform = fig.line(x="Wages", y="EITC", line_color='#2b83ba', muted_color='#2b83ba', line_width=2,
                           line_dash='dashed', legend="Earned Income Tax Credit", muted_alpha=0.1, source=df_reform1)
    ctc_reform = fig.line(x="Wages", y="CTC", line_color='#abdda4', muted_color='#abdda4', line_width=2,
                          line_dash='dashed', legend='Nonrefundable Child Tax Credit', muted_alpha=0.1, source=df_reform1)
    ctc_refund_reform = fig.line(x="Wages", y="CTC Refundable", line_color='#fdae61', muted_color='#fdae61',
                                 line_width=2, line_dash='dashed', legend='Refundable Child Tax Credit', muted_alpha=0.1, source=df_reform1)
    cdcc_reform = fig.line(x="Wages", y="Child care credit", line_color='#d7191c', muted_color='#d7191c', line_width=2,
                           line_dash='dashed', legend='Child and Dependent Care Credit', muted_alpha=0.1, source=df_reform1)

    ctc_base.muted = True
    ctc_refund_base.muted = True
    cdcc_base.muted = True
    ctc_reform.muted = True
    ctc_refund_reform.muted = True
    cdcc_reform.muted = True

    plot_js = """
    object1.visible = toggle.active
    object2.visible = toggle.active
    object3.visible = toggle.active
    object4.visible = toggle.active
    """
    base_callback = CustomJS(code=plot_js, args={})
    base_toggle = Toggle(label="Base", button_type="default",
                         callback=base_callback, active=True)
    base_callback.args = {"toggle": base_toggle, "object1": eitc_base,
                          "object2": cdcc_base, "object3": ctc_base,
                          "object4": ctc_refund_base}

    reform_callback = CustomJS(code=plot_js, args={})
    reform_toggle = Toggle(label="Reform", button_type="default",
                           callback=reform_callback, active=True)
    reform_callback.args = {"toggle": reform_toggle, "object1": eitc_reform,
                            "object2": cdcc_reform, "object3": ctc_reform,
                            "object4": ctc_refund_reform}

    fig.yaxis.formatter = NumeralTickFormatter(format="$0,000")
    fig.yaxis.axis_label = "Tax Credit Received"
    fig.xaxis.formatter = NumeralTickFormatter(format="$0,000")
    fig.xaxis.axis_label = "Household Wages"
    fig.xaxis.minor_tick_line_color = None

    fig.legend.click_policy = "mute"

    layout = column(fig, row(base_toggle, reform_toggle))

    js_credit, div_credit = components(layout)

    outputs = {
        "media_type": "bokeh",
        "title": "Tax Credits by Wage (Holding Other Inputs Constant)",
        "data": {
            "javascript": js_credit,
            "html": div_credit
        }
    }

    return outputs


def liability_plot(df_base, df_reform):
    df_base2 = ColumnDataSource(df_base)
    df_reform2 = ColumnDataSource(df_reform)
    fig = figure(plot_width=700, plot_height=500, x_range=(0, 300000), y_range=(-20000, 100000))
    fig.extra_y_ranges = {"MTR": Range1d(start=-0.1, end=0.5)}
    fig.yaxis.axis_label = "Tax Liabilities"
    fig.yaxis.formatter = NumeralTickFormatter(format="$0,000")
    decimals = NumeralTickFormatter(format='0%')
    fig.add_layout(LinearAxis(y_range_name="MTR",
                              axis_label="Marginal Tax Rates", formatter=decimals), 'right')

    names = ['Income Tax Liability', 'Payroll Tax Liability']
    calcs = ['Individual Income Tax', 'Payroll Tax']
    lines_base = ['eitc_base', 'cdcc_base', 'ctc_base', 'ctc_refund_base']

    iitax_base = fig.line(x="Wages", y="Individual Income Tax", line_color='#2b83ba', muted_color='#2b83ba',
                          line_width=2, legend="Individual Income Tax Liability (Left Axis)", muted_alpha=0.1, source=df_base2)
    payroll_base = fig.line(x="Wages", y="Payroll Tax", line_color='#abdda4', muted_color='#abdda4',
                            line_width=2, legend='Payroll Tax Liability (Left Axis)', muted_alpha=0.1, source=df_base2)
    iitax_mtr_base = fig.line(x="Wages", y="Income Tax MTR", line_color='#fdae61', muted_color='#fdae61', line_width=2,
                              legend="Income Tax Marginal Rate (Right Axis)", muted_alpha=0.1, y_range_name="MTR", source=df_base2)
    payroll_mtr_base = fig.line(x="Wages", y="Payroll Tax MTR", line_color='#d7191c', muted_color='#d7191c', line_width=2,
                                legend='Payroll Tax Marginal Rate (Right Axis)', muted_alpha=0.1, y_range_name="MTR", source=df_base2)

    iitax_reform = fig.line(x="Wages", y="Individual Income Tax", line_color='#2b83ba', muted_color='#2b83ba', line_width=2,
                            line_dash='dashed', legend="Individual Income Tax Liability (Left Axis)", muted_alpha=0.1, source=df_reform2)
    payroll_reform = fig.line(x="Wages", y="Payroll Tax", line_color='#abdda4', muted_color='#abdda4', line_width=2,
                              line_dash='dashed', legend='Payroll Tax Liability (Left Axis)', muted_alpha=0.1, source=df_reform2)
    iitax_mtr_reform = fig.line(x="Wages", y="Income Tax MTR", line_color='#fdae61', muted_color='#fdae61', line_width=2,
                                line_dash='dashed', legend="Income Tax Marginal Rate (Right Axis)", muted_alpha=0.1, y_range_name="MTR", source=df_reform2)
    payroll_mtr_reform = fig.line(x="Wages", y="Payroll Tax MTR", line_color='#d7191c', muted_color='#d7191c', line_width=2,
                                  line_dash='dashed', legend='Payroll Tax Marginal Rate (Right Axis)', muted_alpha=0.1, y_range_name="MTR", source=df_reform2)

    iitax_base.muted = False
    payroll_base.muted = True
    iitax_mtr_base.muted = True
    payroll_mtr_base.muted = True
    iitax_reform.muted = False
    payroll_reform.muted = True
    iitax_mtr_reform.muted = True
    payroll_mtr_reform.muted = True

    plot_js = """
    object1.visible = toggle.active
    object2.visible = toggle.active
    object3.visible = toggle.active
    object4.visible = toggle.active
    """
    base_callback = CustomJS(code=plot_js, args={})
    base_toggle = Toggle(label="Base", button_type="default",
                         callback=base_callback, active=True)
    base_callback.args = {"toggle": base_toggle, "object1": iitax_base,
                          "object2": payroll_base, "object3": iitax_mtr_base,
                          "object4": payroll_mtr_base}

    reform_callback = CustomJS(code=plot_js, args={})
    reform_toggle = Toggle(label="Reform", button_type="default",
                           callback=reform_callback, active=True)
    reform_callback.args = {"toggle": reform_toggle, "object1": iitax_reform,
                            "object2": payroll_reform, "object3": iitax_mtr_reform,
                            "object4": payroll_mtr_reform}

    fig.xaxis.formatter = NumeralTickFormatter(format="$0,000")
    fig.xaxis.axis_label = "Household Wages"
    fig.xaxis.minor_tick_line_color = None

    fig.legend.click_policy = "mute"

    layout = column(fig, row(base_toggle, reform_toggle))

    js_liability, div_liability = components(layout)

    outputs = {
        "media_type": "bokeh",
        "title": "Liabilities and Marginal Rates by Wage (Holding Other Inputs Constant)",
        "data": {
            "javascript": js_liability,
            "html": div_liability
        }
    }

    return outputs