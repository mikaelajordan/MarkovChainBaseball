''' 
Present an interactive lineup explorer for Baseball
batting lineups, with a field visualization.

Use the ``bokeh serve`` command to run the example by executing:
    bokeh serve --show field_dynamic.py 
The visualization should then appear in your browser.

TODO:
[ ] Import player lists
[ ] Import Markov chain commands
[ ] Find optimal batting lineup for each set of 9
[ ] Make interesting optimization 
[x] Make button to run the Markov chain 
		(in case user wants to change multiple positions)
[ ] Make Paragraph text wider than column

'''


#Import packages
import pandas as pd
import numpy as np
import math

#Import Bokeh modules
from bokeh.io import curdoc
from bokeh.layouts import row, column, widgetbox
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import Slider, TextInput, Select, Paragraph, Button
from bokeh.plotting import figure

from bokeh.models import HoverTool, Legend
from bokeh.plotting import figure, show
from bokeh.models import Range1d, LabelSet, Label
from bokeh.io import vform


# Import player lists and transition matrices and probs some other stuff here:
#
#
#
#
#
#
#
#


# Draw field plot
field = figure(tools=[],
            width=650, height=650, toolbar_location="above")
field.set(x_range=Range1d(-3, 3), y_range=Range1d(-1, 5))
field.axis.visible = False
field.grid.grid_line_alpha = 0.0 

field.wedge(x=0, y=0, radius=3.5, 
		start_angle=45-1.4995, end_angle=135+1.4995,
		color="Green", line_color = "black", alpha = 0.6, #also try or LimeGreen
		start_angle_units="deg", end_angle_units="deg")
field.patch(x=[0,1,0,-1], y=[0,1,2,1], line_color = "black", color="tan")


# Set up widgets for 9 positions:
select_catcher    = Select(title="Catcher:", 		value="bar", options=["Jason Castro", "bar", "baz", "quux", "Dude with really long name"])
select_pitcher_dh = Select(title="Pitcher:", 		value="baz", options=["Santana", "bar", "baz", "quux", "Dude with really long name"])
select_first      = Select(title="First Base:", 	value="quux", options=["Joe Mauer", "bar", "baz", "quux", "Dude with really long name"])
select_second     = Select(title="Second Base", 	value="Brian Dozier", options=["Brian Dozier", "bar", "baz", "quux", "Dude with really long name"])
select_third      = Select(title="Third Base", 		value="bar", options=["Brian Dozier", "bar", "baz", "quux", "Dude with really long name"])
select_short      = Select(title="Shortstop:", 		value="bar", options=["Brian Dozier", "bar", "baz", "quux", "Dude with really long name"])
select_lfield     = Select(title="Left Field:", 	value="bar", options=["Brian Dozier", "bar", "baz", "quux", "Dude with really long name"])
select_cfield     = Select(title="Center Field:",	value="bar", options=["Brian Dozier", "bar", "baz", "quux", "Dude with really long name"])
select_rfield     = Select(title="Right Field:", 	value="bar", options=["Brian Dozier", "bar", "baz", "quux", "Dude with really long name"])

output = Paragraph()
batting_lineup_list = " ".join([select_pitcher_dh.value, select_catcher.value, select_first.value, 
                 select_second.value, select_third.value, select_short.value, select_lfield.value, 
                 select_cfield.value, select_rfield.value])
output.text = batting_lineup_list

position_select_list = [select_pitcher_dh,select_catcher, select_first, 
                 select_second, select_third, select_short, select_lfield, 
                 select_cfield, select_rfield]


# Make player text Labels
pitcher_dh = Label(x=0, y=math.sqrt(2)/2, text = " "+select_pitcher_dh.value+", ", 
                   x_offset=0, y_offset=5, #render_mode='canvas',
                   border_line_color='black',
                   background_fill_color='white', 
                   text_align = 'center', # options are 'left', 'right', 'center'
                   text_baseline = "alphabetic")

catcher = Label(x=0, y=0, text=' '+select_catcher.value+' ', 
                x_offset=0, y_offset=-10, border_line_color='black',
                background_fill_color='white', text_align = 'center', text_baseline = "alphabetic")

first = Label(x=1, y=1, text=' '+select_first.value+' ',
              x_offset=-15, y_offset=5,  border_line_color='black',
              background_fill_color='white',  text_align = 'left', text_baseline = "alphabetic") 

second = Label(x=0.2, y=1.8, text=' '+select_second.value+' ',
               x_offset=0, y_offset=0, border_line_color='black',
               background_fill_color='white', text_align = 'left', text_baseline = "alphabetic") 

third = Label(x=-1, y=1, text=' '+select_third.value+' ',
              x_offset=15, y_offset=5,  border_line_color='black',
              background_fill_color='white',  text_align = 'right', text_baseline = "alphabetic") 

short = Label(x=-0.2, y=1.8, text=' '+select_short.value+' ',
              x_offset=0, y_offset=0, border_line_color='black',
              background_fill_color='white', text_align = 'right', text_baseline = "alphabetic") 

lfield = Label(x=-1.5, y=2.5, text=' '+select_lfield.value+' ',
               x_offset=0, y_offset=0, border_line_color='black',
               background_fill_color='white', text_align = 'center', text_baseline = "alphabetic") 

cfield = Label(x=0, y=3, text=' '+select_cfield.value+' ',
               x_offset=0, y_offset=0, border_line_color='black',
               background_fill_color='white', text_align = 'center', text_baseline = "alphabetic") 

rfield = Label(x=1.5, y=2.5, text=' '+select_rfield.value+' ',
               x_offset=0, y_offset=0, border_line_color='black',
               background_fill_color='white', text_align = 'center', text_baseline = "alphabetic") 

# Put text in field plot
field.add_layout(catcher)
field.add_layout(pitcher_dh)
field.add_layout(first)
field.add_layout(second)
field.add_layout(third)
field.add_layout(short)
field.add_layout(lfield)
field.add_layout(cfield)
field.add_layout(rfield)


# Set up callbacks
def update_field(attrname, old, new):

    # Get the current Select values
	pitcher_dh.text = ' '+ select_pitcher_dh.value	+' '
	catcher.text    = ' '+ select_catcher.value		+' '
	first.text      = ' '+ select_first.value		+' '
	second.text     = ' '+ select_second.value		+' '
	third.text      = ' '+ select_third.value		+' '
	short.text      = ' '+ select_short.value		+' '
	lfield.text     = ' '+ select_lfield.value		+' '
	cfield.text     = ' '+ select_cfield.value		+' '
	rfield.text     = ' '+ select_rfield.value		+' '


# Call the update_field function whenever a Select is changed
for w in position_select_list:
    w.on_change('value', update_field)

#Make button
button = Button(label="Update Lineup")


# Callback for button
def update_lineup():
	# Do lineup optimization here:
	#
	#
 	#
	#
	#
	#

	# Print text for batting lineup
	batting_lineup_list = ", ".join([select_pitcher_dh.value, select_catcher.value, select_first.value, 
                 select_second.value, select_third.value, select_short.value, select_lfield.value, 
                 select_cfield.value, select_rfield.value])
	output.text = batting_lineup_list

# Call the update_lineup function whenever button is pushed
button.on_click(update_lineup)


# Make widgetbox for position select dropdowns
position_select_widgetbox = widgetbox(position_select_list + [button])

curdoc().add_root(column(row(position_select_widgetbox, field), output))
curdoc().title = "Baseball Markov Chain"






