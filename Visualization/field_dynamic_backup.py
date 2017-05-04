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
import random
import itertools

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


players_df=pd.read_csv("../Baseball_Data/predicted_player_types.csv", index_col=0)

trans_type=[(),(),(),()]
for i in range(0,4):
	trans_type[i]=pd.read_csv("../Baseball_Data/transition_matrix_type%d"%i,index_col=0)

def run_matrix():
	states=[(0,''), (0,'1'), (0,'2'), (0,'3'), (0, '12'), (0,'13'), (0,'23'), (0,'123'), 
			(1,''), (1,'1'), (1,'2'), (3,'3'), (1, '12'), (1,'13'), (1,'23'), (1,'123'), 
			(2,''), (2,'1'), (2,'2'), (2,'3'), (2, '12'), (2,'13'), (2,'23'),(2,'123'), '0', '1', '2', '3']
	R1=pd.DataFrame(np.reshape(np.zeros(28*28), (28,28)))
	R1.columns=states
	R1.index=states
	for i in states:
		if len(i)==2:
			i_out=i[0]
			i_runners=len(str(i[1]))
			for j in states:
				if len(j)==2:
					j_out=j[0]
					j_runners=len(str(j[1]))
					R1.ix[i,j]=(i_out+i_runners+1)-(j_out+j_runners)
				else:
					R1.ix[i,j]=int(j)
		else:
			for j in states:
				R1.ix[i,j]=int(i)
		R1[R1<0]=0
	return(R1)


def pick_your_team_markov(list_of_nine, decimal_places = 10):
	if len(list_of_nine) != 9:
		return({"runsper9":"ERROR: 9 distinct batters required", "batting_lineup_used":list_of_nine})
	#Making a dictionary with player combo transition matrix
	matrix_list=[]
	for player in list_of_nine:
		probs=players_df.ix[player]
		mat=[(),(),(),()]
		for i in range(0,4):
			mat[i]=trans_type[i].multiply(probs[i])
		df_sum=((mat[0].add(mat[1])).add(mat[2])).add(mat[3])
		matrix_list+=[df_sum]
	trans_dict = dict(zip(list_of_nine, matrix_list))
	possible_orders=list(itertools.permutations(list_of_nine, 9))
	randnum=random.randrange(0,362000,1)
	order=possible_orders[randnum]
	for i in possible_orders:
		order_list=[trans_dict[x] for x in order]
		x0=np.concatenate([[1], np.zeros(27)])
		x=[x0]
		for i in range(1,10):
			vec=np.matmul(x[i-1],order_list[i-1])
			x+=[vec]
		Q=[]
		for i in range(0, len(x)-1):
			runs=np.matmul(np.matmul(x[i], run_matrix()), x[i+1])
			Q+=[runs]    
		return({"runsper9":np.round(sum(Q)*9, decimal_places), "batting_lineup_used":order})



# Import player and team names and data
player_names = pd.read_csv("../Baseball_Data/player_id.csv")
player_names = pd.concat([player_names['bref_id'], 
                          player_names['bref_name'], 
                          player_names['mlb_team'], 
                          player_names['mlb_team_long'], 
                          player_names['mlb_pos']], axis = 1)

player_names = player_names[player_names['bref_id'].isin(players_df.index)]

team_codes = player_names['mlb_team_long']
team_codes = team_codes.drop_duplicates()
team_codes = team_codes.sort_values().tolist()
team_codes = [i for i in team_codes if i != "Anaheim Angels"]

# Initialize team to Rangers
team_select = MultiSelect(title="MLB Team:", value=["Texas Rangers"], options=team_codes)
team_selected_players = player_names.loc[player_names['mlb_team_long'] == "Texas Rangers"] 


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

pitcher_dh_options=team_selected_players
pitcher_dh_list  = [""]+[x for x in pitcher_dh_options['bref_name'].tolist() if str(x) != 'nan']
catcher_options  = team_selected_players.loc[team_selected_players['mlb_pos'] == "C"]
catcher_list     = [""]+[x for x in catcher_options['bref_name'].tolist() if str(x) != 'nan']
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


# Initialize player selects to available Rangers' players
select_pitcher_dh = Select(title="Pitcher/DH:", 	value="Prince Fielder", 
	options=pitcher_dh_list)
