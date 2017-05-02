# David Ebert
# 22 April 2017
# Show team expected runs vs actual runs for 2016
# Based on "Weather" Bokeh example
# Data from team markov chain functions, saved as 'team_data.csv' in folder

# To run from terminal:
# bokeh serve --show team_visualization.py

from os.path import join, dirname
import pandas as pd

from bokeh.io import curdoc
from bokeh.layouts import row, column
from bokeh.models import ColumnDataSource, DataRange1d, Select
from bokeh.plotting import figure

from bokeh.io import show, vform, curdoc
from bokeh.plotting import figure
from bokeh.models import HoverTool
from bokeh.models import Range1d
from bokeh.models import ColumnDataSource, CustomJS
from bokeh.models.widgets import Select
from bokeh.models.annotations import Label


raw_data = pd.read_csv('../Baseball_Data/team_2016_data_with_pred.csv')

def get_dataset(league_option):
    if league_option == "All Teams":
        important_rows = raw_data
    else:
        important_rows = raw_data[(raw_data['league'] == league_option)]

    expected_runs = list(important_rows['expected_runs'])
    actual_runs = list(important_rows['actual_runs'])
    team = list(important_rows.index)
    league= list(important_rows['league'])
    fun_source = ColumnDataSource(
        data={
            "expected_runs" : expected_runs,
            "actual_runs" : actual_runs,
            "team" : team,
            "league" : league
        }
    )
    return(fun_source)


def make_plot(source, title_text, league):

    hover = HoverTool(
        tooltips=[
            ("Team", "@team"),
            ("Expected Runs", "@expected_runs"),
            ("Actual Runs", "@actual_runs"),
            ("League", "@league")
        ]
    )

    p = figure(plot_width=800, plot_height=800, tools=[hover], title = title_text)
    p.x_range = Range1d(3, 7)
    p.y_range = Range1d(3, 7)

    p.xaxis.axis_label = "Expected Runs Per Game"
    p.yaxis.axis_label = "Actual Runs Per Game"
    
    p.circle(x="expected_runs", y="actual_runs", size=15, line_color="black", 
        fill_color="firebrick", fill_alpha=0.5, source=source)
    p.line(x=[3,9],y=[3,9], line_width=4, line_color="navy", alpha=0.7)
    p.line(x=[3,9],y=[3,9], line_width=175, line_color="navy", alpha=0.05)

    print(league)
    if 1==7:
        print("hello world")
        p.add_layout(Label(x=6.638, y=5.42, x_offset=-17, 
            y_offset=10, text="BOS", text_color = "black"))
        p.add_layout(Label(x=5.121, y=3.77, x_offset=-15, 
            y_offset=-30, text="PHI", text_color = "black"))
        p.add_layout(Label(x=4.705, y=4.030, x_offset=-17, 
            y_offset=-30, text="OAK", text_color = "black"))
        p.add_layout(Label(x=5.917, y=4.14, x_offset=-12, 
            y_offset=-30, text="MIL", text_color = "black"))
    return p # show the results


def update_plot(attrname, old, new):
    league = league_select.value
    plot.title.text = "Markov Chain Run Prediction for " + league

    src = get_dataset(league)
    source.data.update(src.data) # This is the part of the code I understand least


league = 'All Teams'
league_options = ['All Teams', 'AL', 'NL']

league_select = Select(value=league, title='League', options=league_options)
league_select.on_change('value', update_plot) 

source = get_dataset(league)
plot = make_plot(source, "Markov Chain Run Prediction for " + league, league)

controls = column(league_select)
curdoc().add_root(row(plot, controls))
curdoc().title = "Team Markov Chain Plot"


