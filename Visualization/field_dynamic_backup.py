''' 
Present an interactive lineup explorer for Baseball
batting lineups, with a field visualization.

Use the ``bokeh serve`` command to run the example by executing:
    bokeh serve --show field_dynamic.py 
The visualization should then appear in your browser.

TODO:
[ ] Import player lists and add to dropdown
[ ] Import Markov chain commands
[ ] Find optimal batting lineup for each set of 9
[ ] Make interesting optimization 
[x] Make button to run the Markov chain 
		(in case user wants to change multiple positions)
[ ] Make labels default, e.g. `background_fill_color='white'`
[ ] Make Paragraph text wider than column (maybe gridLayout)
[ ] Include Select dropdown for team or league
[ ] Include radio button for DH vs pitcher
'''




#Import packages
import pandas as pd
import numpy as np
import math

#Import Bokeh modules
from bokeh.io import curdoc
from bokeh.layouts import row, column, widgetbox
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import Slider, TextInput, Select
from bokeh.models.widgets import Paragraph, Button, MultiSelect
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



# Import player and team names and data
player_names = pd.read_csv("../Baseball_Data/player_id.csv")
player_names = pd.concat([player_names['bref_id'], 
                          player_names['bref_name'], 
                          player_names['mlb_team'], 
                          player_names['mlb_team_long'], 
                          player_names['mlb_pos']], axis = 1)


team_codes = player_names['mlb_team_long']
team_codes = team_codes.drop_duplicates()
team_codes = team_codes.sort_values().tolist()
print(team_codes)
team_codes = [i for i in team_codes if i != "Anaheim Angels"]
print(team_codes)

team_select = MultiSelect(title="MLB Team:", value=["Minnesota Twins"],
                           options=team_codes)
team_selected_players = player_names.loc[player_names['mlb_team_long'] == "Minnesota Twins"] 





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


# Set up Select widgets for 9 positions:
"""
Position codes are as follows: P, C, CF, 1B, RF, OF, 3B, LF, DH, SS, 2B
"""
outfield = ["LF", "CF", "RF"]
infield = ["2B", "3B", "SS"]
pitch_dh = ["P", "DH"]

catcher_options  = team_selected_players.loc[team_selected_players['mlb_pos'] == "C"]
catcher_list     = [""]+[x for x in catcher_options['bref_name'].tolist() if str(x) != 'nan']
pitcher_dh_options=team_selected_players.loc[team_selected_players['mlb_pos'].isin(pitch_dh)]
pitcher_dh_list  = [""]+[x for x in pitcher_dh_options['bref_name'].tolist() if str(x) != 'nan']
first_options    = team_selected_players.loc[team_selected_players['mlb_pos'] == "1B"]
first_list       = [""]+[x for x in first_options['bref_name'].tolist() if str(x) != 'nan']
second_options   = team_selected_players.loc[team_selected_players['mlb_pos'].isin(infield)]
second_list      = [""]+[x for x in second_options['bref_name'].tolist() if str(x) != 'nan']
third_options    = team_selected_players.loc[team_selected_players['mlb_pos'].isin(infield)]
third_list       = [""]+[x for x in third_options['bref_name'].tolist() if str(x) != 'nan']
short_options    = team_selected_players.loc[team_selected_players['mlb_pos'].isin(infield)]
short_list       = [""]+[x for x in short_options['bref_name'].tolist() if str(x) != 'nan']
lfield_options   = team_selected_players.loc[team_selected_players['mlb_pos'].isin(outfield)]
lfield_list      = [""]+[x for x in lfield_options['bref_name'].tolist() if str(x) != 'nan']
cfield_options   = team_selected_players.loc[team_selected_players['mlb_pos'].isin(outfield)]
cfield_list      = [""]+[x for x in cfield_options['bref_name'].tolist() if str(x) != 'nan']
rfield_options   = team_selected_players.loc[team_selected_players['mlb_pos'].isin(outfield)]
rfield_list      = [""]+[x for x in rfield_options['bref_name'].tolist() if str(x) != 'nan']


select_catcher    = Select(title="Catcher:", 		value="", 
	options=catcher_list)
select_pitcher_dh = Select(title="Pitcher:", 		value="", 
	options=pitcher_dh_list)
select_first      = Select(title="First Base:", 	value="", 
	options=first_list)
select_second     = Select(title="Second Base", 	value="", 
	options=second_list)
select_third      = Select(title="Third Base", 		value="", 
	options=third_list)
