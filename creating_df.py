import numpy as np
import pandas as pd
import pickle
import os


### Field names
cols = ['gameid', 'visteam', 'inning', 'batteam', 'outs', 'balls', 'strikes', 'visscore', 'homescore', 'resbatter', 'resbatterhand', 'respitcher', 'respitcherhand', 'firstrunner', 'secondrunner', 'thirdrunner', 'eventtext', 'leadoffflag', 'pinchhitflag', 'defensivepos', 'lineuppos', 'eventtype', 'battereventflag', 'abflag', 'hitvalue', 'SHflag', 'SFflag', 'outsonplay', 'RBIonplay', 'wildpitchflag', 'passedballflag', 'numerrors', 'batterdest', 'runon1dest', 'runon2dest', 'runon3dest']

with open('attributes.txt', "wb") as fp:
    pickle.dump(cols, fp)

## To load the column names 
with open('attributes.txt', "rb") as fp:
    b = pickle.load(fp)
    
batting = []
for filenames in os.listdir('/Users/mikaelajordan/Documents/Projects/MarkovChainBaseball/2016'):
    name = os.path.splitext(filename)[0]
    df = pd.read_csv(filename
    
    
