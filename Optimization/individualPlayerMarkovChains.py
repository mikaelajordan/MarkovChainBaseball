import numpy as np
import pandas as pd
import os
import itertools
from markov_functions import *


def find_top_batters(team_code, n):
    batting = import_raw_batting_data()
    team = find_team_atbats(team_code, batting)
    topPlayers = team['resbatter'].value_counts()[0:n]
    return(topPlayers.index.tolist())
#
yankHitters = find_top_batters('NYA', 9)
print(len(yankHitters))
# yanksMarkov = make_team_transition_matrix('NYA')
# print(yanksMarkov.keys())
print(list(itertools.permutations(list(yankHitters), 9)))


def individual_markov(top_batter_list, team_dictionary, iterations=25):
    battingOrders = list(itertools.combinations(top_batter_list, 9))
    estimatedRuns = []
    for order in battingOrders:
        x0=np.concatenate([[1], np.zeros(27)])
        print(x0)
        x = [x0]
        for i in range(1,(iterations)):
            state = np.matmul(team_dictionary[order[i%9]], x[i-1])
            x += [state]
            # print(state.shape)
        # print(x)
        Q = []
        for i in range(0,(len(x)-1)):
            # runs = np.matmul(x[i], np.matmul(run_matrix(), x[i+1]))
            runs = np.matmul(np.matmul(x[i], run_matrix()), x[i+1])
            print(runs.shape)
            print(runs)
            Q += [runs]
        runsTotal = sum(Q)*9
        print(runsTotal)
        estimatedRuns += [runsTotal]
    print(estimatedRuns)
    topOrder = np.argmax(estimatedRuns)
    print(topOrder)
    highRuns = max(estimatedRuns)
    print(highRuns)
    runDict = {'Best Order': battingOrders[topOrder], 'Associated Run Count': highRuns}
    return(runDict)

# yanksRuns = individual_markov(yankHitters, yanksMarkov, iterations=25)
# print(yanksRuns)
# print(len(list(itertools.combinations(yankHitters, 9))))
# print(len(yanksRuns))

# os.chdir('../Baseball_Data/Play_by_Play/')
# teams = [x.split('.')[0].upper() for x in os.listdir()]
# print(teams)
# print(len(teams))
#
# totalBattingDictionary = {}
# for teamname in teams:
#     print(teamname)
#     hitters = find_top_batters(teamname, 15)
#     markov = make_team_transition_matrix(teamname)
#     runs = individual_markov(hitters, markov, 25)
#     totalBattingDictionary[teamname] = runs['Associated Run Count'].append(runs['Best Order'])
