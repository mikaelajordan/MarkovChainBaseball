from helper.setup import *

#2 lines below are equivalent
baserunners = it.chain.from_iterable(it.combinations(range(1,4), r) for r in range(4))
#baserunners = (x for r in range(4) for x in it.combinations(range(1,4), r))

states = it.product(range(3),baserunners)
states = pd.DataFrame.from_records(states,columns=["outs","baserunners"])
states['num_baserunners'] = states['baserunners'].apply(len)

#Handle runs scored during inning ending play
end = states.iloc[:4].copy()
for runs in range(4):
    end.ix[runs] = [3,runs,runs]
states = states.append(end,ignore_index=True)

header = states.iloc[:,:2]
states['o+b'] = states['outs'] + states['num_baserunners']

#rbis on play = (o+b)_before - (o+b)_after + 1
rbi = np.subtract.outer(states['o+b'],states['o+b'])+1
rbi = pd.DataFrame(rbi,index=header,columns=header)

#Play invalid if negative rbi's
rbi_valid = rbi >= 0
#Play invalid if num outs decreases.  Two lines below are equivalent.
outs_valid = np.less_equal.outer(states['outs'],states['outs'])
#outs_valid = np.subtract.outer(states['outs'],states['outs']) <= 0

valid = rbi_valid & outs_valid
#If play invalid, set entry in rbi matrix to -1
rbi[~valid] = -1
#Drop ROWS for inning ending plays because play can not BEGIN in such a state.
#Keep COLUMNS because play can END in such a state.
rbi = rbi.iloc[:-4]
#display(rbi)

def margins(df):
    #Appends row and column totals
    df = pd.DataFrame(df)
    col_sums = df.sum(axis=0)
    df.loc['TOTAL'] = col_sums
    row_sums = df.sum(axis=1)
    df['TOTAL'] = row_sums
    return df
valid = rbi>=0
#display(margins(valid))


#Define player types and their transition matrices.
player_types = pd.DataFrame(index = ['power','contact','speed','mendoza'])

#Fill with random numbers
#def make_rand_T():
#    T = rbi.copy() #So that row and column size and headers are copied
#    T[:] = np.random.rand(*T.shape) #fill with random
#    T[~valid]=0 #Set prob of invalid plays to 0
#    return T.div(T.sum(axis=1), axis=0) #normalize rows to sum to 1
#player_types['T'] = [make_rand_T() for d in player_types.index]
#display(margins(player_type.ix['power','T']))


#Make crude "typical" random matrices - batting average mean=~.270, std=~.030
#d_outs is number of outs on the play
d_outs = np.subtract.outer(states['outs'],states['outs']).T
d_outs = pd.DataFrame(d_outs,index=header,columns=header)
d_outs = d_outs.ix[:-4,:]
d_outs[~valid] = -1

#f take the prob of hit/out and divides it equally among all possible ways to make a hit/out.
def f(r,bat_ave):    
    #c counts all ways to make 0, 1, 2, or 3 outs during this AB.
    c = r.value_counts()
    #d is total prob of making 0, 1, 2, or 3 outs during this AB.
    #Note d[-1]=0 (impossible) and d[3]=0 (triple plays are extremely rare)
    d = c*0    
    d[0] = bat_ave
    #Give double play 5% prob (if double play is possible in state_in)
    try:
        if c.ix[2] > 0:
            d[2] = 50
    except:
        #fails if 2 is not in c OR if c[2]=0
        pass
    #Remaining prob given to 1 out
    d[1] = 1000 - d.sum()
    #normalizes d
    d /= d.sum()
    #divides by # of ways to make 0, 1, 2, or 3 outs during this AB.
    e = (d/c).fillna(0)
    #fill transition matrix row
    return r.replace(e)

#batting ave center at 0.270 with std .090
player_types['bat_ave'] = 270 + 90*np.random.randn(player_types.shape[0])

player_types['T'] = [d_outs.apply(f,args=[player_types.ix[p,'bat_ave']],axis=1)
                     for p in player_types.index]


#Make our team's roster
players = pd.DataFrame(index = ['Adam','David','Joseph','Mary','Mikaela','Parker','Archie',
                               'Taylor','Bobby','Wesley','Chad','Jeanne','Gerardo','Richard'])
def make_rand_coefs():
    #Each player is a linear combination of the player types above.  For now, random.
    c = np.random.rand(player_types.shape[0])
    return c/c.sum() #normalize so coefs sum to 1
players['coefs'] = [make_rand_coefs() for p in players.index]

#Each player has a unique T which is a linear combination of the player type T's
#using that player's coefs as weights.
players['T'] = [players.ix[p,'coefs'].dot(player_types['T']).values for p in players.index]
players['bat_ave'] = [players.ix[p,'coefs'].dot(player_types['bat_ave']) for p in players.index]

#display(margins(player.ix['David','T']))

os.makedirs('./data', exist_ok=True) 
states.to_csv('./data/states.csv',index=True,header=True)
rbi.to_csv('./data/rbi.csv',index=True,header=True)
players.to_json('./data/players.json',orient='index')

print("Matrix creation complete")