select_catcher    = Select(title="Catcher:", 		value="Jonathan Lucroy", 
	options=catcher_list)
select_first      = Select(title="First Base:", 	value="Mike Napoli", 
	options=first_list)
select_second     = Select(title="Second Base", 	value="Rougned Odor", 
	options=second_list)
select_third      = Select(title="Third Base", 		value="Adrian Beltre", 
	options=third_list)
select_short      = Select(title="Shortstop:", 		value="Elvis Andrus", 
	options=short_list)
select_lfield     = Select(title="Left Field:", 	value="Carlos Gomez", 
	options=lfield_list)
select_cfield     = Select(title="Center Field:",	value="Nomar Mazara", 
	options=cfield_list)
select_rfield     = Select(title="Right Field:", 	value="Shin-Soo Choo", 
	options=rfield_list)

team_text = Paragraph(width = 1000)
batting_order_text = Paragraph(width = 1000)
runsper9_text = Paragraph(width = 1000)
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
	team_selected_players = player_names.loc[player_names['mlb_team_long'].isin(team_select.value)] 

	outfield = ["LF", "CF", "RF"]
	infield = ["2B", "3B", "SS"]
	pitch_dh = ["P", "DH"]
	
	catcher_options  = team_selected_players.loc[team_selected_players['mlb_pos'] == "C"]
	catcher_list     = [""]+[x for x in catcher_options['bref_name'].tolist() if str(x) != 'nan']
	select_catcher.options = catcher_list

	pitcher_dh_options=team_selected_players
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
lineup_button = Button(label="Make Random Lineup")
team_button=Button(label = "Reset Roster")


# Callback for lineup button
def update_lineup():
	update_player_options()
	team_selected_players = player_names.loc[player_names['mlb_team_long'].isin(team_select.value)]
	
	# Print text for batting lineup
	batting_lineup_list = ", ".join([select_pitcher_dh.value, 
				select_catcher.value, select_first.value, select_second.value, 
				select_third.value, select_short.value, select_lfield.value,
				select_cfield.value, select_rfield.value])
	
	batting_lineup_bref_list = team_selected_players[team_selected_players['bref_name'].isin([x for x in batting_lineup_list.split(", ")])]
	batting_lineup_bref_list = batting_lineup_bref_list['bref_id'].tolist()
	result = pick_your_team_markov(batting_lineup_bref_list, decimal_places = 3)

	# Update text values for team, players, and runsper9
	team_list = ", ".join([str(i) for i in team_select.value])
	team_text.text = "MLB TEAMS: \n" + team_list

	random_batting_lineup = pd.DataFrame({'lineup_position': range(1,10),
										'bref_id': result['batting_lineup_used']})

	random_batting_lineup = team_selected_players.join(random_batting_lineup.set_index('bref_id'), on = "bref_id")
	random_batting_lineup = random_batting_lineup.sort(['lineup_position']).dropna(axis = 0, how = "any")['bref_name'].tolist()
	position_nums = [" (1) ", ",  (2) ", ",  (3) ", ",  (4) ", ",  (5) ", ",  (6) ", ",  (7) ", ",  (8) ", ",  (9) "]
	res = [None]*(len(position_nums)+len(random_batting_lineup))
	res[::2] = position_nums
	res[1::2] = random_batting_lineup
	batting_order_text.text = "RANDOM BATTING LINEUP: \n" + "".join([str(x) for x in res])
	
	runsper9_text.text = "EXPECTED RUNS PER 9 INNINGS: \n" + str(result['runsper9'])


# Callback for team select button
def update_players():
	update_player_options()
	select_pitcher_dh.value = ""
	select_catcher.value= ""
	select_first.value  = ""
	select_second.value = ""
	select_third.value  = ""
	select_short.value  = ""
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
	team_text.text = ""
	batting_order_text.text = ""
	runsper9_text.text = ""

# Call the update_lineup function whenever button is pushed
lineup_button.on_click(update_lineup)
team_button.on_click(update_players)


# Make widgetbox for position select dropdowns
position_select_widgetbox = widgetbox(position_select_list + [lineup_button])

curdoc().add_root(column(row(column(team_select, team_button), position_select_widgetbox, field), team_text, batting_order_text, runsper9_text))
curdoc().title = "Baseball Markov Chain"






