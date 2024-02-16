from bokeh.embed import json_item
from bokeh.layouts import column, row
from bokeh.plotting import figure
from bokeh.models import (
    ColumnDataSource,
    CustomJS,
    Toggle,
    NumeralTickFormatter,
    Span,
    Label,
)


def liability_plot(df_base, df_reform, span, mtr_opt):
    df_base = ColumnDataSource(df_base)
    df_reform = ColumnDataSource(df_reform)
    tools = "pan, zoom_in, zoom_out, reset"
    fig = figure(
        width=600,
        height=500,
        x_range=(-10000, 300000),
        y_range=(-20000, 100000),
        tools=tools,
        active_drag="pan",
    )
    fig.yaxis.axis_label = "Tax Liabilities"
    fig.yaxis.formatter = NumeralTickFormatter(format="$0,000")

    filer_income = Span(
        location=span,
        dimension="height",
        line_color="black",
        line_dash="dotted",
        line_width=1.5,
    )
    fig.add_layout(filer_income)
    label_format = f"{span:,}"
    filer_income_label = Label(
        x=span,
        y=25,
        y_units="screen",
        x_offset=10,
        text="{}: $".format(mtr_opt) + label_format,
        text_color="#303030",
        text_font="arial",
        text_font_style="italic",
        text_font_size="10pt",
    )
    fig.add_layout(filer_income_label)
    axis = Span(
        location=0, dimension="width", line_color="#bfbfbf", line_width=1.5
    )
    fig.add_layout(axis)

    iitax_base = fig.line(
        x="Axis",
        y="Individual Income Tax",
        line_color="#2b83ba",
        muted_color="#2b83ba",
        line_width=2,
        legend_label="Individual Income Tax Liability",
        muted_alpha=0.1,
        source=df_base,
    )
    payroll_base = fig.line(
        x="Axis",
        y="Payroll Tax",
        line_color="#abdda4",
        muted_color="#abdda4",
        line_width=2,
        legend_label="Payroll Tax Liability",
        muted_alpha=0.1,
        source=df_base,
    )

    iitax_reform = fig.line(
        x="Axis",
        y="Individual Income Tax",
        line_color="#2b83ba",
        muted_color="#2b83ba",
        line_width=2,
        line_dash="dashed",
        legend_label="Individual Income Tax Liability",
        muted_alpha=0.1,
        source=df_reform,
    )
    payroll_reform = fig.line(
        x="Axis",
        y="Payroll Tax",
        line_color="#abdda4",
        muted_color="#abdda4",
        line_width=2,
        line_dash="dashed",
        legend_label="Payroll Tax Liability",
        muted_alpha=0.1,
        source=df_reform,
    )

    iitax_base.muted = False
    payroll_base.muted = False
    iitax_reform.muted = False
    payroll_reform.muted = False

    plot_js = """
    object1.visible = toggle.active
    object2.visible = toggle.active
    """
    base_callback = CustomJS(code=plot_js, args={})
    base_toggle = Toggle(
        label="Base (Solid)", button_type="default", active=True
    )
    base_callback.args = {
        "toggle": base_toggle,
        "object1": iitax_base,
        "object2": payroll_base,
    }
    base_toggle.js_on_change("active", base_callback)

    reform_callback = CustomJS(code=plot_js, args={})
    reform_toggle = Toggle(
        label="Reform (Dashed)", button_type="default", active=True
    )
    reform_callback.args = {
        "toggle": reform_toggle,
        "object1": iitax_reform,
        "object2": payroll_reform,
    }
    reform_toggle.js_on_change("active", reform_callback)

    fig.xaxis.formatter = NumeralTickFormatter(format="$0,000")
    fig.xaxis.axis_label = mtr_opt
    fig.xaxis.minor_tick_line_color = None

    fig.legend.click_policy = "mute"

    layout = column(fig, row(base_toggle, reform_toggle))

    data = json_item(layout)

    outputs = {
        "media_type": "bokeh",
        "title": "Tax Liabilities by {} (Holding Other Inputs Constant)".format(
            mtr_opt
        ),
        "data": data,
    }

    return outputs