select_short      = Select(title="Shortstop:", 		value="", 
	options=short_list)
select_lfield     = Select(title="Left Field:", 	value="", 
	options=lfield_list)
select_cfield     = Select(title="Center Field:",	value="", 
	options=cfield_list)
select_rfield     = Select(title="Right Field:", 	value="", 
	options=rfield_list)

team_text = Paragraph()
batting_order_text = Paragraph()
"""
batting_lineup_list = " ".join([select_pitcher_dh.value, select_catcher.value, 
				select_first.value, select_second.value, select_third.value, 
				select_short.value, select_lfield.value, select_cfield.value, 
				select_rfield.value])
batting_order_text.text = batting_lineup_list
"""

position_select_list = [select_pitcher_dh,select_catcher, select_first, 
                 select_second, select_third, select_short, select_lfield, 
                 select_cfield, select_rfield]






# Add labels to field plot
pitcher_dh_lab = Label(x=0, y=math.sqrt(2)/2, text = " "+select_pitcher_dh.value+" ", 
                   x_offset=0, y_offset=5, #render_mode='canvas',
                   border_line_color='black',
                   background_fill_color='white', 
                   text_align = 'center', # options are 'left', 'right', 'center'
                   text_baseline = "alphabetic")

catcher_lab = Label(x=0, y=0, text=' '+select_catcher.value+' ', 
                x_offset=0, y_offset=-10, border_line_color='black',
                background_fill_color='white', text_align = 'center', text_baseline = "alphabetic")

first_lab = Label(x=1, y=1, text=' '+select_first.value+' ',
              x_offset=-20, y_offset=5,  border_line_color='black',
              background_fill_color='white',  text_align = 'left', text_baseline = "alphabetic") 

second_lab = Label(x=0.2, y=1.8, text=' '+select_second.value+' ',
               x_offset=0, y_offset=0, border_line_color='black',
               background_fill_color='white', text_align = 'left', text_baseline = "alphabetic") 

third_lab = Label(x=-1, y=1, text=' '+select_third.value+' ',
              x_offset=20, y_offset=5,  border_line_color='black',
              background_fill_color='white',  text_align = 'right', text_baseline = "alphabetic") 

short_lab = Label(x=-0.2, y=1.8, text=' '+select_short.value+' ',
              x_offset=0, y_offset=0, border_line_color='black',
              background_fill_color='white', text_align = 'right', text_baseline = "alphabetic") 

lfield_lab = Label(x=-1.5, y=2.5, text=' '+select_lfield.value+' ',
               x_offset=0, y_offset=0, border_line_color='black',
               background_fill_color='white', text_align = 'center', text_baseline = "alphabetic") 

cfield_lab = Label(x=0, y=3, text=' '+select_cfield.value+' ',
               x_offset=0, y_offset=0, border_line_color='black',
               background_fill_color='white', text_align = 'center', text_baseline = "alphabetic") 

rfield_lab = Label(x=1.5, y=2.5, text=' '+select_rfield.value+' ',
               x_offset=0, y_offset=0, border_line_color='black',
               background_fill_color='white', text_align = 'center', text_baseline = "alphabetic") 

# Put text in field plot
field.add_layout(pitcher_dh_lab)
field.add_layout(catcher_lab)
field.add_layout(first_lab)
field.add_layout(second_lab)
field.add_layout(third_lab)
field.add_layout(short_lab)
field.add_layout(lfield_lab)
field.add_layout(cfield_lab)
field.add_layout(rfield_lab)


