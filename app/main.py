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
from bokeh.palettes import Colorblind8


DATA_FILE = path_join(dirname(__file__),'../', 'hv.csv')
DATA_COLS = ("ts", "VMon0", "IMon0", "VMon1", "IMon1", "VMon2", "IMon2")

source = ColumnDataSource(data=dict(ts=[], IMon1=[], VMon1=[]))
source_static = ColumnDataSource(data=dict(ts=[], IMon1=[], VMon1=[]))

tools = 'pan,reset,save,box_zoom, undo'
#tools = 'pan,xbox_select,reset,save,box_zoom, undo'
tools_secondary = 'pan,save,box_zoom,undo'


#TODO: DatetimeTickFormatter


plotV = figure(plot_width=900, plot_height=300, tools=tools, x_axis_type='datetime', active_drag="box_zoom")

plotI = figure(plot_width=900, plot_height=300, tools=tools_secondary, x_axis_type='datetime', x_range = plotV.x_range, active_drag='pan')


line_opts = {
        'line_width': 2,
        'alpha': 0.6,
        }

for name, color in zip(["VMon1", "VMon2"], Colorblind8):
    plotV.line('ts', name, source=source_static, **line_opts, color = color, legend_label = name)
    plotV.circle('ts', name, size=4, source=source, color=color, fill_color = 'white', selection_color=color, legend_label = name)

for name, color in zip(["IMon1", "IMon2"], Colorblind8):
    plotI.line('ts', name, source=source_static, **line_opts, color = color, legend_label = name)

for p in plotV, plotI:
    p.legend.location = "top_left"
    p.legend.click_policy="hide"


def get_data():

    #TODO: get cached value, os.stat('fname').st_mtime
    date_parser = lambda col: pd.to_datetime(col, unit='s') #\
#            .tz_localize('UTC').tz_convert('Europe/Moscow')

    data = pd.read_csv( DATA_FILE,
            sep=';', comment='#',
            header=None,
            names = DATA_COLS,
            parse_dates = ['ts'],
            date_parser = date_parser,
#            index_col = ['ts'],
            )

    # Quick fix
    data['ts'] = data['ts'] + pd.DateOffset(hours=3)

    return data

def update(selected=None):

    df = get_data()
    update_stats(df)

    # convert ts to ts-local
    data = df[['ts', 'VMon1', 'VMon2', 'IMon1', 'IMon2']]

    source.data = data
    source_static.data = data


def update_stats(data):
    stats.text=data.to_csv(
            sep='\t',
            date_format="%s",
            )


stats = PreText(text='', width=500)
intro = Div(text='''<h1>MWPC IMon and VMon history</h1>
<p>Select controls on the right side of the plots.</p>
<p>Click on legend entries to hide the corresponding lines.</p>''')
layout = column(intro, plotV, plotI)
#layout = column(intro, plotV, plotI, stats)

# init
update()
curdoc().add_root(layout)
curdoc().title = "MWPC - HV"
