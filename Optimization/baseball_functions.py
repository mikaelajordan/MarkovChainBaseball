

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



def get_raw_data():
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
    for filename in os.listdir():
        df = pd.read_csv(filename, header=None)
        print(filename, df.shape)
        batting = batting.append(df)
    os.chdir('..')
    batting.columns = data_cols
    return(batting)