# Set up callbacks
def update_player_options():	
	#print(team_codes)
	print(team_select.value)
	team_selected_players = player_names.loc[player_names['mlb_team_long'].isin(team_select.value)] 
	print(team_selected_players)

	outfield = ["LF", "CF", "RF"]
	infield = ["2B", "3B", "SS"]
	pitch_dh = ["P", "DH"]
	
	catcher_options  = team_selected_players.loc[team_selected_players['mlb_pos'] == "C"]
	catcher_list     = [""]+[x for x in catcher_options['bref_name'].tolist() if str(x) != 'nan']
	select_catcher.options = catcher_list

	pitcher_dh_options=team_selected_players.loc[team_selected_players['mlb_pos'].isin(pitch_dh)]
	pitcher_dh_list  = [""]+[x for x in pitcher_dh_options['bref_name'].tolist() if str(x) != 'nan']
	select_pitcher_dh.options = pitcher_dh_list
	
	first_options    = team_selected_players.loc[team_selected_players['mlb_pos'] == "1B"]
	first_list       = [""]+[x for x in first_options['bref_name'].tolist() if str(x) != 'nan']
	select_first.options = first_list

	second_options   = team_selected_players.loc[team_selected_players['mlb_pos'].isin(infield)]
	second_list      = [""]+[x for x in second_options['bref_name'].tolist() if str(x) != 'nan']
	select_second.options = second_list

	third_options    = team_selected_players.loc[team_selected_players['mlb_pos'].isin(infield)]
	third_list       = [""]+[x for x in third_options['bref_name'].tolist() if str(x) != 'nan']
	select_third.options = third_list

	short_options    = team_selected_players.loc[team_selected_players['mlb_pos'].isin(infield)]
	short_list       = [""]+[x for x in short_options['bref_name'].tolist() if str(x) != 'nan']
	select_short.options = short_list

	lfield_options   = team_selected_players.loc[team_selected_players['mlb_pos'].isin(outfield)]
	lfield_list      = [""]+[x for x in lfield_options['bref_name'].tolist() if str(x) != 'nan']
	select_lfield.options = lfield_list

	cfield_options   = team_selected_players.loc[team_selected_players['mlb_pos'].isin(outfield)]
	cfield_list      = [""]+[x for x in cfield_options['bref_name'].tolist() if str(x) != 'nan']
	select_cfield.options = cfield_list

	rfield_options   = team_selected_players.loc[team_selected_players['mlb_pos'].isin(outfield)]
	rfield_list      = [""]+[x for x in rfield_options['bref_name'].tolist() if str(x) != 'nan']
	select_rfield.options = rfield_list





def update_field(attrname, old, new):
    # Get the current Select values
	pitcher_dh_lab.text = ' '+ select_pitcher_dh.value	+' '
	catcher_lab.text    = ' '+ select_catcher.value		+' '
	first_lab.text      = ' '+ select_first.value		+' '
	second_lab.text     = ' '+ select_second.value		+' '
	third_lab.text      = ' '+ select_third.value		+' '
	short_lab.text      = ' '+ select_short.value		+' '
	lfield_lab.text     = ' '+ select_lfield.value		+' '
	cfield_lab.text     = ' '+ select_cfield.value		+' '
	rfield_lab.text     = ' '+ select_rfield.value		+' '


# Call the update_field function whenever a Select is changed
for w in position_select_list:
    w.on_change('value', update_field)


#Make button
lineup_button = Button(label="Update Lineup")
team_button=Button(label = "Reset Roster")


# Callback for button
def update_lineup():
	update_player_options()
	# Check to see if team has changed
	# Do lineup optimization here:
	#
	#
 	#
	#
	#
	#

	# Print text for batting lineup
	batting_lineup_list = ", ".join([select_pitcher_dh.value, 
				select_catcher.value, select_first.value, select_second.value, 
				select_third.value, select_short.value, select_lfield.value,
				select_cfield.value, select_rfield.value])
	team_list = ", ".join([str(i) for i in team_select.value])
	batting_order_text.text = "PLAYERS: \n" + batting_lineup_list
	team_text.text = "TEAMS: \n" + team_list


# Callback for team select button
def update_players():
	update_player_options()
	select_pitcher_dh.value = ""
	select_catcher.value = ""
	select_first.value = ""
	select_second.value = ""
	select_third.value = ""
	select_short.value = ""
	select_lfield.value = ""
	select_cfield.value = ""
	select_rfield.value = ""
	pitcher_dh_lab.text = ' '+ select_pitcher_dh.value	+' '
	catcher_lab.text    = ' '+ select_catcher.value		+' '
	first_lab.text      = ' '+ select_first.value		+' '
	second_lab.text     = ' '+ select_second.value		+' '
	third_lab.text      = ' '+ select_third.value		+' '
	short_lab.text      = ' '+ select_short.value		+' '
	lfield_lab.text     = ' '+ select_lfield.value		+' '
	cfield_lab.text     = ' '+ select_cfield.value		+' '
	rfield_lab.text     = ' '+ select_rfield.value		+' '


# Call the update_lineup function whenever button is pushed
lineup_button.on_click(update_lineup)
team_button.on_click(update_players)


# Make widgetbox for position select dropdowns
position_select_widgetbox = widgetbox(position_select_list + [lineup_button])

curdoc().add_root(column(row(column(team_select, team_button), position_select_widgetbox, field), team_text, batting_order_text))
curdoc().title = "Baseball Markov Chain"






