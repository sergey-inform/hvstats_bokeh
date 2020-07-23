''' 
Show interactive HV timeline plot using Bokeh appserver.

Use the ``bokeh serve`` command to run the app

    bokeh serve --show /app

at your command prompt. Then navigate to he URL in your browser

    http://localhost:5006/app

--
'''

import pandas as pd
import numpy as np

from os.path import join as path_join, dirname

from bokeh import logging
from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, PreText, Div
from bokeh.plotting import figure
from bokeh.palettes import Colorblind8, Spectral8


DATA_FILE = path_join(dirname(__file__),'../', 'hv.csv')
DATA_COLS = ("ts", "VMon0", "IMon0", "VMon1", "IMon1", "VMon2", "IMon2")

source = ColumnDataSource(data=dict(ts=[], IMon1=[], VMon1=[]))
source_static = ColumnDataSource(data=dict(ts=[], IMon1=[], VMon1=[]))
source_huma = ColumnDataSource(data=dict(ts=[], HumA=[]))
source_humb = ColumnDataSource(data=dict(ts=[], HumB=[]))

tools = 'pan,reset,save,xbox_zoom,wheel_zoom, undo'
#tools = 'pan,xbox_select,reset,save,box_zoom, undo'
tools_secondary = 'pan,save,box_zoom,undo,yzoom_out'



#TODO: DatetimeTickFormatter


plotV = figure(plot_width=900, plot_height=300, tools=tools, x_axis_type='datetime', active_drag="xbox_zoom")
plotI = figure(plot_width=900, plot_height=300, tools=tools_secondary, x_axis_type='datetime', x_range = plotV.x_range, active_drag='pan')
plotHum = figure(plot_width=900, plot_height=300, tools=tools_secondary, x_axis_type='datetime', x_range = plotV.x_range, active_drag='pan')

line_opts = {
        'line_width': 2,
        'alpha': 0.6,
        }

for name, color in zip(["VMon1", "VMon2"], Colorblind8):
    plotV.line('ts', name, source=source_static, **line_opts, color = color, legend_label = name)
    plotV.circle('ts', name, size=4, source=source, color=color, fill_color = 'white', selection_color=color, legend_label = name)

for name, color in zip(["IMon1", "IMon2"], Colorblind8):
    plotI.line('ts', name, source=source_static, **line_opts, color = color, legend_label = name)

for name, _source, color in zip(["HumA","HumB"], [source_huma, source_humb],  Spectral8):
    plotHum.line('ts', name, source=_source, **line_opts, color = color, legend_label = name)

for p in plotV, plotI:
    p.legend.location = "top_left"
    p.legend.click_policy="hide"


def get_data():

    #TODO: get cached value, os.stat('fname').st_mtime
    date_parser = lambda col: pd.to_datetime(col, unit='s') #\
#            .tz_localize('UTC').tz_convert('Europe/Moscow')
    
    CSV_OPTS = { "sep": ';', "comment": '#',
            "header": None,
            "parse_dates":  ['ts'],
            "date_parser":  date_parser,
            }

    
    data = pd.read_csv( DATA_FILE, **CSV_OPTS,
            names = DATA_COLS,
#            index_col = ['ts'],
            )

    data_huma = pd.read_csv('huma_.csv', **CSV_OPTS, 
            names = ['ts', 'HumA']
            )

    data_humb = pd.read_csv('humb_.csv', **CSV_OPTS, 
            names = ['ts', 'HumB']
            )

    # Quick fix
    for x in data, data_huma, data_humb:
        x['ts'] = x['ts'] + pd.DateOffset(hours=3)

    return data, data_huma, data_humb

def update(selected=None):

    df, df_huma, df_humb = get_data()
    update_stats(df_huma)

    data = df[['ts', 'VMon1', 'VMon2', 'IMon1', 'IMon2']]

    source.data = data
    source_static.data = data

    source_huma.data = df_huma
    source_humb.data = df_humb


def update_stats(data):
    stats.text=data.to_csv(
            sep='\t',
            date_format="%s",
            )


stats = PreText(text='', width=500)
intro = Div(text='''<h1>MWPC IMon and VMon history</h1>
<p>Select controls on the right side of the plots.</p>
<p>Click on legend entries to hide the corresponding lines.</p>''')
layout = column(intro, plotV, plotI, plotHum)
#layout = column(intro, plotV, plotI, plotHum, stats)

# init
update()
curdoc().add_root(layout)
curdoc().title = "MWPC - HV"