def rate_plot(df_base, df_reform, span, mtr_opt):
    df_base = ColumnDataSource(df_base)
    df_reform = ColumnDataSource(df_reform)
    tools = "pan, zoom_in, zoom_out, reset"
    fig = figure(
        width=600,
        height=500,
        x_range=(-10000, 300000),
        y_range=(-0.3, 0.5),
        tools=tools,
        active_drag="pan",
    )
    fig.yaxis.axis_label = "Tax Rate"
    fig.yaxis.formatter = NumeralTickFormatter(format="0%")

    filer_income = Span(
        location=span,
        dimension="height",
        line_color="black",
        line_dash="dotted",
        line_width=1.5,
    )
    fig.add_layout(filer_income)
    label_format = f"{span:,}"
    filer_income_label = Label(
        x=span,
        y=25,
        y_units="screen",
        x_offset=10,
        text="{}: $".format(mtr_opt) + label_format,
        text_color="#303030",
        text_font="arial",
        text_font_style="italic",
        text_font_size="10pt",
    )
    fig.add_layout(filer_income_label)
    axis = Span(
        location=0, dimension="width", line_color="#bfbfbf", line_width=1.5
    )
    fig.add_layout(axis)

    iitax_atr_base = fig.line(
        x="Axis",
        y="IATR",
        line_color="#2b83ba",
        muted_color="#2b83ba",
        line_width=2,
        legend_label="Income Tax Average Rate",
        muted_alpha=0.1,
        source=df_base,
    )
    payroll_atr_base = fig.line(
        x="Axis",
        y="PATR",
        line_color="#abdda4",
        muted_color="#abdda4",
        line_width=2,
        legend_label="Payroll Tax Average Rate",
        muted_alpha=0.1,
        source=df_base,
    )
    iitax_mtr_base = fig.line(
        x="Axis",
        y="Income Tax MTR",
        line_color="#fdae61",
        muted_color="#fdae61",
        line_width=2,
        legend_label="Income Tax Marginal Rate",
        muted_alpha=0.1,
        source=df_base,
    )
    payroll_mtr_base = fig.line(
        x="Axis",
        y="Payroll Tax MTR",
        line_color="#d7191c",
        muted_color="#d7191c",
        line_width=2,
        legend_label="Payroll Tax Marginal Rate",
        muted_alpha=0.1,
        source=df_base,
    )

    iitax_atr_reform = fig.line(
        x="Axis",
        y="IATR",
        line_color="#2b83ba",
        muted_color="#2b83ba",
        line_width=2,
        line_dash="dashed",
        legend_label="Income Tax Average Rate",
        muted_alpha=0.1,
        source=df_reform,
    )
    payroll_atr_reform = fig.line(
        x="Axis",
        y="PATR",
        line_color="#abdda4",
        muted_color="#abdda4",
        line_width=2,
        line_dash="dashed",
        legend_label="Payroll Tax Average Rate",
        muted_alpha=0.1,
        source=df_reform,
    )
    iitax_mtr_reform = fig.line(
        x="Axis",
        y="Income Tax MTR",
        line_color="#fdae61",
        muted_color="#fdae61",
        line_width=2,
        line_dash="dashed",
        legend_label="Income Tax Marginal Rate",
        muted_alpha=0.1,
        source=df_reform,
    )
    payroll_mtr_reform = fig.line(
        x="Axis",
        y="Payroll Tax MTR",
        line_color="#d7191c",
        muted_color="#d7191c",
        line_width=2,
        line_dash="dashed",
        legend_label="Payroll Tax Marginal Rate",
        muted_alpha=0.1,
        source=df_reform,
    )

    iitax_atr_base.muted = False
    iitax_mtr_base.muted = True
    payroll_atr_base.muted = True
    payroll_mtr_base.muted = True
    iitax_atr_reform.muted = False
    iitax_mtr_reform.muted = True
    payroll_atr_reform.muted = True
    payroll_mtr_reform.muted = True

    plot_js = """
    object1.visible = toggle.active
    object2.visible = toggle.active
    object3.visible = toggle.active
    object4.visible = toggle.active
    """
    base_callback = CustomJS(code=plot_js, args={})
    base_toggle = Toggle(
        label="Base (Solid)", button_type="default", active=True
    )
    base_callback.args = {
        "toggle": base_toggle,
        "object1": iitax_atr_base,
        "object2": payroll_atr_base,
        "object3": iitax_mtr_base,
        "object4": payroll_mtr_base,
    }
    base_toggle.js_on_change("active", base_callback)

    reform_callback = CustomJS(code=plot_js, args={})
    reform_toggle = Toggle(
        label="Reform (Dashed)", button_type="default", active=True
    )
    reform_callback.args = {
        "toggle": reform_toggle,
        "object1": iitax_atr_reform,
        "object2": payroll_atr_reform,
        "object3": iitax_mtr_reform,
        "object4": payroll_mtr_reform,
    }
    reform_toggle.js_on_change("active", reform_callback)

    fig.xaxis.formatter = NumeralTickFormatter(format="$0,000")
    fig.xaxis.axis_label = mtr_opt
    fig.xaxis.minor_tick_line_color = None

    fig.legend.click_policy = "mute"

    layout = column(fig, row(base_toggle, reform_toggle))

    data = json_item(layout)

    outputs = {
        "media_type": "bokeh",
        "title": "Tax Rates by {} (Holding Other Inputs Constant)".format(
            mtr_opt
        ),
        "data": data,
    }

    return outputs


