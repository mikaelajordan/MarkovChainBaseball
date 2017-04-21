import numpy as np
import pandas as pd
import pickle
import os


os.chdir('/home/david/Desktop/Documents/GitRepos/MarkovChainBaseball')


def import_raw_batting_data():
    """
    Import Raw data from 
    """
    
    ### Field names
    data_cols = ['gameid', 'visteam', 'inning', 'batteam', 'outs', 'balls', 
        'strikes', 'visscore', 'homescore', 'resbatter', 'resbatterhand', 'respitcher', 
        'respitcherhand', 'firstrunner', 'secondrunner', 'thirdrunner', 'eventtext', 'leadoffflag', 
        'pinchhitflag', 'defensivepos', 'lineuppos', 'eventtype', 'battereventflag', 'abflag', 
        'hitvalue', 'SHflag', 'SFflag', 'outsonplay', 'RBIonplay', 'wildpitchflag', 
        'passedballflag', 'numerrors', 'batterdest', 'runon1dest', 'runon2dest', 'runon3dest']
    
    
    os.chdir('2016')
    batting = pd.read_csv('ana.txt', header=None)
    for filename in os.listdir():
        df = pd.read_csv(filename, header=None)
        print(filename, df.shape)
        batting = batting.append(df)
    os.chdir('..')
    batting.columns = data_cols
    return(batting)

batting = import_raw_batting_data()



def make_empty_transition_matrix():
    """
    Initialize a transition matrix with row and column names
    """
    state_vector = pd.Series([
                    (0,''), (0,'1'), (0,'2'), (0,'3'), (0,'12'), (0,'13'), (0,'23'), (0,'123'), 
                    (1,''), (1,'1'), (1,'2'), (1,'3'), (1,'12'), (1,'13'), (1,'23'), (1,'123'),
                    (2,''), (2,'1'), (2,'2'), (2,'3'), (2,'12'), (2,'13'), (2,'23'), (2,'123'),
                    '0', '1', '2', '3'])
    t_matrix = pd.DataFrame(0, columns=state_vector, index = state_vector)
    #print(t_matrix.shape)
    return(t_matrix)

print(make_empty_transition_matrix())




def find_team_atbats(team_code):
    """
    Give a team code, return a dataframe with all the team's at bats
    """
    visiting_atbats = batting[(batting['visteam'] == team_code)&(batting['batteam'] == 0)]
    home_atbats = batting[(batting['gameid'].str.contains(team_code)) & (batting['batteam'] == 1)]
    return(home_atbats.append(visiting_atbats))

min_atbats = find_team_atbats("MIN")





def find_states(batting_row):
    """
    Given a row from the data, interpret the starting and ending state
    """
    # Starting outs and runners
    start_outs = batting_row.outs
    start_runners = ""
    if not pd.isnull(batting_row.firstrunner):
        start_runners+="1"
    if not pd.isnull(batting_row.secondrunner):
        start_runners+="2"
    if not pd.isnull(batting_row.thirdrunner):
        start_runners+="3" 
        
    # Ending outs and runners
    end_outs = start_outs + batting_row.outsonplay
    destinations = [batting_row.batterdest, batting_row.runon1dest, batting_row.runon2dest, batting_row.runon3dest]
    
    if(end_outs<3):
        end_runners = ""
        if 1 in destinations:
            end_runners+="1"
        if 2 in destinations:
            end_runners+="2"
        if 3 in destinations:
            end_runners+="3" 
        end_state = (end_outs, end_runners)
    else:
        end_state = str(sum(pd.Series(destinations)>4))
    return([(start_outs, start_runners), end_state])
    
single_transition = find_states(min_atbats.iloc[1])
print(single_transition)
print(single_transition[0])
print(single_transition[1])


def make_transition_matrix(batting_data):
    """
    Given batting data, create a transition matrix
    """
    t_matrix = make_empty_transition_matrix()
    for index, row in (batting_data.iterrows()):
        transition = find_states(row)
        t_matrix.at[transition[0],transition[1]]+=1
    return(t_matrix)
    

#min_transition = make_transition_matrix(min_atbats.iloc[:100].iterrows())
min_transition = make_transition_matrix(min_atbats)
print(min_transition)
