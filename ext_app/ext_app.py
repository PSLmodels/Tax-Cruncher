import pandas as pd
from taxcrunch.multi_cruncher import Batch
import numpy as np
import bokeh
from bokeh.io import output_notebook, output_file, save, curdoc
from bokeh.plotting import figure, show
from bokeh.models import ColumnDataSource, NumeralTickFormatter, Span, HoverTool, BoxAnnotation, Label, LabelSet, CustomJS
from bokeh.layouts import column, row, WidgetBox
from re import sub
from bokeh.application.handlers import FunctionHandler
from bokeh.application import Application
from bokeh.models.widgets import RadioButtonGroup, Slider, Dropdown, Div
from bokeh.palettes import Category20
from bokeh.core.properties import value
import os

CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))

csv_path = os.path.join(CURRENT_PATH, 'cruncher_data.csv')
df = pd.read_csv(csv_path)

js = """
function commas(x) {
    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}
var v1 = Math.round(cb_obj.data['itax'][0]);
var v2 = Math.round(cb_obj.data['itax'][1]);

var cut = v1 - v2;
var increase = v2 - v1;

var cut_str = "tax cut of $";
var inc_str = "tax increase of $";
var no_change = "no tax change";

d1.text = `<i>Under <b>current law</b>, individual income tax liabilities are: <b>$${commas(v1)}</b></i>`;
d2.text = `<i>Under <b>TCJA extension</b>, individual income tax liabilities are: <b>$${commas(v2)}</b></i>`;

if (v1 > v2) {
    d3.text = `TCJA extension results in a <b>${cut_str.fontcolor("green")}${commas(cut).fontcolor("green")}</b>`;
} else if (v2 > v1) {
    d3.text = `TCJA extension results in a <b>${inc_str.fontcolor("red")}${commas(increase).fontcolor("red")}</b>`;
} else {
    d3.text = `TCJA extension results in <b>${no_change.fontcolor("RebeccaPurple")}</b>`;
}
"""

def find_val(mstat, deps, wages, salt, item):
    df_filter = df.loc[(df['depx'] == deps) & (df['mstat'] == mstat) & (
        df['Wages'] == wages) & (df['otheritem'] == salt) & (df['mortgage'] == item)]
    keep = ['itax base', 'itax ext']
    df_itax = df_filter[keep]
    df_transposed = df_itax.transpose()
    df_transposed.columns = ['itax']
    x_vals = [0.5, 1.5]
    df_transposed['x_vals'] = x_vals
    itax_base = df_transposed.iloc[0, 0]
    itax_ext = df_transposed.iloc[1, 0]
    return ColumnDataSource(df_transposed)


def make_plot(src):
    p = figure(x_range=["Current Law", "TCJA Extension"],
               plot_height=250, plot_width=400, toolbar_location=None, tools="")
    p.vbar(source=src, x='x_vals', top='itax', color='#ff7f0e',
           hover_fill_color='#ff7f0e', hover_fill_alpha=0.8, width=0.3, fill_alpha=0.5)
    hline = Span(location=0, dimension='width', line_color='black')
    p.renderers.extend([hline])
    p.xaxis.axis_line_color = '#d3d3d3'
    p.yaxis.axis_line_color = '#d3d3d3'
    p.yaxis[0].ticker.desired_num_ticks = 2
    p.xaxis.major_tick_line_color = None
    p.xaxis.minor_tick_line_color = None
    p.yaxis.minor_tick_line_color = None
    p.yaxis.major_tick_line_color = '#d3d3d3'
    p.yaxis[0].formatter = NumeralTickFormatter(format="$0,000")
    p.yaxis.axis_label = "Individual Income Tax"
    p.ygrid.grid_line_color = None
    p.xgrid.grid_line_color = None
    p.outline_line_color = None
    p.xaxis.axis_line_color = None
    p.title.text = 'Current Law vs TCJA Extension — 2026'

    hover = HoverTool(tooltips='@itax{$0,000}')
    p.add_tools(hover)

    return p


def update(attr, old, new):
    if mstat_button.labels[mstat_button.active] == 'Single':
        mstat = 1
    else:
        mstat = 2

    deps = deps_slider.value
    wages = wages_slider.value
    salt = salt_slider.value
    item = item_slider.value

    new_src = find_val(mstat=mstat, deps=deps,
                       wages=wages, salt=salt, item=item)

    src.data.update(new_src.data)

mstat_button = RadioButtonGroup(labels=["Single", "Married"], active=0)
deps_slider = Slider(start=0, end=4, value=0, step=1,
                     title="Number of Children")
wages_slider = Slider(start=0, end=500000, value=0,
                      step=10000, title="Wage Income", format="$0,000")
salt_slider = Slider(start=0, end=50000, value=0, step=1000,
                     title="State and Local Taxes Paid", format="$0,000")
item_slider = Slider(start=0, end=50000, value=0, step=1000,
                     title="Other Itemizable Expenses", format="$0,000")

mstat_button.on_change('active', update)
deps_slider.on_change('value', update)
wages_slider.on_change('value', update)
salt_slider.on_change('value', update)
item_slider.on_change('value', update)

controls = WidgetBox(mstat_button, deps_slider,
                     wages_slider, salt_slider, item_slider)

src = find_val(mstat=1, deps=0, wages=0, salt=0, item=0)

p = make_plot(src)

d = Div(text="In 2026...")
d1 = Div(text=f"<i>Under <b>current law</b>, individual income tax liabilities are: <b>${src.data['itax'][0]}</b></i>")
d2 = Div(text=f"<i>Under <b>TCJA extension</b>, individual income tax liabilities are: <b>${src.data['itax'][1]}</b></i>")
d3 = Div(text=f"TCJA extension results in <b><font color='RebeccaPurple'>no tax change</font></b>")

space = Div(text="  ")

src.js_on_change('data', CustomJS(args=dict(d1=d1, d2=d2, d3=d3),
                                  code=js))

layout = column(d, d1, d2, d3, space, row(controls, space, p))

curdoc().add_root(layout)