def credit_plot(df_base, df_reform, span, mtr_opt):
    df_base = ColumnDataSource(df_base)
    df_reform = ColumnDataSource(df_reform)
    tools = "pan, zoom_in, zoom_out, reset"
    fig = figure(
        width=600,
        height=500,
        x_range=(-2500, 70000),
        tools=tools,
        active_drag="pan",
    )

    filer_income = Span(
        location=span,
        dimension="height",
        line_color="black",
        line_dash="dotted",
        line_width=1.5,
    )
    fig.add_layout(filer_income)
    label_format = f"{span:,}"
    filer_income_label = Label(
        x=span,
        y=45,
        y_units="screen",
        x_offset=10,
        text="{}: $".format(mtr_opt) + label_format,
        text_color="#303030",
        text_font="arial",
        text_font_style="italic",
        text_font_size="10pt",
    )
    fig.add_layout(filer_income_label)
    axis = Span(
        location=0, dimension="width", line_color="#bfbfbf", line_width=1.5
    )
    fig.add_layout(axis)

    eitc_base = fig.line(
        x="Axis",
        y="EITC",
        line_color="#2b83ba",
        muted_color="#2b83ba",
        line_width=2,
        legend_label="Earned Income Tax Credit",
        muted_alpha=0.1,
        source=df_base,
    )
    ctc_base = fig.line(
        x="Axis",
        y="CTC",
        line_color="#abdda4",
        muted_color="#abdda4",
        line_width=2,
        legend_label="Nonrefundable Child Tax Credit",
        muted_alpha=0.1,
        source=df_base,
    )
    ctc_refund_base = fig.line(
        x="Axis",
        y="CTC Refundable",
        line_color="#fdae61",
        muted_color="#fdae61",
        line_width=2,
        legend_label="Refundable Child Tax Credit",
        muted_alpha=0.1,
        source=df_base,
    )
    cdcc_base = fig.line(
        x="Axis",
        y="Child care credit",
        line_color="#d7191c",
        muted_color="#d7191c",
        line_width=2,
        legend_label="Child and Dependent Care Credit",
        muted_alpha=0.1,
        source=df_base,
    )

    eitc_reform = fig.line(
        x="Axis",
        y="EITC",
        line_color="#2b83ba",
        muted_color="#2b83ba",
        line_width=2,
        line_dash="dashed",
        legend_label="Earned Income Tax Credit",
        muted_alpha=0.1,
        source=df_reform,
    )
    ctc_reform = fig.line(
        x="Axis",
        y="CTC",
        line_color="#abdda4",
        muted_color="#abdda4",
        line_width=2,
        line_dash="dashed",
        legend_label="Nonrefundable Child Tax Credit",
        muted_alpha=0.1,
        source=df_reform,
    )
    ctc_refund_reform = fig.line(
        x="Axis",
        y="CTC Refundable",
        line_color="#fdae61",
        muted_color="#fdae61",
        line_width=2,
        line_dash="dashed",
        legend_label="Refundable Child Tax Credit",
        muted_alpha=0.1,
        source=df_reform,
    )
    cdcc_reform = fig.line(
        x="Axis",
        y="Child care credit",
        line_color="#d7191c",
        muted_color="#d7191c",
        line_width=2,
        line_dash="dashed",
        legend_label="Child and Dependent Care Credit",
        muted_alpha=0.1,
        source=df_reform,
    )

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
    base_toggle = Toggle(
        label="Base (Solid)", button_type="default", active=True
    )
    base_callback.args = {
        "toggle": base_toggle,
        "object1": eitc_base,
        "object2": cdcc_base,
        "object3": ctc_base,
        "object4": ctc_refund_base,
    }
    base_toggle.js_on_change("active", base_callback)

    reform_callback = CustomJS(code=plot_js, args={})
    reform_toggle = Toggle(
        label="Reform (Dashed)", button_type="default", active=True
    )
    reform_callback.args = {
        "toggle": reform_toggle,
        "object1": eitc_reform,
        "object2": cdcc_reform,
        "object3": ctc_reform,
        "object4": ctc_refund_reform,
    }
    reform_toggle.js_on_change("active", reform_callback)

    fig.yaxis.formatter = NumeralTickFormatter(format="$0,000")
    fig.yaxis.axis_label = "Tax Credits"
    fig.xaxis.formatter = NumeralTickFormatter(format="$0,000")
    fig.xaxis.axis_label = mtr_opt
    fig.xaxis.minor_tick_line_color = None

    fig.legend.click_policy = "mute"

    layout = column(fig, row(base_toggle, reform_toggle))

    data = json_item(layout)

    outputs = {
        "media_type": "bokeh",
        "title": "Tax Credits by {} (Holding Other Inputs Constant)".format(
            mtr_opt
        ),
        "data": data,
    }

    return outputs
