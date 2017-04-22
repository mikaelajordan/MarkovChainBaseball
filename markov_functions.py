import numpy as np
import pandas as pd
import pickle
import os




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
    batting=pd.DataFrame()
    for filename in os.listdir():
        df = pd.read_csv(filename, header=None)
        print(filename, df.shape)
        batting = batting.append(df)
    os.chdir('..')
    batting.columns = data_cols
    return(batting)




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





def find_team_atbats(team_code, batting_data):
    """
    Give a team code, return a dataframe with all the team's at bats
    """
    visiting_atbats = batting_data[(batting_data['visteam'] == team_code)&(batting_data['batteam'] == 0)]
    home_atbats = batting_data[(batting_data['gameid'].str.contains(team_code)) & (batting_data['batteam'] == 1)]
    return(home_atbats.append(visiting_atbats))






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




def make_transition_matrix(batting_data):
    """
    Given batting data, create a transition matrix
    """
    t_matrix = make_empty_transition_matrix()
    for index, row in (batting_data.iterrows()):
        transition = find_states(row)
        t_matrix.at[transition[0],transition[1]]+=1
    for i in range(0, len(t_matrix)):
        row_sum=sum(t_matrix.iloc[i,:])
        for j in range(0, len(t_matrix)):
            if row_sum!=0:
                t_matrix.iloc[i,j]= t_matrix.iloc[i,j]/row_sum
    return(t_matrix)

def prob_vec(transition_mat, iterations):
    x0=np.concatenate([[1], np.zeros(27)])
    x=[x0]
    for i in range(1,iterations):
        vec=np.matmul(x[i-1],transition_mat)
        x+=[vec]
    return x

def predicted_runs(probability_vectors):
    Q=[]
    for i in range(0, len(probability_vectors)-1):
        runs=np.matmul(np.matmul(probability_vectors[i], run_matrix()), probability_vectors[i+1])
        Q+=[runs]
    return(Q)


def team_markov(transition_matrix, iterations=25):
    x0=np.concatenate([[1], np.zeros(27)])
    x=[x0]
    for i in range(1,iterations):
        vec=np.matmul(x[i-1],transition_matrix)
        x+=[vec]
    Q=[]
    for i in range(0, len(x)-1):
        runs=np.matmul(np.matmul(x[i], run_matrix()), x[i+1])
        Q+=[runs]
    return sum(Q)*9
